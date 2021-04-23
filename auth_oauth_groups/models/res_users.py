# Copyright 2021 Avoin.Systems <https://avoin.systems>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from logging import getLogger
from odoo import SUPERUSER_ID, api, models, registry
from odoo.exceptions import ValidationError

_logger = getLogger(__name__)


class ResUsers(models.Model):
    _inherit = "res.users"

    @classmethod
    def _login(cls, db, login, password):
        user_id = super()._login(db, login, password)
        if not user_id:
            return user_id
        with registry(db).cursor() as cr:
            env = api.Environment(cr, SUPERUSER_ID, {})
            user = env["res.users"].browse(user_id)
            if user.oauth_provider_id.provider_service:
                user._update_groups_from_directory()
        return user_id

    def get_directory_groups(self):
        """
        Gets the directory groups from an external system.
        Should be implemented in specific provider modules.
        :return: A list of identifiers of groups that the user belongs to in an external directory.
        """
        return []

    def _update_groups_from_directory(self):
        self.ensure_one()

        sudo_self = self.sudo().with_context(no_reset_password=True)
        provider = sudo_self.oauth_provider_id

        # Get the user's directory groups
        users_directory_groups = self.get_directory_groups()

        # Get the groups from the group mapping and the user's existing groups
        new_odoo_group_mappings = provider.group_mapping_ids \
            .filtered(lambda m: m.directory_group_id.group_identifier in users_directory_groups)
        new_odoo_groups = new_odoo_group_mappings.group_id

        # Check if Odoo was able to find matches for all group IDs
        if provider.new_groups_handling == "ignore":
            # Do nothing
            pass
        elif provider.new_groups_handling == "warn":
            # Log a warning
            unknown_groups = set(users_directory_groups) - \
                             set(new_odoo_group_mappings.mapped("directory_group_id.group_identifier"))
            if unknown_groups:
                _logger.warning(
                    f"User '{self.login}' logged in using OAuth provider '{provider.name}' belongs to the following "
                    f"directory groups that don't exist in Odoo: {list(unknown_groups)}")

        existing_odoo_groups = self.groups_id

        # If there are multiple user types (internal, portal, public) defined in the group mappings,
        # fail the login because that would lead to an unresolvable situation.
        user_type_category = self.env.ref('base.module_category_user_type', raise_if_not_found=False)
        user_type_groups = self.env['res.groups'].search([('category_id', '=', user_type_category.id)])
        conflicting_groups = user_type_groups & new_odoo_groups
        if len(conflicting_groups) > 1:
            user_type_group_names = ", ".join(user_type_groups.mapped("name"))
            conflicting_group_names = ", ".join(conflicting_groups.mapped("name"))
            raise ValidationError(
                f"OAuth provider {provider.name} has conflicting group mappings: {conflicting_group_names}. "
                f"A single user can belong to only one of the following groups at once: {user_type_group_names}."
            )

        # Find groups that the user didn't belong to prior to this login
        groups_to_add = new_odoo_groups - existing_odoo_groups

        if provider.force_groups:
            groups_to_remove = existing_odoo_groups - new_odoo_groups
            if groups_to_add or groups_to_remove:
                sudo_self.write({'groups_id': [(6, 0, new_odoo_groups.ids or [self.env.ref("base.group_public").id])]})
        else:
            groups_to_remove = self.env['res.groups']
            if not groups_to_add:
                # Nothing to do
                return

            # Make sure that the user only belongs to one of the following groups. This is a restriction set by Odoo.
            # Remove them from the other groups.
            groups_to_add_transitive = (groups_to_add | groups_to_add.trans_implied_ids)

            implicit_removals = []
            for user_type_group in user_type_groups:
                other_essential_groups = user_type_groups - user_type_group
                if user_type_group in sudo_self.groups_id and other_essential_groups & groups_to_add_transitive:
                    implicit_removals.append((3, user_type_group.id))
                    groups_to_remove += user_type_group

            sudo_self.write({'groups_id': implicit_removals + [(4, group_id) for group_id in groups_to_add.ids]})

        _logger.info(f"Added user {self.login} to groups {sorted(groups_to_add.ids)} "
                     f"and removed from groups {sorted(groups_to_remove.ids)}")

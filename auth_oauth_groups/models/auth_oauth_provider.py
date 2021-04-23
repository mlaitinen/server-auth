# Copyright 2021 Avoin.Systems <https://avoin.systems>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from logging import getLogger

from odoo import fields, models

_logger = getLogger(__name__)


class AuthOauthProvider(models.Model):
    _inherit = "auth.oauth.provider"

    oauth_group_ids = fields.One2many(
        "auth.oauth.group",
        "provider_id",
        "Directory Groups",
        help="All groups related to this OAuth provider"
    )

    group_mapping_ids = fields.One2many(
        "auth.oauth.group_mapping",
        "provider_id",
        "Group Mappings",
        help="Map directory groups to Odoo groups",
    )

    force_groups = fields.Boolean(
        "Force Groups",
        default=False,
        help=(
            "When enabled, manual changes to group membership are overridden "
            "on every login, so Odoo groups are always synchronous "
            "with directory groups. If not, manually added groups are preserved."
        ),
    )

    provider_service = fields.Selection(
        string="OAuth Provider",
        selection=[],
        default=False,
        required=False,
        help="Choose which OAuth provider to use with group mapping."
    )

    new_groups_handling = fields.Selection(
        string="Handling of New Groups",
        selection=[
            ("warn", "Log a Warning"),
            ("ignore", "Ignore"),
        ],
        default="warn",
        required=True,
        help="Decide what to do when a user logs in using this OAuth provider and belongs to a directory group "
             "that Odoo doesn't identify, ie. there is no matching OAuth Group."
    )

    def refresh_groups(self):
        """
        Refresh the directory groups from an external system.
        The subclasses should implement this method.
        :return:
        """
        raise NotImplementedError()

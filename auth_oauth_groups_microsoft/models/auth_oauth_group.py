# Copyright 2021 Avoin.Systems <https://avoin.systems>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import models, fields, _


class AuthOauthGroup(models.Model):
    _inherit = "auth.oauth.group"

    provider_service = fields.Selection(
        related="provider_id.provider_service",
        store=False,
    )

    def import_users(self):
        """
        Import Active Directory users from specific groups as
        Odoo users.
        :return:
        """
        self.ensure_one()
        if self.provider_service != "microsoft":
            return super().import_users()

        return {
            "name": _("Import Users from Microsoft Graph API"),
            "view_type": "form",
            "view_mode": "form",
            "view_id": self.env.ref("auth_oauth_groups_microsoft.view_res_users_microsoft_wizard").id,
            "res_model": "res.users.microsoft.wizard",
            "type": "ir.actions.act_window",
            "target": "new",
        }

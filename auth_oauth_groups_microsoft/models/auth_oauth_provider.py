# Copyright 2021 Avoin.Systems <https://avoin.systems>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from logging import getLogger

from odoo import _, fields, models

_logger = getLogger(__name__)


class AuthOauthProvider(models.Model):
    _inherit = "auth.oauth.provider"

    provider_service = fields.Selection(
        selection_add=[("microsoft", "Microsoft Active Directory")],
    )

    def refresh_groups(self):
        """
        Refresh the directory groups from Graph API.
        :return:
        """
        self.ensure_one()
        if self.provider_service != "microsoft":
            return super().refresh_groups()

        return {
            "name": _("Fetch Groups from Microsoft Graph API"),
            "view_type": "form",
            "view_mode": "form",
            "view_id": self.env.ref("auth_oauth_groups_microsoft.view_auth_oauth_group_microsoft_wizard").id,
            "res_model": "auth.oauth.group.microsoft.wizard",
            "type": "ir.actions.act_window",
            "target": "new",
        }

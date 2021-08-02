# Copyright 2021 Avoin.Systems <https://avoin.systems>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import logging
import requests
from odoo import fields, _
from odoo.exceptions import UserError
from odoo.models import TransientModel

_logger = logging.getLogger(__name__)


class ImportUsers(TransientModel):
    _name = "res.users.microsoft.wizard"
    _description = "Import Users from Microsoft Azure Groups"

    def _default_group_id(self):
        return self.env["auth.oauth.group"].browse(self.env.context.get("active_id"))

    group_id = fields.Many2one(
        "auth.oauth.group",
        "OAuth Group",
        default=lambda self: self._default_group_id(),
        required=True,
    )

    access_token = fields.Char(
        "Access Token",
        required=True,
        help="The access token to use when connecting to Microsoft Graph API. Can be copied from a recently logged-in "
             "user's User form view."
    )

    def import_users(self):
        """
        Import the group's users from Graph API.
        :return:
        """
        self.ensure_one()

        def recursive_get_graph(url):
            """
            A recursive method for fetching paged results.
            :param url: The URL from where to get the AD groups.
            :return: A list of results
            """
            if not url:
                return []

            response = requests.get(
                url,
                headers={"Authorization": "Bearer {}".format(self.access_token)},
            )
            if response.status_code != 200:
                raise UserError(f"Graph API call failed with status {response.status_code}: {response.text}")

            json_res = response.json()
            page_results = [{"oauth_uid": val["id"],
                             "oauth_provider_id": self.group_id.provider_id.id,
                             "name": val["displayName"],
                             "login": val["userPrincipalName"],
                             "email": val["mail"]}
                            for val in json_res["value"]]
            next_link = json_res["@odata.nextLink"] if "@odata.nextLink" in json_res else False
            return page_results + recursive_get_graph(next_link)

        url = f"https://graph.microsoft.com/v1.0/groups/{self.group_id.group_identifier}/members?$count=true"
        users = recursive_get_graph(url)

        existing_logins = [val["login"] for val in self.env["res.users"].search_read([], ["login"])]

        # Look for users that don't exist in Odoo
        new_user_vals = [
            user for user in users
            if user["login"] not in existing_logins
        ]
        new_users = self.env["res.users"].create(new_user_vals)

        if new_users:
            _logger.info(f"User import complete. "
                         f"Added {len(new_users)} new users for group \"{self.group_id.name}\"")
            return {
                "name": _("New Users"),
                "views": [(self.env.ref("base.view_users_tree").id, "tree"),
                          (self.env.ref("base.view_users_form").id, "form")],
                "res_model": "res.users",
                "type": "ir.actions.act_window",
                "domain": [("id", "in", new_users.ids)],
            }
        else:
            msg = "User import complete. No new users were found."
            _logger.info(msg)
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": "No New Users Found",
                    "message": msg,
                    "sticky": False,
                }
            }

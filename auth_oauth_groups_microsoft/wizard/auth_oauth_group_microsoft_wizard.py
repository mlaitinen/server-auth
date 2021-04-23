# Copyright 2021 Avoin.Systems <https://avoin.systems>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import logging
import requests
from odoo import fields, _
from odoo.exceptions import UserError
from odoo.models import TransientModel

_logger = logging.getLogger(__name__)


class RefreshGroups(TransientModel):
    _name = "auth.oauth.group.microsoft.wizard"
    _description = "Refresh Microsoft Azure Groups"

    def _default_provider_id(self):
        return self.env["auth.oauth.provider"].browse(self.env.context.get("active_id"))

    provider_id = fields.Many2one(
        "auth.oauth.provider",
        "OAuth Provider",
        default=lambda self: self._default_provider_id(),
        required=True,
    )

    access_token = fields.Char(
        "Access Token",
        required=True,
        help="The access token to use when connecting to Microsoft Graph API. Can be copied from a recently logged-in "
             "user's User form view."
    )

    search_filter = fields.Char(
        "API Search Filter",
        help="See filter syntax at https://docs.microsoft.com/en-us/graph/api/group-list?view=graph-rest-1.0&tabs=http."
             "Example: `startswith(displayName, 'MyGroupPrefix')`"
    )

    def fetch_groups(self):
        """
        Refresh the directory groups from Graph API.
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
            page_results = [{"group_identifier": val["id"],
                             "name": val["displayName"],
                             "provider_id": self.provider_id.id}
                            for val in json_res["value"]]
            next_link = json_res["@odata.nextLink"] if "@odata.nextLink" in json_res else False
            return page_results + recursive_get_graph(next_link)

        url = "https://graph.microsoft.com/v1.0/groups"
        if self.search_filter:
            url += f"?$filter={self.search_filter}"

        ad_groups = recursive_get_graph(url)

        existing_group_identifiers = self.provider_id.oauth_group_ids.mapped("group_identifier") or []

        # Look for AD groups that don"t exist in Odoo
        new_ad_groups_vals = [
            ad_group for ad_group in ad_groups
            if ad_group["group_identifier"] not in existing_group_identifiers
        ]
        new_groups = self.env["auth.oauth.group"].create(new_ad_groups_vals)

        if new_groups:
            _logger.info(f"Group refresh complete. "
                         f"Added {len(new_groups)} new directory groups for provider \"{self.provider_id.name}\"")
            return {
                "name": _("New OAuth Groups"),
                "views": [(self.env.ref("auth_oauth_groups.view_oauth_group_tree").id, "tree")],
                "res_model": "auth.oauth.group",
                "type": "ir.actions.act_window",
                "domain": [("id", "in", new_groups.ids)],
            }
        else:
            msg = "Group refresh complete. No new directory groups to add."
            _logger.info(msg)
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": "No New Groups Found",
                    "message": msg,
                    "sticky": False,
                }
            }

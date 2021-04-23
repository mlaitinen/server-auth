# Copyright 2021 Avoin.Systems <https://avoin.systems>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from logging import getLogger

import requests
from odoo import models
from odoo.exceptions import UserError

_logger = getLogger(__name__)


class ResUsers(models.Model):
    _inherit = "res.users"

    def get_directory_groups(self):
        """
        Gets the directory groups from Azure Active Directory.
        :return:
        """

        self.ensure_one()
        if self.oauth_provider_id.provider_service != "microsoft":
            return super().get_directory_groups()

        def recursive_get_memberships(url):
            """
            A recursive method for fetching paged group memberships.
            :param url: The URL from where to get the AD group memberships.
            :return: A list of results
            """
            if not url:
                return []

            response = requests.post(
                url,
                headers={
                    "Authorization": "Bearer {}".format(self.oauth_access_token),
                    "Content-Type": "application/json"
                },
                json={"securityEnabledOnly": True},
            )

            if response.status_code != 200:
                raise UserError(f"Graph API call failed with status {response.status_code}: {response.text}")

            json_res = response.json()
            next_link = json_res["@odata.nextLink"] if "@odata.nextLink" in json_res else False
            return json_res["value"] + recursive_get_memberships(next_link)

        ad_groups = recursive_get_memberships(
            f"https://graph.microsoft.com/v1.0/users/{self.oauth_uid}/getMemberGroups",
        )

        return ad_groups

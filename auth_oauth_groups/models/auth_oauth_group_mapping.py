# Copyright 2021 Avoin.Systems <https://avoin.systems>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class AuthOauthGroupMapping(models.Model):
    _name = "auth.oauth.group_mapping"
    _description = "OAuth Group Mapping"
    _rec_name = "directory_group_id"
    _order = "directory_group_id"

    provider_id = fields.Many2one(
        "auth.oauth.provider",
        "OAuth Provider",
        required=True,
        ondelete="cascade",
    )

    directory_group_id = fields.Many2one(
        "auth.oauth.group",
        "Directory Group",
        help="The group in an external directory",
        required=True,
    )

    group_id = fields.Many2one(
        "res.groups",
        "Odoo Group",
        help="The Odoo group to assign to the directory group",
        required=True,
    )

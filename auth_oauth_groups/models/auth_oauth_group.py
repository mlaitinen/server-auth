# Copyright 2021 Avoin.Systems <https://avoin.systems>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import fields, models, api


class AuthOauthGroup(models.Model):
    _name = "auth.oauth.group"
    _rec_name = "name"
    _description = "Directory Groups"
    _sql_constraints = [(
        "identifier_provider_unique",
        "unique(group_identifier, provider_id)",
        "A provider can't have two directory groups with the same identifier"
    )]

    @api.depends("group_mapping_ids")
    def _has_group_mappings(self):
        for group in self:
            group.has_group_mappings = bool(group.group_mapping_ids.ids)

    provider_id = fields.Many2one(
        "auth.oauth.provider",
        "OAuth Provider",
        required=True,
        ondelete="restrict",
    )

    group_identifier = fields.Char(
        "Group Identifier",
        required=True,
        help="A unique identifier of the group in an external system",
    )

    name = fields.Char(
        required=True,
    )

    group_mapping_ids = fields.One2many(
        "auth.oauth.group_mapping",
        "directory_group_id",
        "Mappings",
        auto_join=True,
        readonly=True,
    )

    has_group_mappings = fields.Boolean(
        "Has Mappings",
        compute=_has_group_mappings,
        store=True,
    )

# Copyright 2021 Avoin.Systems <https://avoin.systems>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "OAuth Group Mapping",
    "version": "13.0.1.0.0",
    "website": "https://github.com/OCA/server-auth",
    "depends": [
        "auth_oauth",
    ],
    "author": "Avoin.Systems, " "Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "summary": "Maps external directory groups to Odoo groups",
    "category": "Authentication",
    "data": [
        "views/auth_oauth_group_views.xml",
        "views/auth_oauth_provider_views.xml",
        "security/ir.model.access.csv"
    ],
}

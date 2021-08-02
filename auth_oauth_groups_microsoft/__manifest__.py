# Copyright 2021 Avoin.Systems <https://avoin.systems>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "OAuth Group Mapping for Azure AD",
    "version": "13.0.1.1.0",
    "website": "https://github.com/OCA/server-auth",
    "depends": [
        "auth_oauth_groups",
        "auth_oauth_microsoft_graph",
    ],
    "author": "Avoin.Systems, " "Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "summary": "Maps external directory groups from Azure Active "
               "Directory to Odoo groups and import users",
    "category": "Authentication",
    "data": [
        "views/auth_oauth_group_views.xml",
        "wizard/auth_oauth_group_microsoft_wizard_views.xml",
        "wizard/res_users_microsoft_wizard_views.xml",
    ],
}

.. image:: https://img.shields.io/badge/license-AGPL--3-blue.png
   :target: https://www.gnu.org/licenses/agpl
   :alt: License: AGPL-3

Automatically assign users belonging to external directory groups to Odoo groups.

The purpose of this module is to act as an abstract base for OAuth Provider specific modules. It
 * adds the OAuth Group model
 * adds the OAuth Group Mapping model
 * takes care of assigning users to correct Odoo groups based on directory group mapping.

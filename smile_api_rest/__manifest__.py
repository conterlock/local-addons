# -*- encoding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2017 Smile (<http://www.smile.fr>). All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    "name": "REST API",
    "version": "0.1",
    "sequence": 100,
    "category": "Tools",
    "author": "Smile",
    "license": 'AGPL-3',
    "website": 'http://www.smile.fr',
    "description": """
There are URIs available:

/api/auth                   POST    - Login in Odoo and set cookies

/api/<model>                GET     - Read all (with optional domain, fields, offset, limit, order)
/api/<model>/<id>           GET     - Read one (with optional fields)
/api/<model>                POST    - Create one
/api/<model>/<id>           PUT     - Update one
/api/<model>/<id>           DELETE  - Delete one
/api/<model>/<id>/<method>  PUT     - Call method (with optional parameters)

WARNING: before calling /api/auth, call /web?db=*** otherwise web service is not found.

Suggestions & Feedback to: Corentin POUHET-BRUNERIE
    """,
    "depends": [
        'base',
    ],
    "data": [],
    "test": [],
    'installable': True,
    'auto_install': False,
    'application': False,
}

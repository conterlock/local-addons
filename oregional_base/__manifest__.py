# -*- coding: utf-8 -*-
{
    'name': "Oregional Base",  # Name first, others listed in alphabetical order
    'application': False,
    'author': "Oregional Kft.",
    'auto_install': False,
    'category': "Tools",  # Odoo Marketplace category
    'currency': "EUR",
    'data': [  # Files are processed in the order of listing
        'security/res_groups.xml',
        'views/ir_module_module.xml',
        'views/res_config_settings.xml',
        'views/menu.xml',
    ],
    'demo': [],
    'depends': [  # Include only direct dependencies
        'base',
    ],
    'description': "",  # Leave description empty
    'images': [  # Odoo Marketplace banner
        'static/description/oregional_base_banner.png',
    ],
    'installable': True,
    'license': "LGPL-3",
    'price': 0,
    'summary': "List and manage Oregional Odoo Apps",
    'test': [],
    'version': "1.0.5",
    'website': "https://oregional.hu",
}

# -*- coding: utf-8 -*-
{
    'name': "Oregional REST API",  # Name first, others listed in alphabetical order
    'application': False,
    'author': "Oregional Kft.",
    'auto_install': False,
    'category': "Tools",  # Odoo Marketplace category
    'currency': "EUR",
    'data': [  # Files are processed in the order of listing
        'data/model_scheme_data.xml',
        'data/model_configuration_data.xml',
        'security/res_groups.xml',
        'security/ir.model.access.csv',
        'views/application.xml',
        'views/application_uri.xml',
        'views/authorization.xml',
        'views/authorization_code.xml',
        'views/authorization_uri.xml',
        'views/model_configuration.xml',
        'views/model_scheme.xml',
        'views/res_users.xml',
        'views/res_config_settings.xml',
        'views/menu.xml',
    ],
    'demo': [],
    'depends': [  # Include only direct dependencies
        'mail',
        'oregional_base'
    ],
    'description': "",  # Leave description empty
    'images': [  # Odoo Marketplace banner
        'static/description/oregional_restapi_banner.png',
    ],
    'installable': True,
    'license': "LGPL-3",
    'price': 0,
    'summary': "REST API for common and specific resources",
    'test': [],
    'version': "1.6.4",
    'website': "https://oregional.hu",
}

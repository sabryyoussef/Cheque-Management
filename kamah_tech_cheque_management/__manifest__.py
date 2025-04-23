# -*- coding: utf-8 -*-
{
    'name': 'Kamah Tech Cheque Management',
    'version': '17.0.1.0.0',
    'category': 'Accounting',
    'summary': 'Advanced Cheque Management System',
    'description': """
        This module provides advanced cheque management functionality with:
        * Custom search views
        * Multiple search boxes
        * Advanced filtering options
        * Comprehensive cheque tracking
    """,
    'author': 'Sabry Youssef',
    'website': 'https://github.com/sabryyoussef',
    'maintainer': 'Sabry Youssef',
    'support': 'vendorah2@gmail.com',
    'depends': ['base', 'account', 'mail'],
    'data': [
        'wizard/check_cycle_wizard_view.xml',
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'data/sms_temp.xml',
        'views/cheque_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'kamah_tech_cheque_management/static/src/scss/cheque_management.scss',
        ],
    },
    'images': ['static/description/banner.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}

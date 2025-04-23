# -*- coding: utf-8 -*-
{
    'name': 'Kamah Tech Cheque Management',
    'version': '18.0.1.0.0',
    'category': 'Accounting',
    'summary': 'Advanced Cheque Management System',
    'description': """
        This module provides advanced cheque management functionality with:
        * Custom search views
        * Multiple search boxes
        * Advanced filtering options
        * Comprehensive cheque tracking
    """,
    'author': 'Kamah Tech',
    'website': 'https://www.kamahtech.com',
    'depends': ['base', 'account'],
    'data': [
        'security/ir.model.access.csv',
        'views/cheque_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}

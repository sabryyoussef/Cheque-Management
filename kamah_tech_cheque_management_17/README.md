# Cheque Management System for Odoo 17

A comprehensive cheque management module for Odoo 17 that enables efficient handling of incoming and outgoing cheques.

## Features

- Complete cheque lifecycle management (Draft → Registered → Received → Deposited → Cleared/Returned)
- Support for both incoming and outgoing cheques
- Advanced filtering and search capabilities
- Integrated with Odoo accounting module
- Automatic journal entries for each cheque state
- Comprehensive tracking system
- Bank integration support
- Multi-company support

## Installation

1. Clone this repository into your Odoo addons directory:
```bash
git clone https://github.com/sabryyoussef/kamah_tech_cheque_management.git
```

2. Update your Odoo addons path to include this module
3. Install the module through Odoo's module installation interface

## Configuration

1. Go to Settings → Users → Access Rights
2. Ensure users have proper accounting access rights
3. Configure default journals for cheque operations

## Usage

### Managing Cheques

1. Navigate to Cheque Management → Cheques
2. Create a new cheque record
3. Fill in required information:
   - Cheque Number
   - Partner
   - Bank
   - Amount
   - Due Date
4. Progress the cheque through its lifecycle using the action buttons

## Support

For support, please contact:
- Email: vendorah2@gmail.com
- Author: Sabry Youssef

## License

This module is licensed under LGPL-3.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
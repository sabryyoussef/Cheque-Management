from odoo import models, fields, api, exceptions, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    check_return_journal = fields.Many2one(
        'account.journal', 
        string="Return Journal",
        config_parameter='kamah_tech_cheque_management.check_return_journal_id')

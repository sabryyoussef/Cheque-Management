from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from dateutil.relativedelta import relativedelta


class CheckCycleWizard(models.TransientModel):
    _name = 'check.cycle.wizard'
    _description = 'Check Cycle Management Wizard'

    name = fields.Char(default="Please choose the bank Account", readonly=True)
    name_cancel = fields.Char(default="Are you sure you want to cancel the checks", readonly=True)
    name_reject = fields.Char(default="Are you sure you want to reject the checks", readonly=True)
    name_return = fields.Char(default="Are you sure you want to return the checks to company", readonly=True)
    name_approve = fields.Char(default="Please choose the bank Account", readonly=True)
    name_debit = fields.Char(default="Please choose the bank Account", readonly=True)
    name_csreturn = fields.Char(default="Are you sure you want to return the checks to customer", readonly=True)
    name_split_merge = fields.Char(default="Please create the new checks", readonly=True)
    account_id = fields.Many2one('account.account', string="Account")
    journal_id = fields.Many2one('account.journal', string="Journal", 
        domain="[('type', 'in', ['bank', 'cash'])]")
    reject_reason = fields.Html(string="Rejection reason")
    check_ids = fields.Many2many('cheque.management', string="Checks")
    total_amount = fields.Monetary(string="Total Amount", compute="_compute_total_amount", store=True)
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id')
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    partner_id = fields.Many2one('res.partner', string="Partner")

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        if self.env.context.get('active_model') == 'cheque.management' and self.env.context.get('active_ids'):
            res['check_ids'] = [(6, 0, self.env.context['active_ids'])]
        return res

    @api.depends('check_ids')
    def _compute_total_amount(self):
        for wizard in self:
            wizard.total_amount = sum(wizard.check_ids.mapped('amount'))

    def action_deposit(self):
        self.ensure_one()
        if not self.journal_id:
            raise ValidationError(_("Please select a bank journal first."))
            
        for check in self.check_ids:
            # Create move
            move_vals = {
                'journal_id': self.journal_id.id,
                'date': fields.Date.context_today(self),
                'ref': _('Deposit Check %s', check.name),
                'partner_id': check.partner_id.id,
            }
            
            line_vals = [
                # Debit bank account
                {
                    'name': _('Deposit Check %s', check.name),
                    'account_id': self.journal_id.default_account_id.id,
                    'partner_id': check.partner_id.id,
                    'debit': check.amount,
                    'credit': 0.0,
                },
                # Credit notes receivable account
                {
                    'name': _('Deposit Check %s', check.name),
                    'account_id': check.journal_id.default_account_id.id,
                    'partner_id': check.partner_id.id,
                    'debit': 0.0,
                    'credit': check.amount,
                }
            ]
            
            move_vals['line_ids'] = [(0, 0, line) for line in line_vals]
            move = self.env['account.move'].create(move_vals)
            move.action_post()
            
            check.write({
                'state': 'deposited',
                'move_id': move.id,
            })
            
        return {'type': 'ir.actions.act_window_close'}

    def action_reject(self):
        self.ensure_one()
        if not self.reject_reason:
            raise ValidationError(_("Please provide a rejection reason."))
            
        for check in self.check_ids:
            check.write({
                'state': 'returned',
                'memo': self.reject_reason,
            })
            check.message_post(body=_("Check rejected. Reason: %s", self.reject_reason))
            
        return {'type': 'ir.actions.act_window_close'}

    def action_clear(self):
        self.ensure_one()
        self.check_ids.write({'state': 'cleared'})
        return {'type': 'ir.actions.act_window_close'}


class ApproveCheckLines(models.TransientModel):
    _name = 'appove.check.lines'
    _description = 'Approve Check Lines'

    check_number = fields.Char()
    check_id = fields.Integer()
    check_amt = fields.Float()
    paid_amt = fields.Float()
    open_amt = fields.Float()


class SplitMergeCheck(models.TransientModel):
    _name = 'split.merge.check'
    _description = 'Split Merge Check'
    _order = 'check_number asc'

    check_number = fields.Char(string=_("Check number"), required=True)
    check_date = fields.Date(string=_('Check Date'), required=True)
    amount = fields.Float(string=_('Amount'), required=True)
    bank = fields.Many2one('res.bank', string=_("Check Bank Name"))
    dep_bank = fields.Many2one('res.bank', string=_("Depoist Bank"))

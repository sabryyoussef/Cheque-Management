# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _
from datetime import date, datetime, time, timedelta
import odoo.addons.decimal_precision as dp


class normal_payments(models.Model):
    _name = 'normal.payments'
    _rec_name = 'name'
    _description = 'Payments'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = "company_id"
    _check_company_auto = True

    def get_user(self):
        return self._uid

    def get_currency(self):
        return self.env['res.users'].search([('id', '=', self.env.user.id)]).company_id.currency_id.id

    type = fields.Selection([
        ('advanced_payment', _('Advanced Payment')),
        ('performance', _('Performance')),
        ('retention', _('Retention')),
        ('bid_bond', _('Bid Bond')),
        ('guarantee', _('Guarantee')),
        ('final', _('Final')),
        ('payment', _('Pyament')),
        ('credit_facility', _('Credit Facility')),
        ('others', _('Others')),
    ])

    project_id = fields.Many2one('sale.order')

    payment_No = fields.Char()
    name = fields.Char(string="", required=False,
                       compute="get_title", readonly=True)
    partner_id = fields.Many2one(
        comodel_name="res.partner", string="Partner Name", required=True)
    company_id = fields.Many2one('res.company', string='Company', required=True, readonly=True,
                                 default=lambda self: self.env.company)
    payment_date = fields.Datetime(
        string="Payment Date", required=True, default=datetime.today())
    amount = fields.Float(
        string="Amount", compute="change_checks_ids", store=True)
    amount1 = fields.Float(string="Amount")
    payment_method = fields.Many2one(comodel_name="account.journal", string="Payment Journal", required=True,
                                     domain=[('type', 'in', ('bank', 'cash'))])
    payment_subtype = fields.Selection(
        related='payment_method.payment_subtype')
    user_id = fields.Many2one(comodel_name="res.users", default=get_user)
    currency_id = fields.Many2one(
        comodel_name="res.currency", default=get_currency)
    state = fields.Selection(selection=[('draft', 'Draft'), ('posted', 'Posted'), ], default='draft',
                             track_visibility='onchange')
    pay_check_ids = fields.One2many(
        'native.payments.check.create', 'nom_pay_id', string=_('Checks'))
    send_rec_money = fields.Selection(string="Payment Type", selection=[(
        'send', 'Send Money'), ('rece', 'Receive Money')], default='rece')
    receipt_number = fields.Char(string="Receipt Number", readonly=True,
                                 default=lambda self: self.env['ir.sequence'].next_by_code('check.payment'))
    account_id = fields.Many2one('account.account', string="Account")
    analyitc_id = fields.Many2one(
        'account.analytic.account', string="Analytic Account")
    computed_move_name = fields.Char(string="", required=False,
                                     readonly=True)

    def _compute_receipt_number(self):

        for rec in self:
            rec.receipt_number = "0"*(4-len(str(rec.id)))+str(rec.id)

    @api.constrains('amount')
    def _total_amount(self):
        if self.payment_subtype:
            if (self.amount) == 0.0:
                raise exceptions.ValidationError(
                    'amount for checks must be more than zerO!')
        else:
            if (self.amount1) == 0.0:
                raise exceptions.ValidationError(
                    'amount for payment must be more than zerO!')

    @api.onchange('partner_id', 'send_rec_money')
    def get_partner_acc(self):
        if self.partner_id:
            if self.send_rec_money == 'send':
                self.account_id = self.partner_id.property_account_payable_id.id
            elif self.send_rec_money == 'rece':
                self.account_id = self.partner_id.property_account_receivable_id.id

    @api.depends('pay_check_ids')
    def change_checks_ids(self):
        for rec in self:
            tot_amnt = 0.0
            if rec.sudo().payment_subtype:
                if rec.sudo().pay_check_ids:
                    for x in rec.sudo().pay_check_ids:
                        tot_amnt += x.amount
            rec.amount = tot_amnt

    def payment_journal_entries(self):
        return {
            'name': ('Journal Items'),
            'view_mode': 'tree',
            'res_model': 'account.move.line',
            'view_id': self.env.ref('account.view_move_line_tree').id,
            'type': 'ir.actions.act_window',
            'domain': [('jebal_con_pay_id', 'in', self.ids)],
        }

    @api.depends('partner_id', 'computed_move_name')
    def get_title(self):
        for rec in self:
            if rec.computed_move_name:
                rec.name = rec.computed_move_name
            elif rec.partner_id:
                rec.name = "Payment for Customer " + str(rec.partner_id.name)
            else:
                rec.name = '*'

        return True

    def action_confirm(self):
        for rec in self:
            pay_amt = 0
            if rec.payment_subtype:
                pay_amt = rec.amount
            else:
                pay_amt = rec.amount1
            move = {
                'name': 'Parnter Payment ' + 'Receipt:' + rec.receipt_number,
                'journal_id': rec.payment_method.id,
                'partner_id': rec.partner_id.id,
                'ref': rec.name,
                'company_id': rec.user_id.company_id.id,
            }
            move_line = {
                'name': 'Parnter Payment ' + 'Receipt:' + rec.receipt_number,
                'partner_id': rec.partner_id.id,
                'ref': rec.name,
                'jebal_con_pay_id': rec.id,
            }
            if rec.send_rec_money == 'send':
                debit_account = [{'account': rec.account_id.id,
                                  'percentage': 100, 'analyitc_id': rec.analyitc_id.id, }]
                credit_account = [
                    {'account': rec.payment_method.default_account_id.id, 'percentage': 100}]
            else:
                credit_account = [{'account': rec.account_id.id,
                                   'percentage': 100, 'analyitc_id': rec.analyitc_id.id, }]
                debit_account = [
                    {'account': rec.payment_method.default_account_id.id, 'percentage': 100}]
            rec.computed_move_name = rec.env['create.moves'].create_move_lines(move=move, move_line=move_line,
                                                                               debit_account=debit_account,
                                                                               credit_account=credit_account,
                                                                               src_currency=rec.currency_id,
                                                                               amount=pay_amt)
            rec.state = 'posted'
            if rec.payment_subtype:
                for check in rec.pay_check_ids:
                    check_line_val = {}
                    check_line_val['check_number'] = check.check_number
                    check_line_val['check_date'] = check.check_date
                    check_line_val['check_bank'] = check.bank.id
                    check_line_val['dep_bank'] = check.dep_bank.id
                    if rec.send_rec_money == 'rece':
                        check_line_val['state'] = 'holding'
                        check_line_val['check_type'] = 'rece'
                    else:
                        check_line_val['state'] = 'handed'
                        check_line_val['check_type'] = 'pay'
                    check_line_val['amount'] = check.amount
                    check_line_val['open_amount'] = check.amount
                    check_line_val['type'] = 'regular'
                    check_line_val['notespayable_id'] = rec.payment_method.default_account_id.id
                    check_line_val['notes_rece_id'] = rec.payment_method.default_account_id.id
                    check_line_val['investor_id'] = rec.partner_id.id
                    rec.env['check.management'].create(check_line_val)
            return True

    @api.model
    def create(self, vals):
        result = super(normal_payments, self).create(vals)
        if result.project_id:
            result.project_id._compute_check()
        return result


class payments_check_create(models.Model):

    _name = 'native.payments.check.create'
    _order = 'check_number asc'

    check_number = fields.Char(string=_("Check number"), required=True)
    check_date = fields.Date(string=_('Check Date'), required=True)
    amount = fields.Float(string=_('Amount'), required=True)
    bank = fields.Many2one('res.bank', string=_("Check Bank Name"))
    dep_bank = fields.Many2one('res.bank', string=_("Depoist Bank"))
    nom_pay_id = fields.Many2one('normal.payments')

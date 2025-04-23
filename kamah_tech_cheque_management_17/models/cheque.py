from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime


class ChequeManagement(models.Model):
    _name = 'cheque.management'
    _description = 'Cheque Management'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc, id desc'

    name = fields.Char(string='Cheque Number', required=True, tracking=True, copy=False)
    partner_id = fields.Many2one('res.partner', string='Partner', required=True, tracking=True)
    bank_id = fields.Many2one('res.bank', string='Bank', required=True, tracking=True)
    amount = fields.Monetary(string='Amount', required=True, tracking=True)
    date = fields.Date(string='Cheque Date', required=True, tracking=True)
    due_date = fields.Date(string='Due Date', required=True, tracking=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('registered', 'Registered'),
        ('received', 'Received'),
        ('deposited', 'Deposited'),
        ('cleared', 'Cleared'),
        ('returned', 'Returned'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft', tracking=True)
    type = fields.Selection([
        ('incoming', 'Incoming'),
        ('outgoing', 'Outgoing')
    ], string='Type', required=True, tracking=True)
    memo = fields.Html(string='Memo')
    journal_id = fields.Many2one('account.journal', string='Journal', tracking=True, 
        domain="[('type', 'in', ['bank', 'cash'])]")
    move_id = fields.Many2one('account.move', string='Journal Entry', tracking=True, copy=False)
    company_id = fields.Many2one('res.company', string='Company', 
        default=lambda self: self.env.company, required=True)
    currency_id = fields.Many2one('res.currency', string='Currency',
        related='company_id.currency_id', store=True, readonly=True)
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('name'):
                vals['name'] = self.env['ir.sequence'].next_by_code('cheque.management') or '/'
        return super().create(vals_list)

    def action_register(self):
        for rec in self:
            if rec.state == 'draft':
                rec.write({'state': 'registered'})

    def action_receive(self):
        for rec in self:
            if rec.state == 'registered':
                rec.write({'state': 'received'})

    def action_deposit(self):
        for rec in self:
            if rec.state == 'received':
                if not rec.journal_id:
                    raise UserError(_("Please select a journal first!"))
                rec.write({'state': 'deposited'})

    def action_clear(self):
        for rec in self:
            if rec.state == 'deposited':
                rec.write({'state': 'cleared'})

    def action_return(self):
        for rec in self:
            if rec.state == 'deposited':
                rec.write({'state': 'returned'})

    def action_cancel(self):
        for rec in self:
            if rec.state in ['draft', 'registered', 'received']:
                rec.write({'state': 'cancelled'})

    @api.constrains('date', 'due_date')
    def _check_dates(self):
        for rec in self:
            if rec.due_date < rec.date:
                raise ValidationError(_("Due date cannot be earlier than cheque date!"))

    @api.constrains('amount')
    def _check_amount(self):
        for rec in self:
            if rec.amount <= 0:
                raise ValidationError(_("Amount must be greater than zero!"))
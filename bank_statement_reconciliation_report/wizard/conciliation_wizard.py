# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
import logging


class ConciliationWizard(models.Model):
    _name = 'conciliation.wizard'
    _description = 'Conciliation Wizard'

    name = fields.Char(string='Compte', compute='_compute_name')
    statement_id = fields.Many2one('account.bank.statement')
    journal_id = fields.Many2one('account.journal', related='statement_id.journal_id')
    date = fields.Date(string='Date', related='statement_id.date')
    balance_end_real = fields.Monetary(string='Ending Balance', related='statement_id.balance_end_real')
    payment_outbound_ids = fields.One2many('account.payment', 'rec_outbound_id', compute='_compute_outbond')
    total_outbound = fields.Monetary(string='Total Oustanding Cheques')
    payment_inbound_ids = fields.One2many('account.payment', 'rec_inbound_id', compute='_compute_inbond')
    total_inbound = fields.Monetary(string='Oustanding Deposits')
    reconciliation_balance = fields.Monetary(string='Calculated Balance with Reconciliation')
    currency_id = fields.Many2one('res.currency')
    total_outbound = fields.Monetary(string='Total Outstanding Cheques', compute='_compute_outbond')
    total_inbound = fields.Monetary(string='Total Outstanding Deposits', compute='_compute_inbond')

    conciliation_balance = fields.Monetary(string='Calculated Balance with Reconciliation',
                                           compute='_compute_balance')
    difference = fields.Monetary(string='Difference',
                                 compute='_compute_balance')
    account_balance = fields.Monetary(string='Total Outstanding Deposits', compute='_compute_balance')

    @api.depends('journal_id')
    def _compute_name(self):
        for item in self:
            item.name = "%s - %s" % (item.journal_id.code, item.journal_id.default_debit_account_id.name)

    def _compute_outbond(self):
        AccountPayment = self.env['account.payment']
        outbound_domain = [('payment_type', '=', 'outbound'), ('journal_id', '=', self.journal_id.id),
                           ('state', 'in', ['posted', 'sent'])]
        outbound_ids = AccountPayment.search(outbound_domain)
        for item in self:
            item.payment_outbound_ids = [(6, 0, outbound_ids.ids)]
            item.total_outbound = sum(outbound_ids.mapped('amount'))

    def _compute_inbond(self):
        AccountPayment = self.env['account.payment']
        inbond_domain = [('payment_type', '=', 'inbound'), ('journal_id', '=', self.journal_id.id),
                         ('state', 'in', ['posted', 'sent'])]
        inbond_ids = AccountPayment.search(inbond_domain)
        for item in self:
            item.payment_inbound_ids = [(6, 0, inbond_ids.ids)]
            item.total_inbound = sum(inbond_ids.mapped('amount'))

    @api.depends('total_outbound', 'total_inbound')
    def _compute_balance(self):
        for item in self:
            item.conciliation_balance = item.balance_end_real - item.total_outbound - item.total_inbound
            item.account_balance = item.statement_id.get_account_balance()
            item.difference = item.conciliation_balance - item.account_balance

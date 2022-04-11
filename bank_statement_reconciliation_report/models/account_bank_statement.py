# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
import logging


class AccountBankStatement(models.Model):
    _inherit = 'account.bank.statement'

    conciliation_id = fields.Many2one('conciliation.wizard')

    @api.model
    def create(self, values):
        ConciliationWizard = self.env['conciliation.wizard']
        current_id = super(AccountBankStatement, self).create(values)
        wizard_id = ConciliationWizard.create({
            'statement_id': current_id.id,
        })
        current_id.conciliation_id = wizard_id.id
        return current_id

    def button_bank_conciliation(self):
        return {
            'name': _('Bank conciliation report'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'conciliation.wizard',
            'views': [(False, 'form')],
            'type': 'ir.actions.act_window',
            'target': 'new',
            'res_id': self.conciliation_id.id
        }

    def compute_outbond(self):
        AccountPayment = self.env['account.payment']
        outbound_domain = [('payment_type', '=', 'outbound'), ('journal_id', '=', self.journal_id.id),
                           ('state', 'in', ['posted', 'sent'])]
        outbound_ids = AccountPayment.search(outbound_domain)
        logging.info('Outound ids ----------------------')
        logging.info(outbound_ids)
        return outbound_ids

    def compute_inbond(self):
        AccountPayment = self.env['account.payment']
        inbond_domain = [('payment_type', '=', 'inbound'), ('journal_id', '=', self.journal_id.id),
                         ('state', 'in', ['posted', 'sent'])]
        inbound_ids = AccountPayment.search(inbond_domain)
        logging.info('Inbound ids ----------------------')
        logging.info(inbound_ids)
        return inbound_ids


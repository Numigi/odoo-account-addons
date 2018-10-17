# © 2017 Savoir-faire Linux
# © 2018 Numigi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, models


class AccountInvoice(models.Model):

    _inherit = 'account.invoice'

    @api.multi
    def action_invoice_open(self):
        super(AccountInvoice, self).action_invoice_open()

        for invoice in self:
            lines = invoice.mapped('move_id.line_ids.analytic_line_ids')
            lines.write({'source': 'account.invoice,%s' % invoice.id})

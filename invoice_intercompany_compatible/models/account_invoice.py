# © 2021 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, models


class AccountInvoice(models.Model):

    _inherit = 'account.invoice'

    @api.onchange("company_id")
    def _onchange_company_set_partner_bank(self):
        if self.company_id and self.type in ('out_invoice', 'in_refund'):
            self.partner_bank_id = self._get_partner_bank_id(self.company_id.id)

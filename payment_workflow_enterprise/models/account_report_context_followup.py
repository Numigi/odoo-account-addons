# -*- coding: utf-8 -*-
# © 2016 Savoir-faire Linux
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, models


class AccountReportContextFollowup(models.TransientModel):

    _inherit = 'account.report.context.followup'

    @api.depends('partner_id')
    @api.one
    def _get_invoice_address(self):
        if self.partner_id:
            self.invoice_address_id = self.partner_id.address_get(
                ['customer_payment'])['customer_payment']
        else:
            self.invoice_address_id = False

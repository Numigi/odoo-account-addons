# © 2017 Savoir-faire Linux
# © 2018 Numigi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, models


class AccountReportContextFollowup(models.TransientModel):

    _inherit = 'account.report.context.followup'

    @api.depends('partner_id')
    def _get_invoice_address(self):
        for partner in self:
            if partner.partner_id:
                partner.invoice_address_id = (
                    partner.partner_id.get_preferred_address(
                        ['customer_payment', 'invoice']))
            else:
                partner.invoice_address_id = False

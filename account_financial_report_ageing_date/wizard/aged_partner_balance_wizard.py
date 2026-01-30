# Copyright 2026 Numigi
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api, _


class AgedPartnerBalanceWizard(models.TransientModel):
    """ Inherit wizard to add the ageing method selection. """
    _inherit = 'aged.partner.balance.wizard'

    ageing_method = fields.Selection(
        selection=[
            ('date_due', 'Due Date'),
            ('date', 'Invoice Date'),
        ],
        string='Ageing Method',
        default='date_due',
        required=True,
        help="Choose 'Due Date' for collection analysis or 'Invoice Date' for financial analysis."
    )

    @api.onchange('ageing_method', 'show_move_line_details')
    def _onchange_ageing_method(self):
        """ Prevent selecting 'Invoice Date' if details are shown. """
        if self.ageing_method == 'date' and self.show_move_line_details:
            self.ageing_method = 'date_due'
            return {
                'warning': {
                    'title': _('Incompatible Options'),
                    'message': _('The "Invoice Date" ageing method is not compatible with "Show Move Line Details". '
                                 'Please disable details to use this method. '
                                 'The method has been reset to "Due Date".')
                }
            }

    def _prepare_report_aged_partner_balance(self):
        """ Override to pass the ageing_method to the transient report model. """
        res = super(AgedPartnerBalanceWizard, self)._prepare_report_aged_partner_balance()
        res['ageing_method'] = self.ageing_method
        return res
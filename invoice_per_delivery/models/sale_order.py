# © Numigi (tm) and all its contributors (https://numigi.com/r/home)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models

import logging
_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):

    _inherit = "sale.order"

    def _get_invoiceable_lines(self, final=False):
        """
        Select only sale order lines to invoice for the delivery order in context.
        Ensure down payment lines are kept so they can be correctly deducted.
        """
        invoiceable_lines = super()._get_invoiceable_lines(final)
        picking_id = self._context.get("picking_id", False)

        if not picking_id:
            return invoiceable_lines

        filtered_lines = invoiceable_lines.filtered(
            lambda line: (
                picking_id in line.move_ids.mapped("picking_id")
                or line.is_downpayment
            )
        )
        return filtered_lines

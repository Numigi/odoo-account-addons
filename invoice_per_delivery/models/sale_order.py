# Copyright 2024 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models

import logging
_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):

    _inherit = "sale.order"

    def _get_invoiceable_lines(self, final=False):
        """Select only sale order lines to invoice for the delevery order in context """
        invoiceable_lines = super()._get_invoiceable_lines(final)
        picking_id = self._context.get("picking_id", False)
        if picking_id:
            invoiceable_lines.filtered(
                lambda il: il.move_ids.mapped("picking_id") in [picking_id]
            )
        return invoiceable_lines

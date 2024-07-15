# Copyright 2024 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models


class SaleOrderLine(models.Model):

    _inherit = "sale.order.line"

    def _prepare_invoice_line(self, **optional_values):
        """
        Set the delivered qty as the quantity to invoice.
        """
        self.ensure_one()
        picking_id = self._context.get("picking_id", False)
        if picking_id:
            qty_to_invoice = self.move_ids.filtered(
                lambda m: m.picking_id == picking_id
            ).quantity_done
            res = super()._prepare_invoice_line(quantity=qty_to_invoice)
        else:
            res = super()._prepare_invoice_line()
        return res

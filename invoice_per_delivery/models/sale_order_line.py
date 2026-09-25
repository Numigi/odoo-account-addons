# © Numigi (tm) and all its contributors (https://numigi.com/r/home)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models


class SaleOrderLine(models.Model):

    _inherit = "sale.order.line"

    def _prepare_invoice_line(self, **optional_values):
        """
        Set the delivered qty as the quantity to invoice.
        Bypass this logic for down payment lines to keep standard Odoo behavior.
        """
        self.ensure_one()
        picking_id = self._context.get("picking_id", False)

        # If no picking in context or if it's a down payment, rely on standard logic
        if not picking_id or self.is_downpayment:
            return super()._prepare_invoice_line(**optional_values)

        # Retrieve the quantity actually done in the specific picking
        qty_to_invoice = sum(
            self.move_ids.filtered(
                lambda move: move.picking_id == picking_id
            ).mapped("quantity_done")
        )

        return super()._prepare_invoice_line(
            quantity=qty_to_invoice,
            **optional_values
        )

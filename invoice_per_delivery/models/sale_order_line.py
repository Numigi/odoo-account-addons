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

        # Retrieve the quantity actually done in the specific picking.
        # quantity_done is expressed in the move UoM (product base unit), which
        # may differ from the sale line UoM used on the invoice line. Convert it
        # so a delivery of 10 units on a "Pack of 10" line invoices 1 pack, not 10.
        moves = self.move_ids.filtered(
            lambda move: move.picking_id == picking_id
        )
        qty_to_invoice = sum(
            move.product_uom._compute_quantity(
                move.quantity_done, self.product_uom
            )
            for move in moves
        )

        return super()._prepare_invoice_line(
            quantity=qty_to_invoice,
            **optional_values
        )

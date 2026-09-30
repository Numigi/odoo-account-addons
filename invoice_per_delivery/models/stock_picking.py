# © Numigi (tm) and all its contributors (https://numigi.com/r/home)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models


class StockPicking(models.Model):

    _inherit = "stock.picking"

    def _create_invoice(self):
        self.ensure_one()
        if self.sale_id and self.partner_id.invoice_per_delivery:
            if any(line for line in self.sale_id.order_line
                    if line.product_uom_qty != line.qty_invoiced):
                # final=True so down payment lines (qty_to_invoice < 0) are kept
                # by the standard _get_invoiceable_lines and deducted from the
                # delivery invoice instead of being silently dropped.
                self.sale_id.sudo().with_context(
                    picking_id=self
                )._create_invoices(final=True)
        return

    def write(self, vals):
        for rec in self:
            outgoings = rec.filtered(
                lambda sp: (
                    sp.picking_type_code == "outgoing"
                    and sp.location_dest_id.usage == "customer"
                )
            )
            if (vals.get("date_done") and outgoings):
                rec._create_invoice()
        return super(StockPicking, self).write(vals)

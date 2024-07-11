# Copyright 2024 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class StockPicking(models.Model):

    _inherit = "stock.picking"

    invoice_id = fields.Many2one(
        string="Invoice",
        comodel_name="account.move",
        ondelete="restrict",
    )

    def action_view_invoice(self):
        form_view = [(self.env.ref("account.view_move_form").id, "form")]
        return {
            "type": "ir.actions.act_window",
            "name": "Invoice",
            "view_mode": "form",
            "views": form_view,
            "res_model": "account.move",
            "res_id": self.invoice_id.id,
            "domain": [("id", "=", self.invoice_id.id)],
        }

    def _create_invoice(self):
        self.ensure_one()
        if self.sale_id and self.partner_id.invoice_per_delivery:
            if any(line for line in self.sale_id.order_line
                    if line.product_uom_qty != line.qty_invoiced):
                invoice = self.sale_id.sudo().with_context(picking_id=self)._create_invoices()
                invoice.write({"picking_id": self.id})
                self.invoice_id = invoice

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

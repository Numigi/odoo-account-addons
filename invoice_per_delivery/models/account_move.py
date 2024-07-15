# Copyright 2024 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class AccountMove(models.Model):

    _inherit = "account.move"

    picking_id = fields.Many2one(
        string="Delivery",
        comodel_name="stock.picking",
        ondelete="restrict",
    )

    def action_view_delivery(self):
        form_view = [(self.env.ref("stock.view_picking_form").id, "form")]
        return {
            "type": "ir.actions.act_window",
            "name": "Delivery",
            "view_mode": "form",
            "views": form_view,
            "res_model": "stock.picking",
            "res_id": self.picking_id.id,
            "domain": [("id", "=", self.picking_id.id)],
        }

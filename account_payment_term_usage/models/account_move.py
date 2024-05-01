# © 2020 - today Numigi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class AccountMove(models.Model):

    _inherit = "account.move"

    payment_term_usage = fields.Selection(
        [
            ("sale", "Sales"),
            ("purchase", "Purchases"),
        ],
        compute="_compute_payment_term_usage",
    )

    @api.depends("move_type")
    def _compute_payment_term_usage(self):
        for move in self:
            if move.move_type in ("in_invoice", "in_refund"):
                move.payment_term_usage = "purchase"
            elif move.move_type in ("out_invoice", "out_refund"):
                move.payment_term_usage = "sale"
            else:
                move.payment_term_usage = False

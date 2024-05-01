# © 2023 Numigi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import logging
from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class HrExpense(models.Model):

    _inherit = "hr.expense"

    tax_line_ids = fields.One2many(
        "hr.expense.tax",
        "expense_id",
        "Detailed Taxes",
        readonly=True,
        copy=True,
        states={
            "draft": [("readonly", False)],
            "reported": [("readonly", False)],
            "refused": [("readonly", False)],
            "approved": [("readonly", False)],
        },
    )

    @api.onchange(
        "product_id", "quantity", "unit_amount", "tax_ids", "company_id", "currency_id"
    )
    def _onchange_amount_setup_tax_lines(self):
        if self.quantity and self.unit_amount and self.tax_ids:
            self._setup_tax_lines()
        else:
            self.tax_line_ids = self.env["hr.expense.tax"]

    def _setup_tax_lines(self):
        """Setup the taxes on the expense."""
        self.tax_line_ids = self.env["hr.expense.tax"]

        currency = self.currency_id or self.company_id.currency_id
        taxes = self.tax_ids.with_context(round=True).compute_all(
            self.unit_amount, currency, self.quantity, self.product_id
        )
        print("TAXES", taxes)

        for tax in taxes["taxes"]:
            self.tax_line_ids |= self.env["hr.expense.tax"].new(
                {
                    "amount": tax["amount"],
                    "account_id": tax["account_id"],
                    "tax_id": tax["id"] or tax["id"].origin,
                    "price_include": tax["price_include"],
                }
            )

    def _move_line_get_using_tax_lines(self):
        # TODO this function must be fixed and _prepare_move_line value obsolete on v14
        expense_move_line = self._prepare_move_line_value()
        expense_move_line["price"] = self.untaxed_amount
        move_lines = [expense_move_line]

        for line in self.tax_line_ids:
            move_lines.append(
                {
                    "type": "tax",
                    "name": line.tax_id.name,
                    "price_unit": line.amount,
                    "quantity": 1,
                    "price": line.amount,
                    "account_id": line.account_id.id,
                    "tax_line_id": line.tax_id.id,
                    "expense_id": self.id,
                }
            )

        return move_lines

    @api.depends(
        "quantity", "unit_amount", "tax_ids", "currency_id", "tax_line_ids.amount"
    )
    def _compute_amount(self):
        expenses_with_tax_lines = self.filtered(lambda e: e.tax_ids)
        expenses_without_tax_lines = self.filtered(lambda e: not e.tax_ids)

        for expense in expenses_with_tax_lines:
            included_tax_amount = sum(
                line.amount for line in expense.tax_line_ids if line.price_include
            )
            tax_amount = sum(line.amount for line in expense.tax_line_ids)

            expense.untaxed_amount = (
                expense.unit_amount * expense.quantity - included_tax_amount
            )
            expense.total_amount = expense.untaxed_amount + tax_amount

        super(HrExpense, expenses_without_tax_lines)._compute_amount()

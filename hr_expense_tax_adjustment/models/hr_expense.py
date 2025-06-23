# Copyright 2023-today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models, _
from odoo.exceptions import UserError


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
        "product_id",
        "quantity",
        "unit_amount",
        "tax_ids",
        "company_id",
        "currency_id",
    )
    def _onchange_amount_setup_tax_lines(self):
        if self.quantity and self.unit_amount and self.tax_ids:
            self._setup_tax_lines()
        else:
            self.tax_line_ids = False

    #
    def _setup_tax_lines(self):
        """Setup the taxes on the expense."""
        # Reset values
        self.tax_line_ids = False

        currency = self.currency_id or self.company_id.currency_id
        taxes = self.tax_ids.with_context(round=True).compute_all(
            self.unit_amount, currency, self.quantity, self.product_id
        )
        for tax in taxes["taxes"]:
            if not tax["account_id"]:
                raise UserError(
                    _("The tax {tax} has no receivable account.").format(
                        tax=tax["name"]
                    )
                )
            self.tax_line_ids |= self.env["hr.expense.tax"].new(
                {
                    "amount": tax["amount"],
                    "account_id": tax["account_id"],
                    "tax_id": tax["id"] or tax["id"].origin,
                    "price_include": tax["price_include"],
                }
            )

        # for expense in self:
        #     included_tax_amount = sum(
        #         line.amount for line in expense.tax_line_ids if line.price_include
        #     )
        #     tax_amount = sum(line.amount for line in expense.tax_line_ids)
        #     untaxed_amount = (
        #         expense.unit_amount * expense.quantity - included_tax_amount
        #     )
        #     expense.total_amount = untaxed_amount + tax_amount

    # @api.depends(
    #     "quantity", "unit_amount", "tax_ids", "currency_id", "tax_line_ids.amount"
    # )
    # @api.depends("tax_ids", "tax_line_ids.amount"
    # )
    # def _compute_tax_expense(self):
    #     for expense in self:
    #         expense.amount_tax = 10
    #     super(HrExpense, self)._compute_amount()

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
            untaxed_amount = (
                expense.unit_amount * expense.quantity - included_tax_amount
            )
            expense.with_context(skip_inverse_total_amount=True).total_amount = (
                untaxed_amount + tax_amount
            )
        super(HrExpense, expenses_without_tax_lines)._compute_amount()

    @api.depends("total_amount", "tax_ids", "currency_id", "tax_line_ids.amount")
    def _compute_amount_tax(self):
        expenses_with_tax_lines = self.filtered(lambda e: e.tax_ids)
        expenses_without_tax_lines = self.filtered(lambda e: not e.tax_ids)
        for expense in expenses_with_tax_lines:
            included_tax_amount = sum(
                line.amount for line in expense.tax_line_ids if line.price_include
            )
            expense.untaxed_amount = (
                expense.unit_amount * expense.quantity - included_tax_amount
            )
            expense.amount_tax = sum(line.amount for line in expense.tax_line_ids)
        super(HrExpense, expenses_without_tax_lines)._compute_amount_tax()

    def _inverse_total_amount(self):
        if (
            self.env.context.get("skip_inverse_total_amount")
            or self.tax_line_ids
            or (not self.product_id.standard_price and self.unit_amount)
        ):
            return
        # Original inverse logic here
        super()._inverse_total_amount()

    # in some case, unit_amount change too in the original compute

    # @api.depends('product_id.standard_price')
    # def _compute_product_has_cost(self):
    #     """Override to ensure that the product has a cost before computing the total amount."""
    #     for expense in self:
    #         previous_unit_amount = expense.unit_amount
    #         super()._compute_product_has_cost()
    #         if not expense.product_has_cost and expense.state == 'draft' and previous_unit_amount != 0:
    #             expense.unit_amount = previous_unit_amount

# © 2023 Numigi
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
            self.unit_amount, currency, self.quantity, self.product_id)
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

    def _get_account_move_line_values(self):
        """Inject the manually-adjusted tax amounts into the journal entry.

        The standard method recomputes the taxes from the untaxed amount and
        the fiscal configuration (``tax_ids.compute_all``), which discards any
        manual correction stored on ``tax_line_ids``. We keep the structure
        produced by the standard method (tax repartition lines, tags, base
        amount) but override the amounts with the ones displayed on the
        expense so the accounting entry matches the supplier receipt to the
        cent.
        """
        values_by_expense = super()._get_account_move_line_values()

        for expense in self:
            tax_lines = expense.tax_line_ids
            if not tax_lines:
                continue

            values = values_by_expense.get(expense.id)
            if not values:
                continue

            # values = [source_line, *tax_lines, destination_line]
            move_tax_lines = values[1:-1]
            if len(move_tax_lines) != len(tax_lines):
                # The structures diverge (e.g. split tax repartition): keep the
                # standard behaviour rather than risk an unbalanced entry.
                continue

            company_currency = expense.company_id.currency_id
            account_date = (
                expense.date
                or expense.sheet_id.accounting_date
                or fields.Date.context_today(expense)
            )

            source_line = values[0]
            dst_line = values[-1]

            # Source (untaxed) line based on the manually-adjusted untaxed amount.
            amount_currency = expense.untaxed_amount
            balance = expense.currency_id._convert(
                amount_currency, company_currency, expense.company_id, account_date
            )
            source_line["debit"] = balance if balance > 0 else 0
            source_line["credit"] = -balance if balance < 0 else 0
            source_line["amount_currency"] = amount_currency

            total_amount = -balance
            total_amount_currency = -amount_currency

            # Tax lines based on the manually-adjusted tax amounts.
            for move_tax_line, tax_line in zip(move_tax_lines, tax_lines):
                amount_currency = tax_line.amount
                balance = expense.currency_id._convert(
                    amount_currency, company_currency, expense.company_id, account_date
                )
                move_tax_line["debit"] = balance if balance > 0 else 0
                move_tax_line["credit"] = -balance if balance < 0 else 0
                move_tax_line["amount_currency"] = amount_currency
                total_amount -= balance
                total_amount_currency -= amount_currency

            # Destination line balances the entry (payable or bank account).
            dst_line["debit"] = total_amount > 0 and total_amount
            dst_line["credit"] = total_amount < 0 and -total_amount
            dst_line["amount_currency"] = total_amount_currency

        return values_by_expense

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

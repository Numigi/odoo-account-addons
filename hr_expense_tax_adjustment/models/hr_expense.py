# © 2018 Numigi
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
                    "tax_id": tax["id"],
                    "price_include": tax["price_include"],
                }
            )

    @api.depends(
        "quantity", "unit_amount", "tax_ids", "currency_id", "tax_line_ids.amount"
    )
    def _compute_amount(self):
        """Compute the fields untaxed_amount and total_amount using the amounts on tax lines"""
        for expense in self:
            included_tax_amount = sum(
                l.amount for l in expense.tax_line_ids if l.price_include
            )
            tax_amount = sum(l.amount for l in expense.tax_line_ids)

            expense.untaxed_amount = (
                expense.unit_amount * expense.quantity - included_tax_amount
            )
            expense.total_amount = expense.untaxed_amount + tax_amount

    @api.multi
    def action_move_create(self):
        for expense in self:
            if not expense.tax_line_ids:
                expense._setup_tax_lines()

        return super().action_move_create()

    @api.multi
    def _get_account_move_line_values(self):
        """Override the method to inject taxes based on ajustment lines."""
        return {expense.id: expense._get_move_line_values() for expense in self}

    def _get_move_line_values(self):
        result = [vals for vals in self._iter_move_line_values()]

        if self._has_foreign_currency():
            for vals in result:
                self._set_amount_foreign_currency(vals)

            result[0]["debit"] -= sum(vals["debit"] for vals in result)

        return result

    def _iter_move_line_values(self):
        yield self._get_expense_move_line_values()

        for tax in self.tax_line_ids:
            yield self._get_tax_move_line_values(tax)

        yield self._get_payable_move_line_values()

    def _get_expense_move_line_values(self):
        return {
            "name": self._get_move_line_name(),
            "quantity": self.quantity or 1,
            "debit": self.untaxed_amount,
            "credit": 0,
            "account_id": self._get_expense_account_source().id,
            "product_id": self.product_id.id,
            "product_uom_id": self.product_uom_id.id,
            "analytic_account_id": self.analytic_account_id.id,
            "analytic_tag_ids": [(6, 0, self.analytic_tag_ids.ids)],
            "expense_id": self.id,
            "partner_id": self._get_commercial_partner().id,
            "tax_ids": [(6, 0, self.tax_ids.ids)],
            "currency_id": None,
            "amount_currency": 0,
        }

    def _get_tax_move_line_values(self, tax):
        analytic_account_id = (
            self.analytic_account_id.id if tax.tax_id.analytic else False
        )
        analytic_tag_ids = (
            [(6, 0, self.analytic_tag_ids.ids)] if tax.tax_id.analytic else False
        )
        return {
            "name": tax.tax_id.name,
            "quantity": 1,
            "debit": tax.amount,
            "credit": 0,
            "account_id": tax.account_id.id,
            "tax_line_id": tax.tax_id.id,
            "expense_id": self.id,
            "partner_id": self._get_commercial_partner().id,
            "analytic_account_id": analytic_account_id,
            "analytic_tag_ids": analytic_tag_ids,
            "currency_id": None,
            "amount_currency": 0,
        }

    def _get_payable_move_line_values(self):
        return {
            "name": self._get_move_line_name(),
            "debit": -self.total_amount,
            "credit": 0,
            "account_id": self._get_expense_account_destination(),
            "date_maturity": self._get_accounting_date(),
            "expense_id": self.id,
            "partner_id": self._get_commercial_partner().id,
            "currency_id": None,
            "amount_currency": 0,
        }

    def _set_amount_foreign_currency(self, vals):
        amount = vals.get("debit") or 0
        account_date = self._get_accounting_date()
        amount_company_currency = self.currency_id._convert(
            amount, self.company_id.currency_id, self.company_id, account_date
        )
        vals["currency_id"] = self.currency_id.id
        vals["amount_currency"] = amount
        vals["debit"] = amount_company_currency

    def _get_accounting_date(self):
        return (
            self.sheet_id.accounting_date
            or self.date
            or fields.Date.context_today(expense)
        )

    def _has_foreign_currency(self):
        return self.currency_id and self.currency_id != self.company_id.currency_id

    def _get_move_line_name(self):
        return self.employee_id.name + ": " + self.name.split("\n")[0][:64]

    def _get_commercial_partner(self):
        return self.employee_id.address_home_id.commercial_partner_id

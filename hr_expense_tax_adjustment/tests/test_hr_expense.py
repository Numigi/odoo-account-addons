# © 2018 Numigi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from datetime import datetime
from odoo.tests import common
from odoo.exceptions import UserError


class ExpenseCase(common.SavepointCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.tax_account = cls.env['account.account'].create({
            'code': 'TAX1',
            'name': 'Tax 1',
            'user_type_id': cls.env.ref('account.data_account_type_receivable').id,
            'reconcile': True,
        })

        cls.tax_account_2 = cls.env['account.account'].create({
            'code': 'TAX2',
            'name': 'Tax 2',
            'user_type_id': cls.env.ref('account.data_account_type_receivable').id,
            'reconcile': True,
        })

        # This case of taxes is based on the GST/QST taxes in Canada
        cls.tax_1 = cls.env['account.tax'].create({
            'name': 'Tax 1 (5%)',
            'amount': 4.5464878,
            'amount_type': 'percent',
            'type_tax_use': 'purchase',
            'price_include': True,
            'account_id': cls.tax_account.id,
        })
        cls.tax_2 = cls.env['account.tax'].create({
            'name': 'Tax 2 (9.9975%)',
            'amount': 9.975,
            'amount_type': 'percent',
            'type_tax_use': 'purchase',
            'price_include': True,
            'account_id': cls.tax_account_2.id,
        })
        cls.parent_tax = cls.env['account.tax'].create({
            'name': 'Parent Tax',
            'amount': 0,
            'amount_type': 'group',
            'type_tax_use': 'purchase',
        })
        cls.parent_tax.children_tax_ids = cls.tax_1 | cls.tax_2

        cls.product = cls.env.ref('hr_expense.air_ticket')
        cls.product.supplier_taxes_id = cls.parent_tax

        cls.user = cls.env.ref('base.user_demo')
        cls.employee = cls.env.ref('hr.employee_mit')
        cls.employee.user_id = cls.user

        cls.payable = cls.env['account.account'].create({
            "name": "Expenses Payable",
            "code": "222222",
            "user_type_id": cls.env.ref('account.data_account_type_payable').id,
            "reconcile": True,
        })

        cls.employee.address_home_id.property_account_payable_id = cls.payable.id

        cls.sheet = cls.env['hr.expense.sheet'].create({
            'name': 'Air Tickets',
            'employee_id': cls.employee.id,
        })

        cls.expense = cls.env['hr.expense'].sudo(cls.user).create({
            'name': 'Car Travel Expenses',
            'employee_id': cls.employee.id,
            'product_id': cls.product.id,
            'unit_amount': 700.00,
            'tax_ids': [(6, 0, [cls.parent_tax.id])],
            'sheet_id': cls.sheet.id,
        })


class TestExpenseInCompanyCurrency(ExpenseCase):

    def test_onchangeAmountSetupTaxLines_thenTaxLinesAreComputed(self):
        self.assertFalse(self.expense.tax_line_ids)

        self.expense._onchange_amount_setup_tax_lines()

        assert self.expense.total_amount == 700

        lines = self.expense.tax_line_ids
        assert len(lines) == 2
        assert lines[0].tax_id == self.tax_1
        assert lines[1].tax_id == self.tax_2
        assert lines[0].amount == round(700 * (0.05 / 1.14975), 2)
        assert lines[1].amount == round(700 * (0.09975 / 1.14975), 2)

    def test_ifTaxesExcludedFromPrice_thenTaxLinesAmountAreBasedOnPrice(self):
        self.assertFalse(self.expense.tax_line_ids)

        self.tax_1.amount = 5
        self.tax_1.price_include = False
        self.tax_2.price_include = False

        self.expense._onchange_amount_setup_tax_lines()

        assert self.expense.total_amount == round(700 * 1.14975, 2)

        lines = self.expense.tax_line_ids
        assert len(lines) == 2
        assert lines[0].tax_id == self.tax_1
        assert lines[1].tax_id == self.tax_2
        assert lines[0].amount == round(700 * 0.05, 2)
        assert lines[1].amount == round(700 * 0.09975, 2)

    def test_onchangeAmountSetupTaxLines_ifNoReceivableAccountDefined_thenRaiseError(self):
        self.tax_1.account_id = False

        with self.assertRaises(UserError):
            self.expense._onchange_amount_setup_tax_lines()

    def test_tax_amounts_properly_propagated_to_account_move(self):
        self.expense._onchange_amount_setup_tax_lines()
        self.expense.tax_line_ids[0].amount = 10
        self.expense.tax_line_ids[1].amount = 5

        self.sheet.approve_expense_sheets()
        self.sheet.action_sheet_move_create()

        move_lines = self.sheet.account_move_id.line_ids
        assert len(move_lines) == 4

        tax_1 = move_lines.filtered(lambda l: l.account_id == self.tax_account)
        tax_2 = move_lines.filtered(lambda l: l.account_id == self.tax_account_2)
        payable = move_lines.filtered(lambda l: l.account_id == self.payable)
        assert tax_1.debit == 10
        assert tax_2.debit == 5
        assert payable.credit == round(700, 2)

    def test_whenValidatingExpense_thenTaxesAreCorrectlyAccounted(self):
        self.expense._onchange_amount_setup_tax_lines()

        self.sheet.approve_expense_sheets()
        self.sheet.action_sheet_move_create()

        move_lines = self.sheet.account_move_id.line_ids
        assert len(move_lines) == 4

        tax_1 = move_lines.filtered(lambda l: l.account_id == self.tax_account)
        tax_2 = move_lines.filtered(lambda l: l.account_id == self.tax_account_2)
        payable = move_lines.filtered(lambda l: l.account_id == self.payable)
        assert tax_1.debit == round(700 * (0.05 / 1.14975), 2)
        assert tax_2.debit == round(700 * (0.09975 / 1.14975), 2)
        assert payable.credit == round(700, 2)

    def test_whenValidatingExpenseWithExcludedTaxes_thenTaxesAreCorrectlyAccounted(self):
        self.tax_1.amount = 5
        self.tax_1.price_include = False
        self.tax_2.price_include = False

        self.expense._onchange_amount_setup_tax_lines()

        self.sheet.approve_expense_sheets()
        self.sheet.action_sheet_move_create()

        move_lines = self.sheet.account_move_id.line_ids
        assert len(move_lines) == 4

        tax_1 = move_lines.filtered(lambda l: l.account_id == self.tax_account)
        tax_2 = move_lines.filtered(lambda l: l.account_id == self.tax_account_2)
        payable = move_lines.filtered(lambda l: l.account_id == self.payable)
        assert tax_1.debit == round(700 * 0.05, 2)
        assert tax_2.debit == round(700 * 0.09975, 2)
        assert payable.credit == round(700 * 1.14975, 2)

    def test_ifTaxesAreIncludedAndExpenseHasNoTaxeLines_thenTaxesAreCorrectlyAccounted(self):
        self.sheet.approve_expense_sheets()
        self.sheet.action_sheet_move_create()

        move_lines = self.sheet.account_move_id.line_ids
        assert len(move_lines) == 4

        tax_1 = move_lines.filtered(lambda l: l.account_id == self.tax_account)
        tax_2 = move_lines.filtered(lambda l: l.account_id == self.tax_account_2)
        payable = move_lines.filtered(lambda l: l.account_id == self.payable)
        assert tax_1.debit == round(700 * (0.05 / 1.14975), 2)
        assert tax_2.debit == round(700 * (0.09975 / 1.14975), 2)
        assert payable.credit == 700

    def test_ifTaxesAreExcludedAndExpenseHasNoTaxeLines_thenTaxesAreCorrectlyAccounted(self):
        self.tax_1.amount = 5
        self.tax_1.price_include = False
        self.tax_2.price_include = False

        self.sheet.approve_expense_sheets()
        self.sheet.action_sheet_move_create()

        move_lines = self.sheet.account_move_id.line_ids
        assert len(move_lines) == 4

        tax_1 = move_lines.filtered(lambda l: l.account_id == self.tax_account)
        tax_2 = move_lines.filtered(lambda l: l.account_id == self.tax_account_2)
        payable = move_lines.filtered(lambda l: l.account_id == self.payable)
        assert tax_1.debit == round(700 * 0.05, 2)
        assert tax_2.debit == round(700 * 0.09975, 2)
        assert payable.credit == round(700 * 1.14975, 2)

    def test_withMultipleExpenseLines_totalAmountsAreComputedProperly(self):
        self.expense._onchange_amount_setup_tax_lines()

        expense_2 = self.expense.copy({'unit_amount': 500})
        expense_2._onchange_amount_setup_tax_lines()

        (self.expense | expense_2)._compute_amount()

        assert self.expense.total_amount == 700
        assert expense_2.total_amount == 500
        assert self.expense.untaxed_amount == round(700 / 1.14975, 2)
        assert expense_2.untaxed_amount == round(500 / 1.14975, 2)

    def test_withMultipleExpenseLines_taxesAreCorrectlyAccounted(self):
        self.expense._onchange_amount_setup_tax_lines()

        expense_2 = self.expense.copy({'unit_amount': 500})
        expense_2._onchange_amount_setup_tax_lines()
        expense_2.sheet_id = self.sheet

        self.sheet.approve_expense_sheets()
        self.sheet.action_sheet_move_create()

        move_lines = self.sheet.account_move_id.line_ids

        tax_1 = move_lines.filtered(lambda l: l.account_id == self.tax_account)
        tax_2 = move_lines.filtered(lambda l: l.account_id == self.tax_account_2)
        payable = move_lines.filtered(lambda l: l.account_id == self.payable)

        total_amount = 700 + 500
        assert round(sum(tax_1.mapped('debit'))) == round(total_amount * (0.05 / 1.14975))
        assert round(sum(tax_2.mapped('debit'))) == round(total_amount * (0.09975 / 1.14975))
        assert sum(payable.mapped('credit')) == total_amount


class TestExpenseInForeignCurrency(ExpenseCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.cad = cls.env.ref("base.CAD")
        cls.journal = cls.env["account.journal"].create(
            {
                "name": "My Journal In CAD",
                "code": "EXPC",
                "currency_id": cls.cad.id,
                "type": "purchase",
            }
        )
        cls.expense.write({
            "journal_id": cls.journal.id,
            "currency_id": cls.cad.id,
        })
        cls.payable.currency_id = cls.cad

        cls.rate = 0.5

        cls.env["res.currency.rate"].search([]).unlink()
        cls.env["res.currency.rate"].create({
            "currency_id": cls.cad.id,
            "name": datetime.now().date(),
            "rate": cls.rate,
        })

    def test_amount_in_foreign_currency(self):
        self.expense._onchange_amount_setup_tax_lines()
        self.sheet.approve_expense_sheets()
        self.sheet.action_sheet_move_create()

        move_lines = self.sheet.account_move_id.line_ids
        tax_1 = move_lines.filtered(lambda l: l.account_id == self.tax_account)
        tax_2 = move_lines.filtered(lambda l: l.account_id == self.tax_account_2)
        payable = move_lines.filtered(lambda l: l.account_id == self.payable)
        expense = move_lines - tax_1 - tax_2 - payable

        tax_1_amount = 700 * (0.05 / 1.14975)
        tax_2_amount = 700 * (0.09975 / 1.14975)
        total = 700

        assert tax_1.amount_currency == round(tax_1_amount, 2)
        assert tax_2.amount_currency == round(tax_2_amount, 2)
        assert payable.amount_currency == round(-total, 2)
        assert expense.amount_currency == round(total - tax_1_amount - tax_2_amount, 2)

        assert tax_1.debit == round(tax_1.amount_currency / self.rate, 2)
        assert tax_2.debit == round(tax_2.amount_currency / self.rate, 2)
        assert payable.credit == round(-payable.amount_currency / self.rate, 2)
        assert expense.debit == round(expense.amount_currency / self.rate, 2)

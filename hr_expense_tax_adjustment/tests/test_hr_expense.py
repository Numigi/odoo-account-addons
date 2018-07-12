# © 2018 Numigi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.tests import common
from odoo.exceptions import UserError


class TestAccountMoveLine(common.SavepointCase):

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

        cls.payable = cls.env['account.account'].search(
            [('user_type_id.type', '=', 'payable')], limit=1)

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

    def test_onchangeAmountSetupTaxLines_thenTaxLinesAreComputed(self):
        self.assertFalse(self.expense.tax_line_ids)

        self.expense._onchange_amount_setup_tax_lines()

        self.assertEqual(self.expense.total_amount, 700)

        lines = self.expense.tax_line_ids
        self.assertEqual(len(lines), 2)
        self.assertEqual(lines[0].tax_id, self.tax_1)
        self.assertEqual(lines[1].tax_id, self.tax_2)
        self.assertAlmostEqual(lines[0].amount, 700 * (0.05 / 1.14975), 2)
        self.assertAlmostEqual(lines[1].amount, 700 * (0.09975 / 1.14975), 2)

    def test_ifTaxesExcludedFromPrice_thenTaxLinesAmountAreBasedOnPrice(self):
        self.assertFalse(self.expense.tax_line_ids)

        self.tax_1.amount = 5
        self.tax_1.price_include = False
        self.tax_2.price_include = False

        self.expense._onchange_amount_setup_tax_lines()

        self.assertAlmostEqual(self.expense.total_amount, 700 * 1.14975, 2)

        lines = self.expense.tax_line_ids
        self.assertEqual(len(lines), 2)
        self.assertEqual(lines[0].tax_id, self.tax_1)
        self.assertEqual(lines[1].tax_id, self.tax_2)
        self.assertAlmostEqual(lines[0].amount, 700 * 0.05, 2)
        self.assertAlmostEqual(lines[1].amount, 700 * 0.09975, 2)

    def test_onchangeAmountSetupTaxLines_ifNoReceivableAccountDefined_thenRaiseError(self):
        self.tax_1.account_id = False

        with self.assertRaises(UserError):
            self.expense._onchange_amount_setup_tax_lines()

    def test_whenValidatingExpense_thenTaxesAreCorrectlyAccounted(self):
        self.expense._onchange_amount_setup_tax_lines()

        self.sheet.approve_expense_sheets()
        self.sheet.action_sheet_move_create()

        move_lines = self.sheet.account_move_id.line_ids
        self.assertEqual(len(move_lines), 4)

        tax_1 = move_lines.filtered(lambda l: l.account_id == self.tax_account)
        tax_2 = move_lines.filtered(lambda l: l.account_id == self.tax_account_2)
        payable = move_lines.filtered(lambda l: l.account_id == self.payable)
        self.assertAlmostEqual(tax_1.debit, 700 * (0.05 / 1.14975), 2)
        self.assertAlmostEqual(tax_2.debit, 700 * (0.09975 / 1.14975), 2)
        self.assertAlmostEqual(payable.credit, 700, 2)

    def test_whenValidatingExpenseWithExcludedTaxes_thenTaxesAreCorrectlyAccounted(self):
        self.tax_1.amount = 5
        self.tax_1.price_include = False
        self.tax_2.price_include = False

        self.expense._onchange_amount_setup_tax_lines()

        self.sheet.approve_expense_sheets()
        self.sheet.action_sheet_move_create()

        move_lines = self.sheet.account_move_id.line_ids
        self.assertEqual(len(move_lines), 4)

        tax_1 = move_lines.filtered(lambda l: l.account_id == self.tax_account)
        tax_2 = move_lines.filtered(lambda l: l.account_id == self.tax_account_2)
        payable = move_lines.filtered(lambda l: l.account_id == self.payable)
        self.assertAlmostEqual(tax_1.debit, 700 * 0.05, 2)
        self.assertAlmostEqual(tax_2.debit, 700 * 0.09975, 2)
        self.assertAlmostEqual(payable.credit, 700 * 1.14975, 2)

    def test_ifTaxesAreIncludedAndExpenseHasNoTaxeLines_thenTaxesAreCorrectlyAccounted(self):
        self.sheet.approve_expense_sheets()
        self.sheet.action_sheet_move_create()

        move_lines = self.sheet.account_move_id.line_ids
        self.assertEqual(len(move_lines), 4)

        tax_1 = move_lines.filtered(lambda l: l.account_id == self.tax_account)
        tax_2 = move_lines.filtered(lambda l: l.account_id == self.tax_account_2)
        payable = move_lines.filtered(lambda l: l.account_id == self.payable)
        self.assertAlmostEqual(tax_1.debit, 700 * (0.05 / 1.14975), 2)
        self.assertAlmostEqual(tax_2.debit, 700 * (0.09975 / 1.14975), 2)
        self.assertAlmostEqual(payable.credit, 700)

    def test_ifTaxesAreExcludedAndExpenseHasNoTaxeLines_thenTaxesAreCorrectlyAccounted(self):
        self.tax_1.amount = 5
        self.tax_1.price_include = False
        self.tax_2.price_include = False

        self.sheet.approve_expense_sheets()
        self.sheet.action_sheet_move_create()

        move_lines = self.sheet.account_move_id.line_ids
        self.assertEqual(len(move_lines), 4)

        tax_1 = move_lines.filtered(lambda l: l.account_id == self.tax_account)
        tax_2 = move_lines.filtered(lambda l: l.account_id == self.tax_account_2)
        payable = move_lines.filtered(lambda l: l.account_id == self.payable)
        self.assertAlmostEqual(tax_1.debit, 700 * 0.05, 2)
        self.assertAlmostEqual(tax_2.debit, 700 * 0.09975, 2)
        self.assertAlmostEqual(payable.credit, 700 * 1.14975, 2)

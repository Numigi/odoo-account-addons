# © 2025 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo.addons.stock_account.tests.test_stockvaluation import _create_accounting_data

from odoo.tests.common import SavepointCase
from odoo import fields
from odoo.exceptions import UserError


class TestStockForeignValuation(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.usd = cls.env.ref('base.USD')

        cls.partner = cls.env['res.partner'].create({
            'name': 'US Vendor',
            'property_purchase_currency_id': cls.usd.id,
            'supplier_rank': 1,
        })
        cls.acc_input, cls.acc_output, cls.acc_valuation, cls.acc_expense, cls.journal = _create_accounting_data(cls.env)

        cls.categ = cls.env['product.category'].create({
            'name': 'Test Categ',
            'property_valuation': 'real_time',
            'property_stock_account_input_categ_id': cls.acc_input.id,
            'property_stock_account_output_categ_id': cls.acc_output.id,
            'property_stock_valuation_account_id': cls.acc_valuation.id,
            'property_stock_journal': cls.journal.id,
        })

        cls.product = cls.env['product.product'].create({
            'name': 'Test Product',
            'type': 'product',
            'standard_price': 0.0,
            'list_price': 100.0,
            'categ_id': cls.categ.id,
        })

        cls.product.write({
            'property_account_expense_id': cls.acc_expense.id,
        })

    def test_valuation_with_currency_change_and_reconciliation(self):
        po = self.env['purchase.order'].create({
            'partner_id': self.partner.id,
            'currency_id': self.usd.id,
            'order_line': [(0, 0, {
                'product_id': self.product.id,
                'name': self.product.name,
                'product_qty': 1.0,
                'product_uom': self.product.uom_id.id,
                'price_unit': 100.0,
            })]
        })
        po.button_confirm()

        # picking IN reception
        picking = po.picking_ids[0]
        picking.move_ids_without_package.quantity_done = 1.0
        picking.button_validate()

        # Chane the currency rate
        self.usd.write({'rate': 2.0})

        # Invoice validation
        po.action_create_invoice()
        invoice = po.invoice_ids
        invoice.write({'invoice_date': fields.Date.today()})
        invoice.action_post()

        # Full reconcile check
        stock_lines = self.env['account.move.line'].search([
            ('account_id', '=', self.acc_input.id),
            ('move_id.state', '=', 'posted'),
            ('move_id.stock_move_id', '!=', False),
        ])

        invoice_lines = invoice.line_ids.filtered(lambda l: l.account_id.id == self.acc_input.id)

        all_lines = stock_lines | invoice_lines
        self.assertTrue(all(line.full_reconcile_id for line in all_lines), "The account move line are not reconciled")

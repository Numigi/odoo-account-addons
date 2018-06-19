# © 2018 Numigi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models
from odoo.addons import decimal_precision as dp


class HrExpenseTax(models.Model):

    _name = 'hr.expense.tax'
    _description = 'Taxes On Expense Lines'

    expense_id = fields.Many2one(
        'hr.expense', 'Expense', required=True, ondelete='cascade', index=True)
    amount = fields.Float('Amount', required=True, digits=dp.get_precision('Account'))
    account_id = fields.Many2one(
        'account.account', 'Account', required=True, ondelete='restrict')
    tax_id = fields.Many2one(
        'account.tax', 'Tax', required=True, ondelete='restrict')
    currency_id = fields.Many2one(
        'res.currency', 'Currency', related='expense_id.currency_id', readonly=True)
    price_include = fields.Boolean('Included In Price')

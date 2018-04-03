# © 2017 Savoir-faire Linux
# © 2018 Numigi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class AccountFinancialReportLine(models.Model):

    _inherit = 'account.financial.html.report.line'

    formula_type = fields.Selection([
        ('sum_of_children', 'Sum of Children Lines'),
        ('sum_of_categories', 'Sum of Account Categories'),
    ], 'Formula Type')

    reverse_sum = fields.Boolean('Reverse the Result Amount')

    account_tag_id = fields.Many2one(
        'account.account.tag', 'Account Tag')

    account_type_ids = fields.Many2many(
        'account.account.type', string='Account Types')

    special_date_changer = fields.Selection([
        ('to_beginning_of_period', 'Balance at the beginning of the period'),
        ('from_beginning', 'Balance at the end of period'),
        ('normal', 'Movement of the period (Income Statement)'),
        ('strict_range', 'Movement of the period (Cash Flow)'),
    ], default='normal', string='Type of Amount')

    _sql_constraints = [
        ('value_code', 'unique(code)',
         'The code must be unique per report line'),
    ]

    @api.onchange(
        'account_tag_id', 'account_type_ids', 'formula_type',
        'reverse_sum')
    def _onchange_account_categories(self):
        self._update_formulas_from_type()

    @api.onchange('parent_id')
    def _onchange_parent_id_update_level(self):
        if self.parent_id:
            self.level = self.parent_id.level + 1

    @api.model
    def create(self, vals):
        res = super(AccountFinancialReportLine, self).create(vals)
        res._update_formulas_from_type()
        if res.parent_id:
            res.parent_id._update_formulas_from_type()
        return res

    @api.multi
    def write(self, vals):
        old_parent = self.parent_id
        super(AccountFinancialReportLine, self).write(vals)

        if (
            'account_tag_id' in vals or
            'account_type_ids' in vals or
            'formula_type' in vals or
            'reverse_sum' in vals
        ):
            self._update_formulas_from_type()

        if 'parent_id' in vals:
            (old_parent | self.parent_id)._update_formulas_from_type()

        return True

    def _update_formulas_from_type(self):
        for line in self:
            if line.formula_type == 'sum_of_children':
                if line.children_ids:
                    line.formulas = 'balance = ' + ' + '.join([
                        '%s.balance' % c.code for c in line.children_ids
                    ])
                else:
                    line.formulas = 'balance = 0'

                line.groupby = None
                line.domain = None

            elif line.formula_type == 'sum_of_categories':
                if line.reverse_sum:
                    line.formulas = 'balance = -sum.balance'
                else:
                    line.formulas = 'balance = sum.balance'

                line.groupby = 'account_id'

                domain = []

                if line.account_tag_id:
                    domain.append(
                        ('account_id.tag_ids', '=',
                            line.account_tag_id.id))

                if line.account_type_ids:
                    domain.append(
                        ('account_id.user_type_id', 'in',
                            line.account_type_ids.ids))

                line.domain = str(domain)

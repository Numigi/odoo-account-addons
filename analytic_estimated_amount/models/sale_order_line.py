# -*- coding: utf-8 -*-
# © 2017 Savoir-faire Linux
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class SaleOrderLine(models.Model):
    """Sale Order Line"""

    _inherit = 'sale.order.line'

    analytic_line_id = fields.Many2one(
        'account.analytic.line', 'Analytic Line')

    @api.multi
    def _remove_analytic_lines(self):
        analytic_lines = self.mapped('analytic_line_id')
        if analytic_lines:
            analytic_lines.unlink()

    @api.multi
    def _estimative_line_required(self):
        self.ensure_one()
        return True if self.order_id.project_id else False

    def _get_analytic_line_vals(self):
        self.ensure_one()
        return {
            'name': self.name,
            'estimated_amount': self.price_subtotal,
            'unit_amount': self.product_uom_qty,
            'product_uom_id': self.product_uom.id,
            'product_id': self.product_id.id,
            'account_id': self.order_id.project_id.id,
            'user_id': self.order_id.user_id.id,
        }

    @api.multi
    def _generate_analytic_line(self):
        self._remove_analytic_lines()
        line_cls = self.env['account.analytic.line']
        for line in self:
            if line._estimative_line_required():
                line.analytic_line_id = line_cls.create(
                    line._get_analytic_line_vals())

    @api.multi
    def unlink(self):
        self._remove_analytic_lines()
        return super(SaleOrderLine, self).unlink()

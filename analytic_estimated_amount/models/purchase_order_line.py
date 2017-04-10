# -*- coding: utf-8 -*-
# © 2017 Savoir-faire Linux
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class PurchaseOrderLine(models.Model):

    _inherit = 'purchase.order.line'

    analytic_line_id = fields.Many2one(
        'account.analytic.line', 'Analytic Line')

    def _get_analytic_line_vals(self):
        self.ensure_one()
        return {
            'name': self.name,
            'estimated_amount': -self.price_subtotal,
            'unit_amount': self.product_qty,
            'product_uom_id': self.product_uom.id,
            'product_id': self.product_id.id,
            'account_id': self.account_analytic_id.id,
        }

    @api.multi
    def _generate_analytic_line(self):
        self._remove_analytic_lines()
        line_cls = self.env['account.analytic.line']
        for line in self:
            if line.account_analytic_id:
                line.analytic_line_id = line_cls.create(
                    line._get_analytic_line_vals())

    @api.multi
    def _remove_analytic_lines(self):
        analytic_lines = self.mapped('analytic_line_id')
        if analytic_lines:
            analytic_lines.unlink()
        return True

    @api.multi
    def unlink(self):
        self._remove_analytic_lines()
        return super(PurchaseOrderLine, self).unlink()

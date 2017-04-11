# -*- coding: utf-8 -*-
# © 2017 Savoir-faire Linux
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, models


class PurchaseOrder(models.Model):

    _inherit = 'purchase.order'

    @api.multi
    def unlink(self):
        self._remove_analytic_lines()
        return super(PurchaseOrder, self).unlink()

    @api.multi
    def button_confirm(self):
        res = super(PurchaseOrder, self).button_confirm()
        self.mapped('order_line')._generate_analytic_line()
        return res

    @api.multi
    def button_cancel(self):
        res = super(PurchaseOrder, self).button_cancel()
        self._remove_analytic_lines()
        return res

    @api.multi
    def _remove_analytic_lines(self):
        analytic_lines = self.mapped('order_line.analytic_line_id')
        if analytic_lines:
            analytic_lines.unlink()
        return True

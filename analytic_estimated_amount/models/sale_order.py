# -*- coding: utf-8 -*-
# © 2017 Savoir-faire Linux
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, models


class SaleOrder(models.Model):
    """Sale Order Line"""

    _inherit = 'sale.order'

    @api.multi
    def action_confirm(self):
        """
        Handle the case where the analytic account is manually set
        on the order.

        It is important that the analytic lines are created before
        calling super because in order to prevent duplicates.
        When the sale order is confirmed, if the account is not set,
        it may be created.
        """
        for order in self:
            if order.project_id:
                order.order_line._generate_analytic_line()

        res = super(SaleOrder, self).action_confirm()
        return res

    @api.multi
    def _create_analytic_account(self):
        """
        Handle the case where the account / project is created from
        the sale order. This method may be called from action_confirm
        or not.
        """
        res = super(SaleOrder, self)._create_analytic_account()
        self.mapped('order_line')._generate_analytic_line()
        return res

    @api.multi
    def _remove_analytic_lines(self):
        analytic_lines = self.mapped('order_line.analytic_line_id')
        if analytic_lines:
            analytic_lines.unlink()
        return True

    @api.multi
    def action_cancel(self):
        res = super(SaleOrder, self).action_cancel()
        self._remove_analytic_lines()
        return res

    @api.multi
    def action_draft(self):
        res = super(SaleOrder, self).action_draft()
        self._remove_analytic_lines()
        return res

    @api.multi
    def unlink(self):
        self._remove_analytic_lines()
        return super(SaleOrder, self).unlink()

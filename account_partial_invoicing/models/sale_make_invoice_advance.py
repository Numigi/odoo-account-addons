# -*- coding: utf-8 -*-
# © 2017 Savoir-faire Linux
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import time
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    is_partial_invoice = fields.Boolean(string='Choose invoice lines')
    sale_order_line_ids = fields.Many2many(
        string='Lines To Choose',
        comodel_name='sale.order.line',
        domain=lambda self: [
            ('invoice_status', '=', 'to invoice'),
            ('order_id', '=', self._context.get('active_ids'))
        ]
    )

    @api.onchange('advance_payment_method')
    def onchange_advance_payment_method(self):
        res = {'value': {'is_partial_invoice': False,
                         'sale_order_line_ids': []}}
        return res

    @api.onchange('is_partial_invoice')
    def onchange_is_partial_invoice(self):
        res = {'value': {'sale_order_line_ids': []}}
        return res

    # Modify the version of create_invoices from
    # https://github.com/odoo/odoo/blob/10.0/addons/sale/wizard/
    # sale_make_invoice_advance.py#L126
    @api.multi
    def create_invoices(self):
        sale_orders = self.env['sale.order'].browse(
            self._context.get('active_ids', []))

        if self.advance_payment_method == 'delivered':
            if len(self.sale_order_line_ids) > 0:
                sale_orders.action_invoice_create(
                    partial=True,
                    sol_ids=self.sale_order_line_ids.ids)
            else:
                sale_orders.action_invoice_create()
        elif self.advance_payment_method == 'all':
            if len(self.sale_order_line_ids) > 0:
                sale_orders.action_invoice_create(
                    final=True,
                    partial=True,
                    sol_ids=self.sale_order_line_ids.ids)
            else:
                sale_orders.action_invoice_create(final=True)
        else:
            # Create deposit product if necessary
            if not self.product_id:
                vals = self._prepare_deposit_product()
                self.product_id = self.env['product.product'].create(vals)
                self.env['ir.values'].sudo().set_default(
                    'sale.config.settings',
                    'deposit_product_id_setting',
                    self.product_id.id)

            sale_line_obj = self.env['sale.order.line']
            for order in sale_orders:
                if self.advance_payment_method == 'percentage':
                    amount = order.amount_untaxed * self.amount / 100
                else:
                    amount = self.amount
                if self.product_id.invoice_policy != 'order':
                    raise UserError(_(
                        'The product used to invoice a down payment should '
                        'have an invoice policy set to "Ordered quantities".'
                        ' Please update your deposit product to be able to '
                        'create a deposit invoice.'))
                if self.product_id.type != 'service':
                    raise UserError(_(
                        "The product used to invoice a down payment should be"
                        " of type 'Service'. Please use another product or "
                        "update this product."))
                taxes = self.product_id.taxes_id.filtered(
                    lambda r:
                    not order.company_id or r.company_id == order.company_id
                )
                if order.fiscal_position_id and taxes:
                    tax_ids = order.fiscal_position_id.map_tax(taxes).ids
                else:
                    tax_ids = taxes.ids
                so_line = sale_line_obj.create({
                    'name': _('Advance: %s') % (time.strftime('%m %Y'),),
                    'price_unit': amount,
                    'product_uom_qty': 0.0,
                    'order_id': order.id,
                    'discount': 0.0,
                    'product_uom': self.product_id.uom_id.id,
                    'product_id': self.product_id.id,
                    'tax_id': [(6, 0, tax_ids)],
                })
                self._create_invoice(order, so_line, amount)
        if self._context.get('open_invoices', False):
            return sale_orders.action_view_invoice()
        return {'type': 'ir.actions.act_window_close'}

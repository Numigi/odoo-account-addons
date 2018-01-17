# -*- coding: utf-8 -*-
# © 2017 Savoir-faire Linux
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import _, api, models
from odoo.exceptions import UserError
from odoo.tools import float_is_zero


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def action_invoice_create(self, grouped=False, final=False,
                              partial=False, sol_ids=False
                              ):
        """
        Create the invoice associated to the SO.
        :param grouped: if True, invoices are grouped by SO id. If False,
        invoices are grouped by (partner_invoice_id, currency)
        :param final: if True, refunds will be generated if necessary
        :param partial: if True, only selected SOL will be invoiced
        :param sol_ids: selected sale order lines
        :returns: list of created invoices
        """
        inv_obj = self.env['account.invoice']
        precision = self.env['decimal.precision'].precision_get(
            'Product Unit of Measure')
        invoices = {}
        references = {}
        for order in self:
            if not partial:
                sol_ids = order.order_line.ids
            group_key = order.id if grouped else (
                order.partner_invoice_id.id, order.currency_id.id
            )
            for line in order.order_line.sorted(
                    key=lambda l: (l.qty_to_invoice < 0)):
                if line.id in sol_ids:
                    if float_is_zero(
                            line.qty_to_invoice,
                            precision_digits=precision
                    ):
                        continue
                    if group_key not in invoices:
                        inv_data = order._prepare_invoice()
                        invoice = inv_obj.create(inv_data)
                        references[invoice] = order
                        invoices[group_key] = invoice
                    elif group_key in invoices:
                        vals = {}
                        if order.name not in invoices[group_key].origin.split(
                                ', '
                        ):
                            vals['origin'] = (
                                invoices[
                                    group_key
                                ].origin + ', ' + order.name
                            )
                        if (
                            order.client_order_ref and
                            order.client_order_ref not in
                            invoices[group_key].name.split(', ') and
                            order.client_order_ref != invoices[group_key].name
                        ):
                            vals['name'] = (
                                invoices[
                                    group_key
                                ].name + ', ' + order.client_order_ref
                            )
                        invoices[group_key].write(vals)
                    if line.qty_to_invoice > 0:
                        line.invoice_line_create(
                            invoices[group_key].id, line.qty_to_invoice
                        )
                    elif line.qty_to_invoice < 0 and final:
                        line.invoice_line_create(
                            invoices[group_key].id, line.qty_to_invoice
                        )

            if references.get(invoices.get(group_key)):
                if order not in references[invoices[group_key]]:
                    references[invoice] = references[invoice] | order

        if not invoices:
            raise UserError(_('There is no invoicable line.'))

        for invoice in invoices.values():
            if not invoice.invoice_line_ids:
                raise UserError(_('There is no invoicable line.'))
            # If invoice is negative, do a refund invoice instead
            if invoice.amount_untaxed < 0:
                invoice.type = 'out_refund'
                for line in invoice.invoice_line_ids:
                    line.quantity = -line.quantity
            # Use additional field helper function (for account extensions)
            for line in invoice.invoice_line_ids:
                line._set_additional_fields(invoice)
            # Necessary to force computation of taxes.
            # In account_invoice, they are triggered
            # by onchanges, which are not triggered when doing a create.
            invoice.compute_taxes()
            invoice.message_post_with_view('mail.message_origin_link',
                                           values={'self': invoice,
                                                   'origin': references[
                                                       invoice]},
                                           subtype_id=self.env.ref(
                                               'mail.mt_note').id)
        return [inv.id for inv in invoices.values()]

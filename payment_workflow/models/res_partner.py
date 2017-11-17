# -*- coding: utf-8 -*-
# © 2017 Savoir-faire Linux
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class ResPartner(models.Model):

    _inherit = 'res.partner'

    type = fields.Selection([
        ('contact', 'Contact'),
        ('invoice', 'Invoice address'),
        ('supplier_payment', 'Supplier Payment'),
        ('customer_payment', 'Customer Payment'),
        ('delivery', 'Shipping address'),
        ('other', 'Other address')
    ])

    def get_preferred_address(self, contact_types):
        for contact_type in contact_types:
            contact_id = self.address_get([contact_type])[contact_type]
            if contact_id != self.id:
                return self.browse(contact_id)

        return self

# -*- coding: utf-8 -*-
# © 2017 Savoir-faire Linux
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class ResPartner(models.Model):

    _inherit = 'res.partner'

    type = fields.Selection(selection_add=[
        ('supplier_payment', 'Supplier Payment'),
        ('customer_payment', 'Customer Payment'),
    ])

    def get_preferred_address(self, contact_types):
        """Get a preferred address from a partner.

        This function is meant to be used in a email template.

        For example, in a payment notice email, the field partner_to
        could be filled as follow:

            ${object.partner_id.get_preferred_address(
                ['supplier_payment', 'invoice']).id|safe}

        If the partner has an address of type 'supplier_payment',
        this address will be used in the email. Otherwise, an address
        of type 'invoice' will be selected. If the partner does not have
        an address of type 'invoice' either, the email will be sent
        to the partner himself.

        :param list contact_types: The types of address in order of priority
        :rtype: res.partner
        :return: The address
        """
        for contact_type in contact_types:
            contact_id = self.address_get([contact_type])[contact_type]
            if contact_id != self.id:
                return self.browse(contact_id)

        return self

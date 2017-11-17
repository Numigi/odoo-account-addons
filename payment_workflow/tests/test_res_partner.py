# -*- coding: utf-8 -*-
# © 2017 Savoir-faire Linux
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from openerp.tests import SavepointCase


class TestResPartner(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestResPartner, cls).setUpClass()

        cls.parent = cls.env['res.partner'].create({
            'name': 'Parent',
        })

        cls.invoice_address = cls.env['res.partner'].create({
            'name': 'Invoice Address',
            'type': 'invoice',
            'parent_id': cls.parent.id,
        })

        cls.customer_payment = cls.env['res.partner'].create({
            'name': 'Customer Payment',
            'type': 'customer_payment',
            'parent_id': cls.parent.id,
        })

    def test_01_get_preferred_address_first_contact_returned(self):
        contact = self.parent.get_preferred_address(
            ['customer_payment', 'invoice'])
        self.assertEquals(contact, self.customer_payment)

    def test_02_get_preferred_address_second_contact_returned(self):
        contact = self.parent.get_preferred_address(
            ['supplier_payment', 'invoice'])
        self.assertEquals(contact, self.invoice_address)

    def test_03_get_preferred_address_parent_returned(self):
        contact = self.parent.get_preferred_address(
            ['supplier_payment', 'delivery'])
        self.assertEquals(contact, self.parent)

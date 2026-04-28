# -*- coding: utf-8 -*-
from odoo.tests import common, tagged


@tagged('post_install', '-at_install')
class TestReceivableEmail(common.TransactionCase):

    def setUp(self):
        super(TestReceivableEmail, self).setUp()
        self.partner = self.env['res.partner'].create({
            'name': 'Test Client',
            'email': 'client@test.com',
        })

        self.receivable_contact = self.env['res.partner'].create({
            'name': 'Contact Compta',
            'email': 'compta@test.com',
            'is_receivable_account': True,
        })

        self.journal = self.env['account.journal'].create({
            'name': 'Test Bank',
            'type': 'bank',
            'code': 'BNKT',
            'currency_id': self.env.company.currency_id.id,
        })
        self.payment_method = self.env.ref('account.account_payment_method_manual_in')

    def test_01_assign_receivable_contact(self):
        """ Test: Assign a receivable accounts contact """
        self.partner.payment_email_id = self.receivable_contact.id
        self.assertEqual(self.partner.payment_email_id.email, "compta@test.com")

    def test_02_mail_composer_injection(self):
        """ Test: The wizard injects the ID of the selected contact """
        self.partner.payment_email_id = self.receivable_contact.id

        payment = self.env['account.payment'].create({
            'payment_type': 'inbound',
            'partner_type': 'customer',
            'partner_id': self.partner.id,
            'amount': 100,
            'journal_id': self.journal.id,
            'payment_method_id': self.payment_method.id,
        })

        composer = self.env['mail.compose.message'].with_context(
            default_model='account.payment',
            default_res_id=payment.id,
            active_ids=[payment.id],
            active_model='account.payment'
        ).create({'body': 'Test body'})

        # 1. Test Onchange (Visual)
        onchange_res = composer.onchange_template_id(
            False, 'comment', 'account.payment', payment.id
        )

        if onchange_res and 'value' in onchange_res:
            self.assertEqual(onchange_res['value'].get('partner_ids'),
                             [(6, 0, [self.receivable_contact.id])])

        # 2. Test Get Mail Values (Sending Logic)
        mail_values = composer.get_mail_values([payment.id])[payment.id]

        if 'partner_ids' in mail_values:
            self.assertEqual(mail_values['partner_ids'], [self.receivable_contact.id])

        if 'recipient_ids' in mail_values:
            self.assertEqual(mail_values['recipient_ids'],
                             [(5, 0, 0), (4, self.receivable_contact.id)])

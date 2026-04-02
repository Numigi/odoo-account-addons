# -*- coding: utf-8 -*-
from odoo.tests import common, tagged


@tagged('post_install', '-at_install')
class TestReceivableEmail(common.TransactionCase):

    def setUp(self):
        super(TestReceivableEmail, self).setUp()
        # Create a test partner
        self.partner = self.env['res.partner'].create({
            'name': 'Test Client',
            'email': 'client@test.com',
        })

        # Minimal configuration for a payment (Journal + Method)
        self.journal = self.env['account.journal'].create({
            'name': 'Test Bank',
            'type': 'bank',
            'code': 'BNKT',
            'currency_id': self.env.company.currency_id.id,
        })
        self.payment_method = self.env.ref('account.account_payment_method_manual_in')

    def test_01_sync_parent_to_child(self):
        """ Test: Parent (payment_email) -> Child (Create/Update/Archive) """

        # 1. Set a payment email
        email_a = "accounting@client.com"
        self.partner.payment_email = email_a

        # Verify child contact creation
        child = self.env['res.partner'].search([
            ('parent_id', '=', self.partner.id),
            ('is_receivable_account', '=', True)
        ])
        self.assertTrue(child, "The child contact should be created.")

        # VERIFY FAKE EMAIL LOGIC & TYPES
        fake_email_a = f"{email_a}.{self.partner.id}"
        self.assertEqual(child.payment_email, email_a,
                         "The child payment_email must match the parent payment email.")
        self.assertEqual(child.email, fake_email_a,
                         "The standard email must be the falsified unique email.")

        # Vérification des types
        self.assertEqual(child.type, 'other', "The contact type must be 'other'.")
        self.assertEqual(child.company_type, 'person', "The company_type must be 'person'.")

        # 2. Update parent email
        email_b = "billing@client.com"
        self.partner.payment_email = email_b

        # Verify that the SAME contact is updated with new fake email
        fake_email_b = f"{email_b}.{self.partner.id}"
        self.assertEqual(child.payment_email, email_b,
                         "The child payment_email should be updated.")
        self.assertEqual(child.email, fake_email_b, "The child fake email should be updated.")
        self.assertEqual(len(self.partner.child_ids), 1, "There should be no duplicates.")

        # 3. Clear the field (Archive)
        self.partner.payment_email = False
        self.assertFalse(child.active,
                         "The child contact should be archived if the field is cleared.")

        # 4. Set an email again (Reactivate)
        self.partner.payment_email = email_a
        self.assertTrue(child.active, "The child contact should be reactivated.")
        self.assertEqual(child.payment_email, email_a)

    def test_02_sync_child_to_parent(self):
        """ Test: Child (write payment_email) -> Parent (payment_email) """

        # Initialization
        self.partner.payment_email = "init@test.com"
        child = self.env['res.partner'].search([
            ('parent_id', '=', self.partner.id),
            ('is_receivable_account', '=', True)
        ])

        # Modify payment_email directly on the child contact
        # Note: We now listen to changes on 'payment_email', not 'email'
        new_email = "new_child@test.com"
        child.payment_email = new_email

        # Verify sync back to parent
        self.assertEqual(self.partner.payment_email, new_email,
                         "Changes on the child's payment_email must update the parent field.")

    def test_03_mail_composer_injection(self):
        """ Test: The wizard avoids sending to fake email and uses email_to string """

        # Setup: Partner with specific config
        target_email = "specific@test.com"
        self.partner.payment_email = target_email

        # Create a payment linked to this partner
        payment = self.env['account.payment'].create({
            'payment_type': 'inbound',
            'partner_type': 'customer',
            'partner_id': self.partner.id,
            'amount': 100,
            'journal_id': self.journal.id,
            'payment_method_id': self.payment_method.id,
        })

        # Instantiate the Mail Composer wizard
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

        # Verify that partner_ids is visually cleared
        if onchange_res and 'value' in onchange_res:
            self.assertEqual(onchange_res['value'].get('partner_ids'), [(6, 0, [])],
                             "The interface must visually clear the default recipients.")

        # 2. Test Get Mail Values (Sending Logic)
        # We must ensure that the wizard does NOT use partner_ids (because of fake email)
        # but uses the raw 'email_to' string.
        mail_values = composer.get_mail_values([payment.id])[payment.id]

        # A. Verify Comment Mode (partner_ids must be empty)
        if 'partner_ids' in mail_values:
            self.assertEqual(mail_values['partner_ids'], [],
                             "partner_ids must be empty so the"
                             " mail isn't sent to the fake address.")

        # B. Verify Mass Mail Mode (recipient_ids must be cleared)
        # In mass mail, it uses recipient_ids with commands. We expect [(5, 0, 0)] (clear all).
        if 'recipient_ids' in mail_values:
            self.assertEqual(mail_values['recipient_ids'], [(5, 0, 0)],
                             "recipient_ids must be cleared using ORM command.")

        # C. Verify email_to has the true string email
        self.assertEqual(mail_values.get('email_to'), target_email,
                         "email_to must contain the true raw email string.")


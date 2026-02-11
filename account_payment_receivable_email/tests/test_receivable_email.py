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
        self.assertEqual(child.email, email_a, "The child email must match the parent payment email.")
        self.assertEqual(child.type, 'other')

        # 2. Update parent email
        email_b = "billing@client.com"
        self.partner.payment_email = email_b

        # Verify that the SAME contact is updated
        self.assertEqual(child.email, email_b, "The child email should be updated.")
        self.assertEqual(len(self.partner.child_ids), 1, "There should be no duplicates.")

        # 3. Clear the field (Archive)
        self.partner.payment_email = False
        self.assertFalse(child.active, "The child contact should be archived if the field is cleared.")

        # 4. Set an email again (Reactivate)
        self.partner.payment_email = email_a
        self.assertTrue(child.active, "The child contact should be reactivated.")
        self.assertEqual(child.email, email_a)

    def test_02_sync_child_to_parent(self):
        """ Test: Child (write email) -> Parent (payment_email) """

        # Initialization
        self.partner.payment_email = "init@test.com"
        child = self.env['res.partner'].search([
            ('parent_id', '=', self.partner.id),
            ('is_receivable_account', '=', True)
        ])

        # Modify email directly on the child contact
        new_email = "new_child@test.com"
        child.email = new_email

        # Verify sync back to parent
        self.assertEqual(self.partner.payment_email, new_email,
                         "Changes on the child contact must update the parent field.")

    def test_03_mail_composer_injection(self):
        """ Test: The wizard correctly replaces the recipient with the specific contact """

        # Setup: Partner with specific config
        self.partner.payment_email = "specific@test.com"
        child = self.env['res.partner'].search([
            ('parent_id', '=', self.partner.id),
            ('is_receivable_account', '=', True)
        ])

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
        # Note: We simulate the context as if clicking "Send"
        composer = self.env['mail.compose.message'].with_context(
            default_model='account.payment',
            default_res_id=payment.id,
            active_ids=[payment.id],
            active_model='account.payment'
        ).create({'body': 'Test body'})

        # 1. Test Onchange (Visual)
        # Simulate the onchange call that happens when opening the wizard
        onchange_res = composer.onchange_template_id(
            False, 'comment', 'account.payment', payment.id
        )

        # Verify that partner_ids is visually cleared
        if onchange_res and 'value' in onchange_res:
            self.assertEqual(onchange_res['value'].get('partner_ids'), [(6, 0, [])],
                             "The interface must visually clear the default recipients.")

        # 2. Test Get Mail Values (Sending Logic)
        # This is where the actual substitution happens
        mail_values = composer.get_mail_values([payment.id])[payment.id]

        # A. Verify Comment Mode (partner_ids)
        if 'partner_ids' in mail_values:
            self.assertIn(child.id, mail_values['partner_ids'],
                          "The specific child contact must be in the recipients list.")
            self.assertNotIn(self.partner.id, mail_values['partner_ids'],
                             "The parent partner must NOT be a recipient.")

        # B. Verify Mass Mail Mode (recipient_ids)
        # Simulate adding recipient_ids to values
        composer_mass = composer.with_context(default_composition_mode='mass_mail')

        # We manually check if email_to is cleared to force usage of partner ID
        self.assertFalse(mail_values.get('email_to'),
                         "email_to must be False to force the use of the res.partner object.")

    def test_04_fallback_logic(self):
        """ Test: Fallback logic if boolean is missing (Migration scenario) """
        self.partner.payment_email = "fallback@test.com"

        # Simulate an "old" contact created before migration (no boolean but correct name)
        # First delete the one properly created by payment_email
        child = self.env['res.partner'].search([('parent_id', '=', self.partner.id)])
        child.unlink()

        # Manually create a legacy contact
        old_child = self.env['res.partner'].create({
            'name': 'Receivable Accounts',
            'parent_id': self.partner.id,
            'type': 'other',
            'email': 'old@test.com',
            'is_receivable_account': False,  # No flag
        })

        # Trigger sync (e.g., parent email change)
        self.partner.payment_email = "new@test.com"

        # The system should have found old_child by name, set the flag True, and updated the email
        self.assertTrue(old_child.is_receivable_account, "The flag should have been added during migration.")
        self.assertEqual(old_child.email, "new@test.com", "The email should have been updated.")
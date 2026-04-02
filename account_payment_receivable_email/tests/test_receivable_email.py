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
    self.assertEqual(child.payment_email, email_b, "The child payment_email should be updated.")
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

from odoo.addons.test_mail.tests.common import mail_new_test_user
from odoo.tests import common


class TestBankStatementPartnerMappingBase(common.TransactionCase):

    def setUp(self):
        """Prepare Users."""
        super(TestBankStatementPartnerMappingBase, self).setUp()

        # Test users to use through the various tests
        self.user_account = mail_new_test_user(self.env, login='sebastien', groups='account.group_account_user')
        self.user_account_id = self.user_account.id
        self.manager_account = mail_new_test_user(self.env, login='frederic', groups='account.group_account_manager')
        self.manager_account_id = self.manager_account.id

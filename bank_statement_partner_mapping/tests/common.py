from odoo.addons.test_mail.tests.common import mail_new_test_user
from odoo.tests import common
import time


class TestBankStatementPartnerMappingBase(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        """Prepare Users and Bank Statements."""
        super(TestBankStatementPartnerMappingBase, cls).setUpClass()

        # Test users to use through the various tests
        cls.user_account = mail_new_test_user(
            cls.env, login="sebastien", groups="account.group_account_user"
        )
        cls.user_account_id = cls.user_account.id
        cls.manager_account = mail_new_test_user(
            cls.env, login="frederic", groups="account.group_account_manager"
        )
        cls.manager_account_id = cls.manager_account.id

        cls.acc_bank_stmt_model = cls.env["account.bank.statement"]
        cls.acc_bank_stmt_line_model = cls.env["account.bank.statement.line"]
        cls.acc_stmt_partner_mapping_model = cls.env["bank.statement.partner.mapping"]
        cls.bank_journal_euro = cls.env["account.journal"].create(
            {"name": "Bank", "type": "bank", "code": "BNK67"}
        )
        cls.partner_stmt_complete = cls.env["res.partner"].create({"name": "Azure"})
        cls.partner_stmt_partial = cls.env["res.partner"].create(
            {"name": "Revenu Quebec"}
        )
        cls.partner_stmt = cls.env["res.partner"].create({"name": "Deco"})

        # Prepare setting
        cls.acc_stmt_partner_mapping_model.sudo(cls.manager_account_id).create(
            {
                "label": "RET Source",
                "mapping_type": "partial",
                "partner_id": cls.partner_stmt_partial.id,
            }
        )
        cls.acc_stmt_partner_mapping_model.sudo(cls.manager_account_id).create(
            {
                "label": "Compte A Payer",
                "mapping_type": "complete",
                "partner_id": cls.partner_stmt_complete.id,
            }
        )
        # Create Statement
        cls.bank_stmt = cls.acc_bank_stmt_model.create(
            {
                "journal_id": cls.bank_journal_euro.id,
                "date": time.strftime("%Y") + "-01-01",
            }
        )

        # create statement line without partner and  withoutjournal entry for complete mapping

        cls.bank_stmt_line = cls.acc_bank_stmt_line_model.sudo(
            cls.user_account_id
        ).create(
            {
                "name": "Compte A Payer",
                "statement_id": cls.bank_stmt.id,
                "amount": 40,
                "date": time.strftime("%Y") + "-01-01",
            }
        )
        # create statement line with partner and without journal entry
        cls.bank_stmt_partner_line = cls.acc_bank_stmt_line_model.sudo(
            cls.user_account_id
        ).create(
            {
                "name": "Compte A Payer",
                "statement_id": cls.bank_stmt.id,
                "amount": 500,
                "partner_id": cls.partner_stmt.id,
                "date": time.strftime("%Y") + "-01-01",
            }
        )

        # create statement line without partner and without journal entry for partal mapping
        cls.bank_stmt_patial_partner_line = cls.acc_bank_stmt_line_model.sudo(
            cls.user_account_id
        ).create(
            {
                "name": "RET Source 20",
                "statement_id": cls.bank_stmt.id,
                "amount": 500,
                "date": time.strftime("%Y") + "-01-01",
            }
        )

        # Create Statement  without  partner and with journal entry

        cls.statement = cls.acc_bank_stmt_model.create(
            {"journal_id": cls.bank_journal_euro.id, "balance_end_real": 500}
        )

        cls.statement_line = cls.acc_bank_stmt_line_model.sudo(
            cls.user_account_id
        ).create(
            {
                "name": "Compte A Payer",
                "statement_id": cls.statement.id,
                "amount": 500,
                "date": time.strftime("%Y") + "-01-01",
                "account_id": cls.bank_journal_euro.default_debit_account_id.id,
            }
        )

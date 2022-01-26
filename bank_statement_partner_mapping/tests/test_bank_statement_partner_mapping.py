from .common import TestBankStatementPartnerMappingBase


class TestBankStatementPartnerMapping(TestBankStatementPartnerMappingBase):

    def test_partner_not_defined_and_journal_entry_null(self):
        self.bank_stmt.button_recuperate_partners()
        assert self.bank_stmt_line.partner_id == self.partner_stmt_complete
        assert self.bank_stmt_patial_partner_line.partner_id == self.partner_stmt_partial

    def test_partner_defined_and_journal_entry_null(self):
        self.bank_stmt.button_recuperate_partners()
        assert self.bank_stmt_partner_line.partner_id == self.partner_stmt

    def test_partner_defined_and_journal_entry_not_null(self):
        self.bank_stmt.balance_end_real = 1040
        self.bank_stmt.line_ids.update({'account_id' :self.bank_journal_euro.default_debit_account_id.id})
        self.bank_stmt.button_confirm_bank()
        self.bank_stmt.button_recuperate_partners()
        assert self.bank_stmt_partner_line.partner_id == self.partner_stmt

    def test_partner_not_defined_and_journal_entry_not_null(self):
        self.statement.button_confirm_bank()
        self.statement.button_recuperate_partners()
        assert not self.statement_line.partner_id
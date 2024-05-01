# © 2024 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from .common import TestBankStatementPartnerMappingBase


class TestBankStatementPartnerMapping(TestBankStatementPartnerMappingBase):
    def test_partner_not_defined_and_bank_statement_open(self):
        self.bank_stmt.button_recuperate_partners()
        assert self.bank_stmt_line.partner_id == self.partner_stmt_complete
        assert (
            self.bank_stmt_patial_partner_line.partner_id == self.partner_stmt_partial
        )

    def test_partner_defined_and_bank_statement_open(self):
        self.bank_stmt.button_recuperate_partners()
        assert self.bank_stmt_partner_line.partner_id == self.partner_stmt

    def test_partner_defined_and_bank_statement_posted(self):
        self.bank_stmt.balance_end_real = 1040
        self.bank_stmt.button_post()
        self.bank_stmt.button_recuperate_partners()
        assert self.bank_stmt_partner_line.partner_id == self.partner_stmt

    def test_partner_not_defined_and_bank_statement_posted(self):
        self.statement.button_post()
        self.statement.button_recuperate_partners()
        assert not self.statement_line.partner_id

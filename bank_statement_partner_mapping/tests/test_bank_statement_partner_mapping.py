from odoo.addons.bank_statement_partner_mapping.tests.common import TestBankStatementPartnerMappingBase
from odoo.tools import mute_logger
import time


class TestBankStatementPartnerMapping(TestBankStatementPartnerMappingBase):

    @mute_logger('odoo.addons.base.models.ir_model', 'odoo.models')
    def test_partner_completion(self):

        self.acc_bank_stmt_model = self.env['account.bank.statement']
        self.acc_bank_stmt_line_model = self.env['account.bank.statement.line']
        self.acc_stmt_partner_mapping_model = self.env['bank.statement.partner.mapping']
        self.bank_journal_euro = self.env['account.journal'].create({'name': 'Bank', 'type': 'bank', 'code': 'BNK67'})
        self.partner_stmt = self.env['res.partner'].create({'name': 'Azure'})
        self.partner_stmt_1 = self.env['res.partner'].create({'name': 'Revenu Quebec'})

        # Prepare setting
        self.acc_stmt_partner_mapping_model.sudo(self.manager_account_id).create({'label': 'Compte A Payer',
                                                                                  'mapping_type': 'complete',
                                                                                  'partner_id': self.partner_stmt.id})
        # Test Bank Statement

        bank_stmt = self.acc_bank_stmt_model.create({
            'journal_id': self.bank_journal_euro.id,
            'date': time.strftime('%Y') + '-01-01',
        })

        # create statement line without partner and journal entry

        self.bank_stmt_line = self.acc_bank_stmt_line_model.sudo(self.user_account_id).create({'name': 'Compte A Payer',
                                                                                               'statement_id': bank_stmt.id,
                                                                                               'amount': 40,
                                                                                               'date': time.strftime('%Y') + '-01-01', })
        # create statement line with partner and journal entry
        self.bank_stmt_partner_line = self.acc_bank_stmt_line_model.sudo(self.user_account_id).create({'name': 'Compte A Payer',
                                                                                                       'statement_id': bank_stmt.id,
                                                                                                       'amount': 500,
                                                                                                       'partner_id': self.partner_stmt_1.id,
                                                                                                       'date': time.strftime('%Y') + '-01-01', })

        bank_stmt.button_recuperate_partners()
        # test partner_completion if partner_id not defined and journal_entry_ids is null : recuperate partner
        self.assertEqual(self.bank_stmt_line.partner_id, self.partner_stmt)
        # test partner_completion if partner_id defined and journal_entry_ids is null : keep the same partner
        self.assertEqual(self.bank_stmt_partner_line.partner_id, self.partner_stmt_1)

        statement = self.acc_bank_stmt_model.create({
            'journal_id': self.bank_journal_euro.id,
            'balance_end_real': 1100})

        self.statement_line = self.acc_bank_stmt_line_model.sudo(self.user_account_id).create(
            {'name': 'Compte A Payer',
             'statement_id': statement.id,
             'amount': 500,
             'date': time.strftime('%Y') + '-01-01',
             'account_id': self.bank_journal_euro.default_debit_account_id.id})

        self.statement_partner_line = self.acc_bank_stmt_line_model.sudo(self.user_account_id).create(
            {'name': 'Compte A Payer',
             'statement_id': statement.id,
             'amount': 600,
             'partner_id': self.partner_stmt_1.id,
             'date': time.strftime('%Y') + '-01-01',
             'account_id': self.bank_journal_euro.default_debit_account_id.id})

        statement.button_open()
        statement.button_confirm_bank()
        statement.button_recuperate_partners()
        # test partner_completion if partner_id not defined and journal_entry_ids is not null : don't recuperate partner
        self.assertTrue(self.statement_line.sudo().journal_entry_ids)
        self.assertFalse(self.statement_line.partner_id)
        # test partner_completion if partner_id  defined and journal_entry_ids is not null : keep the same partner
        self.assertTrue(self.statement_partner_line.sudo().journal_entry_ids)
        self.assertEqual(self.statement_partner_line.partner_id, self.partner_stmt_1)

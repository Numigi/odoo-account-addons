# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
import logging


class AccountBankStatement(models.Model):
    _inherit = "account.bank.statement"

    conciliation_id = fields.Many2one("conciliation.wizard")

    @api.model
    def create(self, values):
        ConciliationWizard = self.env["conciliation.wizard"]
        current_id = super(AccountBankStatement, self).create(values)
        wizard_id = ConciliationWizard.create(
            {
                "statement_id": current_id.id,
            }
        )
        current_id.conciliation_id = wizard_id.id
        return current_id

    def button_bank_conciliation(self):
        return {
            "name": _("Bank conciliation report"),
            "view_type": "form",
            "view_mode": "form",
            "res_model": "conciliation.wizard",
            "views": [(False, "form")],
            "type": "ir.actions.act_window",
            "target": "new",
            "res_id": self.conciliation_id.id,
        }

    def compute_outbound(self):
        outbound_ids = self.conciliation_id.get_defaut_line().filtered(lambda x: x.date <= self.date and x.credit > 0)
        return outbound_ids

    def compute_inbound(self):
        inbound_ids = self.conciliation_id.get_defaut_line().filtered(lambda x: x.date <= self.date and x.debit > 0)
        return inbound_ids

    def get_sum_inbound(self):
        payments = self.compute_inbound()
        return sum(payments.mapped("debit"))

    def get_sum_outbound(self):
        payments = self.compute_outbound()
        return sum(payments.mapped("credit"))

    def get_conciliation_balance(self):
        return self.balance_end_real - self.get_sum_outbound() + self.get_sum_inbound()

    def get_account_balance(self):
        AccountMoveLine = self.env["account.move.line"]
        account_ids = [
            self.journal_id.default_debit_account_id.id,
            self.journal_id.default_credit_account_id.id,
        ]
        line_ids = AccountMoveLine.search([("account_id", "in", account_ids)])
        debit = sum(line_ids.mapped("debit"))
        credit = sum(line_ids.mapped("credit"))
        return debit - credit

    def get_difference(self):
        return self.get_conciliation_balance() - self.get_account_balance()

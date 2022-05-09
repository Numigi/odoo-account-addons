# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ConciliationWizard(models.Model):
    _name = "conciliation.wizard"
    _description = "Conciliation Wizard"

    name = fields.Char(string="Compte", compute="_compute_name")
    statement_id = fields.Many2one("account.bank.statement")
    journal_id = fields.Many2one("account.journal", related="statement_id.journal_id")
    date = fields.Date(string="Date", related="statement_id.date")
    balance_end_real = fields.Monetary(
        string="Ending Balance", related="statement_id.balance_end_real"
    )
    payment_outbound_ids = fields.One2many(
        "account.move.line", "rec_outbound_id", compute="_compute_outbond"
    )
    total_outbound = fields.Monetary(string="Total Oustanding Cheques")
    payment_inbound_ids = fields.One2many(
        "account.move.line", "rec_inbound_id", compute="_compute_inbond"
    )
    total_inbound = fields.Monetary(string="Oustanding Deposits")
    reconciliation_balance = fields.Monetary(
        string="Calculated Balance with Reconciliation"
    )
    currency_id = fields.Many2one("res.currency")
    total_outbound = fields.Monetary(
        string="Total Outstanding Cheques", compute="_compute_outbond"
    )
    total_inbound = fields.Monetary(
        string="Total Outstanding Deposits", compute="_compute_inbond"
    )

    conciliation_balance = fields.Monetary(
        string="Calculated Balance with Reconciliation", compute="_compute_balance"
    )
    difference = fields.Monetary(string="Difference", compute="_compute_balance")
    account_balance = fields.Monetary(
        string="Total Outstanding Deposits", compute="_compute_balance"
    )

    @api.depends("journal_id")
    def _compute_name(self):
        for item in self:
            item.name = "%s - %s" % (
                item.journal_id.code,
                item.journal_id.default_debit_account_id.name,
            )

    def get_defaut_line(self):
        AccountMoveLine = self.env["account.move.line"]
        journal_default_accounts = [
            self.journal_id.default_debit_account_id.id,
            self.journal_id.default_credit_account_id.id,
        ]
        default_domain = [
            ("journal_id", "=", self.journal_id.id),
            ("account_id", "in", journal_default_accounts),
            ("statement_line_id", "=", False),
            ("state", "=", "posted"),
        ]
        return AccountMoveLine.search(default_domain)

    def _compute_outbond(self):
        outbound_ids = self.get_defaut_line().filtered(
            lambda x: x.date <= self.date and x.credit > 0
        )
        for item in self:
            item.payment_outbound_ids = [(6, 0, outbound_ids.ids)]
            item.total_outbound = sum(outbound_ids.mapped("credit"))

    def _compute_inbond(self):
        inbound_ids = self.get_defaut_line().filtered(
            lambda x: x.date <= self.date and x.debit > 0
        )
        for item in self:
            item.payment_inbound_ids = [(6, 0, inbound_ids.ids)]
            item.total_inbound = sum(inbound_ids.mapped("debit"))

    @api.depends("total_outbound", "total_inbound")
    def _compute_balance(self):
        for item in self:
            item.conciliation_balance = (
                item.balance_end_real - item.total_outbound - item.total_inbound
            )
            item.account_balance = item.statement_id.get_account_balance()
            item.difference = item.conciliation_balance - item.account_balance

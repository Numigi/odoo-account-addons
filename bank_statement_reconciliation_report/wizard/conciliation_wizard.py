# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ConciliationWizard(models.Model):
    _name = "conciliation.wizard"
    _description = "Conciliation Wizard"

    name = fields.Char(string="Account", compute="_compute_name")
    statement_id = fields.Many2one("account.bank.statement")
    journal_id = fields.Many2one(
        "account.journal", related="statement_id.journal_id", store=True)
    date = fields.Date(
        string="Bank statement end date", related="statement_id.date_end_bank_statement", store=True
    )
    balance_end_real = fields.Monetary(
        string="Statement Ending Balance", related="statement_id.balance_end_real", store=True
    )
    payment_outbound_ids = fields.One2many(
        "account.move.line", "rec_outbound_id", compute="_compute_outbound"
    )
    payment_inbound_ids = fields.One2many(
        "account.move.line", "rec_inbound_id", compute="_compute_inbound"
    )
    currency_id = fields.Many2one(
        "res.currency", related="statement_id.currency_id", store=True)
    total_outbound = fields.Monetary(
        string="Total Outstanding Cheques", compute="_compute_outbound"
    )
    total_inbound = fields.Monetary(
        string="Total Outstanding Deposits", compute="_compute_inbound")

    conciliation_balance = fields.Monetary(
        string="Calculated Balance with Reconciliation", compute="_compute_balance"
    )
    difference = fields.Monetary(
        string="Difference", compute="_compute_balance")
    account_balance = fields.Monetary(
        string="Balance at date", compute="_compute_balance")

    @api.depends("journal_id")
    def _compute_name(self):
        for item in self:
            journal = item.journal_id
            item.name = "%s - %s" % (
                journal.code,
                journal.default_debit_account_id.name,
            )

    def _compute_outbound(self):
        for item in self:
            outbounds = item._outbound_credit(item.date)
            item.payment_outbound_ids = [(6, 0, outbounds.ids)]
            journal_account = item.journal_id.default_debit_account_id
            if journal_account and journal_account.currency_id \
                    and journal_account.currency_id != \
                    item.statement_id.company_id.currency_id:
                item.total_outbound = sum(
                    outbounds.mapped("amount_currency")) * -1
            else:
                item.total_outbound = sum(outbounds.mapped("credit"))

    def _outbound_credit(self, date):
        return self._get_move_lines(date).filtered(lambda move_line: move_line.credit > 0)

    def _get_move_lines(self, date):
        journal = self.journal_id
        journal_debit_id = journal.default_debit_account_id.id
        journal_credit_id = journal.default_credit_account_id.id
        if journal_debit_id == journal_credit_id:
            domain = [("journal_id", "=", journal.id),
                      ("account_id", "=", journal_debit_id)]
        else:
            domain = [
                ("journal_id", "=", journal.id),
                ("account_id", "in", [journal_debit_id, journal_credit_id]),
            ]
        domain += [
            ("statement_line_id", "=", False),
            ("state", "=", "posted"),
            ("date", "<=", date),
        ]
        return self.env["account.move.line"].search(domain)

    def _compute_inbound(self):
        for item in self:
            inbounds = item._inbound_debit(item.date)
            item.payment_inbound_ids = [(6, 0, inbounds.ids)]
            journal_account = item.journal_id.default_debit_account_id
            if journal_account and journal_account.currency_id \
                    and journal_account.currency_id != \
                    item.statement_id.company_id.currency_id:
                item.total_inbound = sum(
                    inbounds.mapped("amount_currency"))
            else:
                item.total_inbound = sum(inbounds.mapped("debit"))

    def _inbound_debit(self, date):
        return self._get_move_lines(date).filtered(lambda move_line: move_line.debit > 0)

    @api.depends("total_outbound", "total_inbound")
    def _compute_balance(self):
        for item in self:
            item.conciliation_balance = (
                item.balance_end_real - item.total_outbound + item.total_inbound
            )
            item.account_balance = item._get_account_balance()
            item.difference = item.conciliation_balance - item.account_balance

    def _get_account_balance(self):
        journal = self.journal_id
        account_debit_id = journal.default_debit_account_id.id
        account_credit_id = journal.default_credit_account_id.id
        domain = [('date', '<=', self.date), ("state", "=", "posted")]
        if account_debit_id == account_credit_id:
            domain.append(("account_id", "=", account_debit_id))
        else:
            domain.append(
                ("account_id", "in", [account_debit_id, account_credit_id]))
        move_lines = self.env["account.move.line"].search(domain)
        journal_account = journal.default_debit_account_id
        if journal_account and journal_account.currency_id \
                and journal_account.currency_id != \
                self.statement_id.company_id.currency_id:
            return sum(move_lines.mapped("amount_currency"))
        else:
            return sum(move_lines.mapped("debit")) - sum(move_lines.mapped("credit"))

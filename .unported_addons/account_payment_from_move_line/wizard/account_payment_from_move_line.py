# © 2019 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class PaymentFromMoveLineWizard(models.TransientModel):

    _name = "account.payment.from.move.line"
    _description = "Payment from Move Line Wizard"

    move_line_ids = fields.Many2many(
        "account.move.line",
        "account_payment_from_move_line_rel",
        "wizard_id",
        "move_line_id",
        string="Move Lines",
    )

    partner_id = fields.Many2one(
        "res.partner",
        "Partner",
        compute="_compute_partner",
    )

    @api.depends("move_line_ids")
    def _compute_partner(self):
        for wizard in self:
            wizard.partner_id = wizard.move_line_ids.mapped(
                "partner_id.commercial_partner_id",
            )

    counterpart_account_id = fields.Many2one(
        "account.account",
        "Counterpart Account",
        compute="_compute_receivable_account",
    )

    @api.depends("move_line_ids")
    def _compute_receivable_account(self):
        for wizard in self:
            wizard.counterpart_account_id = wizard.move_line_ids.mapped("account_id")

    company_currency_id = fields.Many2one(
        "res.currency",
        compute="_compute_currencies",
    )

    move_lines_currency_id = fields.Many2one(
        "res.currency",
        compute="_compute_currencies",
    )

    @api.depends("move_line_ids")
    def _compute_currencies(self):
        for wizard in self:
            wizard.company_currency_id = wizard.move_line_ids.mapped(
                "company_id.currency_id"
            )
            wizard.move_lines_currency_id = (
                wizard.move_line_ids.mapped("currency_id") or wizard.company_currency_id
            )

    amount = fields.Monetary("Payment Amount")

    move_lines_residual_amount = fields.Monetary(
        "Residual Amount",
        currency_field="move_lines_currency_id",
        compute="_compute_move_lines_residual_amount",
    )

    @api.depends("move_lines_currency_id", "company_currency_id", "move_line_ids")
    def _compute_move_lines_residual_amount(self):
        for wizard in self:
            if wizard.move_lines_currency_id == wizard.company_currency_id:
                wizard.move_lines_residual_amount = sum(
                    line.amount_residual for line in wizard.move_line_ids
                )
            else:
                wizard.move_lines_residual_amount = sum(
                    line.amount_residual_currency for line in wizard.move_line_ids
                )

    currency_id = fields.Many2one("res.currency", "Currency")
    journal_id = fields.Many2one(
        "account.journal",
        string="Payment Journal",
        domain=[("type", "in", ("bank", "cash"))],
    )
    payment_method_id = fields.Many2one("account.payment.method", "Payment Method")
    communication = fields.Char("Memo")
    payment_date = fields.Date(string="Payment Date", default=fields.Date.context_today)

    payment_difference = fields.Monetary(compute="_compute_payment_difference")
    payment_difference_handling = fields.Selection(
        [
            ("open", "Keep open"),
            ("reconcile", "Mark as fully paid"),
        ],
        default="open",
    )
    writeoff_account_id = fields.Many2one(
        "account.account",
        string="Difference Account",
        domain=[("deprecated", "=", False)],
    )
    writeoff_label = fields.Char(
        string="Payment Difference Label",
        help="The label of the counterpart that will hold the payment difference.",
        default="Write-Off",
    )

    def _get_available_payment_methods(self):
        return self.journal_id.inbound_payment_method_ids

    @api.onchange("journal_id")
    def _onchange_journal_set_available_payment_methods(self):
        available_methods = self._get_available_payment_methods()
        self.payment_method_id = available_methods and available_methods[0] or False
        return {"domain": {"payment_method_id": [("id", "in", available_methods.ids)]}}

    @api.depends("move_line_ids", "amount", "payment_date", "currency_id")
    def _compute_payment_difference(self):
        wizards_with_move_lines = self.filtered(lambda w: w.move_line_ids)

        for wizard in wizards_with_move_lines:
            residual_amount = wizard.move_lines_residual_amount
            residual_amount_currency = wizard.move_lines_currency_id
            payment_currency = wizard.currency_id
            company = wizard.move_line_ids.mapped("company_id")
            residual_amount_in_payment_currency = residual_amount_currency._convert(
                residual_amount,
                payment_currency,
                company,
                wizard.payment_date or fields.Date.today(),
            )
            wizard.payment_difference = (
                residual_amount_in_payment_currency - wizard.amount
            )

    def compute_amount_and_currency(self):
        """Compute the amount and currency for the wizard.

        The computation of these fields must be triggered manually,
        so that the user may override these values.
        """
        self.amount = self.move_lines_residual_amount
        self.currency_id = self.move_lines_currency_id

    def compute_communication(self):
        lines_with_reference = self.move_line_ids.filtered(lambda l: l.ref)
        self.communication = " ".join(sorted(lines_with_reference.mapped("ref")))

    def _get_payment_vals(self):
        return {
            "amount": self.amount,
            "currency_id": self.currency_id.id,
            "journal_id": self.journal_id.id,
            "partner_id": self.partner_id.id,
            "partner_type": "customer",
            "payment_method_id": self.payment_method_id.id,
            "payment_type": "inbound",
            "communication": self.communication,
            "payment_date": self.payment_date,
        }

    def _get_payment_post_context(self):
        return {
            "force_payment_destination_account_id": self.counterpart_account_id.id,
        }

    def _reconcile_payment(self, payment):
        payment_move_line = payment.move_line_ids.filtered(
            lambda l: l.account_id == self.counterpart_account_id
        )
        lines_to_reconcile = self.move_line_ids | payment_move_line

        if self.payment_difference and self.payment_difference_handling == "reconcile":
            lines_to_reconcile.reconcile(
                writeoff_acc_id=self.writeoff_account_id,
                writeoff_journal_id=self.journal_id,
            )
        else:
            lines_to_reconcile.reconcile()

    def validate(self):
        payment = self.env["account.payment"].create(self._get_payment_vals())
        payment.with_context(**self._get_payment_post_context()).post()
        self._reconcile_payment(payment)
        return payment.get_formview_action()

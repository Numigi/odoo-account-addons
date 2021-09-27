# © 2021 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import json
import stripe
from stripe.error import AuthenticationError
from datetime import datetime
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from ..interface import BalanceTransactionInterface

STRIPE = "stripe"


class OnlineBankStatementProvider(models.Model):

    _inherit = "online.bank.statement.provider"

    stripe_api_key = fields.Char()

    def test_stripe_api_key(self):
        try:
            self._try_stripe_api_key()
        except AuthenticationError:
            raise UserError(_("The Stripe API key is invalid."))
        else:
            raise UserError(_("The Stripe API key is valid."))

    def _try_stripe_api_key(self):
        stripe.Balance.retrieve(api_key=self.stripe_api_key)

    @api.model
    def _get_available_services(self):
        return super()._get_available_services() + [(STRIPE, "Stripe")]

    @api.multi
    def _obtain_statement_data(self, date_since, date_until):
        if self.service != STRIPE:
            return super()._obtain_statement_data(date_since, date_until)

        self._check_stripe_api_key()

        interface = self._get_stripe_interface(date_since, date_until)
        lines = self._iter_statement_lines_from_stripe(interface)
        statement_values = self._get_stripe_statement_values(interface)
        return list(lines), statement_values

    def _check_stripe_api_key(self):
        if not self.stripe_api_key:
            raise ValidationError(
                _("The stripe api key is not defined on the Stripe provider.")
            )

    def _get_stripe_interface(self, date_since, date_until):
        currency = self._get_stripe_currency_code()
        return BalanceTransactionInterface(
            datetime_from=date_since,
            datetime_to=date_until,
            api_key=self.stripe_api_key,
            currency=currency,
        )

    def _get_stripe_statement_values(self, interface):
        return {
            "balance_start": interface.get_start_balance(),
            "balance_end_real": interface.get_end_balance(),
        }

    def _iter_statement_lines_from_stripe(self, interface):
        transactions = interface.list_transactions()
        unimported_transactions = self._get_unimported_transactions(
            transactions
        )

        for tx in unimported_transactions:
            yield self._map_stripe_transaction(tx)

            if tx.get("fee"):
                yield self._map_stripe_fee(tx)

    def _get_unimported_transactions(self, transactions):
        tx_ids = [tx["id"] for tx in transactions]
        statement_lines = self.env["account.bank.statement.line"].search(
            [("stripe_id", "in", tx_ids)]
        )
        imported_tx_ids = set(statement_lines.mapped("stripe_id"))
        return [tx for tx in transactions if tx["id"] not in imported_tx_ids]

    def _map_stripe_transaction(self, tx):
        vals = self._map_stripe_common(tx)
        label = _("Transaction ({})").format(tx.get("description"))
        vals.update(
            name=label,
            note=label,
            amount=tx.get("amount", 0) / 100,
        )
        return vals

    def _map_stripe_fee(self, tx):
        vals = self._map_stripe_common(tx)
        label = _("Fee ({})").format(tx.get("description"))
        vals.update(
            name=label,
            note=label,
            amount=-tx.get("fee", 0) / 100,
        )
        return vals

    def _map_stripe_common(self, tx):
        return {
            "stripe_id": tx["id"],
            "stripe_payload": json.dumps(tx, indent=2, sort_keys=True),
            "partner_id": self._get_stripe_partner_id(tx),
            "partner_name": self._get_stripe_partner_display_name(tx),
            "ref": tx.get("description"),
            "date": self._get_stripe_transaction_date(tx),
        }

    def _get_stripe_partner_id(self, tx):
        email = self._get_stripe_email(tx)
        if email:
            partner = self.env["res.partner"].search([("email", "=", email)])
            if len(partner) == 1:
                return partner.id

    def _get_stripe_partner_display_name(self, tx):
        email = self._get_stripe_email(tx)
        name = self._get_stripe_partner_name(tx)
        return f"{name} ({email})" if email else name

    def _get_stripe_partner_name(self, tx):
        billing_details = self._get_stripe_billing_details(tx)
        return billing_details.get("name")

    def _get_stripe_email(self, tx):
        billing_details = self._get_stripe_billing_details(tx)
        return billing_details.get("email")

    def _get_stripe_billing_details(self, tx):
        source = tx.get("source") or {}
        return source.get("billing_details") or {}

    def _get_stripe_transaction_date(self, tx):
        timestamp = tx["created"]
        datetime_ = datetime.fromtimestamp(timestamp)
        return fields.Date.context_today(self, datetime_)

    def _get_stripe_currency_code(self):
        currency = self.journal_id.currency_id or self.company_id.currency_id
        return currency.name

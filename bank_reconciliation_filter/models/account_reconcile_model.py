# © 2021 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class AccountReconcileModel(models.AbstractModel):

    _inherit = "account.reconcile.model"

    def _apply_conditions(self, query, params):
        if self.rule_type == 'invoice_matching':
            query, params = self._apply_show_payment_only_condition(query, params)

        return super()._apply_conditions(query, params)

    def _apply_show_payment_only_condition(self, query, params):
        disabled_journals = self._get_journals_with_show_payment_only()
        liquidity_accounts = self._get_liquidity_accounts()

        if disabled_journals:
            query += ' AND (st_line.journal_id NOT IN %s OR aml.account_id IN %s)'
            params += [tuple(disabled_journals.ids), tuple(liquidity_accounts.ids)]

        return query, params

    def _get_journals_with_show_payment_only(self):
        return self.env["account.journal"].search(
            [
                ("reconcile_show_payments_only", "=", True),
            ]
        )

    def _get_liquidity_accounts(self):
        return self.env["account.account"].search(
            [
                ("internal_type", "=", "liquidity"),
            ]
        )

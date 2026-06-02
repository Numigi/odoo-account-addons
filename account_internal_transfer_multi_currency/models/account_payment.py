# Copyright 2026 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).


# -*- coding: utf-8 -*-
from odoo import fields, models


class AccountPayment(models.Model):
    _inherit = "account.payment"

    def copy_data(self, default=None):
        """ 1. Handle amount and currency conversion when creating the paired payment """
        default = dict(default or {})

        # Check if the copy is triggered by the creation of a paired internal transfer
        is_paired_transfer = bool(default.get("paired_internal_transfer_payment_id"))

        vals_list = super().copy_data(default)

        if is_paired_transfer:
            for payment, vals in zip(self, vals_list):
                dest_journal = payment.destination_journal_id

                # Target currency: the journal's currency or, if none, the journal's company currency
                dest_currency = dest_journal.currency_id or dest_journal.company_id.currency_id
                source_currency = payment.currency_id or payment.journal_id.company_id.currency_id

                # If there is a currency change, apply the conversion
                if dest_currency and source_currency != dest_currency:
                    # _convert automatically handles rounding (round=True by default)
                    converted_amount = source_currency._convert(
                        payment.amount,
                        dest_currency,
                        payment.company_id,
                        payment.date or fields.Date.context_today(payment),
                    )

                    # Inject our modified values into the creation dictionary
                    vals["amount"] = converted_amount
                    vals["currency_id"] = dest_currency.id

        return vals_list

    def _generate_journal_entry(self, write_off_line_vals=None, force_balance=None, line_ids=None):
        """ 2. Force the balance in company currency to avoid the 1-cent rounding difference """

        # If we are generating the journal entry for the paired payment (which was just copied)
        if not force_balance and len(self) == 1:
            orig_payment = self.paired_internal_transfer_payment_id

            # Ensure the original payment exists and belongs to the same company
            if orig_payment and orig_payment.company_id == self.company_id:

                # Fetch the counterpart journal item of the original payment
                _liquidity, counterpart, _writeoff = orig_payment._seek_for_lines()

                if counterpart:
                    # Force the new payment's balance to be exactly the same as the original's
                    force_balance = abs(sum(counterpart.mapped('balance')))

        # Let Odoo generate the journal entry with this forced balance
        return super()._generate_journal_entry(
            write_off_line_vals=write_off_line_vals,
            force_balance=force_balance,
            line_ids=line_ids
        )

    def _create_paired_internal_transfer_payment(self):
        """ 3. Concaténer les références des 2 pièces comptables dans le mémo """
        # On laisse Odoo générer et valider le paiement miroir
        res = super()._create_paired_internal_transfer_payment()

        for payment in self:
            paired = payment.paired_internal_transfer_payment_id

            # Si le paiement miroir a bien été créé et que les deux ont un nom (référence de pièce)
            if paired and payment.name and paired.name:
                # Concaténation des deux références (ex: "BNK1/2026/0001 - BNK2/2026/0001")
                combined_memo = f"{payment.name} - {paired.name}"

                # Mise à jour du mémo sur les deux paiements
                payment.memo = combined_memo
                paired.memo = combined_memo

        return res

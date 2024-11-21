# Copyright 2024 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import operator
from datetime import date
from collections import OrderedDict

from odoo import api, models
from odoo.tools import float_is_zero
from odoo.addons.account_financial_report.report.aged_partner_balance import (
    AgedPartnerBalanceReport as AgedPartnerBalanceReportOriginal,
)


class AgedPartnerBalanceReport(AgedPartnerBalanceReportOriginal):

    def _get_move_lines_data(
        self,
        company_id,
        account_ids,
        partner_ids,
        date_at_object,
        date_from,
        only_posted_moves,
        show_move_line_details,
    ):
        domain = self._get_move_lines_domain_not_reconciled(
            company_id, account_ids, partner_ids, only_posted_moves, date_from
        )
        ml_fields = self._get_ml_fields()
        line_model = self.env["account.move.line"]
        move_lines = line_model.search_read(domain=domain, fields=ml_fields)
        journals_ids = set()
        partners_ids = set()
        partners_data = {}
        ag_pb_data = {}
        if date_at_object < date.today():
            (
                acc_partial_rec,
                debit_amount,
                credit_amount,
                debit_amount_currency,
                credit_amount_currency,
            ) = self._get_account_partial_reconciled(company_id, date_at_object)
            if acc_partial_rec:
                ml_ids = list(map(operator.itemgetter("id"), move_lines))
                debit_ids = list(
                    map(operator.itemgetter("debit_move_id"), acc_partial_rec)
                )
                credit_ids = list(
                    map(operator.itemgetter("credit_move_id"), acc_partial_rec)
                )
                move_lines = self._recalculate_move_lines(
                    move_lines,
                    debit_ids,
                    credit_ids,
                    debit_amount,
                    credit_amount,
                    ml_ids,
                    account_ids,
                    company_id,
                    partner_ids,
                    only_posted_moves,
                    debit_amount_currency,
                    credit_amount_currency,
                )
        move_lines = [
            move_line
            for move_line in move_lines
            if move_line["date"] <= date_at_object
            and not float_is_zero(move_line["amount_residual"], precision_digits=2)
        ]
        for move_line in move_lines:
            journals_ids.add(move_line["journal_id"][0])
            acc_id = move_line["account_id"][0]
            if move_line["partner_id"]:
                prt_id = move_line["partner_id"][0]
                prt_name = move_line["partner_id"][1]
            else:
                prt_id = 0
                prt_name = ""
            if prt_id not in partners_ids:
                partners_data.update({prt_id: {"id": prt_id, "name": prt_name}})
                partners_ids.add(prt_id)
            if acc_id not in ag_pb_data.keys():
                ag_pb_data = self._initialize_account(ag_pb_data, acc_id)
            if prt_id not in ag_pb_data[acc_id]:
                ag_pb_data = self._initialize_partner(ag_pb_data, acc_id, prt_id)
            move_line_data = {}
            if show_move_line_details:
                if move_line["ref"] == move_line["name"]:
                    if move_line["ref"]:
                        ref_label = move_line["ref"]
                    else:
                        ref_label = ""
                elif not move_line["ref"]:
                    ref_label = move_line["name"]
                elif not move_line["name"]:
                    ref_label = move_line["ref"]
                else:
                    ref_label = move_line["ref"] + str(" - ") + move_line["name"]
                move_line_data.update(
                    {
                        "line_rec": line_model.browse(move_line["id"]),
                        "date": move_line["date"],
                        "entry": move_line["move_id"][1],
                        "jnl_id": move_line["journal_id"][0],
                        "acc_id": acc_id,
                        "partner": prt_name,
                        "ref_label": ref_label,
                        "due_date": move_line["date_maturity"],
                        "residual": move_line["amount_residual"],
                        # Add amount_currency and currency_id data
                        "amount_currency": move_line["amount_currency"],
                        "currency_id": move_line["currency_id"],
                    }
                )
                ag_pb_data[acc_id][prt_id]["move_lines"].append(move_line_data)
            ag_pb_data = self._calculate_amounts(
                ag_pb_data,
                acc_id,
                prt_id,
                move_line["amount_residual"],
                move_line["date_maturity"],
                date_at_object,
                # Add amount_currency and currency_id data
                move_line["amount_currency"],
                move_line["currency_id"][0],  # it is a tuple of id and name
            )
        journals_data = self._get_journals_data(list(journals_ids))
        accounts_data = self._get_accounts_data(ag_pb_data.keys())

        # Sort partners data by name, apply the same order to ag_pb_data
        partners_data = self._sort_partners_data(partners_data)
        partner_names = self._extract_partner_names(partners_data)
        ag_pb_data = self._sort_partners(ag_pb_data, partner_names)

        return ag_pb_data, accounts_data, partners_data, journals_data

    def _create_account_list(
        self,
        ag_pb_data,
        accounts_data,
        partners_data,
        journals_data,
        show_move_line_details,
        date_at_oject,
    ):
        aged_partner_data = []
        for account in accounts_data.values():
            acc_id = account["id"]
            account.update(
                {
                    "residual": ag_pb_data[acc_id]["residual"],
                    "current": ag_pb_data[acc_id]["current"],
                    "30_days": ag_pb_data[acc_id]["30_days"],
                    "60_days": ag_pb_data[acc_id]["60_days"],
                    "90_days": ag_pb_data[acc_id]["90_days"],
                    "120_days": ag_pb_data[acc_id]["120_days"],
                    "older": ag_pb_data[acc_id]["older"],
                    "partners": [],
                    # Add amount_currency and currency_id data
                    "amount_currency": ag_pb_data[acc_id]["amount_currency"],
                    "currency_id": ag_pb_data[acc_id]["currency_id"],
                }
            )
            for prt_id in ag_pb_data[acc_id]:
                if isinstance(prt_id, int):
                    partner = {
                        "name": partners_data[prt_id]["name"],
                        "residual": ag_pb_data[acc_id][prt_id]["residual"],
                        "current": ag_pb_data[acc_id][prt_id]["current"],
                        "30_days": ag_pb_data[acc_id][prt_id]["30_days"],
                        "60_days": ag_pb_data[acc_id][prt_id]["60_days"],
                        "90_days": ag_pb_data[acc_id][prt_id]["90_days"],
                        "120_days": ag_pb_data[acc_id][prt_id]["120_days"],
                        "older": ag_pb_data[acc_id][prt_id]["older"],
                        # Add amount_currency and currency_id data
                        "amount_currency": ag_pb_data[acc_id][prt_id][
                            "amount_currency"
                        ],
                        "currency_id": ag_pb_data[acc_id][prt_id]["currency_id"],
                    }
                    if show_move_line_details:
                        move_lines = []
                        for ml in ag_pb_data[acc_id][prt_id]["move_lines"]:
                            ml.update(
                                {
                                    "journal": journals_data[ml["jnl_id"]]["code"],
                                    "account": accounts_data[ml["acc_id"]]["code"],
                                }
                            )
                            self._compute_maturity_date(ml, date_at_oject)
                            move_lines.append(ml)
                        move_lines = sorted(move_lines, key=lambda k: (k["date"]))
                        partner.update({"move_lines": move_lines})
                    account["partners"].append(partner)
            aged_partner_data.append(account)
        return aged_partner_data

    AgedPartnerBalanceReportOriginal._get_move_lines_data = _get_move_lines_data
    AgedPartnerBalanceReportOriginal._create_account_list = _create_account_list


class AgedPartnerBalanceReportInherit(models.AbstractModel):
    _inherit = "report.account_financial_report.aged_partner_balance"

    def _sort_partners_data(self, partners_data):
        return OrderedDict(
            sorted(partners_data.items(), key=lambda item: item[1]["name"])
        )

    def _extract_partner_names(self, partners_data):
        return {prt_id: prt_data["name"] for prt_id, prt_data in partners_data.items()}

    def _sort_partners(self, ag_pb_data, partner_names):
        sorted_ag_pb_data = {}
        for acc_id, acc_data in ag_pb_data.items():
            # Extract partner data
            partners = {
                prt_id: prt_data
                for prt_id, prt_data in acc_data.items()
                if isinstance(prt_id, int)
            }
            # Sort partners by name
            sorted_partners = OrderedDict(
                sorted(partners.items(), key=lambda item: partner_names[item[0]])
            )
            # Update account data with sorted partners
            sorted_ag_pb_data[acc_id] = {
                k: v for k, v in acc_data.items() if not isinstance(k, int)
            }
            sorted_ag_pb_data[acc_id].update(sorted_partners)
        return sorted_ag_pb_data

    @api.model
    def _initialize_account(self, ag_pb_data, acc_id):
        ag_pb_data = super()._initialize_account(ag_pb_data, acc_id)
        ag_pb_data[acc_id]["amount_currency"] = 0.0
        ag_pb_data[acc_id]["currency_id"] = None
        return ag_pb_data

    @api.model
    def _initialize_partner(self, ag_pb_data, acc_id, prt_id):
        ag_pb_data = super()._initialize_partner(ag_pb_data, acc_id, prt_id)
        ag_pb_data[acc_id][prt_id]["amount_currency"] = 0.0
        ag_pb_data[acc_id][prt_id]["currency_id"] = None
        return ag_pb_data

    def _get_ml_fields(self):
        res = super()._get_ml_fields()
        res.append("amount_currency")
        res.append("currency_id")
        return res

    @api.model
    def _calculate_amounts(
        self,
        ag_pb_data,
        acc_id,
        prt_id,
        residual,
        due_date,
        date_at_object,
        amount_currency=None,
        currency_id=None,
    ):
        ag_pb_data = super()._calculate_amounts(
            ag_pb_data, acc_id, prt_id, residual, due_date, date_at_object
        )
        if amount_currency:
            ag_pb_data[acc_id]["amount_currency"] += amount_currency
            ag_pb_data[acc_id][prt_id]["amount_currency"] += amount_currency
        if currency_id:
            ag_pb_data[acc_id]["currency_id"] = currency_id
            ag_pb_data[acc_id][prt_id]["currency_id"] = currency_id
        return ag_pb_data

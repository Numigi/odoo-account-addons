# Copyright 2024-today Numigi and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, models


class AccountMoveLine(models.Model):

    _inherit = "account.move.line"

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            _update_vals_debit_credit(vals)
        print(vals_list)
        return super().create(vals_list)

    def write(self, vals):
        _update_vals_debit_credit(vals)
        return super().write(vals)


def _update_vals_debit_credit(vals):
    """Update debit and credit fields in a values dictionnary.

    If either the debit or the credit is negative, permutate the two fields.

    :param vals: a dictionnary of values
    """
    if vals.get("debit", 0) < 0 or vals.get("credit", 0) < 0:
        vals["debit"], vals["credit"] = -vals.get("credit", 0), -vals.get("debit", 0)

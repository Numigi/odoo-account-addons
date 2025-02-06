# Copyright 2019 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).


from odoo import _, api, fields, models

from odoo.exceptions import UserError

from ..tools.transaction_types import TRANSACTION_TYPES, DEFAULT_TRANSACTION_TYPE


class AccountPaymentMethod(models.Model):

    _inherit = "account.payment.method"

    @api.model
    def _get_payment_method_information(self):
        methods_info = super()._get_payment_method_information()
        methods_info.update({
            'eft': {'mode': 'multi', 'domain': [('type', 'in', ('bank'))]},
        })
        return methods_info

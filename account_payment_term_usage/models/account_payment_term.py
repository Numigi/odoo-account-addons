# © 2020 - today Numigi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models
from odoo.osv.expression import AND


class AccountPaymentTerm(models.Model):

    _inherit = "account.payment.term"

    usage = fields.Selection(
        [
            ("sale", "Sales"),
            ("purchase", "Purchases"),
            ("sale_and_purchase", "Sales & Purchases"),
        ]
    )

    @api.model
    def _search(
        self,
        args,
        offset=0,
        limit=None,
        order=None,
        count=False,
        access_rights_uid=None,
    ):
        usage = self._context.get("enabled_payment_term_usage")

        if usage:
            args = AND(
                [
                    args,
                    [
                        "|",
                        ("usage", "=", False),
                        ("usage", "in", ("sale_and_purchase", usage)),
                    ],
                ]
            )

        return super()._search(
            args,
            offset=offset,
            limit=limit,
            order=order,
            count=count,
            access_rights_uid=access_rights_uid,
        )

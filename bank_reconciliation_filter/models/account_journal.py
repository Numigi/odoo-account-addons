# © 2021 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountJournal(models.AbstractModel):

    _inherit = "account.journal"

    reconcile_show_payments_only = fields.Boolean(
        "Bank Reconciliation - Show Payments Only",
    )

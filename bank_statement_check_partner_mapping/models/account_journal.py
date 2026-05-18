# © Numigi (tm) and all its contributors (https://numigi.com/r/home)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class AccountJournal(models.Model):
    _inherit = "account.journal"

    check_format = fields.Char(
        string="Check Format on Statement",
        default="{check_number}",
        help="Format used on bank statements. Use {check_number} as placeholder. "
             "For example, 'Check - {check_number}' or '{check_number} -CAD' or "
             "'CHQ-{check_number}-RBC'.",
    )

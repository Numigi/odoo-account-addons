# © Numigi (tm) and all its contributors (https://numigi.com/r/home)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class BankStatementPartnerMapping(models.Model):
    _inherit = "bank.statement.partner.mapping"

    _order = "create_date desc"

    payment_id = fields.Many2one(
        comodel_name="account.payment",
        string="Origin Payment",
        ondelete="set null",
        help="The payment that automatically generated this mapping rule.",
    )

    journal_id = fields.Many2one(
        comodel_name="account.journal",
        string="Bank Journal",
        domain="[('type', '=', 'bank')]",
        help="The specific bank journal this rule applies to. "
             "If empty, it applies to all bank journals.",
    )
    active = fields.Boolean(
        string="Active",
        default=True,
        help="Set to false to archive the mapping rule.",
    )

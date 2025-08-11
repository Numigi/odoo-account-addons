# Copyright Numigi (tm) and all its contributors (https://numigi.com/r/home)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    fiscalyear_last_day = fields.Integer(
        related="company_id.fiscalyear_last_day", required=True, readonly=False
    )
    fiscalyear_last_month = fields.Selection(
        related="company_id.fiscalyear_last_month", required=True, readonly=False
    )

    property_stock_account_input_categ_id = fields.Many2one(
        "account.account",
        related="company_id.property_stock_account_input_categ_id",
        readonly=False,
        string="Stock Input Account",
        check_company=True,
        help="""Counterpart journal items for all incoming stock moves
        will be posted in this account, unless there is a specific valuation
        account set on the source location. This is the default value
        for all productsin this category. It can also directly
        be set on each product.""",
    )

    property_stock_account_output_categ_id = fields.Many2one(
        "account.account",
        readonly=False,
        related="company_id.property_stock_account_output_categ_id",
        string="Stock Output Account",
        check_company=True,
        help=(
            "When doing automated inventory valuation, counterpart journal items "
            "for all outgoing stock moves will be posted in this account, unless "
            "there is a specific valuation account set on the destination location. "
            "This is the default value for all products in this category. It can "
            "also directly be set on each product."
        ),
    )

    property_stock_valuation_account_id = fields.Many2one(
        "account.account",
        related="company_id.property_stock_valuation_account_id",
        readonly=False,
        string="Stock Valuation Account",
        check_company=True,
        help="""When automated inventory valuation is enabled on a product,
        this account will hold the current value of the products.""",
    )

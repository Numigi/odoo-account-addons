# Copyright 2025 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    transfer_account_id = fields.Many2one(
        "account.account",
        string="Transfer Account",
        related="company_id.transfer_account_id",
        readonly=False,
        check_company=True,
        domain=lambda self: [
            ("reconcile", "=", True),
            (
                "user_type_id.id",
                "=",
                self.env.ref("account.data_account_type_current_assets").id,
            ),
        ],
        help="Intermediary account used when moving money from a liquidity account "
        "to another",
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

    account_journal_suspense_account_id = fields.Many2one(
        "account.account",
        related="company_id.account_journal_suspense_account_id",
        string="Journal Suspense Account",
        check_company=True,
        readonly=False,
        domain=lambda self: "[('deprecated', '=', False), ('company_id', '=', company_id), \
                             ('user_type_id.type', 'not in', ('receivable', 'payable')), \
                             ('user_type_id', '=', %s)]"
        % self.env.ref("account.data_account_type_current_assets").id,
        help="""Bank statements transactions will be posted on the
        suspense account until the final reconciliation allowing finding
        the right account.""",
    )

    fiscalyear_last_day = fields.Integer(
        related="company_id.fiscalyear_last_day", required=True, readonly=False
    )
    fiscalyear_last_month = fields.Selection(
        related="company_id.fiscalyear_last_month", required=True, readonly=False
    )

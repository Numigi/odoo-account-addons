# © 2024 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class BankStatementPartnerMapping(models.Model):

    _name = "bank.statement.partner.mapping"
    _description = "Bank Statement Partner Mapping"

    mapping_type = fields.Selection(
        string="Mapping Type",
        selection=[("complete", "Complete Label"), ("partial", "Partial Label")],
        required=1,
    )
    partner_id = fields.Many2one("res.partner", string="Partner", required=1)
    label = fields.Char(string="Operation Label", required=1)

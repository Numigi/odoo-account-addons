# Copyright 2023 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).


from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    use_transit_account = fields.Boolean(
        string="Use a transit Account",
        config_parameter="canada_bank_transfer.use_transit_account",
    )

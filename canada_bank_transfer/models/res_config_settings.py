from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    use_transit_account = fields.Boolean(
        string="Use a Transit Account",
        config_parameter="canada_bank_transfer.use_transit_account",
    )

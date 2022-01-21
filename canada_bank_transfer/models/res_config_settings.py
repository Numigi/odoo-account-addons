from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    use_transit_account = fields.Boolean(string="Use a transit Account", related="company_id.use_transit_account", readonly=0)

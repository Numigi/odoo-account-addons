# © 2019 - today Numigi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, models, fields


class Company(models.Model):

    _inherit = "res.company"

    use_transit_account = fields.Boolean(string="Use a transit Account")

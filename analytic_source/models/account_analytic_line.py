# © 2017 Savoir-faire Linux
# © 2018 Numigi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class AccountAnalyticLine(models.Model):

    _inherit = 'account.analytic.line'

    source = fields.Reference(selection=[
        ('account.invoice', 'Invoice'),
    ], readonly=True, string="Source")

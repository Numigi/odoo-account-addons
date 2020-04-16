# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/LGPL.html).

from odoo import fields, models


class Account(models.Model):

    _inherit = 'account.account'

    opening_debit = fields.Monetary(inverse=lambda self: None)
    opening_credit = fields.Monetary(inverse=lambda self: None)

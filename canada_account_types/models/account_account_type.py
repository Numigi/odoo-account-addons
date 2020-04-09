# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/LGPL.html).

from odoo import fields, models


class AccountType(models.Model):

    _inherit = ('account.account.type', 'xml.rename.mixin')
    _name = 'account.account.type'
    _order = 'sequence'

    sequence = fields.Integer()

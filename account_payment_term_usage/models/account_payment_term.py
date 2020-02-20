# © 2020 - today Numigi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class AccountPaymentTerm(models.Model):

    _inherit = 'account.payment.term'

    usage = fields.Selection([
        ('sale', 'Sales'),
        ('purchase', 'Purchases'),
        ('sale_and_purchase', 'Sales & Purchases'),
    ])

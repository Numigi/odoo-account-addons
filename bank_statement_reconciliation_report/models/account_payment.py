# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    rec_outbound_id = fields.Many2one('reconciliation.wizard')
    rec_inbound_id = fields.Many2one('reconciliation.wizard')

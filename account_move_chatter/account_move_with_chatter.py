# © 2019 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class AccountMoveWithChatter(models.Model):

    _name = "account.move"
    _inherit = ['account.move', 'mail.thread']

    name = fields.Char(track_visibility='onchange')
    date = fields.Date(track_visibility='onchange')
    journal_id = fields.Many2one(track_visibility='onchange')
    state = fields.Selection(track_visibility='onchange')
    partner_id = fields.Many2one(track_visibility='onchange')

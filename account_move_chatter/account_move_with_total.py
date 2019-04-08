# © 2019 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class AccountMoveWithTotal(models.Model):

    _inherit = 'account.move'

    company_currency_id = fields.Many2one(
        'res.currency', related='company_id.currency_id', string="Company Currency")
    total_amount = fields.Monetary(
        compute='_compute_total',
        store=True,
        currency_field='company_currency_id',
        track_visibility='onchange',
    )

    @api.depends('line_ids.debit')
    def _compute_total(self):
        for move in self:
            move.total_amount = sum(l.debit for l in move.line_ids)

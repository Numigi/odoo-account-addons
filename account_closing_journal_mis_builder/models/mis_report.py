# Copyright 2020 - Today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class MisReport(models.Model):

    _inherit = "mis.report"

    exclude_closing_entries = fields.Boolean()
    move_lines_source_model = fields.Char(related="move_lines_source.model")

    @api.onchange('move_lines_source')
    def __onchange_move_lines_source(self):
        if self.move_lines_source_model != "account.move.line":
            self.exclude_closing_entries = False

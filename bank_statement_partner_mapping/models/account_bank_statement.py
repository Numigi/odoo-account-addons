# © 2019 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models


class BankStatement(models.Model):
    _inherit = 'account.bank.statement'

    def button_recuperate_partners(self):
        """Recuperate Partners ."""
        for line in self.line_ids.filtered(
                lambda line_statement: not line_statement.partner_id and not line_statement.journal_entry_ids):
            mapping_type = self.env['bank.statement.partner.mapping'].search([('label', '=', line.name)])
            if not mapping_type:
                mapping_type = self.env['bank.statement.partner.mapping'].search(
                    [('mapping_type', '=', 'partial')]).filtered(
                    lambda mapping_type: line.name.find(mapping_type.label) != -1)
            line.partner_id = mapping_type and mapping_type[0].partner_id.id or False

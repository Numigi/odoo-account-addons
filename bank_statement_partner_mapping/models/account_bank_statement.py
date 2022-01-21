# © 2019 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models


class BankStatement(models.Model):
    _inherit = 'account.bank.statement'

    def button_recuperate_partners(self):
        """Recuperate Partners  ."""
        for statement in self:
            for line in statement.line_ids:
                if not line.partner_id and not line.journal_entry_ids:
                    mapping_type_complete = self.env['bank.statement.partner.mapping'].search([('label', '=', line.name)], limit=1)
                    if mapping_type_complete:
                        line.partner_id = mapping_type_complete.partner_id.id
                    else:
                        mapping_types_partial = self.env['bank.statement.partner.mapping'].search(
                            [('mapping_type', '=', 'partial')])
                        for mapping_type_partial in mapping_types_partial:
                            if line.name.replace(' ', '').find(mapping_type_partial.label.replace(' ', '')) != -1:
                                line.partner_id = mapping_type_partial.partner_id.id
                                break

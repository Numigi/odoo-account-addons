# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _


class AccountBankStatement(models.Model):
    _inherit = "account.bank.statement"

    conciliation_id = fields.Many2one("conciliation.wizard")
    date_end_bank_statement = fields.Date(
        string="Bank statement end date", compute="_compute_date_end_bank_statement", store=True
    )

    @api.multi
    @api.depends("date", "line_ids", "line_ids.date")
    def _compute_date_end_bank_statement(self):
        for record in self:
            dates = record.line_ids.mapped("date")
            dates += [record.date]
            record.date_end_bank_statement = max(dates)

    def button_bank_conciliation(self):
        conciliation_id = self.conciliation_id.id
        if not conciliation_id:
            conciliation_id = self.env["conciliation.wizard"].create({"statement_id": self.id}).id
            self.conciliation_id = conciliation_id
        return {
            "name": _("Bank conciliation report"),
            "view_type": "form",
            "view_mode": "form",
            "res_model": "conciliation.wizard",
            "views": [(False, "form")],
            "type": "ir.actions.act_window",
            "target": "new",
            "res_id": conciliation_id,
        }

# © 2022 - Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from base64 import b64decode
from io import StringIO
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from ..loader import BankStatementLoader
from ..error import BankStatementError


class BankStatementImportWizard(models.TransientModel):

    _name = "bank.statement.import.wizard"
    _description = "Bank Statement Import Wizard"

    journal_id = fields.Many2one(
        "account.journal", default=lambda self: self._context.get("journal_id")
    )
    config_id = fields.Many2one("bank.statement.import.config", required=True)

    filename = fields.Char("File Name")
    file = fields.Binary(attachment=True)

    line_ids = fields.One2many("bank.statement.import.wizard.line", "wizard_id")

    show_reference = fields.Boolean(compute="_compute_show_fields")
    show_partner_name = fields.Boolean(compute="_compute_show_fields")
    show_balance = fields.Boolean(compute="_compute_show_fields")
    show_currency_amount = fields.Boolean(compute="_compute_show_fields")

    has_error = fields.Boolean(compute="_compute_has_error")
    is_ready = fields.Boolean(compute="_compute_is_ready")

    statement_id = fields.Many2one("account.bank.statement")

    @api.onchange("journal_id")
    def _onchange_journal(self):
        self.config_id = self.journal_id.statement_import_config_id

    @api.depends("line_ids", "config_id")
    def _compute_show_fields(self):
        for wizard in self:
            config = wizard.config_id
            wizard.show_reference = config.reference_enabled
            wizard.show_partner_name = config.partner_name_enabled
            wizard.show_balance = config.balance_enabled
            wizard.show_currency_amount = config.currency_amount_enabled

    @api.depends("line_ids")
    def _compute_has_error(self):
        for wizard in self:
            wizard.has_error = any(line.has_error for line in self.line_ids)

    @api.depends("line_ids", "has_error")
    def _compute_is_ready(self):
        for wizard in self:
            wizard.is_ready = wizard.line_ids and not wizard.has_error

    def confirm(self):
        self.statement_id = self._make_bank_statement()
        return self.statement_id.get_formview_action()

    def load_file(self):
        loader = self._get_loader()
        content = self._get_file_content()
        data = loader.load(StringIO(content))

        self.line_ids = [
            (5, 0),
            *((0, 0, self._make_line_vals(vals)) for vals in data["rows"]),
        ]

        return self.get_wizard_action()

    def get_wizard_action(self):
        action = self.get_formview_action()
        action["target"] = "new"
        return action

    def _make_line_vals(self, vals):
        vals["has_error"] = any(
            isinstance(v, BankStatementError) for v in vals.values()
        )
        return {k: self._format_line_value(v) for k, v in vals.items()}

    def _format_line_value(self, value):
        if isinstance(value, BankStatementError):
            return _(value.msg).format(*value.args, **value.kwargs)
        return value

    def _get_file_content(self):
        try:
            return self._try_get_file_content()
        except UnicodeDecodeError:
            raise ValidationError(
                _(
                    "The encoding defined in the configuration ({encoding}) "
                    "does not match the selected file ({filename})."
                ).format(
                    encoding=self.config_id.encoding,
                    filename=self.filename,
                )
            )

    def _try_get_file_content(self):
        bytes_content = b64decode(self.file)
        return bytes_content.decode(self.config_id.encoding)

    def _get_loader(self):
        config = self._get_csv_loader_config()
        if not self.config_id.decimal_separator.strip():
            # Field is already required but this avoid when calling function separately
            raise ValidationError(
                _("Decimal separator must not be empty or filled by spaces.")
            )
        if (
            self.config_id.decimal_separator == ","
            and self.config_id.thousands_separator == ","
        ):
            raise ValidationError(
                _(
                    "Decimal separator and thousands separator "
                    "must not be together as comma."
                )
            )
        return BankStatementLoader(config)

    def _get_csv_loader_config(self):
        return self.config_id.get_csv_loader_config()

    def _make_bank_statement(self):
        vals = self._get_statement_vals()
        return self.env["account.bank.statement"].create(vals)

    def _get_statement_vals(self):
        vals = {
            "name": self.filename,
            "journal_id": self.journal_id.id,
            "line_ids": self._get_statement_line_vals(),
        }

        if self.config_id.balance_enabled:
            first_line, last_line = self._get_first_and_last_line()
            vals["balance_start"] = float(first_line.balance) - float(first_line.amount)
            vals["balance_end_real"] = float(last_line.balance)

        return vals

    def _get_first_and_last_line(self):
        lines = self.line_ids

        if self.config_id.reversed_order:
            return lines[-1], lines[0]
        else:
            return lines[0], lines[-1]

    def _get_statement_line_vals(self):
        lines = self.line_ids
        return [(0, 0, line._get_statement_line_vals()) for line in lines]

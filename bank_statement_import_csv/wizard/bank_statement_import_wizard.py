# © 2021 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import json
from base64 import b64decode
from io import StringIO
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from odoo.addons.base_sparse_field.models.fields import Serialized
from ..loader import BankStatementLoader
from ..error import BankStatementError


class BankStatementImportWizard(models.TransientModel):

    _name = "bank.statement.import.wizard"
    _description = "Bank Statement Import Wizard"

    journal_id = fields.Many2one(
        "account.journal",
        default=lambda self: self.context.get("journal_id")
    )
    config_id = fields.Many2one("bank.statement.import.config", required=True)

    filename = fields.Char("File Name")
    file = fields.Binary(attachment=True)

    line_ids = fields.One2many("bank.statement.import.wizard.line", "wizard_id")

    show_description = fields.Boolean(compute="_compute_show_fields")
    show_reference = fields.Boolean(compute="_compute_show_fields")
    show_balance = fields.Boolean(compute="_compute_show_fields")
    show_currency_amount = fields.Boolean(compute="_compute_show_fields")

    has_error = fields.Boolean(compute="_compute_has_error")
    show_confirm = fields.Boolean(compute="_compute_show_confirm")

    @api.onchange("journal_id")
    def _onchange_journal(self):
        self.config_id = self.journal_id.statement_import_config_id

    @api.depends("line_ids", "config_id")
    def _compute_show_fields(self):
        for wizard in self:
            config = wizard.config_id
            wizard.show_description = config.description_enabled
            wizard.show_reference = config.reference_enabled
            wizard.show_balance = config.balance_enabled
            wizard.show_currency_amount = config.currency_amount_enabled

    @api.depends("line_ids")
    def _compute_has_error(self):
        for wizard in self:
            wizard.has_error = any(l.has_error for l in self.line_ids)

    @api.depends("line_ids", "has_error")
    def _compute_show_confirm(self):
        for wizard in self:
            wizard.show_confirm = wizard.line_ids and not wizard.has_error

    def confirm(self):
        pass

    def load_file(self):
        loader = self._get_loader()
        content = self._get_file_content()
        data = loader.load(StringIO(content))

        self.line_ids = [
            (5, 0),
            *((0, 0, self._make_line_vals(vals)) for vals in data["rows"]),
        ]

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
        else:
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
        return BankStatementLoader(config)

    def _get_csv_loader_config(self):
        return self.config_id.get_csv_loader_config()

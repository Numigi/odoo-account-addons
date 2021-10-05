# © 2021 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from base64 import b64decode
from io import StringIO
from odoo import api, fields, models
from odoo.addons.base_sparse_field.models.fields import Serialized
from ..loader import BankStatementLoader


class BankStatementImportWizard(models.TransientModel):

    _name = "bank.statement.import.wizard"
    _description = "Bank Statement Import Wizard"

    config_id = fields.Many2one("bank.statement.import.config", required=True)

    file = fields.Binary()
    data = Serialized()

    def load_file(self):
        loader = self._get_loader()
        content = self._get_file_content()
        self.data = loader.load(StringIO(content))

    def _get_file_content(self):
        bytes_content = b64decode(self.file)
        return bytes_content.decode(self.config_id.encoding)

    def _get_loader(self):
        config = self._get_csv_loader_config()
        return BankStatementLoader(config)

    def _get_csv_loader_config(self):
        return self.config_id.get_csv_loader_config()

import logging

from odoo import models, api
from .tools.translation_utils import _update_translations

_logger = logging.getLogger(__name__)


class IrHttp(models.AbstractModel):
    _inherit = "ir.http"

    @api.model
    def get_translations_for_webclient(self, modules, lang):
        """Override to update specific French-Canadian translation terms."""
        translations, lang_params = super().get_translations_for_webclient(
            modules, lang
        )
        if lang in ["fr_FR", "fr_CA"]:
            _logger.info("Updating translations for language: %s", lang)
            _update_translations(translations, python_translations=False)
        return translations, lang_params

# Copyright 2024 Numigi and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import SUPERUSER_ID
from odoo.tools.translate import TranslationImporter as BaseTranslationImporter
from odoo.tools.translate import GettextAlias as BaseGettextAlias

import odoo

_base_load_translation = BaseTranslationImporter._load
_base_get_translation = BaseGettextAlias._get_translation


def replace_vals(data, mapping, lang="fr_FR"):
    """
    Replace strings in the given dict `data` based on the `mapping`
    provided for a specific language key.
    """

    def recursive_replace(current_dict):
        for key, value in current_dict.items():
            if isinstance(value, dict):
                recursive_replace(value)
            elif key == lang and isinstance(value, str):
                for old, new in mapping.items():
                    if old in value:
                        current_dict[key] = value.replace(old, new)
                        break

    recursive_replace(data)
    return data


class TranslationImporter(BaseTranslationImporter):

    def _load(self, reader, lang, xmlids=None):
        """
        Load and apply language-specific term replacements.
        """

        _base_load_translation(self, reader, lang, xmlids)

        if lang == "fr_FR":
            term_model = "translate.term.fr_ca"
            mapping_dict = (
                {
                    record.term_fr: record.term_ca
                    for record in self.env[term_model].search([])
                }
                if term_model in self.env.registry.models
                else {}
            )

            if mapping_dict:
                self.model_translations = replace_vals(
                    self.model_translations, mapping_dict
                )
                self.model_terms_translations = replace_vals(
                    self.model_terms_translations, mapping_dict
                )


class GettextAlias(BaseGettextAlias):
    def _get_translation(self, source, module=None):
        res = _base_get_translation(self, source, module=None)
        db = self._get_db()
        cr = False
        if db is not None:
            cr = db.cursor()
        if cr:
            env = odoo.api.Environment(cr, SUPERUSER_ID, {})
            lang = env["res.users"].context_get()["lang"]
            if lang == "fr_FR":
                term_model = "translate.term.fr_ca"
                mapping_dict = (
                    {
                        record.term_fr: record.term_ca
                        for record in env[term_model].search([])
                    }
                    if term_model in env.registry.models
                    else {}
                )

                for old, new in mapping_dict.items():
                    if old in res:
                        res = res.replace(old, new)
                        break

        return res


BaseTranslationImporter._load = TranslationImporter._load
BaseGettextAlias._get_translation = GettextAlias._get_translation

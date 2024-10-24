# Copyright 2024 Numigi and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.tools.translate import TranslationImporter as BaseTranslationImporter


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


original_load = BaseTranslationImporter._load


class TranslationImporter(BaseTranslationImporter):

    def load_terms(self, reader, lang, xmlids=None):
        """
        Load and apply language-specific term replacements.
        """
        term_model = "translate.term.fr_ca"
        mapping_dict = (
            {
                record.term_fr: record.term_ca
                for record in self.env[term_model].search([])
            }
            if term_model in self.env.registry.models
            else {}
        )

        original_load(self, reader, lang, xmlids)

        if mapping_dict:
            self.model_translations = replace_vals(
                self.model_translations, mapping_dict
            )
            self.model_terms_translations = replace_vals(
                self.model_terms_translations, mapping_dict
            )


BaseTranslationImporter._load = TranslationImporter.load_terms

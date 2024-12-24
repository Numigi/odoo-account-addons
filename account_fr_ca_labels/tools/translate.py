from odoo.tools.translate import CodeTranslations as BaseCodeTranslations
from .translation_utils import _update_translations


class CodeTranslations(BaseCodeTranslations):

    def get_python_translations(self, module_name, lang):
        """Rewrite get_python_translations to update translations."""

        if (module_name, lang) not in self.python_translations:
            self._load_python_translations(module_name, lang)
        translations = self.python_translations[(module_name, lang)]
        # Check if the language is French or Canadian French
        if lang in ["fr_FR", "fr_CA"]:
            _update_translations(translations, python_translations=True)
        return translations


BaseCodeTranslations.get_python_translations = CodeTranslations.get_python_translations

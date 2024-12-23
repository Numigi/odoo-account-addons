import logging
from odoo.tools.translate import CodeTranslations as BaseCodeTranslations


_logger = logging.getLogger(__name__)

ENGLISH_CREDIT_NOTE_TERMS = [
    "credit note",
    "credit notes",
    "Credit Note",
    "Credit Notes",
    "Credit note",
    "Credit notes",
    "Credits notes",
    "refund",
    "Refund",
]

FRENCH_CREDIT_NOTE_TERMS = [
    "Facture de l'avoir",
    "l'avoir",
    "L'avoir",
    "d'avoirs",
    "d'avoir",
    "les avoirs",
    "un avoir",
    "aux avoirs",
    "le même avoir",
    "le prochain avoir",
    "avoir",
    "Avoir",
    # Grammatical errors
    "Note de crédits",
    "note de crédits",
    "notes de crédits",
]


def _replace_terms(translations, mapping):
    """Replace terms in the translations dictionary based on a mapping."""
    if not isinstance(translations, dict):
        _logger.error("Invalid translations format. Expected a dictionary.")
        return
    # Iterate over the source translations in the current module
    for src, value in translations.items():
        # Apply the mapping to replace old terms with new ones
        for old, new in mapping:
            if old in value:
                _logger.info(
                    "Replacing '%s' with '%s', string: '%s'",
                    old,
                    new,
                    value,
                )
                value = value.replace(old, new)
                _logger.info("Result: '%s'", value)

        # After processing, update the translation value
        translations[src] = value


def _update_credit_note_translations(translations):
    mapping = [
        ("Facture de l'avoir", "Note de crédit"),
        ("l'avoir", "la note de crédit"),
        ("L'avoir", "La note de crédit"),
        ("d'avoirs", "de notes de crédit"),
        ("d'avoir", "de note de crédit"),
        ("les avoirs", "les notes de crédit"),
        ("un avoir", "une note de crédit"),
        ("aux avoirs", "aux notes de crédit"),
        ("le même avoir", "la même note de crédit"),
        ("le prochain avoir", "la prochaine note de crédit"),
        ("avoir", "note de crédit"),
        ("Avoir", "Note de crédit"),
        # Grammatical errors
        ("Note de crédits", "Notes de crédit"),
        ("note de crédits", "notes de crédit"),
        ("notes de crédits", "notes de crédit"),
    ]
    _replace_terms(translations, mapping)


def _update_aged_balance_translations(translations):
    mapping = [
        ("Balance agée des clients", "Âge des comptes clients"),
        ("Balance agée des fournisseurs", "Âge des comptes fournisseurs"),
        ("Balances agées des tiers", "Âge des comptes"),
        ("Balance agée", "Âge des comptes"),
        ("balance agée", "âge des comptes"),
    ]
    _replace_terms(translations, mapping)


def _update_reconciliation_translations(translations):
    mapping = [
        ("Modèles de lettrage", "Modèles de conciliation bancaire"),
        ("de lettrage", "de conciliation"),
        ("du lettrage", "de la conciliation"),
        ("le lettrage", "la conciliation"),
        ("Non lettré", "Non réconcilié"),
        ("Lettrer", "Réconcilier"),
        ("lettrer", "réconcilier"),
        ("Lettrage", "Conciliation"),
        # Grammatical errors
        ("annuler le lettrage l'entrée", "annuler la conciliation"),
    ]
    _replace_terms(translations, mapping)


def _update_payment_translations(translations):
    mapping = [
        ("Payments Sortants", "Paiements sortants"),
        ("Configuration des Payements", "Configuration des paiements"),
        ("Compte de Payements Sortants", "Compte de paiement sortant"),
        ("Compte de Payements Entrants", "Compte de paiement entrant"),
    ]
    _replace_terms(translations, mapping)


def _translation_contains_credit_note(source):
    """Check if the source contains any English credit note terms."""
    return any(term in source for term in ENGLISH_CREDIT_NOTE_TERMS)


def _update_fr_ca_terms(translations):
    """Apply all translation updates."""
    _update_credit_note_translations(translations)
    _update_aged_balance_translations(translations)
    _update_reconciliation_translations(translations)
    _update_payment_translations(translations)


class CodeTranslations(BaseCodeTranslations):

    def get_python_translations(self, module_name, lang):
        """Override get_python_translations to update translations."""

        # Call the original method to load Python translations
        translations = BaseCodeTranslations.get_python_translations(
            self, module_name, lang
        )

        # Check if the language is French or Canadian French
        if lang in ["fr_FR", "fr_CA"]:
            _update_fr_ca_terms(translations)
        return translations


BaseCodeTranslations.get_python_translations = CodeTranslations.get_python_translations

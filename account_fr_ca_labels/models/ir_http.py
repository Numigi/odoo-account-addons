import logging
from odoo import models, api

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
            self._update_fr_ca_terms(translations)
        return translations, lang_params

    def _update_fr_ca_terms(self, translations):
        """Apply all translation updates."""
        self._update_credit_note_translations(translations)
        self._update_aged_balance_translations(translations)
        self._update_reconciliation_translations(translations)
        self._update_payment_translations(translations)

    def _update_credit_note_translations(self, translations):
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
        self._replace_terms(translations, mapping)

    def _update_aged_balance_translations(self, translations):
        mapping = [
            ("Balance agée des clients", "Âge des comptes clients"),
            ("Balance agée des fournisseurs", "Âge des comptes fournisseurs"),
            ("Balances agées des tiers", "Âge des comptes"),
            ("Balance agée", "Âge des comptes"),
            ("balance agée", "âge des comptes"),
        ]
        self._replace_terms(translations, mapping)

    def _update_reconciliation_translations(self, translations):
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
        self._replace_terms(translations, mapping)

    def _update_payment_translations(self, translations):
        mapping = [
            ("Payments Sortants", "Paiements sortants"),
            ("Configuration des Payements", "Configuration des paiements"),
            ("Compte de Payements Sortants", "Compte de paiement sortant"),
            ("Compte de Payements Entrants", "Compte de paiement entrant"),
        ]
        self._replace_terms(translations, mapping)

    def _replace_terms(self, translations, mapping):
        """Replace terms in the translations dictionary based on a mapping."""
        if not isinstance(translations, dict):
            _logger.error("Invalid translations format. Expected a dictionary.")
            return

        # Iterate over all modules in the translations dictionary
        for module, content in translations.items():
            if not isinstance(content, dict) or 'messages' not in content:
                continue  # Skip invalid content

            for message in content['messages']:
                # Ensure each message has a 'string' field
                if not isinstance(message, dict) or 'string' not in message:
                    continue
                for old, new in mapping:
                    if old in message['string']:
                        if (
                            old in FRENCH_CREDIT_NOTE_TERMS
                            and not self._translation_contains_credit_note(
                                message["id"]
                            )
                        ):
                            # Skip FRENCH_CREDIT_NOTE_TERMS that is not
                            # a translation of credit note
                            continue
                        _logger.info(
                            "Replacing '%s' with '%s' in module '%s', string: '%s'",
                            old, new, module, message['string']
                        )
                        message['string'] = message['string'].replace(old, new)

    def _translation_contains_credit_note(self, source):
        """Check if the source contains any English credit note terms."""
        return any(term in source for term in ENGLISH_CREDIT_NOTE_TERMS)

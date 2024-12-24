import logging

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

TRANSLATION_MAPPINGS = {
    "credit_note": [
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
    ],
    "aged_balance": [
        ("Balance agée des clients", "Âge des comptes clients"),
        ("Balance agée des fournisseurs", "Âge des comptes fournisseurs"),
        ("Balances agées des tiers", "Âge des comptes"),
        ("Balance agée", "Âge des comptes"),
        ("balance agée", "âge des comptes"),
    ],
    "reconciliation": [
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
    ],
    "payment": [
        ("Payments Sortants", "Paiements sortants"),
        ("Configuration des Payements", "Configuration des paiements"),
        ("Compte de Payements Sortants", "Compte de paiement sortant"),
        ("Compte de Payements Entrants", "Compte de paiement entrant"),
    ],
}


def _translation_contains_credit_note(source):
    """Check if the source contains any English credit note terms."""
    return any(term in source for term in ENGLISH_CREDIT_NOTE_TERMS)


def _replace_terms(
    translations, mapping, contains_credit_note_check=None, python_translations=True
):
    """Replace terms in the translations dictionary based on a mapping."""
    if not isinstance(translations, dict):
        _logger.error("Invalid translations format. Expected a dictionary.")
        return

    if python_translations:
        # Process for Python translations format
        for src, value in translations.items():
            for old, new in mapping:
                if old in value:
                    if (
                        contains_credit_note_check
                        and old in FRENCH_CREDIT_NOTE_TERMS
                        and not contains_credit_note_check(src)
                    ):
                        # Skip terms unrelated to credit notes
                        continue
                    _logger.info("Replacing '%s' with '%s' in: '%s'", old, new, value)
                    value = value.replace(old, new)
            translations[src] = value
    else:
        # Process for web client translations format
        for module, content in translations.items():
            if not isinstance(content, dict) or "messages" not in content:
                continue  # Skip invalid content

            for message in content["messages"]:
                if not isinstance(message, dict) or "string" not in message:
                    continue
                for old, new in mapping:
                    if old in message["string"]:
                        if (
                            contains_credit_note_check
                            and old in FRENCH_CREDIT_NOTE_TERMS
                            and not contains_credit_note_check(message["id"])
                        ):
                            # Skip terms unrelated to credit notes
                            continue
                        _logger.info(
                            "Replacing '%s' with '%s' in module '%s', string: '%s'",
                            old,
                            new,
                            module,
                            message["string"],
                        )
                        message["string"] = message["string"].replace(old, new)


def _update_translations(translations, python_translations=True):
    """Apply all translation updates."""
    for key, mapping in TRANSLATION_MAPPINGS.items():
        contains_credit_note_check = (
            _translation_contains_credit_note if key == "credit_note" else None
        )
        _replace_terms(
            translations,
            mapping,
            contains_credit_note_check,
            python_translations=python_translations,
        )

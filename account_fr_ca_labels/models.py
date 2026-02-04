# © 2019 Numigi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import logging
from odoo import models

_logger = logging.getLogger(__name__)


ENGLISH_CREDIT_NOTE_TERMS = [
    "credit note",
    "credit notes",
    "Credit Note",
    "Credit Notes",
    "Credit note",
    "Credit notes",
    "refund",
    "Refund",
]


class IrTranslation(models.Model):

    _inherit = "ir.translation"

    def _load_module_terms(self, modules, langs, overwrite=False):
        result = super()._load_module_terms(modules, langs, overwrite)
        self._update_fr_ca_terms()
        return result

    def _update_fr_ca_terms(self):
        _update_credit_note_translations(self.env)
        _update_aged_balance_translations(self.env)
        _update_reconciliation_translations(self.env)
        _update_payment_translations(self.env)


def _update_credit_note_translations(env):
    """Update the term `Avoir` to `Note de crédit`.

    The term `Avoir` and all its derivatives (avoir, avoirs, l'avoir, d'avoir)
    must not always be updated to `Note de crédit`.

    Example:

    ..

        Un terme de paiement ne devrait `avoir` qu'une seule ligne de type Balance.

    The strategy to update is to target only translations
    with `credit note` (or a derivative) in the source term.
    """
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
    ]
    for source, destination in mapping:
        translations = _find_translations_term_with_value(env, source)
        # Fixing it not using lambda function:
        # lambda t: _translation_contains_credit_note(t)
        # Use instead _translation_contains_credit_note. It is the same.
        credit_note_translations = translations.filtered(
            _translation_contains_credit_note
        )
        for translation in credit_note_translations:
            _replace_term_in_translation(translation, source, destination)


def _update_aged_balance_translations(env):
    """Update the term `Balance âgée` to `Âge des comptes`."""
    mapping = [
        ("Balance agée des clients", "Âge des comptes clients"),
        ("Balance agée des fournisseurs", "Âge des comptes fournisseurs"),
        ("Balances agées des tiers", "Âge des comptes"),
        ("Balance agée", "Âge des comptes"),
        ("balance agée", "âge des comptes"),
    ]
    _replace_terms(env, mapping)


def _update_reconciliation_translations(env):
    """Update the term `Lettrage` to `Conciliation`."""
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
    _replace_terms(env, mapping)


def _update_payment_translations(env):
    mapping = [
        ("Payments Sortants", "Paiements sortants"),
        ("Configuration des Payements", "Configuration des paiements"),
        ("Compte de Payements Sortants", "Compte de paiement sortant"),
        ("Compte de Payements Entrants", "Compte de paiement entrant"),
    ]
    _replace_terms(env, mapping)


def _replace_terms(env, mapping):
    for source, destination in mapping:
        translations = _find_translations_term_with_value(env, source)
        for translation in translations:
            _replace_term_in_translation(translation, source, destination)


def _find_translations_term_with_value(env, value):
    """Find translations that contain the given value.

    The search excludes translation rows from models
    except technical models (ir.model, ir.model.fields, ir.ui.view, etc).

    :param value: the value to find in translations.
    :return: the ir.translation records found
    """
    env.cr.execute(
        """
        SELECT id FROM ir_translation
        WHERE lang in ('fr_FR', 'fr_CA')
        AND (
            type in ('code', 'selection', 'sql_constraint')
            OR name like %s
        )
        AND value like %s
        """,
        (
            "ir.%",
            "%{}%".format(value),
        ),
    )
    translation_ids = [r[0] for r in env.cr.fetchall()]
    return env["ir.translation"].browse(translation_ids)


def _translation_contains_credit_note(translation):
    """Evaluate whether the source of the translation contains `credit note`."""
    return any(source in translation.src for source in ENGLISH_CREDIT_NOTE_TERMS)


def _replace_term_in_translation(translation, source, dest):
    _logger.info(
        (
            "Replacing the term '{source}' with '{dest}' for the french translation "
            "'{value}'."
        ).format(source=source, dest=dest, value=translation.value)
    )
    translation.value = translation.value.replace(source, dest)

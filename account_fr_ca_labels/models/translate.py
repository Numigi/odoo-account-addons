# Copyright 2024-today Numigi and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import logging
import threading
import psycopg2

from odoo import api, SUPERUSER_ID, sql_db
from odoo.tools.translate import TranslationImporter as BaseTranslationImporter
from odoo.tools.translate import CodeTranslations as BaseCodeTranslations
from odoo.tools.misc import ReadonlyDict

_logger = logging.getLogger(__name__)

base_load_translation = BaseTranslationImporter._load
base_get_web_translations = BaseCodeTranslations.get_web_translations
base_get_python_translations = BaseCodeTranslations.get_python_translations


def _process_dict_item(current_dict, key, value, mapping, lang):
    if isinstance(value, dict):
        replace_values(value, mapping, lang)
    elif key == lang and isinstance(value, str):
        _apply_mapping_safely(current_dict, key, value, mapping)


def _apply_mapping_safely(current_dict, key, value, mapping):
    try:
        current_dict[key] = _apply_mapping(value, mapping)
    except Exception as error:
        _logger.error("Failed mapping for key '%s': %s", key, error)


def replace_values(data_dict, mapping, lang="fr_FR"):
    for key, value in data_dict.items():
        _process_dict_item(data_dict, key, value, mapping, lang)
    return data_dict


def _replace_term_in_string(value, old_term, new_term):
    if old_term and str(old_term) in value:
        return value.replace(str(old_term), str(new_term))
    return value


def _apply_mapping(value, mapping):
    if not isinstance(value, str):
        return value

    sorted_keys = sorted(mapping.keys(), key=lambda k: len(str(k)), reverse=True)

    for old_term in sorted_keys:
        value = _replace_term_in_string(value, old_term, mapping[old_term])

    return value


def _get_env_from_database(db_name):
    database = sql_db.db_connect(db_name)
    if database is None:
        return None, None
    db_cursor = database.cursor()
    environment = api.Environment(db_cursor, SUPERUSER_ID, {})
    return environment, db_cursor


def get_odoo_environment():
    db_name = getattr(threading.current_thread(), "dbname", None)
    if not db_name:
        raise RuntimeError("Failed to retrieve the dbname from thread.")

    environment, db_cursor = _get_env_from_database(db_name)

    if environment is None or db_cursor is None:
        _logger.error("Could not retrieve environment for db: %s", db_name)
        raise RuntimeError("Failed to retrieve the Odoo environment.")

    return environment, db_cursor


def _fetch_terms_from_model(environment, term_model):
    mapping_dict = {}
    try:
        mapping_dict = {
            record.term_fr: record.term_ca
            for record in environment[term_model].search([])
        }
        _logger.info("Loaded %s terms from %s.", len(mapping_dict), term_model)
    except psycopg2.errors.UndefinedTable:
        _logger.warning("Table %s not defined yet. Skipping.", term_model)
    except Exception as error:
        _logger.error("Database error while fetching mapping: %s", error)

    return mapping_dict


def get_translation_mapping(environment, term_model="translate.term.fr_ca"):
    mapping_dict = {}
    if term_model in environment.registry.models:
        mapping_dict = _fetch_terms_from_model(environment, term_model)
    return mapping_dict


def _apply_mapping_to_model_translations(importer_instance, mapping_dict):
    importer_instance.model_translations = replace_values(
        importer_instance.model_translations, mapping_dict
    )
    importer_instance.model_terms_translations = replace_values(
        importer_instance.model_terms_translations, mapping_dict
    )


class TranslationImporter(BaseTranslationImporter):
    def _load(self, reader, lang, xmlids=None):
        base_load_translation(self, reader, lang, xmlids)
        if lang == "fr_FR":
            mapping_dict = get_translation_mapping(self.env)
            if mapping_dict:
                _apply_mapping_to_model_translations(self, mapping_dict)


def _build_python_translations_dict(orig, mapping_dict):
    return ReadonlyDict(
        {src: _apply_mapping(val, mapping_dict) for src, val in orig.items()}
    )


def _process_python_translations_fr(instance, module_name, lang):
    try:
        environment, db_cursor = get_odoo_environment()
        mapping_dict = get_translation_mapping(environment)
        db_cursor.close()

        if mapping_dict:
            orig = instance.python_translations[(module_name, lang)]
            instance.python_translations[
                (module_name, lang)
            ] = _build_python_translations_dict(orig, mapping_dict)
    except Exception as error:
        _logger.error("Error in python translations for %s: %s", module_name, error)


class CodeTranslations(BaseCodeTranslations):
    def get_python_translations(self, module_name, lang):
        if (module_name, lang) not in self.python_translations:
            BaseCodeTranslations._load_python_translations(self, module_name, lang)
            if lang == "fr_FR":
                _process_python_translations_fr(self, module_name, lang)
        return self.python_translations[(module_name, lang)]

    def get_web_translations(self, module_name, lang):
        if (module_name, lang) not in self.web_translations:
            BaseCodeTranslations._load_web_translations(self, module_name, lang)
            if lang == "fr_FR":
                _process_web_translations_fr(self, module_name, lang)
        return self.web_translations[(module_name, lang)]


def _build_web_message_dict(msg, mapping_dict):
    return ReadonlyDict(
        {
            "id": msg["id"],
            "string": _apply_mapping(msg["string"], mapping_dict),
        }
    )


def _build_web_translations_tuple(orig, mapping_dict):
    return tuple(
        _build_web_message_dict(msg, mapping_dict) for msg in orig.get("messages", ())
    )


def _process_web_translations_fr(instance, module_name, lang):
    try:
        environment, db_cursor = get_odoo_environment()
        mapping_dict = get_translation_mapping(environment)
        db_cursor.close()

        if mapping_dict:
            orig = instance.web_translations[(module_name, lang)]
            new_messages = _build_web_translations_tuple(orig, mapping_dict)
            instance.web_translations[(module_name, lang)] = ReadonlyDict(
                {"messages": new_messages}
            )
    except Exception as error:
        _logger.error("Error in web translations for %s: %s", module_name, error)


BaseTranslationImporter._load = TranslationImporter._load
BaseCodeTranslations.get_web_translations = CodeTranslations.get_web_translations
BaseCodeTranslations.get_python_translations = CodeTranslations.get_python_translations

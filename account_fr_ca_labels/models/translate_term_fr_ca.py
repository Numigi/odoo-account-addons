# Copyright 2024 Numigi and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models

from odoo.tools.translate  import TranslationImporter,TranslationFileReader
import logging
_logger = logging.getLogger(__name__)


class TranslateTermFrCA(models.Model):

    _name = "translate.term.fr_ca"

    term_fr = fields.Char(string="Term Fr")
    term_ca = fields.Char(string="Term CA")


# class TranslationImporterFrCA(TranslationImporter):
#
#     def load(self, fileobj, fileformat, lang, xmlids=None):
#         _logger.info('HHHEEEEEEEEEEEEEEEERE')
#         super(TranslationImporterFrCA, self).load(fileobj, fileformat, lang, xmlids)
#         _logger.info('ENNNNNNNNNNNNNNNNND')
#
#     def _load(self, reader, lang, xmlids=None):
#         super(TranslationImporterFrCA, self)._load(reader, lang, xmlids)
#         _logger.info('elf.model_terms_translations %s', self.model_terms_translations)

def get_ca_translation(value, mapping):
    for term, translation in mapping.items():
        value = value.replace(term,translation)
    return value


def _load(self, reader, lang, xmlids=None):
    if xmlids and not isinstance(xmlids, set):
        xmlids = set(xmlids)
    fr_ca_terms = self.env["translate.term.fr_ca"].search([])
    dict_mapping = {record.term_fr: record.term_ca for record in fr_ca_terms}
    print("dict_mapping",dict_mapping)
    for row in reader:
        if not row.get('value') or not row.get('src'):  # ignore empty translations
            continue
        if row.get('type') == 'code':  # ignore code translations
            continue
        # TODO: CWG if the po file should not be trusted, we need to check each model term
        model_name = row.get('imd_model')
        module_name = row['module']
        if model_name not in self.env:
            continue
        field_name = row['name'].split(',')[1]
        field = self.env[model_name]._fields.get(field_name)
        if not field or not field.translate or not field.store:
            continue
        xmlid = module_name + '.' + row['imd_name']
        if xmlids and xmlid not in xmlids:
            continue
        cr_term = get_ca_translation(row['value'], dict_mapping)
        print("term %s ----- translation CA  %s"%(row['value'],cr_term))
        if row.get('type') == 'model' and field.translate is True:
            self.model_translations[model_name][field_name][xmlid][lang] = cr_term
        elif row.get('type') == 'model_terms' and callable(field.translate):
            self.model_terms_translations[model_name][field_name][xmlid][row['src']][
                lang] = cr_term




TranslationImporter._load = _load


# Copyright 2024 Numigi and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).


from odoo.tools.translate import TranslationImporter as TLI


def get_ca_translation(value, mapping):
    for term, translation in mapping.items():
        value = value.replace(term, translation)
    return value


original_load = TLI._load


class TranslationImporter(TLI):

    def term_fr_ca_load(self, reader, lang, xmlids=None):
        fr_ca_terms = self.env["translate.term.fr_ca"].search([])
        dict_mapping = {record.term_fr: record.term_ca for record in fr_ca_terms}
        for row in reader:
            if not row.get("value") or not row.get("src"):
                continue
            if row.get("type") == "code":
                continue

            model_name = row.get("imd_model")
            module_name = row["module"]

            if model_name not in self.env:
                continue
            field_name = row["name"].split(",")[1]
            field = self.env[model_name]._fields.get(field_name)

            if not field or not field.translate or not field.store:
                continue
            xmlid = module_name + "." + row["imd_name"]
            if xmlids and xmlid not in xmlids:
                continue
            ca_term = get_ca_translation(row["value"], dict_mapping)
            if row.get("type") == "model" and field.translate is True:
                self.model_translations[model_name][field_name][xmlid][lang] = ca_term
            elif row.get("type") == "model_terms" and callable(field.translate):
                self.model_terms_translations[model_name][field_name][xmlid][
                    row["src"]
                ][lang]


TLI._load = TranslationImporter.term_fr_ca_load

# Copyright 2019-today Numigi and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).


from . import models

# from odoo import tools
# from odoo.api import Environment, SUPERUSER_ID
# import base64
# import contextlib
# import io
# import tempfile
# from io import BytesIO
# from odoo.tools.translate import CodeTranslations
#
#
# def _update_fr_ca_terms(cr, registry):
#     mods = []
#     lang = 'fr_FR'
#     format = 'po'
#     mapping = _get_credit_note_translations()
#     alias = CodeTranslations()
#     # for term in mapping:
#     #     source=term[0]
#     #     print("mapping",term[0])
#     #     print(alias.get_python_translations("account", "en_US").get(source,source))
#     # print(n)
#     mapping = mapping + _get_aged_balance_translations()
#     mapping = mapping + _get_reconciliation_translations()
#     mapping = mapping + _get_payment_translations()
#     with contextlib.closing(io.BytesIO()) as buf:
#         # Export the translations to a buffer
#         tools.trans_export(lang, mods, buf, format, cr)
#         buf.seek(0)  # Rewind the buffer to the beginning
#
#         # Read the exported data
#         po_data = buf.getvalue().decode('utf-8')
#
#         # Modify the msgstr values in the .po file content
#         modified_po_data = []
#         for line in po_data.splitlines():
#             if line.startswith('msgstr'):
#                 for term, translation in mapping:
#                     if term in line:
#                         line = line.replace(term, translation)
#             modified_po_data.append(line)
#
#         # Join the modified data back
#         modified_po_data = '\n'.join(modified_po_data)
#         # Import the modified translation back into Odoo
#         with tempfile.TemporaryFile() as buf:
#             buf.write(modified_po_data.encode('utf-8'))
#             fileformat = format.lower()
#             tools.trans_load_data(cr, buf, fileformat, lang, verbose=True,
#                 overwrite=True)
#
#
# def _get_credit_note_translations():
#     mapping = [
#         ("Facture de l'avoir", "Note de crédit"),
#         ("l'avoir", "la note de crédit"),
#         ("L'avoir", "La note de crédit"),
#         ("d'avoirs", "de notes de crédit"),
#         ("d'avoir", "de note de crédit"),
#         ("les avoirs", "les notes de crédit"),
#         ("un avoir", "une note de crédit"),
#         ("aux avoirs", "aux notes de crédit"),
#         ("le même avoir", "la même note de crédit"),
#         ("le prochain avoir", "la prochaine note de crédit"),
#         ("avoir", "note de crédit"),
#         ("Avoir", "Note de crédit"),
#         ("Remboursements", "Notes de crédit"),
#         # Grammatical errors
#         ("Note de crédits", "Notes de crédit"),
#         ("note de crédits", "notes de crédit"),
#     ]
#     return mapping
#
#
# def _get_aged_balance_translations():
#     mapping = [
#         ("Balance agée des clients", "Âge des comptes clients"),
#         ("Balance agée des fournisseurs", "Âge des comptes fournisseurs"),
#         ("Balances agées des tiers", "Âge des comptes"),
#         ("Balance agée", "Âge des comptes"),
#         ("balance agée", "âge des comptes"),
#     ]
#     return mapping
#
#
# def _get_reconciliation_translations():
#     mapping = [
#         ("Modèles de lettrage", "Modèles de conciliation bancaire"),
#         ("de lettrage", "de conciliation"),
#         ("du lettrage", "de la conciliation"),
#         ("le lettrage", "la conciliation"),
#         ("Non lettré", "Non réconcilié"),
#         ("Lettrer", "Réconcilier"),
#         ("lettrer", "réconcilier"),
#         ("Lettrage", "Conciliation"),
#         # Grammatical errors
#         ("annuler le lettrage l'entrée", "annuler la conciliation"),
#     ]
#     return mapping
#
#
# def _get_payment_translations():
#     mapping = [
#         ("Payments Sortants", "Paiements sortants"),
#         ("Configuration des Payements", "Configuration des paiements"),
#         ("Compte de Payements Sortants", "Compte de paiement sortant"),
#         ("Compte de Payements Entrants", "Compte de paiement entrant"),
#     ]
#     return mapping

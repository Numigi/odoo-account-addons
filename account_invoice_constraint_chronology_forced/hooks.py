# Copyright 2024 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import SUPERUSER_ID, api


def sale_journals_check_chronology(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    sale_journal_ids = env["account.journal"].search([("type", "=", "sale")])
    for journal in sale_journal_ids:
        journal.check_chronology = True

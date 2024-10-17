# Copyright 2014 Numigi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from ddt import ddt, data
from odoo.tests.common import TranslationCase


@ddt
class TestTranslation(TranslationCase):

    @data(
        ('Outgoing Payments', 'Payments Sortants'),
        ('Payments Configuration', 'Configuration des Payements'),
        ('Outstanding Payments Account', 'Compte de Payements Sortants'),
        ('Outstanding Receipts Account', 'Compte de Payements Entrants'),
    )
    def test_no_translation_found_with_wrong_term(self, data):
        assert not self._find_translation(data[0], data[1])

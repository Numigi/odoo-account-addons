# © 2019 Numigi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from ddt import ddt, data
from odoo.tests import common


class TranslationCase(common.TransactionCase):

    def _find_translation(self, source, value):
        return self.env['ir.translation'].search(
            [
                ('src', '=', source),
                ('value', '=', value),
            ]
        )

    @staticmethod
    def is_enterprise(env):
        # List of modules exclusive to Odoo Enterprise
        enterprise_modules = [
            'web_enterprise',
            'hr_payroll',
            'account_accountant',
            'account_reports',
            # Add more enterprise-specific modules as needed
        ]

        # Check if any of the enterprise modules are installed
        installed_modules = env['ir.module.module'].search(
            [('name', 'in', enterprise_modules), ('state', '=', 'installed')]
        )
        return bool(installed_modules)


@ddt
class TestCreditNote(TranslationCase):

    @data(
        ('Add Credit Note', 'Ajouter un avoir'),
        ('Dedicated Credit Note Sequence', 'Séquence dédiée aux avoirs'),
        ('Refund Date', "Date de l'avoir"),
    )
    def test_no_translation_found_with_wrong_term(self, data):
        assert not self._find_translation(data[0], data[1])

    @data(
        ('Add Credit Note', 'Ajouter une note de crédit'),
        ('Dedicated Credit Note Sequence', 'Séquence dédiée aux notes de crédit'),
        ('Refund Date', "Date de la note de crédit"),
    )
    def test_translations_found_with_correct_term(self, data):
        assert self._find_translation(data[0], data[1])


@ddt
class TestAgedBalance(TranslationCase):

    @data(
        ('Aged Receivable', 'Balance agée clients'),
        ('Aged Payable', 'Balance agée fournisseurs'),
        ('Aged Partner Balances', 'Balances agées des tiers'),
    )
    def test_no_translation_found_with_wrong_term(self, data):
        assert not self._find_translation(data[0], data[1])

    # Terms only available on account_reports in odoo-enterprise
    @data(
        ('Aged Receivable', 'Âge des comptes clients'),
        ('Aged Payable', 'Âge des comptes fournisseurs'),
        ('Aged Partner Balances', 'Âge des comptes'),
    )
    def test_translations_found_with_correct_term(self, data):
        if self.is_enterprise():
            assert self._find_translation(data[0], data[1])

    # @classmethod
    # def is_enterprise(cls):
    #     # List of modules exclusive to Odoo Enterprise
    #     enterprise_modules = [
    #         'web_enterprise',
    #         'hr_payroll',
    #         'account_accountant',
    #         'account_reports',
    #         # Add more enterprise-specific modules as needed
    #     ]

    #     # Check if any of the enterprise modules are installed
    #     installed_modules = cls.env['ir.module.module'].search(
    #         [('name', 'in', enterprise_modules), ('state', '=', 'installed')]
    #     )
    #     return bool(installed_modules)


@ddt
class TestReconciliation(TranslationCase):

    @data(
        ('Reconcile', 'Lettrer'),
        ('Unreconcile', 'Annuler le lettrage'),
        ('Reconciliation Models', 'Modèles de lettrage'),
        ('Reconciliation', 'Lettrage'),
    )
    def test_no_translation_found_with_wrong_term(self, data):
        assert not self._find_translation(data[0], data[1])

    @data(
        ('Reconcile', 'Réconcilier'),
        ('Unreconcile', 'Annuler la conciliation'),
        ('Reconciliation Models', 'Modèles de conciliation bancaire'),
        # Terms only available in enterprise version
        ('Reconciliation', 'Conciliation'),
    )
    def test_translations_found_with_correct_term(self, data):
        term, translation = data
        if term == 'Reconciliation':
            if self.is_enterprise:
                assert self._find_translation(term, translation)
        else:
            assert self._find_translation(term, translation)

    # @classmethod
    # def is_enterprise(cls):
    #     # List of modules exclusive to Odoo Enterprise
    #     enterprise_modules = [
    #         'web_enterprise',
    #         'hr_payroll',
    #         'account_accountant',
    #         'account_reports',
    #         # Add more enterprise-specific modules as needed
    #     ]

    #     # Check if any of the enterprise modules are installed
    #     installed_modules = cls.env['ir.module.module'].search(
    #         [('name', 'in', enterprise_modules), ('state', '=', 'installed')]
    #     )
    #     return bool(installed_modules)


@ddt
class TestPayment(TranslationCase):

    @data(
        ('Outgoing Payments', 'Payments Sortants'),
        ('Payments Configuration', 'Configuration des Payements'),
        ('Outstanding Payments Account', 'Compte de Payements Sortants'),
        ('Outstanding Receipts Account', 'Compte de Payements Entrants'),
    )
    def test_no_translation_found_with_wrong_term(self, data):
        assert not self._find_translation(data[0], data[1])

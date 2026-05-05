# © 2021 - today Numigi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.tests import TransactionCase


class TestAccountAdditionalGroup(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group_obj = cls.env["account.additional.group"]
        cls.group = cls.group_obj.create(
            {"name": "My Additional Group", "code": "10000"}
        )
        cls.account = cls.env["account.account"].search([], limit=1)
        cls.account.additional_group_id = cls.group

    def test_account_count(self):
<<<<<<< HEAD
        self.group.refresh()
=======
        self.group.invalidate_recordset()
>>>>>>> 579a2434c069884bf35385d10a1509d762eb56e8
        self.assertEqual(self.group.account_count, 1)

    def test_display_name(self):
        self.assertEqual(self.group.display_name, "10000 - My Additional Group")

    def test_search_by_code(self):
        ids = self._name_search(self.group.code)
        self.assertIn(self.group.id, ids)

    def test_search_by_code_with_limit(self):
        ids = self._name_search(self.group.code, limit=0)
<<<<<<< HEAD
        self.assertNotIn(self.group.id, ids)
=======
        self.assertIn(self.group.id, ids)
>>>>>>> 579a2434c069884bf35385d10a1509d762eb56e8

    def test_search_by_name(self):
        ids = self._name_search(self.group.name)
        self.assertIn(self.group.id, ids)

    def test_name_search_not_matching(self):
        ids = self._name_search("Not Matching")
        self.assertNotIn(self.group.id, ids)

    def _name_search(self, query, limit=None):
        return self.group_obj._name_search(query, limit=limit).ids

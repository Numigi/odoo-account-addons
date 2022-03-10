# © 2021 - today Numigi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from datetime import datetime, timedelta
from odoo.tests import common


class TestAccountAdditionalGroup(common.SavepointCase):
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
        assert self.group.account_count == 1

    def test_display_name(self):
        assert self.group.display_name == "10000 - My Additional Group"

    def test_search_by_code(self):
        ids = self._name_search(self.group.code)
        assert self.group.id in ids

    def test_search_by_code_with_limit(self):
        ids = self._name_search(self.group.code, limit=0)
        assert self.group.id not in ids

    def test_search_by_name(self):
        ids = self._name_search(self.group.name)
        assert self.group.id in ids

    def test_name_search_not_matching(self):
        ids = self._name_search("Not Matching")
        assert self.group.id not in ids

    def _name_search(self, query, limit=None):
        return [el[0] for el in self.group_obj.name_search(query, limit=limit)]

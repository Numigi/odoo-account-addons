# © 2021 - today Numigi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class AccountAdditionalGroup(models.Model):

    _name = "account.additional.group"
    _description = "Additional Group of Account"

    _parent_name = "parent_id"
    _parent_store = True
    _order = "code"

    name = fields.Char(required=True, translate=True)
    code = fields.Char(required=True,)

    parent_id = fields.Many2one("account.additional.group", ondelete="restrict")
    parent_path = fields.Char(index=True)
    active = fields.Boolean(default=True)

    account_ids = fields.Many2many("account.account", compute="_compute_accounts")
    account_count = fields.Integer(compute="_compute_account_count")

    def name_get(self):
        return [(r.id, "{} - {}".format(r.code, r.name)) for r in self]

    @api.model
    def _name_search(self, name="", args=None, operator="ilike", limit=100, order=None):
        """Search for records by name or code."""
        domain = args or []
        if operator in ("=", "ilike", "=ilike", "like", "=like"):
            domain = ['|', ('name', operator, name), ('code', operator, name)] + domain
        return self.search(domain, limit=limit, order=order or self._order)

    def _compute_accounts(self):
        for group in self:
            group.account_ids = (
                self.env["account.account"]
                .search([("additional_group_id", "child_of", group.id)])
            )

    @api.depends("account_ids")
    def _compute_account_count(self):
        for group in self:
            group.account_count = len(group.account_ids)

# © 2019 Numigi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class Account(models.Model):

    _inherit = 'account.account'

    manual_entry_group_ids = fields.Many2many(
        'res.groups',
        'account_manual_entry_group_rel',
        'account_id',
        'group_id',
        'Entry Restriction',
    )


class JournalEntry(models.Model):

    _inherit = 'account.move'

    def _check_manual_entry_restrictions(self):
        restricted_accounts = self.mapped('line_ids.account_id').filtered(
            lambda a: a.manual_entry_group_ids)

        for account in restricted_accounts:
            allowed_groups = account.manual_entry_group_ids
            user_is_forbidden = not (allowed_groups & self.env.user.groups_id)
            if user_is_forbidden:
                raise ValidationError(_(
                    'Access right error:\n\n'
                    'Only the following user group(s) are authorized to post in the account '
                    '{account}:\n\n'
                    '{groups}'
                    '\n\n'
                    'Please contact your administrator.'
                ).format(
                    account=account.display_name,
                    groups='\n'.join(['- {}'.format(g.display_name) for g in allowed_groups])
                ))

    @api.multi
    def action_post(self):
        """Verify the contrains on manual journal entries.

        This method is a wrapper around the method post.

        It is only called by the button from the form
        view of account.move.

        The method post is called directly for automatted entries
        (invoices, payments, expenses, etc).
        """
        self._check_manual_entry_restrictions()
        return super().action_post()

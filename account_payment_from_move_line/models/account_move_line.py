# © 2019 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models, _
from odoo.exceptions import UserError


def _check_has_partner(line: 'account.move.line', context: dict):
    if not line.partner_id:
        raise UserError(_(
            'The journal item has no partner.'
        ))


def _check_has_receivable_account(line: 'account.move.line', context: dict):
    if line.account_id.internal_type != 'receivable':
        raise UserError(_(
            'Only journal items with a receivable account '
            'can be selected to register a payment.'
        ))


def _check_is_posted(line: 'account.move.line', context: dict):
    if line.move_id.state != 'posted':
        raise UserError(_(
            'Only posted journal items '
            'can be selected to register a payment.'
        ))


def _check_is_not_reconciled(line: 'account.move.line', context: dict):
    if line.full_reconcile_id:
        raise UserError(_(
            'The journal item is already reconciled.'
        ))


def _check_single_line_is_selectable(line: 'account.move.line', context: dict):
    try:
        _check_has_receivable_account(line, context)
        _check_is_posted(line, context)
        _check_is_not_reconciled(line, context)
        _check_has_partner(line, context)
    except UserError as err:
        raise UserError(_(
            'The journal item {item} can not be selected to register a payment.\n'
            '{error}'
        ).format(item=line.display_name, error=err.name))


def _check_lines_have_common_commercial_partner(lines: 'account.move.line', context: dict):
    partners = lines.mapped('partner_id.commercial_partner_id')
    if len(partners) > 1:
        raise UserError(_(
            'The selected journal items are bound to multiple commercial partners:'
            '\n'
            '\t * {partners}'
            '\n'
            'A payment can only be registered for a single commercial partner.'
        ).format(partners='\n\t * '.join(partners.mapped('display_name'))))


def _check_lines_have_common_account(lines: 'account.move.line', context: dict):
    accounts = lines.mapped('account_id')
    if len(accounts) > 1:
        raise UserError(_(
            'The selected journal items are bound to multiple journal accounts:'
            '\n'
            '\t * {accounts}'
            '\n'
            'A payment can only be registered for a single account.'
        ).format(accounts='\n\t * '.join(accounts.mapped('display_name'))))


def _check_lines_have_common_currency(lines: 'account.move.line', context: dict):
    currencies = lines.mapped('currency_id')

    lines_without_currency = lines.filtered(lambda l: not l.currency_id)
    if lines_without_currency:
        currencies |= lines_without_currency.mapped('company_id.currency_id')

    if len(currencies) > 1:
        raise UserError(_(
            'The selected journal items are in multiple currencies:'
            '\n'
            '\t * {currencies}'
            '\n'
            'A payment can only be registered for a single account.'
        ).format(currencies='\n\t * '.join(currencies.mapped('display_name'))))


def _check_at_least_one_line_selected(lines: 'account.move.line', context: dict):
    if not lines:
        raise UserError(_(
            'You must select at least one journal item to generate payments.'
        ))


def _check_lines_are_selectable(lines: 'account.move.line', context: dict):
    user_errors = []
    for line in lines:
        try:
            _check_single_line_is_selectable(line, context)
        except UserError as err:
            user_errors.append(err)

    if user_errors:
        raise UserError('\n\n'.join([e.name for e in user_errors]))


class AccountMoveLine(models.Model):

    _inherit = 'account.move.line'

    def open_payment_from_move_line_wizard(self):
        _check_at_least_one_line_selected(self, self._context)
        _check_lines_have_common_commercial_partner(self, self._context)
        _check_lines_have_common_account(self, self._context)
        _check_lines_have_common_currency(self, self._context)
        _check_lines_are_selectable(self, self._context)

        wizard = self.env['account.payment.from.move.line'].create({})
        wizard.move_line_ids = self
        wizard.compute_amount_and_currency()
        wizard.compute_communication()

        action = wizard.get_formview_action()
        action['target'] = 'new'
        action['name'] = _('Register Payment')
        return action

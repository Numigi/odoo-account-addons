# © 2019 Numigi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from datetime import date
from odoo.addons.account.models.account_payment import account_payment as Payment


def change_payment_date(payment: Payment, new_date: date) -> None:
    """Change the date of the payment to the given date.

    Odoo posts accounting entries before the payments are technically sent.
    For some reason, the payment is not always sent on the same day.
    This function allows to change the date of the accounting entry properly.

    Super user priviledges are used to prevent access right errors.
    """
    payment_sudo = payment.sudo()
    account_move = payment_sudo.mapped('move_line_ids.move_id')
    account_move.write({
        'state': 'draft',
        'date': new_date,
    })
    account_move.line_ids.write({'date_maturity': new_date})
    account_move.state = 'posted'
    payment_sudo.payment_date = new_date

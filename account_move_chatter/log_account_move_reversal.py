# © 2019 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, models, _

MOVE_REVERSAL_MESSAGE = 'Journal entry reversed'


class AccountMoveWithLogReversal(models.Model):

    _inherit = 'account.move'

    @api.multi
    def _reverse_move(self, *args, **kwargs):
        result = super()._reverse_move(*args, **kwargs)
        self.message_post(_(MOVE_REVERSAL_MESSAGE))
        return result

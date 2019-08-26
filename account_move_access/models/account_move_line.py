# © 2019 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models, _
from odoo.exceptions import AccessError


class AccountMoveLine(models.Model):

    _inherit = 'account.move.line'

    def get_extended_security_domain(self):
        result = super().get_extended_security_domain()
        if not self.env.user.has_group('account.group_account_invoice'):
            return [('id', '=', False)]
        return result

    def check_extended_security_all(self):
        super().check_extended_security_all()
        if not self.env.user.has_group('account.group_account_invoice'):
            raise AccessError(_("You are not allowed to access journal items."))

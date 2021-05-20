# © 2019 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models, _
from odoo.exceptions import AccessError

INVOICE_CREATE_ERROR_MESSAGE = _(
    "You are not authorized to create an invoice."
)

INVOICE_WRITE_ERROR_MESSAGE = _(
    "You are not authorized to update an invoice."
)

INVOICE_UNLINK_ERROR_MESSAGE = _(
    "You are not authorized to delete an invoice."
)


class Invoice(models.Model):

    _inherit = 'account.invoice'

    def check_extended_security_write(self):
        super().check_extended_security_write()
        if not self.env.user.has_group('invoice_write_access.group_invoice'):
            raise AccessError(_(INVOICE_WRITE_ERROR_MESSAGE))

    def check_extended_security_create(self):
        super().check_extended_security_create()
        if not self.env.user.has_group('invoice_write_access.group_invoice'):
            raise AccessError(_(INVOICE_CREATE_ERROR_MESSAGE))

    def check_extended_security_unlink(self):
        super().check_extended_security_unlink()
        if not self.env.user.has_group('invoice_write_access.group_invoice'):
            raise AccessError(_(INVOICE_UNLINK_ERROR_MESSAGE))

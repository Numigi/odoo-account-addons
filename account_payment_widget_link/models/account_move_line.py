# © 2019 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/LGPL.html).

from odoo import models


class AccountMoveLine(models.Model):

    _inherit = 'account.move.line'

    def _get_payment_widget_origin_document(self):
        """Get the origin document related to this journal item.

        This method could be inherited to add extra types of source documents.
        """
        if self.invoice_id:
            return self.invoice_id

        if self.payment_id:
            return self.payment_id

    def get_payment_widget_link_action(self):
        document_to_open = self._get_payment_widget_origin_document() or self.move_id
        return document_to_open.get_formview_action()

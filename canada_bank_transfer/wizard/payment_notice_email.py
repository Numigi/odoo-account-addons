# © 2019 Numigi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import _, api, fields, models


class MailComposeWizard(models.TransientModel):

    _inherit = 'mail.compose.message'

    is_eft_payment_notice = fields.Boolean()
    eft_id = fields.Many2one('account.eft', 'EFT')

    @api.multi
    def action_send_mail(self):
        result = super().action_send_mail()
        if self.is_eft_payment_notice:
            self.eft_id.message_post(_('Payment notices sent.'))
            self.eft_id.payment_notices_sent = True
        return result

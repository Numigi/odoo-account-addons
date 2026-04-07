# © Numigi (tm) and all its contributors (https://numigi.com/r/home)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api


class MailMail(models.Model):
    _inherit = 'mail.mail'

    @api.model_create_multi
    def create(self, values_list):
        """
        Intercept the creation of outgoing emails.
        In Form View (comment mode), message_post delegates mail creation
        and often omits 'model' and 'res_id' in the values, relying on 'mail_message_id'.
        We must explicitly fetch the model and res_id from the linked message.
        """
        for values in values_list:
            model = values.get('model')
            res_id = values.get('res_id')

            # Fallback to fetch model/res_id from the related mail.message
            if not model and values.get('mail_message_id'):
                message = self.env['mail.message'].browse(values['mail_message_id'])
                model = message.model
                res_id = message.res_id

            if model in ['account.payment', 'account.move'] and res_id:
                record = self.env[model].browse(res_id)
                partner = getattr(record, 'partner_id', False)

                if partner and partner.payment_email:
                    values['email_to'] = partner.payment_email
                    if 'recipient_ids' in values:
                        values['recipient_ids'] = [(5, 0, 0)]
        return super(MailMail, self).create(values_list)

    def _postprocess_sent_message(self, success_pids, failure_reason=False, failure_type=None):
        """
        Because we stripped the recipient_ids during creation, Odoo's standard
        post-processing won't find the partner ID in success_pids.
        As a result, the notification stays in 'ready' state, causing a red envelope.
        We manually mark it as 'sent' if the SMTP transmission was successful.
        """
        res = super(MailMail, self)._postprocess_sent_message(
            success_pids, failure_reason=failure_reason, failure_type=failure_type)

        for mail in self:
            if mail.model in ['account.payment', 'account.move'] and mail.mail_message_id:
                record = self.env[mail.model].browse(mail.res_id)
                partner = getattr(record, 'partner_id', False)

                # If there is no genuine SMTP failure, we force the notification success
                if partner and partner.payment_email and not failure_reason:
                    # Find orphaned notifications stuck in 'ready' or 'exception'
                    notifications = mail.mail_message_id.notification_ids.filtered(
                        lambda n: n.notification_status in ['ready', 'exception']
                    )
                    if notifications:
                        notifications.write({
                            'notification_status': 'sent',
                            'failure_type': False,
                            'failure_reason': False,
                        })
        return res


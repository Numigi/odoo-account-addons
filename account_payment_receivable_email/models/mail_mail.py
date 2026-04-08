# © Numigi (tm) and all its contributors (https://numigi.com/r/home)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api
from odoo.tools import formataddr  # Import nécessaire pour formater le nom


class MailMail(models.Model):
    _inherit = 'mail.mail'

    @api.model_create_multi
    def create(self, values_list):
        for values in values_list:
            model = values.get('model')
            res_id = values.get('res_id')

            if not model and values.get('mail_message_id'):
                message = self.env['mail.message'].browse(values['mail_message_id'])
                model = message.model
                res_id = message.res_id

            if model in ['account.payment', 'account.move'] and res_id:
                record = self.env[model].browse(res_id)
                partner = getattr(record, 'partner_id', False)

                if partner and partner.payment_email:
                    # On formate proprement le nom pour le destinataire
                    formatted_name = f"{partner.name}, Comptes recevables"
                    values['email_to'] = formataddr((formatted_name, partner.payment_email))

                    # ON COUPE LE LIEN AVEC LE CONTACT ENFANT (qui a la fausse adresse)
                    if 'recipient_ids' in values:
                        values['recipient_ids'] = [(5, 0, 0)]

        return super(MailMail, self).create(values_list)

    def _postprocess_sent_message(self, success_pids, failure_reason=False, failure_type=None):
        mails_to_process = []
        for mail in self:
            if mail.model in ['account.payment', 'account.move'] and mail.mail_message_id:
                mails_to_process.append({
                    'message_id': mail.mail_message_id,
                    'model': mail.model,
                    'res_id': mail.res_id,
                })

        res = super(MailMail, self)._postprocess_sent_message(
            success_pids, failure_reason=failure_reason, failure_type=failure_type)

        for mail_data in mails_to_process:
            if (mail_data['model'] in ['account.payment', 'account.move']
                    and mail_data['message_id']):
                record = self.env[mail_data['model']].browse(mail_data['res_id'])
                partner = getattr(record, 'partner_id', False)

                # Force le succès de la notification
                if partner and partner.payment_email and not failure_reason:
                    notifications = mail_data['message_id'].notification_ids.filtered(
                        lambda n: n.notification_status in ['ready', 'exception']
                    )
                    if notifications:
                        notifications.write({
                            'notification_status': 'sent',
                            'failure_type': False,
                            'failure_reason': False,
                        })
        return res

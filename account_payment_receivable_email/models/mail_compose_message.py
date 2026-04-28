# © Numigi (tm) and all its contributors (https://numigi.com/r/home)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class MailComposer(models.TransientModel):
    _inherit = 'mail.compose.message'

    def onchange_template_id(self, template_id, composition_mode, model, res_id):
        """
        Update the UI when the template changes.
        Only works in 'comment' mode or single record selection (res_id is set).
        For Mass Mailing (EFT), res_id is often False, so UI update is skipped,
        but logic will be handled in get_mail_values.
        """
        res = super(MailComposer, self).onchange_template_id(
            template_id, composition_mode, model, res_id)

        if model not in ['account.payment', 'account.move'] or not res_id:
            return res

        record = self.env[model].browse(res_id)
        partner = getattr(record, 'partner_id', False)

        if partner and partner.payment_email_id:
            if 'value' not in res:
                res['value'] = {}
            res['value']['partner_ids'] = [(6, 0, [partner.payment_email_id.id])]

        return res

    def get_mail_values(self, res_ids):
        self.ensure_one()
        results = super(MailComposer, self).get_mail_values(res_ids)
        if self.model not in ["account.payment", "account.move"]:
            return results

        for res_id, mail_values in results.items():
            record = self.env[self.model].browse(res_id)
            partner = getattr(record, 'partner_id', False)

            if partner and partner.payment_email_id:
                target_id = partner.payment_email_id.id

                if 'partner_ids' in mail_values:
                    mail_values['partner_ids'] = [target_id]

                if 'recipient_ids' in mail_values:
                    mail_values['recipient_ids'] = [(5, 0, 0), (4, target_id)]

        return results

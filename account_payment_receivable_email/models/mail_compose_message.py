# © Numigi (tm) and all its contributors (https://numigi.com/r/home)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class MailComposer(models.TransientModel):
    _inherit = 'mail.compose.message'

    def onchange_template_id(self, template_id, composition_mode, model, res_id):
        """
        Override to update the wizard UI when the template changes.
        We clear the 'Recipients' field visually if a specific payment email is set.
        """
        res = super(MailComposer, self).onchange_template_id(template_id, composition_mode, model, res_id)

        # Apply only for relevant models with a valid record
        if model not in ['account.payment', 'account.eft'] or not res_id:
            return res

        record = self.env[model].browse(res_id)
        partner = getattr(record, 'partner_id', False)

        # If a specific payment email is configured on the partner
        if partner and partner.payment_email:
            if 'value' not in res:
                res['value'] = {}

            # Clear partner_ids in the UI using the ORM command [(6, 0, [])]
            # This ensures the user sees an empty recipient list instead of the default partner.
            res['value']['partner_ids'] = [(6, 0, [])]

        return res

    def get_mail_values(self, res_ids):
        """
        Override to inject the correct recipient at sending time.
        Handles both 'comment' mode (single email) and 'mass_mail' mode.
        """
        self.ensure_one()
        results = super(MailComposer, self).get_mail_values(res_ids)

        if self.model not in ["account.payment", "account.move"]:
            return results

        for res_id, mail_values in results.items():
            record = self.env[self.model].browse(res_id)
            partner = getattr(record, 'partner_id', False)

            if partner and partner.payment_email:
                # 1. Search for the dedicated child contact (type='other')
                receivable_contact = self.env['res.partner'].search([
                    ('parent_id', '=', partner.id),
                    ('type', '=', 'other'),
                    ('email', '=', partner.payment_email)
                ], limit=1)

                if receivable_contact:
                    # CASE A: Contact exists. Use it for proper notification tracking.

                    # 'comment' mode uses a simple list of IDs for partner_ids
                    if 'partner_ids' in mail_values:
                        mail_values['partner_ids'] = [receivable_contact.id]

                    # 'mass_mail' mode uses ORM commands for recipient_ids
                    if 'recipient_ids' in mail_values:
                        mail_values['recipient_ids'] = [(6, 0, [receivable_contact.id])]

                    # Ensure email_to is False to force usage of partner_id/recipient_ids
                    mail_values['email_to'] = False
                else:
                    # CASE B: Fallback if contact is missing. Use raw email.
                    mail_values['email_to'] = partner.payment_email

                    # Clear default recipients to avoid sending to the main partner
                    if 'partner_ids' in mail_values:
                        mail_values['partner_ids'] = []
                    if 'recipient_ids' in mail_values:
                        mail_values['recipient_ids'] = [(5, 0, 0)]  # Clear all command

        return results

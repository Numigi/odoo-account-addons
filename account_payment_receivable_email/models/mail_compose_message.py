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

        # Check model: we target Payment and Invoices
        if model not in ['account.payment', 'account.move'] or not res_id:
            return res

        record = self.env[model].browse(res_id)
        partner = getattr(record, 'partner_id', False)

        if partner and partner.payment_email:
            if 'value' not in res:
                res['value'] = {}

            # VISUAL ONLY: Clear recipients in the wizard view
            # We use Command (6) to replace the list with empty
            res['value']['partner_ids'] = [(6, 0, [])]

        return res

    def get_mail_values(self, res_ids):
        """
        Override to inject the specific recipient at sending time.
        COMPATIBLE WITH:
        - Standard Send (Comment mode)
        - Mass Mailing (Batch Send)
        - Canada Bank Transfer (EFT Wizards)
        """
        self.ensure_one()
        results = super(MailComposer, self).get_mail_values(res_ids)

        # Safety check on model
        if self.model not in ["account.payment", "account.move"]:
            return results

        for res_id, mail_values in results.items():
            record = self.env[self.model].browse(res_id)
            partner = getattr(record, 'partner_id', False)

            if partner and partner.payment_email:
                # 1. Search for the 'Receivable Accounts' child contact
                receivable_contact = self.env['res.partner'].search([
                    ('parent_id', '=', partner.id),
                    ('type', '=', 'other'),
                    ('email', '=', partner.payment_email)
                ], limit=1)

                # Determine the target: Contact ID or Raw Email
                target_partner_id = receivable_contact.id if receivable_contact else False
                target_email = partner.payment_email if not receivable_contact else False

                # 2. FORCE RECIPIENT LOGIC

                # A. Handle 'partner_ids' (Used in Comment/Single mode)
                # We simply set the list of IDs
                if 'partner_ids' in mail_values:
                    mail_values['partner_ids'] = [target_partner_id] \
                        if target_partner_id else []

                # B. Handle 'recipient_ids' (Used in Mass Mail / EFT mode)
                # CRITICAL: Must use ORM Commands [(5,0,0), (4, id)]
                # (5, 0, 0) = Clear all existing recipients (followers/main partner)
                # (4, id) = Add the new specific partner
                if 'recipient_ids' in mail_values:
                    commands = [(5, 0, 0)]  # Start by clearing
                    if target_partner_id:
                        commands.append((4, target_partner_id))
                    mail_values['recipient_ids'] = commands

                # C. Handle 'email_to'
                # If we have a partner, force email_to to False (so Odoo uses the partner)
                # If not, set the raw string.
                mail_values['email_to'] = target_email or False

        return results

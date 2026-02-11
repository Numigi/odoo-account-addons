# © Numigi (tm) and all its contributors (https://numigi.com/r/home)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class MailTemplate(models.Model):
    _inherit = "mail.template"

    def generate_email(self, res_ids, fields=None):
        """
        Override to use payment_email if defined on the partner
        when sending payment related documents.
        """
        results = super().generate_email(res_ids, fields=fields)

        # Identify if we are dealing with account.payment or account.move
        # based on the template's model
        if self.model not in ["account.payment", "account.move"]:
            return results

        multi_mode = True
        if isinstance(res_ids, int):
            res_ids = [res_ids]
            multi_mode = False

        for res_id in res_ids:
            record = self.env[self.model].browse(res_id)
            partner = getattr(record, 'partner_id', False)

            if partner and partner.payment_email:
                res_key = res_id if multi_mode else res_ids[0]
                if results.get(res_key):
                    results[res_key]['email_to'] = partner.payment_email

        return results
# © Numigi (tm) and all its contributors (https://numigi.com/r/home)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, _


class ResPartner(models.Model):
    _inherit = "res.partner"

    is_receivable_account = fields.Boolean(
        string="Is Receivable Account",
        default=False,
        copy=False,
    )

    payment_email = fields.Char(
        string="Receivable Accounts Email",
        help="Email address to send payment notifications and receipts",
        inverse="_inverse_payment_email"
    )

    def _inverse_payment_email(self):
        """
        Sync from Parent Field -> Child Contact.
        Uses the 'is_receivable_account' boolean to identify the target.
        """
        for partner in self:
            # --- ANTI- UNLIMITED LOOP ---
            if partner.is_receivable_account:
                continue

            if partner.payment_email:
                child_partner = self.env['res.partner'].with_context(active_test=False).search([
                    ('parent_id', '=', partner.id),
                    ('is_receivable_account', '=', True)
                ], limit=1)

                unique_fake_email = f"{partner.payment_email}.{partner.id}"

                if child_partner:
                    # Update existing contact
                    if child_partner.payment_email != partner.payment_email:
                        child_partner.payment_email = partner.payment_email
                        child_partner.email = unique_fake_email

                    # Reactivate if it was archived
                    if not child_partner.active:
                        child_partner.active = True
                else:
                    # Create NEW contact with the Boolean set to True
                    self.env['res.partner'].create({
                        'name': _('Receivable Accounts'),
                        'parent_id': partner.id,
                        'type': 'other',
                        'company_type': 'person',
                        'email': unique_fake_email,
                        'payment_email': partner.payment_email,
                        'is_receivable_account': True,
                        'comment': _('Automatically created from the '
                                     'Receivable Accounts Email field.'),
                    })

            else:
                # Field Cleared -> Find the boolean contact and Archive it
                child_to_archive = self.env['res.partner'].search([
                    ('parent_id', '=', partner.id),
                    ('is_receivable_account', '=', True)
                ], limit=1)

                if child_to_archive:
                    child_to_archive.active = False

    def write(self, vals):
        """
        Sync from Child Contact -> Parent Field.
        We strictly listen to contacts marked with 'is_receivable_account'.
        """
        records_to_sync = self.env['res.partner']
        if 'payment_email' in vals:
            for record in self:
                if record.parent_id and record.is_receivable_account:
                    records_to_sync += record

        # Perform Standard Write
        res = super(ResPartner, self).write(vals)

        # Propagate to parents
        for record in records_to_sync:
            if record.parent_id.payment_email != vals['payment_email']:
                record.parent_id.payment_email = vals['payment_email']

        return res

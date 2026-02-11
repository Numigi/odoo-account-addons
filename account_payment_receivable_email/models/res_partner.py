# © Numigi (tm) and all its contributors (https://numigi.com/r/home)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, _


class ResPartner(models.Model):
    _inherit = "res.partner"

    payment_email = fields.Char(
        string="Receivable Accounts Email",
        help="Email address to send payment notifications and receipts",
        inverse="_inverse_payment_email"
    )

    def _inverse_payment_email(self):
        """
        Create or update a child contact of type 'other'
        when the payment_email is defined.
        """
        for partner in self:
            if not partner.payment_email:
                continue

            # 1. Check if a child contact of type 'other'
            # with this email already exists for this parent
            child_partner = self.env['res.partner'].search([
                ('parent_id', '=', partner.id),
                ('type', '=', 'other'),
                ('email', '=', partner.payment_email)
            ], limit=1)

            # 2. If not found, create it
            if not child_partner:
                self.env['res.partner'].create({
                    'name': _('Receivable Accounts'),  # Default name
                    'parent_id': partner.id,
                    'type': 'other',
                    'email': partner.payment_email,
                    'comment': _('Automatically created from the Receivable'
                                 ' Accounts Email field.'),
                })

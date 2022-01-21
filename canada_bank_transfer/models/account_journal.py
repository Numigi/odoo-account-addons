# © 2019 Numigi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class AccountJournal(models.Model):

    _inherit = "account.journal"

    canada_transit = fields.Char(
        "Transit Number",
        size=5,
        related="bank_account_id.canada_transit",
        readonly=False,
    )

    eft_user_short_name = fields.Char(
        "EFT User Short Name",
        size=15,
        help="A short version of your company name. "
        "Must be composed of maximum 15 alphanumeric caracters.",
    )

    eft_user_long_name = fields.Char(
        "EFT User Long Name",
        size=30,
        help="A long version of your company name. "
        "Must be composed of maximum 30 alphanumeric caracters.",
    )

    eft_user_number = fields.Char(
        "EFT User Number",
        size=10,
        help="This number is attributed by your bank to identify your company. "
        "It is composed of 10 alphanumeric caracters.",
    )

    eft_destination = fields.Char(
        "EFT Destination",
        size=5,
        help="Technical value of 5 digits used in the EFT file. "
        "It indicates the data processing center that will handle your tranfers. "
        "The value depends on the bank and the location of your company.",
    )

    eft_enabled = fields.Boolean(compute="_compute_eft_enabled", store=True)

    eft_sequence_id = fields.Many2one(
        "ir.sequence", string="EFT Sequence", ondelete="restrict"
    )
    transit_account = fields.Many2one('account.account', string="Transit Account", store=1)
    use_transit_account = fields.Boolean(string="Use a transit Account", related="company_id.use_transit_account")

    @api.depends("outbound_payment_method_ids")
    def _compute_eft_enabled(self):
        """Compute the field eft_enabled.

        raise_if_not_found=False is used because the field may be evaluated
        before the xml ID was loaded in the system.
        """
        eft_method = self.env.ref(
            "canada_bank_transfer.payment_method_eft", raise_if_not_found=False
        )
        for journal in self:
            journal.eft_enabled = (
                eft_method and eft_method in journal.outbound_payment_method_ids
            )

    @api.model
    def create(self, vals):
        journal = super().create(vals)
        journal._setup_eft_sequence()
        return journal

    @api.multi
    def write(self, vals):
        super().write(vals)
        if "outbound_payment_method_ids" in vals:
            for journal in self:
                journal._setup_eft_sequence()
        return True

    def _setup_eft_sequence(self):
        if self.eft_enabled and not self.eft_sequence_id:
            self.eft_sequence_id = self.env["ir.sequence"].create(
                {
                    "name": "EFT ({})".format(self.name),
                    "number_next": 1,
                    "number_increment": 1,
                    "company_id": self.company_id.id,
                    "implementation": "no_gap",
                })

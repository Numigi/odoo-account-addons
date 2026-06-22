# -*- coding: utf-8 -*-
# Copyright 2026-today Numigi and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, _
from odoo.exceptions import ValidationError


class AccountMove(models.Model):
    _inherit = "account.move"

    def action_register_payment(self):
        self._verify_moves_are_posted()
        return super().action_register_payment()

    def _verify_moves_are_posted(self):
        unposted_moves = self.filtered(lambda m: m.state != "posted")
        if unposted_moves:
            raise ValidationError(
                _("You cannot register a payment for an unposted invoice.")
            )

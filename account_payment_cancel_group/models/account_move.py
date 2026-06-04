# Copyright 2024-today Numigi and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import logging
from odoo import models, _
from odoo.exceptions import AccessError

# Initialisation du logger
_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = "account.move"

    def button_draft(self):
        _logger.info(
            "=== [AccountMove] button_draft appelé pour les IDs: %s ===", self.ids
        )
        self._check_payment_cancel_authorization()
        return super().button_draft()

    def button_cancel(self):
        _logger.info(
            "=== [AccountMove] button_cancel appelé pour les IDs: %s ===", self.ids
        )
        self._check_payment_cancel_authorization()
        return super().button_cancel()

    def _check_payment_cancel_authorization(self):
        _logger.info(
            "=== [AccountMove] _check_payment_cancel_authorization en cours d'exécution ==="
        )

        contains_payments = self._contains_payments()
        user_can_cancel = self._user_can_cancel_payments()

        _logger.info("   -> _contains_payments retourné : %s", contains_payments)
        _logger.info("   -> _user_can_cancel_payments retourné : %s", user_can_cancel)

        if contains_payments and not user_can_cancel:
            _logger.warning("   -> Accès refusé ! Levée de l'exception AccessError.")
            raise AccessError(
                _("You are not authorized to reset to draft or cancel payments.")
            )
        else:
            _logger.info("   -> Autorisation accordée. Aucune exception levée.")

    def _user_can_cancel_payments(self):
        has_group = self.env.user.has_group(
            "account_payment_cancel_group.group_cancel_payments"
        )
        _logger.info(
            "   -> Vérification du groupe pour l'utilisateur '%s' (ID: %s) : %s",
            self.env.user.name,
            self.env.user.id,
            has_group,
        )
        return has_group

    def _contains_payments(self):
        has_payment = bool(
            self
            and self.env["account.payment"].search_count([("move_id", "in", self.ids)])
        )
        _logger.info(
            "   -> Vérification si les pièces comptables %s contiennent des paiements : %s",
            self.ids,
            has_payment,
        )
        return has_payment

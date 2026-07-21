# Copyright 2024 Numigi and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class TranslateTermFrCA(models.Model):

    _name = "translate.term.fr_ca"
    _description = "Translation Terms (FR to CA)"

    term_fr = fields.Char(string="Term Fr")
    term_ca = fields.Char(string="Term CA")

    def action_apply_translations(self):
        # Trigger manual translation update from the view button
        installed_modules = self._get_installed_modules()
        installed_modules._update_translations(["fr_FR"], True)
        self.env.registry.clear_cache()
        return self._build_success_notification()

    def _get_installed_modules(self):
        # Fetch all currently installed modules to update their translations
        return self.env["ir.module.module"].search([("state", "=", "installed")])

    def _build_success_notification(self):
        # Return a client action to notify the user of successful execution
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": "Success",
                "message": "Translations applied successfully.",
                "type": "success",
                "sticky": False,
            },
        }

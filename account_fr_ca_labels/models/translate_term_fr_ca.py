# Copyright 2024 Numigi and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class TranslateTermFrCA(models.Model):

    _name = "translate.term.fr_ca"

    term_fr = fields.Char(string="Term Fr")
    term_ca = fields.Char(string="Term CA")

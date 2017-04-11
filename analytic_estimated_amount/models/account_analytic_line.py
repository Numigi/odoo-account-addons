# -*- coding: utf-8 -*-
# © 2017 Savoir-faire Linux
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class AccountAnalyticLine(models.Model):

    _inherit = 'account.analytic.line'

    estimated_amount = fields.Monetary('Estimated Amount')

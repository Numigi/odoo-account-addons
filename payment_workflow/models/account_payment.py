# -*- coding: utf-8 -*-
# © 2017 Savoir-faire Linux
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class AccountPayment(models.Model):

    _name = 'account.payment'
    _inherit = ['mail.thread', 'account.payment']

    payment_type = fields.Selection(track_visibility='onchange')
    payment_method_id = fields.Many2one(track_visibility='onchange')
    partner_type = fields.Selection(track_visibility='onchange')
    partner_id = fields.Many2one(track_visibility='onchange')
    amount = fields.Monetary(track_visibility='onchange')
    currency_id = fields.Many2one(track_visibility='onchange')
    payment_date = fields.Date(track_visibility='onchange')
    communication = fields.Char(track_visibility='onchange')
    journal_id = fields.Many2one(track_visibility='onchange')
    state = fields.Selection(track_visibility='onchange')
    payment_reference = fields.Char(track_visibility='onchange')
    check_amount_in_words = fields.Char(track_visibility='onchange')
    check_number = fields.Integer(track_visibility='onchange')

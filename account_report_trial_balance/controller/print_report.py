# © 2021 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import json
from odoo import http
from odoo.http import request


class PrintGeneralLedger(http.Controller):

    @http.route('/web/account_report_trial_balance/<int:report_id>', type='http', auth='user')
    def account_report_trial_balance_pdf(self, report_id, token):
        output_pdf = request.env['account.report.trial.balance'].browse(report_id).get_pdf()
        response = request.make_response(
            output_pdf,
            headers=[
                ('Content-Type', 'application/pdf'),
                ('Content-Disposition', 'attachment; filename=trial_balance.pdf;')
            ]
        )
        response.set_cookie('fileToken', token)
        return response

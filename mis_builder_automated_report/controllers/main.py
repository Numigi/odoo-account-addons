# © 2022 - Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.addons.report_xlsx.controllers import main as report
from odoo.http import content_disposition, route, request
from odoo.exceptions import UserError, ValidationError
from odoo.tools.safe_eval import safe_eval

import json
import time
import werkzeug
import base64


class ReportController(report.ReportController):

    def _create_attachment(self, data, file):
        res_id = data['context'].get("active_id")
        model = data['context'].get("active_model")
        uid = data['context'].get("uid")
        record = request.env[model].browse(res_id)
        return (
            request.env["ir.attachment"]
            .sudo()
            .create(
                {
                    "res_model": model,
                    "res_id": res_id,
                    "name": record.display_name,
                    "create_uid": uid,
                    "datas": base64.encodebytes(file),
                    "type": 'binary',
                    "datas_fname": record.display_name,
                }
            )
        )

    # @route()
    # def report_routes(self, reportname, docids=None, converter=None, **data):
    #     if converter == 'xlsx':
    #         try:
    #             report = request.env['ir.actions.report'
    #             ]._get_report_from_name(reportname)
    #             context = dict(request.env.context)
    #             if docids:
    #                 docids = [int(i) for i in docids.split(',')]
    #             if data.get('options'):
    #                 data.update(json.loads(data.pop('options')))
    #             if data.get('context'):
    #                 # Ignore 'lang' here, because the context in data is the
    #                 # one from the webclient *but* if the user explicitely
    #                 # wants to change the lang, this mechanism overwrites it.
    #                 data['context'] = json.loads(data['context'])
    #                 if data['context'].get('lang'):
    #                     del data['context']['lang']
    #                 context.update(data['context'])
    #             xlsx = report.with_context(context).render_xlsx(
    #                 docids, data=data
    #             )[0]
    #             report_name = report.report_file
    #             if report.print_report_name and not len(docids) > 1:
    #                 obj = request.env[report.model].browse(docids[0])
    #                 report_name = safe_eval(report.print_report_name,
    #                                         {'object': obj, 'time': time})
    #         except (UserError, ValidationError) as odoo_error:
    #             raise werkzeug.exceptions.HTTPException(
    #                 description='{error_name}. {error_value}'.format(
    #                     error_name=odoo_error.name,
    #                     error_value=odoo_error.value,
    #                 ))
    #         xlsxhttpheaders = [
    #             ('Content-Type', 'application/vnd.openxmlformats-'
    #                              'officedocument.spreadsheetml.sheet'),
    #             ('Content-Length', len(xlsx)),
    #             (
    #                 'Content-Disposition',
    #                 content_disposition(report_name + '.xlsx')
    #             )
    #         ]
    #         if data['context'].get('automated_edition'):
    #             self._create_attachment(data, xlsx)
    #             # TODO return empty request: return request.make_response('')
    #         return request.make_response(xlsx, headers=xlsxhttpheaders)
    #     return super(ReportController, self).report_routes(
    #         reportname, docids, converter, **data
    #     )

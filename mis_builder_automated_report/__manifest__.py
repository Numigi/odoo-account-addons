# © 2022 - Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    'name': 'Mis Builder Automated Report',
    'version': '1.0.0',
    'author': 'Numigi',
    'maintainer': 'Numigi',
    'website': 'https://www.numigi.com',
    'license': 'LGPL-3',
    'category': 'Accounting',
    'summary': 'Add Automated Edition to Export xlsx Report',
    'depends': [
        'mis_builder',
        'queue_job',
    ],
    'data': [
        "data/queue_job_function.xml",
        "views/assets_template.xml",
        "views/mis_report_instance.xml",
        "views/automated_report.xml",
    ],
    'qweb': ["static/src/xml/mis_report_widget.xml"],
    'installable': True,
}

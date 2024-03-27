# © 2023 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Account Fiscalyear End on Company',
    'version': '1.1.1',
    'author': 'Numigi',
    'maintainer': 'Numigi',
    'license': 'AGPL-3',
    'category': 'Accounting',
    'summary': 'Shows `Fiscal Year End` on company view form.',
    'depends': [
        'account',
    ],
    'data': [
        'views/res_company.xml',
    ],
    'installable': True,
}

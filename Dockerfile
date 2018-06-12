FROM quay.io/numigi/odoo-public:11.0
MAINTAINER numigi <contact@numigi.com>

COPY account_negative_debit_credit /mnt/extra-addons/account_negative_debit_credit
COPY analytic_source /mnt/extra-addons/analytic_source
COPY hr_expense_tax_adjustment /mnt/extra-addons/hr_expense_tax_adjustment
COPY invoice_currency_validation /mnt/extra-addons/invoice_currency_validation
COPY invoice_fiscal_position_required /mnt/extra-addons/invoice_fiscal_position_required

COPY .docker_files/main /mnt/extra-addons/main
COPY .docker_files/odoo.conf /etc/odoo

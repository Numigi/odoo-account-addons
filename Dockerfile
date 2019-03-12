FROM quay.io/numigi/odoo-public:12.0
MAINTAINER numigi <contact@numigi.com>

USER root

COPY .docker_files/test-requirements.txt .
RUN pip3 install -r test-requirements.txt

COPY .docker_files/requirements.txt .
RUN pip3 install -r requirements.txt

USER odoo

COPY account_analytic_required_forbidden /mnt/extra-addons/account_analytic_required_forbidden
COPY account_negative_debit_credit /mnt/extra-addons/account_negative_debit_credit
COPY canada_bank_transfer /mnt/extra-addons/canada_bank_transfer
COPY hr_expense_tax_adjustment /mnt/extra-addons/hr_expense_tax_adjustment
COPY invoice_currency_validation /mnt/extra-addons/invoice_currency_validation
COPY invoice_fiscal_position_required /mnt/extra-addons/invoice_fiscal_position_required
COPY account_move_chatter /mnt/extra-addons/account_move_chatter
COPY invoice_refund_not_earlier /mnt/extra-addons/invoice_refund_not_earlier

COPY .docker_files/main /mnt/extra-addons/main
COPY .docker_files/odoo.conf /etc/odoo

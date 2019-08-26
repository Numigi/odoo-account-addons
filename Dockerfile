FROM quay.io/numigi/odoo-public:12.0
MAINTAINER numigi <contact@numigi.com>

USER root

COPY .docker_files/test-requirements.txt .
RUN pip3 install -r test-requirements.txt

COPY .docker_files/requirements.txt .
RUN pip3 install -r requirements.txt

# Variable used for fetching private git repositories.
ARG GIT_TOKEN

ENV THIRD_PARTY_ADDONS /mnt/third-party-addons
RUN mkdir -p "${THIRD_PARTY_ADDONS}" && chown -R odoo "${THIRD_PARTY_ADDONS}"
COPY ./gitoo.yml /gitoo.yml
RUN gitoo install-all --conf_file /gitoo.yml --destination "${THIRD_PARTY_ADDONS}"

USER odoo

COPY account_analytic_required_forbidden /mnt/extra-addons/account_analytic_required_forbidden
COPY account_bank_menu /mnt/extra-addons/account_bank_menu
COPY account_budget_balance /mnt/extra-addons/account_budget_balance
COPY account_fr_ca_labels /mnt/extra-addons/account_fr_ca_labels
COPY account_manual_entry_restricted /mnt/extra-addons/account_manual_entry_restricted
COPY account_move_access /mnt/extra-addons/account_move_access
COPY account_move_chatter /mnt/extra-addons/account_move_chatter
COPY account_negative_debit_credit /mnt/extra-addons/account_negative_debit_credit
COPY account_payment_cancel_group /mnt/extra-addons/account_payment_cancel_group
COPY account_report_line_menu /mnt/extra-addons/account_report_line_menu
COPY budget_analysis_account_move_line /mnt/extra-addons/budget_analysis_account_move_line
COPY canada_bank_transfer /mnt/extra-addons/canada_bank_transfer
COPY hr_expense_tax_adjustment /mnt/extra-addons/hr_expense_tax_adjustment
COPY invoice_currency_validation /mnt/extra-addons/invoice_currency_validation
COPY invoice_fiscal_position_required /mnt/extra-addons/invoice_fiscal_position_required
COPY invoice_refund_not_earlier /mnt/extra-addons/invoice_refund_not_earlier
COPY invoice_write_access /mnt/extra-addons/invoice_write_access
COPY invoice_write_access_purchase /mnt/extra-addons/invoice_write_access_purchase
COPY invoice_write_access_sale /mnt/extra-addons/invoice_write_access_sale
COPY vendor_invoice_full_list /mnt/extra-addons/vendor_invoice_full_list

COPY .docker_files/main /mnt/extra-addons/main
COPY .docker_files/odoo.conf /etc/odoo

FROM quay.io/numigi/odoo-public:14.latest
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

COPY account_additional_group /mnt/extra-addons/account_additional_group
COPY account_analytic_required_forbidden /mnt/extra-addons/account_analytic_required_forbidden
COPY account_bank_menu /mnt/extra-addons/account_bank_menu
COPY account_check_deposit_enhanced /mnt/extra-addons/account_check_deposit_enhanced
COPY account_closing_journal /mnt/extra-addons/account_closing_journal
COPY account_closing_journal_mis_builder /mnt/extra-addons/account_closing_journal_mis_builder
COPY account_closing_wizard /mnt/extra-addons/account_closing_wizard
COPY account_fiscalyear_end_on_company /mnt/extra-addons/account_fiscalyear_end_on_company
COPY account_fr_ca_labels /mnt/extra-addons/account_fr_ca_labels
COPY account_invoice_constraint_chronology_forced /mnt/extra-addons/account_invoice_constraint_chronology_forced
COPY account_invoice_groupby_parent_affiliate /mnt/extra-addons/account_invoice_groupby_parent_affiliate
COPY account_move_reversal_access /mnt/extra-addons/account_move_reversal_access
COPY account_move_reversed_entry /mnt/extra-addons/account_move_reversed_entry
COPY account_move_unique_reversal /mnt/extra-addons/account_move_unique_reversal
COPY account_negative_debit_credit /mnt/extra-addons/account_negative_debit_credit
COPY account_payment_cancel_group /mnt/extra-addons/account_payment_cancel_group
COPY account_payment_term_usage /mnt/extra-addons/account_payment_term_usage
COPY account_payment_term_usage_purchase /mnt/extra-addons/account_payment_term_usage_purchase
COPY account_payment_term_usage_sale /mnt/extra-addons/account_payment_term_usage_sale
COPY account_payment_widget_link /mnt/extra-addons/account_payment_widget_link
COPY account_report_line_menu /mnt/extra-addons/account_report_line_menu
COPY account_report_trial_balance /mnt/extra-addons/account_report_trial_balance
COPY account_search_by_amount /mnt/extra-addons/account_search_by_amount
COPY account_show_full_features /mnt/extra-addons/account_show_full_features
COPY account_type_archive /mnt/extra-addons/account_type_archive
COPY account_type_sane /mnt/extra-addons/account_type_sane
COPY account_unaffected_earnings_disabled /mnt/extra-addons/account_unaffected_earnings_disabled
COPY bank_statement_extra_columns /mnt/extra-addons/bank_statement_extra_columns
COPY bank_statement_import_csv /mnt/extra-addons/bank_statement_import_csv
COPY bank_statement_no_reverse /mnt/extra-addons/bank_statement_no_reverse
COPY bank_statement_online_stripe /mnt/extra-addons/bank_statement_online_stripe
COPY bank_statement_partner_mapping /mnt/extra-addons/bank_statement_partner_mapping
COPY bank_statement_partner_name /mnt/extra-addons/bank_statement_partner_name
COPY canada_account_types /mnt/extra-addons/canada_account_types
COPY canada_bank_transfer /mnt/extra-addons/canada_bank_transfer
COPY hr_expense_tax_adjustment /mnt/extra-addons/hr_expense_tax_adjustment
COPY invoice_currency_validation /mnt/extra-addons/invoice_currency_validation
COPY invoice_fiscal_position_required /mnt/extra-addons/invoice_fiscal_position_required
COPY invoice_intercompany_compatible  /mnt/extra-addons/invoice_intercompany_compatible
COPY invoice_list_email /mnt/extra-addons/invoice_list_email
COPY invoice_mass_mailing_with_layout /mnt/extra-addons/invoice_mass_mailing_with_layout
COPY invoice_refund_not_earlier /mnt/extra-addons/invoice_refund_not_earlier
COPY old_accounts /mnt/extra-addons/old_accounts
COPY payment_list_not_sent /mnt/extra-addons/payment_list_not_sent
COPY payment_stripe_not_silenced /mnt/extra-addons/payment_stripe_not_silenced

COPY .docker_files/main /mnt/extra-addons/main
COPY .docker_files/odoo.conf /etc/odoo

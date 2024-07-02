FROM quay.io/numigi/odoo-public:16.latest
LABEL maintainer="numigi <contact@numigi.com>"

USER root

COPY .docker_files/requirements.txt .
RUN pip3 install -r requirements.txt

ENV THIRD_PARTY_ADDONS /mnt/third-party-addons
RUN mkdir -p "${THIRD_PARTY_ADDONS}" && chown -R odoo "${THIRD_PARTY_ADDONS}"
COPY ./gitoo.yml /gitoo.yml
RUN gitoo install-all --conf_file /gitoo.yml --destination "${THIRD_PARTY_ADDONS}"

USER odoo

COPY account_bank_menu /mnt/extra-addons/account_bank_menu
COPY account_closing_journal /mnt/extra-addons/account_closing_journal
COPY account_invoice_constraint_chronology_forced /mnt/extra-addons/account_invoice_constraint_chronology_forced
COPY account_show_full_features /mnt/extra-addons/account_show_full_features
COPY old_accounts /mnt/extra-addons/old_accounts

COPY .docker_files/main /mnt/extra-addons/main
COPY .docker_files/odoo.conf /etc/odoo

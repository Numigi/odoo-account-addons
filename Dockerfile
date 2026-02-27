FROM quay.io/numigi/odoo-public:18.latest
LABEL maintainer="numigi <contact@numigi.com>"

USER root

COPY .docker_files/requirements.txt .
RUN pip3 install -r requirements.txt

ENV THIRD_PARTY_ADDONS /mnt/third-party-addons
RUN mkdir -p "${THIRD_PARTY_ADDONS}" && chown -R odoo "${THIRD_PARTY_ADDONS}"
COPY ./gitoo.yml /gitoo.yml
RUN if [ -s /gitoo.yml ]; then \
        gitoo install-all --conf_file /gitoo.yml --destination "${THIRD_PARTY_ADDONS}"; \
    fi

USER odoo
COPY account_additional_group /mnt/extra-addons/account_additional_group
COPY canada_mis_report /mnt/extra-addons/canada_mis_report
COPY canada_account_types /mnt/extra-addons/canada_account_types

COPY .docker_files/main /mnt/extra-addons/main
COPY .docker_files/odoo.conf /etc/odoo

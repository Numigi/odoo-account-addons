FROM quay.io/numigi/odoo-public:11.0
MAINTAINER numigi <contact@numigi.com>

USER root

COPY ./analytic_source /mnt/extra-addons/analytic_source
COPY ./invoice_currency_validation /mnt/extra-addons/invoice_currency_validation
COPY ./docker_files/main /mnt/extra-addons/main

COPY ./docker_files/odoo.conf /etc/odoo/odoo.conf

USER odoo

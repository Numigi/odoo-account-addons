# Copyright 2025 Numigi (tm) and all its contributors (https://numigi.com/r/home)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).


# Copyright 2025 Your Company
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging
import datetime
import pytz
from odoo import fields, models
from odoo.tools.safe_eval import (
    safe_eval,
    time as safe_time,
    datetime as safe_datetime,
    dateutil as safe_dateutil
)

# Import aggregation functions from the original module to avoid code duplication logic
from odoo.addons.mis_builder.models.aggregate import _avg, _max, _min, _sum
from odoo.addons.mis_builder.models.accounting_none import AccountingNone

_logger = logging.getLogger(__name__)


class AutoStruct(object):
    """ Simple wrapper to access dict keys as attributes,
    similar to the original one in mis_builder. """

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


def _utc_midnight(d, tz_name, add_day=0):
    """ Helper to convert date to UTC datetime at midnight, local to the original file. """
    d = fields.Datetime.from_string(d) + datetime.timedelta(days=add_day)
    utc_tz = pytz.timezone("UTC")
    context_tz = pytz.timezone(tz_name)
    local_timestamp = context_tz.localize(d, is_dst=False)
    return fields.Datetime.to_string(local_timestamp.astimezone(utc_tz))


class MisReportQuery(models.Model):
    _inherit = "mis.report.query"

    ignore_date_from = fields.Boolean(
        string="Ignore Start Date",
        help=(
            "If checked, the query will fetch all data up to the end date, "
            "ignoring the report start date."
        ),
    )


class MisReport(models.Model):
    _inherit = "mis.report"

    def _fetch_query_result(self, query, model, domain):
        """Fetches and aggregates data for a single query."""
        field_names = [f.name for f in query.field_ids]
        all_stored = all([model._fields[f].store for f in field_names])

        # Standard data fetching logic (same as original)
        if not query.aggregate:
            data = model.search_read(domain, field_names)
            return [AutoStruct(**d) for d in data]
        elif query.aggregate == "sum" and all_stored:
            # Use read_group for optimization if aggregation is 'sum' and fields are stored
            data = model.read_group(domain, field_names, [])
            # Handle case where read_group returns empty result
            count = data[0]["__count"] if data else 0
            s = AutoStruct(count=count)

            if data:
                for field_name in field_names:
                    try:
                        v = data[0][field_name]
                    except KeyError:
                        _logger.error(
                            "field %s not found in read_group for %s; not summable?",
                            field_name,
                            model._name,
                        )
                        v = AccountingNone
                    setattr(s, field_name, v)
            else:
                # Initialize with 0/None if no data
                for field_name in field_names:
                    setattr(s, field_name, 0.0)

            return s
        else:
            # Fallback to Python aggregation
            data = model.search_read(domain, field_names)
            s = AutoStruct(count=len(data))
            if query.aggregate == "min":
                agg = _min
            elif query.aggregate == "max":
                agg = _max
            elif query.aggregate == "avg":
                agg = _avg
            elif query.aggregate == "sum":
                agg = _sum
            for field_name in field_names:
                setattr(s, field_name, agg([d[field_name] for d in data]))
            return s

    def _fetch_queries(self, date_from, date_to, get_additional_query_filter=None):
        """
        Override of _fetch_queries to handle the 'ignore_date_from' flag on queries.
        If the flag is set, the domain will not include the start date condition.
        """
        self.ensure_one()
        res = {}
        for query in self.query_ids:
            model = self.env[query.model_id.model]
            eval_context = {
                "env": self.env,
                "time": safe_time,
                "datetime": safe_datetime,
                "dateutil": safe_dateutil,
                "uid": self.env.uid,
                "context": self.env.context,
            }
            # Evaluate the base domain defined on the query
            domain = query.domain and safe_eval(query.domain, eval_context) or []

            # Add dynamic filters if provided (e.g. from hooks)
            if get_additional_query_filter:
                domain.extend(get_additional_query_filter(query))

            # --- MODIFIED LOGIC START ---
            if query.date_field.ttype == "date":
                # Only add the start date filter if the flag is NOT set
                if not query.ignore_date_from:
                    domain.append((query.date_field.name, ">=", date_from))
                # Always add the end date filter
                domain.append((query.date_field.name, "<=", date_to))

            else:  # datetime case
                tz = str(self.env["ir.fields.converter"]._input_tz())
                datetime_to = _utc_midnight(date_to, tz, add_day=1)

                # Only add the start datetime filter if the flag is NOT set
                if not query.ignore_date_from:
                    datetime_from = _utc_midnight(date_from, tz)
                    domain.append((query.date_field.name, ">=", datetime_from))

                # Always add the end datetime filter
                domain.append((query.date_field.name, "<", datetime_to))
            # --- MODIFIED LOGIC END ---

            res[query.name] = self._fetch_query_result(query, model, domain)

        return res

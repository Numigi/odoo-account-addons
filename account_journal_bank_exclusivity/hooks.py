# Copyright 2026-today Numigi and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
from collections import defaultdict

_logger = logging.getLogger(__name__)


def post_init_hook(env):
    duplicates = _collect_duplicates(env)
    if not any(duplicates.values()):
        return

    _log_duplicates(duplicates)
    _notify_admin(env, duplicates)


def _collect_duplicates(env):
    return {
        "default_account": _find_duplicate_default_accounts(env),
        "payment_method_account": _find_duplicate_payment_method_accounts(env),
        "suspense_account": _find_duplicate_suspense_accounts(env),
    }


def _find_duplicate_default_accounts(env):
    journals = env["account.journal"].search(
        [("type", "=", "bank"), ("default_account_id", "!=", False)]
    )
    grouped = defaultdict(list)
    for journal in journals:
        grouped[journal.default_account_id].append(journal)
    return {acc: js for acc, js in grouped.items() if len(js) > 1}


def _find_duplicate_payment_method_accounts(env):
    lines = env["account.payment.method.line"].search(
        [
            ("journal_id.type", "=", "bank"),
            ("payment_account_id", "!=", False),
        ]
    )
    grouped = defaultdict(list)
    for line in lines:
        grouped[line.payment_account_id].append(line)
    return {
        acc: ls
        for acc, ls in grouped.items()
        if len({rec.journal_id for rec in ls}) > 1
    }


def _find_duplicate_suspense_accounts(env):
    journals = env["account.journal"].search(
        [
            ("type", "=", "bank"),
            ("reconcile_mode", "=", "keep"),
            ("suspense_account_id", "!=", False),
        ]
    )
    grouped = defaultdict(list)
    for journal in journals:
        grouped[journal.suspense_account_id].append(journal)
    return {acc: js for acc, js in grouped.items() if len(js) > 1}


def _log_duplicates(duplicates):
    for account, journals in duplicates["default_account"].items():
        names = ", ".join(j.display_name for j in journals)
        _logger.warning(
            "account_journal_bank_exclusivity: default account %s is shared "
            "by bank journals: %s",
            account.code,
            names,
        )
    for account, lines in duplicates["payment_method_account"].items():
        names = ", ".join(sorted({rec.journal_id.display_name for rec in lines}))
        _logger.warning(
            "account_journal_bank_exclusivity: payment account %s is used in "
            "multiple bank journals: %s",
            account.code,
            names,
        )
    for account, journals in duplicates["suspense_account"].items():
        names = ", ".join(j.display_name for j in journals)
        _logger.warning(
            "account_journal_bank_exclusivity: suspense account %s is shared "
            "by keep-mode bank journals: %s",
            account.code,
            names,
        )


def _notify_admin(env, duplicates):
    admin_partner = env.ref("base.partner_admin", raise_if_not_found=False)
    if not admin_partner:
        return

    body = _build_notification_body(duplicates)
    env["mail.thread"].message_notify(
        partner_ids=admin_partner.ids,
        subject=env._("Bank journal duplicates detected"),
        body=body,
    )


def _build_notification_body(duplicates):
    sections = []
    sections.append(
        "<p>The module <b>account_journal_bank_exclusivity</b> was installed "
        "while the following duplicates already existed. The constraints will "
        "not be enforced on this legacy data, but new modifications will be "
        "blocked. Please review and rectify:</p>"
    )

    default_dups = duplicates["default_account"]
    if default_dups:
        sections.append(
            "<p><b>Bank journals sharing the same default account:</b></p><ul>"
        )
        for account, journals in default_dups.items():
            names = ", ".join(j.display_name for j in journals)
            sections.append(f"<li>{account.code} — {names}</li>")
        sections.append("</ul>")

    payment_dups = duplicates["payment_method_account"]
    if payment_dups:
        sections.append(
            "<p><b>Payment accounts used in multiple bank journals:</b></p><ul>"
        )
        for account, lines in payment_dups.items():
            names = ", ".join(sorted({rec.journal_id.display_name for rec in lines}))
            sections.append(f"<li>{account.code} — {names}</li>")
        sections.append("</ul>")

    suspense_dups = duplicates["suspense_account"]
    if suspense_dups:
        sections.append(
            "<p><b>Suspense accounts shared by keep-mode bank journals:</b></p><ul>"
        )
        for account, journals in suspense_dups.items():
            names = ", ".join(j.display_name for j in journals)
            sections.append(f"<li>{account.code} — {names}</li>")
        sections.append("</ul>")

    return "".join(sections)

# Copyright 2024-today Numigi and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models


class AccountBankStatementLine(models.Model):
    _inherit = "account.bank.statement.line"

    def _get_new_ids(self, data):
        result = {}
        for key, value in data.items():
            key_number = key.origin
            result[key_number] = value
        return result

    def _compute_running_balance(self):
        self.statement_id.flush_model(['balance_start', 'first_line_index'])
        self.flush_model(['internal_index', 'date', 'journal_id', 'statement_id',
                          'amount', 'state'])
        record_by_id = {x.id: x for x in self}
        for journal in self.journal_id:
            journal_lines_indexes = self.filtered(
                lambda line: line.journal_id == journal).sorted('internal_index')\
                .mapped('internal_index')
            min_index, max_index = journal_lines_indexes[0], journal_lines_indexes[-1]

            # Find the oldest index for each journal.
            self._cr.execute(
                """
                    SELECT first_line_index, COALESCE(balance_start, 0.0)
                    FROM account_bank_statement
                    WHERE
                        first_line_index < %s
                        AND journal_id = %s
                    ORDER BY first_line_index DESC
                    LIMIT 1
                """,
                [min_index, journal.id],
            )
            current_running_balance = 0.0
            extra_clause = ''
            extra_params = []
            row = self._cr.fetchone()
            if row:
                starting_index, current_running_balance = row
                extra_clause = "AND st_line.internal_index >= %s"
                extra_params.append(starting_index)

            self._cr.execute(
                f"""
                    SELECT
                        st_line.id,
                        st_line.amount,
                        st.first_line_index = st_line.internal_index AS is_anchor,
                        COALESCE(st.balance_start, 0.0),
                        move.state
                    FROM account_bank_statement_line st_line
                    JOIN account_move move ON move.id = st_line.move_id
                    LEFT JOIN account_bank_statement st ON st.id = st_line.statement_id
                    WHERE
                        st_line.internal_index <= %s
                        AND move.journal_id = %s
                        {extra_clause}
                    ORDER BY st_line.internal_index
                """,
                [max_index, journal.id] + extra_params,
            )
            for st_line_id, amount, is_anchor, balance_start, state\
                    in self._cr.fetchall():
                if is_anchor:
                    current_running_balance = balance_start
                if state == 'posted':
                    current_running_balance += amount
                if record_by_id.get(st_line_id):
                    record_by_id[st_line_id].running_balance = current_running_balance
                else:
                    new_ids = self._get_new_ids(record_by_id)
                    if new_ids.get(st_line_id):
                        new_ids[st_line_id].running_balance = current_running_balance

# © Numigi (tm) and all its contributors (https://numigi.com/r/home)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from dataclasses import dataclass, field


@dataclass
class BankStatementError:
    msg: str
    args: list = field(default_factory=lambda: [])
    kwargs: dict = field(default_factory=lambda: {})


def is_bank_statement_error(value):
    return isinstance(value, BankStatementError)

# Copyright 2026-today Numigi and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

"""Initialize the account_move_secure module."""

from . import models


def post_init_hook(env):
    resequence_action = env.ref(
        "account.action_account_resequence", raise_if_not_found=False
    )
    if resequence_action:
        resequence_action.write({"binding_model_id": False})

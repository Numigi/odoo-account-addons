# © Numigi (tm) and all its contributors (https://numigi.com/r/home)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging
_logger = logging.getLogger(__name__)


def migrate(cr, version):
    """
    This script runs BEFORE the model update by the ORM.
    It pre-creates the column to avoid the "column does not exist" error
    when the ORM reads res.partner prematurely.
    """
    _logger.info("START PRE-MIGRATION: Checking/Creating column "
                 "'payment_email_id' in 'res_partner'...")

    cr.execute("ALTER TABLE res_partner ADD COLUMN IF NOT EXISTS payment_email_id integer;")

    _logger.info("END PRE-MIGRATION: Column 'payment_email_id' is ready for the ORM.")

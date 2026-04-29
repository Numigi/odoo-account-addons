# © Numigi (tm) and all its contributors (https://numigi.com/r/home)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
def migrate(cr, version):
    """
    This script runs BEFORE the model is updated by the ORM.
    It pre-creates the column to avoid the “column does not exist” error
    when the ORM reads res.partner prematurely.
    """
    cr.execute("ALTER TABLE res_partner ADD COLUMN IF NOT EXISTS payment_email_id integer;")
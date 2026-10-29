from odoo import SUPERUSER_ID, api


def migrate(cr, version):
    """Corrige la cuenta de base de retención creada fuera de balance.

    La versión 18.0.2.1.0 creó la cuenta 910101 como "fuera de balance",
    lo que impide registrar pagos con retención.

    :param cr: cursor de base de datos.
    :param version: versión instalada antes de la actualización.
    """
    env = api.Environment(cr, SUPERUSER_ID, {})
    env['account.tax']._g7_setup_withholding()

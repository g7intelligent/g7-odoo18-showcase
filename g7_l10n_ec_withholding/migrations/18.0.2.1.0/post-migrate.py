from odoo import SUPERUSER_ID, api


def migrate(cr, version):
    """Aplica en bases existentes el uso compras/ventas y la cuenta de base.

    Las bases instaladas con 18.0.2.0.0 tienen las retenciones con uso
    "ninguno", por lo que no aparecen en la ventana de pago.

    :param cr: cursor de base de datos.
    :param version: versión instalada antes de la actualización.
    """
    env = api.Environment(cr, SUPERUSER_ID, {})
    env['account.tax']._g7_setup_withholding()

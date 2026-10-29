from odoo import SUPERUSER_ID, api


def migrate(cr, version):
    """Asigna uso a las retenciones que quedaron en "ninguno" por nombre duplicado.

    En 18.0.2.1.0 y 18.0.2.1.1, la retención de renta "10% WTH" de ventas
    no pudo cambiar de uso porque la de IVA del 10% tiene el mismo nombre.

    :param cr: cursor de base de datos.
    :param version: versión instalada antes de la actualización.
    """
    env = api.Environment(cr, SUPERUSER_ID, {})
    env['account.tax']._g7_setup_withholding()

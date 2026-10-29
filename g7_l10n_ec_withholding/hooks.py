def post_init_hook(env):
    """Configura las retenciones de las compañías que ya existen.

    Las compañías creadas después se configuran al cargar el plan
    contable de Ecuador (ver ``account.chart.template._post_load_data``).

    :param env: entorno de Odoo provisto por el instalador.
    """
    env['account.tax']._g7_setup_withholding()

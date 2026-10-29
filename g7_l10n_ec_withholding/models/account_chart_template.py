from odoo import models


class AccountChartTemplate(models.AbstractModel):
    _inherit = 'account.chart.template'

    # ------------------------------------------------------
    # DEFAULT METHODS
    # ------------------------------------------------------

    # ------------------------------------------------------
    # COMPUTE AND INVERSE METHODS
    # ------------------------------------------------------

    # ------------------------------------------------------
    # SELECTION METHODS
    # ------------------------------------------------------

    # ------------------------------------------------------
    # CONSTRAINTS AND VALIDATIONS
    # ------------------------------------------------------

    # ------------------------------------------------------
    # ONCHANGE METHODS
    # ------------------------------------------------------

    # ------------------------------------------------------
    # CRUD METHODS
    # ------------------------------------------------------

    # ------------------------------------------------------
    # ACTIONS
    # ------------------------------------------------------

    # ------------------------------------------------------
    # OTHER BUSINESS METHODS
    # ------------------------------------------------------

    def _post_load_data(self, template_code, company, template_data):
        """Configura las retenciones al cargar el plan contable de Ecuador.

        Cubre las compañías creadas después de instalar el módulo, a las
        que no llega el ``post_init_hook``.

        :param template_code: código del plan contable que se cargó.
        :param company: compañía en la que se cargó el plan.
        :param template_data: datos del plan, según ``super()``.
        :return: resultado de ``super()``.
        """
        result = super()._post_load_data(template_code, company, template_data)
        if template_code == 'ec':
            self.env['account.tax']._g7_setup_withholding(company)
        return result

    # ------------------------------------------------------
    # COLUMNS
    # ------------------------------------------------------

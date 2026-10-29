import logging

from odoo import api, models
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)

# Subtipo de grupo de impuesto de l10n_ec -> uso del impuesto en el pago.
# Retenciones que PET SMILE hace a proveedores: compras.
# Retenciones que los clientes le hacen a la empresa: ventas.
WITHHOLDING_TAX_USE = {
    'withhold_vat_purchase': 'purchase',
    'withhold_income_purchase': 'purchase',
    'withhold_vat_sale': 'sale',
    'withhold_income_sale': 'sale',
}
WITHHOLDING_TAX_TYPES = tuple(WITHHOLDING_TAX_USE)

# Sufijo para distinguir retenciones con el mismo nombre base (en inglés).
# l10n_ec nombra "10% WTH" tanto la retención de IVA como la de renta del 10%.
WITHHOLDING_NAME_SUFFIX = {
    'withhold_vat_purchase': 'VAT',
    'withhold_vat_sale': 'VAT',
    'withhold_income_purchase': 'Income',
    'withhold_income_sale': 'Income',
}


class AccountTax(models.Model):
    _inherit = 'account.tax'

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

    @api.model
    def _g7_setup_withholding(self, companies=None):
        """Deja las retenciones de l10n_ec listas para usarse en los pagos.

        Punto de entrada único: lo usan la instalación, la migración y la
        carga del plan contable en compañías nuevas.

        :param companies: compañías a configurar; si se omite, todas las que
            tienen el plan contable de Ecuador.
        """
        companies = companies or self.env['res.company'].search([('chart_template', '=', 'ec')])
        self._g7_enable_withholding_on_payment(companies)
        self._g7_set_withholding_tax_use(companies)
        for company in companies:
            company._g7_setup_withholding_base_account()

    @api.model
    def _g7_enable_withholding_on_payment(self, companies=None):
        """Marca los impuestos de retención de l10n_ec para retenerse en el pago.

        Identifica las retenciones por el subtipo del grupo de impuesto
        (``l10n_ec_type``) y no por el signo del monto.

        :param companies: compañías a configurar; si se omite, todas.
        :return: impuestos que se modificaron.
        """
        domain = [
            ('tax_group_id.l10n_ec_type', 'in', WITHHOLDING_TAX_TYPES),
            ('is_withholding_tax_on_payment', '=', False),
        ]
        if companies:
            domain.append(('company_id', 'in', companies.ids))
        taxes = self.with_context(active_test=False).search(domain)
        taxes.write({'is_withholding_tax_on_payment': True})
        _logger.info(
            '[G7_EC_WITHHOLDING] %d impuestos de retención activados en compañías %s.',
            len(taxes), taxes.company_id.ids,
        )
        return taxes

    @api.model
    def _g7_set_withholding_tax_use(self, companies=None):
        """Asigna compras o ventas a cada retención según su grupo.

        l10n_ec crea las retenciones con uso "ninguno", y el motor de
        retención en pagos solo ofrece las de compras (al pagar) o las de
        ventas (al cobrar). Se cambia impuesto por impuesto: si alguno no se
        puede modificar (por ejemplo, porque ya se usó), se registra y se
        continúa con los demás.

        :param companies: compañías a configurar; si se omite, todas.
        :return: impuestos que se modificaron.
        """
        domain = [
            ('tax_group_id.l10n_ec_type', 'in', WITHHOLDING_TAX_TYPES),
            ('type_tax_use', '=', 'none'),
        ]
        if companies:
            domain.append(('company_id', 'in', companies.ids))
        changed = self.browse()
        for tax in self.with_context(active_test=False).search(domain):
            tax_use = WITHHOLDING_TAX_USE[tax.tax_group_id.l10n_ec_type]
            tax._g7_make_name_unique(tax_use)
            if tax._g7_try_set_tax_use(tax_use):
                changed |= tax
        _logger.info('[G7_EC_WITHHOLDING] %d retenciones con uso compras/ventas asignado.', len(changed))
        return changed

    def _g7_make_name_unique(self, tax_use):
        """Evita el choque de nombres antes de cambiar el uso del impuesto.

        Odoo no permite dos impuestos con el mismo nombre y uso en una
        compañía. Si el nombre base (inglés) ya lo usa otra retención con el
        uso destino, se le agrega el tipo ("VAT" o "Income"). Los nombres
        traducidos que ve el usuario no cambian.

        :param tax_use: uso que se le va a asignar ('purchase' o 'sale').
        """
        self.ensure_one()
        tax_en = self.with_context(lang='en_US')
        duplicate = self.with_context(active_test=False, lang='en_US').search([
            ('id', '!=', self.id),
            ('company_id', '=', self.company_id.id),
            ('type_tax_use', '=', tax_use),
            ('name', '=', tax_en.name),
        ], limit=1)
        if not duplicate:
            return
        old_name = tax_en.name
        tax_en.name = f'{old_name} ({WITHHOLDING_NAME_SUFFIX[self.tax_group_id.l10n_ec_type]})'
        _logger.info(
            '[G7_EC_WITHHOLDING] Impuesto %s renombrado de "%s" a "%s" para evitar duplicado.',
            self.id, old_name, tax_en.name,
        )

    def _g7_try_set_tax_use(self, tax_use):
        """Intenta cambiar el uso de un impuesto sin afectar a los demás.

        :param tax_use: 'purchase' o 'sale'.
        :return: True si se cambió, False si Odoo lo impidió.
        """
        self.ensure_one()
        try:
            with self.env.cr.savepoint():
                self.write({'type_tax_use': tax_use})
        except (UserError, ValidationError) as error:
            _logger.warning(
                '[G7_EC_WITHHOLDING] No se pudo asignar uso %s al impuesto %s (%s): %s',
                tax_use, self.id, self.name, error,
            )
            return False
        return True

    # ------------------------------------------------------
    # COLUMNS
    # ------------------------------------------------------

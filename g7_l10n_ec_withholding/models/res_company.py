import logging

from odoo import _, models

_logger = logging.getLogger(__name__)

# Cuenta de control donde el motor de retenciones anota la base de cada
# retención (una vez al débito y otra al crédito: su saldo siempre es cero).
# Debe ser una cuenta de balance: Odoo no permite mezclar cuentas "fuera de
# balance" con cuentas normales en un mismo asiento.
WITHHOLDING_BASE_ACCOUNT_CODE = '910101'
WITHHOLDING_BASE_ACCOUNT_TYPE = 'asset_current'


class ResCompany(models.Model):
    _inherit = 'res.company'

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

    def _g7_setup_withholding_base_account(self):
        """Asigna la cuenta de base de retención, creándola si no existe.

        No reemplaza una cuenta que el usuario ya haya configurado. Corrige
        la cuenta 910101 si una versión anterior la creó fuera de balance.

        :return: account.account asignada.
        """
        self.ensure_one()
        self._g7_fix_withholding_base_account_type()
        if self.withholding_tax_base_account_id:
            return self.withholding_tax_base_account_id
        account = self.env['account.account'].search([
            ('company_ids', 'in', self.id),
            ('code', '=', WITHHOLDING_BASE_ACCOUNT_CODE),
        ], limit=1) or self.env['account.account'].create({
            'code': WITHHOLDING_BASE_ACCOUNT_CODE,
            'name': _('Base de retenciones en pagos (control)'),
            'account_type': WITHHOLDING_BASE_ACCOUNT_TYPE,
            'company_ids': [(6, 0, self.ids)],
        })
        self.withholding_tax_base_account_id = account
        _logger.info('[G7_EC_WITHHOLDING] Compañía %s: cuenta de base de retención %s.', self.id, account.code)
        return account

    def _g7_fix_withholding_base_account_type(self):
        """Convierte la cuenta 910101 a cuenta de balance si quedó fuera de balance.

        La versión 18.0.2.1.0 la creó como "fuera de balance", lo que impide
        registrar pagos con retención.
        """
        self.ensure_one()
        account = self.env['account.account'].search([
            ('company_ids', 'in', self.id),
            ('code', '=', WITHHOLDING_BASE_ACCOUNT_CODE),
            ('account_type', '=', 'off_balance'),
        ], limit=1)
        if account:
            account.account_type = WITHHOLDING_BASE_ACCOUNT_TYPE
            _logger.info('[G7_EC_WITHHOLDING] Compañía %s: cuenta %s pasada a cuenta de balance.', self.id, account.code)

    # ------------------------------------------------------
    # COLUMNS
    # ------------------------------------------------------

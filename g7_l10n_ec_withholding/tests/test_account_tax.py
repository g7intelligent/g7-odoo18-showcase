from odoo.tests import tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon
from odoo.addons.g7_l10n_ec_withholding.models.account_tax import WITHHOLDING_TAX_TYPES


@tagged('post_install_l10n', 'post_install', '-at_install')
class TestG7WithholdingTax(AccountTestInvoicingCommon):

    @classmethod
    @AccountTestInvoicingCommon.setup_country('ec')
    def setUpClass(cls):
        """Compañía de Ecuador con plan contable l10n_ec y datos de prueba."""
        super().setUpClass()
        cls.withholding_taxes = cls.env['account.tax'].with_context(active_test=False).search([
            ('company_id', '=', cls.env.company.id),
            ('tax_group_id.l10n_ec_type', 'in', WITHHOLDING_TAX_TYPES),
        ])

    def test_chart_load_enables_withholding(self):
        """Al cargar el plan de Ecuador, todas las retenciones quedan activas en pagos."""
        self.assertTrue(self.withholding_taxes, 'El plan de Ecuador debería traer retenciones.')
        self.assertTrue(all(self.withholding_taxes.mapped('is_withholding_tax_on_payment')))

    def test_vat_taxes_untouched(self):
        """Los impuestos de IVA no se marcan como retención."""
        vat_taxes = self.env['account.tax'].search([
            ('company_id', '=', self.env.company.id),
            ('tax_group_id.l10n_ec_type', 'in', ('vat15', 'zero_vat')),
        ])
        self.assertFalse(any(vat_taxes.mapped('is_withholding_tax_on_payment')))

    def test_enable_is_idempotent(self):
        """Ejecutar la activación dos veces no modifica impuestos ya activos."""
        changed = self.env['account.tax']._g7_enable_withholding_on_payment(self.env.company)
        self.assertFalse(changed)

    def test_purchase_withholdings_use_purchase(self):
        """Las retenciones que se hacen a proveedores quedan con uso compras."""
        taxes = self.withholding_taxes.filtered(
            lambda tax: tax.tax_group_id.l10n_ec_type in ('withhold_vat_purchase', 'withhold_income_purchase')
        )
        self.assertTrue(taxes)
        self.assertEqual(set(taxes.mapped('type_tax_use')), {'purchase'})

    def test_sale_withholdings_use_sale(self):
        """Las retenciones que hacen los clientes quedan con uso ventas."""
        taxes = self.withholding_taxes.filtered(
            lambda tax: tax.tax_group_id.l10n_ec_type in ('withhold_vat_sale', 'withhold_income_sale')
        )
        self.assertTrue(taxes)
        self.assertEqual(set(taxes.mapped('type_tax_use')), {'sale'})

    def test_company_has_withholding_base_account(self):
        """La compañía queda con su cuenta de control de base de retención."""
        account = self.env.company.withholding_tax_base_account_id
        self.assertTrue(account)
        self.assertNotEqual(account.account_type, 'off_balance')

    def test_setup_is_idempotent(self):
        """Repetir la configuración no crea cuentas duplicadas ni cambia impuestos."""
        account = self.env.company.withholding_tax_base_account_id
        self.env['account.tax']._g7_setup_withholding(self.env.company)
        self.assertEqual(self.env.company.withholding_tax_base_account_id, account)
        self.assertFalse(self.env['account.tax']._g7_set_withholding_tax_use(self.env.company))

    def test_duplicate_names_resolved(self):
        """Las retenciones del 10% de IVA y de renta en ventas quedan ambas con uso ventas."""
        taxes = self.withholding_taxes.filtered(
            lambda tax: tax.tax_group_id.l10n_ec_type in ('withhold_vat_sale', 'withhold_income_sale')
            and tax.amount == -10.0
        )
        self.assertEqual(len(taxes), 2)
        self.assertEqual(set(taxes.mapped('type_tax_use')), {'sale'})
        self.assertEqual(len(set(taxes.with_context(lang='en_US').mapped('name'))), 2)

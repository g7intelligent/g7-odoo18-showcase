{
    'name': 'G7 Localización Ecuador - Retenciones',
    'version': '18.0.2.1.2',
    'summary': 'Activa las retenciones SRI de l10n_ec en el motor nativo de retención en pagos',
    'description': """
Configura las retenciones Ecuador para el motor nativo de Odoo
(l10n_account_withholding_tax) usando los impuestos de l10n_ec.

No desarrolla lógica propia de retenciones.

Aporta:

- Marca is_withholding_tax_on_payment en los impuestos cuyo grupo es de
  retención (withhold_vat_sale, withhold_vat_purchase,
  withhold_income_sale, withhold_income_purchase).
- Asigna uso compras o ventas a cada retención según su grupo, porque
  el motor de retención en pagos no ofrece las de uso "ninguno".
- Si dos retenciones tienen el mismo nombre base (por ejemplo "10% WTH"
  de IVA y de renta), agrega el tipo al nombre en inglés para que ambas
  puedan usarse; los nombres en español no cambian.
- Crea y asigna la cuenta de control de base de retención (910101),
  como cuenta de balance con saldo siempre en cero.
- Lo aplica al instalar, al actualizar (migraciones 18.0.2.1.0 a 18.0.2.1.2) y cada vez
  que una compañía carga el plan contable de Ecuador.
    """,
    'author': 'G7 Intelligent Solutions',
    'website': 'https://github.com/g7intelligent/g7-odoo18-showcase',
    'category': 'Accounting/Localizations',
    'license': 'LGPL-3',
    'depends': [
        'l10n_account_withholding_tax',
        'g7_l10n_ec_base',
    ],
    'data': [],
    'installable': True,
    'application': False,
    'auto_install': False,
    'post_init_hook': 'post_init_hook',
}

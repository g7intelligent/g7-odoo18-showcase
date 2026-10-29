# G7 Odoo 18 Showcase

Módulo de muestra de **G7 Intelligent Solutions**: localización ecuatoriana para **Odoo 18 Community**.

## g7_l10n_ec_withholding — Retenciones SRI en pagos

Activa las retenciones de IVA y renta de `l10n_ec` en el motor nativo de retención en pagos de Odoo 18 (`l10n_account_withholding_tax`). No reimplementa lógica de retenciones: configura correctamente lo que ya existe en el core.

### Problema que resuelve

Con `l10n_ec` instalado, las retenciones de Ecuador no aparecen al registrar un pago:

- Vienen con uso de impuesto **"ninguno"**, y el motor de retención en pagos solo ofrece impuestos de compras o ventas.
- Existen retenciones con el mismo nombre (por ejemplo, **"10% WTH"** de IVA y de renta), lo que genera conflictos.
- Falta la cuenta de control para la base de retención.

### Qué hace

- Marca `is_withholding_tax_on_payment` en los impuestos de los grupos de retención (`withhold_vat_sale`, `withhold_vat_purchase`, `withhold_income_sale`, `withhold_income_purchase`).
- Asigna el uso compras o ventas a cada retención según su grupo.
- Resuelve los nombres duplicados agregando el tipo al nombre en inglés, sin cambiar los nombres en español.
- Crea y asigna la cuenta de control **910101** (cuenta de balance, con saldo siempre en cero).
- Aplica la configuración al instalar, al actualizar y cada vez que una compañía carga el plan contable de Ecuador.

### Aspectos técnicos

- **Migraciones versionadas** (`18.0.2.1.0` → `18.0.2.1.2`) con scripts `post-migrate` para bases existentes.
- **`post_init_hook`** y extensión de `account.chart.template` para compañías nuevas.
- **Tests automatizados** en `tests/test_account_tax.py`.
- Normas de código propias: docstrings obligatorios, métodos cortos, sin valores de negocio fijos en el código y logging con prefijo por módulo.

### Dependencias

- `l10n_account_withholding_tax` (Odoo 18 core)
- `g7_l10n_ec_base` (módulo base de la suite G7, no incluido en este repositorio de muestra)

### Ejecutar los tests

```bash
odoo -d <base> -i g7_l10n_ec_withholding --test-enable \
  --test-tags /g7_l10n_ec_withholding --stop-after-init
```

## Sobre G7 Intelligent Solutions

Suite de localización ecuatoriana para Odoo 18 Community (retenciones, ATS, facturación electrónica SRI y estados financieros), además de soluciones de IA para PYMES.

**Autor:** Wladimir Gualoto Alvaro — Quito, Ecuador

## Licencia

LGPL-3

# 📋 Importador de Comprobantes Contables - Modelo SIIGO

Módulo para importar, validar y procesar comprobantes contables según el modelo de importación de SIIGO.

## 📊 Estructura del Archivo

El archivo Excel debe tener una hoja llamada **"Datos"** con las siguientes **27 columnas**:

| # | Columna | Tipo | Descripción | Requerido |
|---|---------|------|-------------|-----------|
| 1 | Tipo de comprobante | Texto | ND, NC, FV, FC, REC, CHQ, TR | ✅ Sí |
| 2 | Consecutivo comprobante | Texto | Número único del comprobante | ✅ Sí |
| 3 | Fecha de elaboración | Fecha | YYYY-MM-DD | ✅ Sí |
| 4 | Sigla moneda | Texto | COP, USD, EUR, etc. | ✅ Sí |
| 5 | Tasa de cambio | Número | Ej: 1.0, 4200.50 | ⚠️ Opcional |
| 6 | Código cuenta contable | Texto | Ej: 1105, 2205, 5105 | ✅ Sí |
| 7 | Identificación tercero | Texto | CC, NIT del cliente/proveedor | ⚠️ Opcional |
| 8 | Sucursal | Texto | Código de sucursal | ⚠️ Opcional |
| 9 | Código producto | Texto | Código del producto | ⚠️ Opcional |
| 10 | Código de bodega | Texto | Código de bodega | ⚠️ Opcional |
| 11 | Acción | Texto | Compra, Venta, Movimiento | ⚠️ Opcional |
| 12 | Cantidad producto | Número | Cantidad en unidades | ⚠️ Opcional |
| 13 | Prefijo | Texto | Prefijo de factura | ⚠️ Opcional |
| 14 | Consecutivo | Número | Consecutivo de factura | ⚠️ Opcional |
| 15 | No. cuota | Número | Número de cuota (si aplica) | ⚠️ Opcional |
| 16 | Fecha vencimiento | Fecha | YYYY-MM-DD | ⚠️ Opcional |
| 17 | Código impuesto | Texto | IVA, RETENCION, etc. | ⚠️ Opcional |
| 18 | Código grupo activo fijo | Texto | Grupo de activo fijo | ⚠️ Opcional |
| 19 | Código activo fijo | Texto | Código del activo fijo | ⚠️ Opcional |
| 20 | Descripción | Texto | Descripción del movimiento | ✅ Sí |
| 21 | Código centro/subcentro de costos | Texto | Centro de costos | ⚠️ Opcional |
| 22 | Débito | Número | Valor en débito | ✅ Sí |
| 23 | Crédito | Número | Valor en crédito | ✅ Sí |
| 24 | Observaciones | Texto | Notas adicionales | ⚠️ Opcional |
| 25 | Base gravable libro compras/ventas | Número | Base para libro | ⚠️ Opcional |
| 26 | Base exenta libro compras/ventas | Texto | Base exenta | ⚠️ Opcional |
| 27 | Mes de cierre | Texto | MM/YYYY | ⚠️ Opcional |

## 🔧 Tipos de Comprobante

```
ND  → Nota Débito
NC  → Nota Crédito
FV  → Factura Venta
FC  → Factura Compra
REC → Recibo
CHQ → Cheque
TR  → Traslado
```

## ✅ Validaciones

El sistema realiza las siguientes validaciones:

1. **Estructura**: Verifica que todas las columnas estén presentes
2. **Tipos de datos**: Convierte fechas, números y valores monetarios
3. **Comprobantes**: Valida que tengan tipo de comprobante válido
4. **Cuentas**: Verifica que cada línea tenga cuenta contable
5. **Balance**: Débitos = Créditos por comprobante
6. **Montos**: Cada línea debe tener débito O crédito
7. **Fechas**: Valida formato de fechas

## 📤 Salidas Generadas

### 1. Excel Validado
- **Hoja Comprobantes**: Todos los comprobantes importados
- **Hoja Validacion**: Balance contable y errores
- **Hoja Por Cuenta**: Agrupado por cuenta contable
- **Hoja Por Tercero**: Agrupado por tercero

### 2. Plano SIIGO (TXT)
Formato:
```
01;1105;1020304050;Descripción;2500000.00;D
01;1105;1020304050;Descripción;2500000.00;C
```

Campos:
- Tipo de movimiento (01)
- Cuenta contable
- Documento
- Descripción
- Valor
- Naturaleza (D=Débito, C=Crédito)

## 📋 Ejemplo de Uso

### Via Python

```python
from comprobantes_contables import (
    importar_comprobantes,
    validar_comprobantes,
    generar_resumen_comprobantes,
    generar_excel_comprobantes,
    generar_plano_siigo_desde_comprobantes
)

# 1. Importar
df, error = importar_comprobantes("comprobantes.xlsx")
if error:
    print(f"Error: {error}")
    exit()

# 2. Validar
validaciones = validar_comprobantes(df)
print(f"Balance: ${validaciones['balance']['total_debitos']:,.2f}")
print(f"Estado: {'Balanceado ✅' if validaciones['balance']['balanceado'] else 'Desbalanceado ❌'}")

# 3. Ver resumen
resumen = generar_resumen_comprobantes(df)
print(resumen)

# 4. Exportar Excel
generar_excel_comprobantes(df, "comprobantes_validados.xlsx")

# 5. Generar plano SIIGO
generar_plano_siigo_desde_comprobantes(df, "plano_siigo.txt")
```

### Via Web (Streamlit)

1. Abre http://localhost:8501
2. Ve a la pestaña "📋 Comprobantes"
3. Carga tu archivo Excel
4. Click en "🔍 Procesar Comprobantes"
5. Revisa validaciones
6. Descarga Excel validado o Plano SIIGO

## 🎯 Casos de Uso

### Caso 1: Importación de Facturas de Compra
```
Tipo: FC (Factura Compra)
Consecutivo: FAC-2024-001
Cuenta: 2205 (Cuentas por Pagar)
Débito: 0
Crédito: 1000000
```

### Caso 2: Nota Crédito
```
Tipo: NC (Nota Crédito)
Consecutivo: NC-2024-001
Cuenta: 1105 (Bancos)
Débito: 500000
Crédito: 0
```

### Caso 3: Traslado de Mercancía
```
Tipo: TR (Traslado)
Consecutivo: TR-2024-001
Cuenta Origen: 1110
Cuenta Destino: 1120
Débito/Crédito: Según movimiento
```

## 🔍 Errores Comunes

### Error: "Columnas faltantes"
**Solución**: Verifica que el archivo tenga la hoja "Datos" con todas las 27 columnas.

### Error: "Comprobantes desbalanceados"
**Solución**: Asegúrate de que para cada comprobante, Débitos = Créditos.

### Error: "Tipo de comprobante inválido"
**Solución**: Usa solo los tipos válidos: ND, NC, FV, FC, REC, CHQ, TR.

### Error: "Sin código de cuenta"
**Solución**: Cada línea debe tener un "Código cuenta contable" válido.

## 📊 Métricas Generadas

- ✅ Total de comprobantes procesados
- ✅ Total débitos
- ✅ Total créditos
- ✅ Diferencia (debe ser 0)
- ✅ Movimientos por cuenta
- ✅ Movimientos por tercero
- ✅ Distribución por tipo de comprobante

## 🔐 Integridad de Datos

El sistema garantiza:
- ✅ Balance contable (Débitos = Créditos)
- ✅ Validación de tipos de datos
- ✅ Detección de duplicados
- ✅ Integridad referencial
- ✅ Trazabilidad completa

---

**Versión**: 1.0  
**Compatible con**: SIIGO 8.0+  
**Formatos soportados**: .xlsx  

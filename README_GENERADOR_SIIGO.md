# 🧮 Generador de Plano SIIGO - Documentación de Uso

Generador completo y validado de archivos de comprobantes contables compatibles con SIIGO.

---

## 📋 Contenido

- `generador_plano_siigo_corregido.py` - Código principal (982 líneas)
- `CAMBIOS_GENERADOR_SIIGO.md` - Detalle de 12 cambios aplicados
- `MODELO_COMPROBANTES_CONTABLES.md` - Estructura del modelo SIIGO

---

## 🚀 Instalación Rápida

```bash
# 1. Instalar dependencias
pip install pandas openpyxl

# 2. Importar módulo
from generador_plano_siigo_corregido import (
    SiigoConfig,
    construir_plano_siigo,
    validar_plano_siigo,
    exportar_plano_siigo
)
```

---

## 💻 Uso Básico

### Paso 1: Crear datos de entrada

```python
import pandas as pd

movimientos = pd.DataFrame([
    {
        "Tipo de comprobante": "FC",  # Factura Compra
        "Consecutivo comprobante": "COM-001",
        "Fecha de elaboración": "2026-06-14",
        "Sigla moneda": "COP",
        "Tasa de cambio": "",
        "Código cuenta contable": "2205",
        "Identificación tercero": "800123456",
        "Sucursal": "BOGOTA",
        "Código producto": "",
        "Código de bodega": "",
        "Acción": "",
        "Cantidad producto": "",
        "Prefijo": "PUP",
        "Consecutivo": "1001",
        "No. cuota": "1",
        "Fecha vencimiento": "2026-07-14",
        "Código impuesto": "IVA",
        "Código grupo activo fijo": "",
        "Código activo fijo": "",
        "Descripción": "Factura de compra",
        "Código centro/subcentro de costos": "1-1",
        "Débito": "",
        "Crédito": "5000000.00",
        "Observaciones": "Ejemplo",
        "Base gravable libro compras/ventas": "5000000.00",
        "Base exenta libro compras/ventas": "",
        "Mes de cierre": "NO",
    },
])
```

### Paso 2: Configurar reglas condicionales

```python
config = SiigoConfig(
    moneda_local="COP",
    
    # Cuentas que necesitan inventario
    cuentas_inventario={"143505", "143510"},
    
    # Cuentas que necesitan vencimiento
    cuentas_vencimiento={"130505", "220505"},
    
    # Cuentas que necesitan impuesto
    cuentas_impuesto={"240805"},
    
    # Cuentas que necesitan activos fijos
    cuentas_activo_fijo={"152405"},
)
```

### Paso 3: Construir plano

```python
plano = construir_plano_siigo(movimientos, config=config)
# Resultado: DataFrame con 27 columnas normalizadas
```

### Paso 4: Validar

```python
plano_validado, errores = validar_plano_siigo(plano, config=config)

# Ver errores
if not errores.empty:
    print(errores)
else:
    print("✅ Sin errores")
```

### Paso 5: Exportar

```python
archivo = exportar_plano_siigo(
    df_plano=plano_validado,
    df_errores=errores,
    ruta_excel="plano_siigo.xlsx",
    ruta_csv="plano_siigo.csv"
)
```

---

## 📊 Estructura de 27 Columnas

| # | Columna | Tipo | Obligatorio | Ejemplo |
|---|---------|------|-------------|---------|
| 1 | Tipo de comprobante | Texto (3) | ✅ | FC |
| 2 | Consecutivo comprobante | Texto (20) | ✅ | COM-001 |
| 3 | Fecha de elaboración | DD/MM/AAAA | ✅ | 14/06/2026 |
| 4 | Sigla moneda | Texto (3) | ✅ | COP |
| 5 | Tasa de cambio | Decimal (5.9) | ⚠️ | 1.000000000 |
| 6 | Código cuenta contable | Texto (10) | ✅ | 2205 |
| 7 | Identificación tercero | Texto (15) | ✅ | 800123456 |
| 8 | Sucursal | Texto (10) | ⚠️ | BOGOTA |
| 9 | Código producto | Texto (15) | ⚠️ | PROD-001 |
| 10 | Código de bodega | Texto (10) | ⚠️ | BOD-01 |
| 11 | Acción | Texto (15) | ⚠️ | Compra |
| 12 | Cantidad producto | Decimal (11.2) | ⚠️ | 10.00 |
| 13 | Prefijo | Texto (6) | ⚠️ | PUP |
| 14 | Consecutivo | Texto (10) | ⚠️ | 1001 |
| 15 | No. cuota | Decimal (3) | ⚠️ | 1 |
| 16 | Fecha vencimiento | DD/MM/AAAA | ⚠️ | 14/07/2026 |
| 17 | Código impuesto | Texto (10) | ⚠️ | IVA |
| 18 | Código grupo activo fijo | Texto (10) | ⚠️ | |
| 19 | Código activo fijo | Texto (15) | ⚠️ | |
| 20 | Descripción | Texto (100) | ✅ | Factura de compra |
| 21 | Código centro/subcentro de costos | Texto (20) | ⚠️ | 1-1 |
| 22 | Débito | Decimal (11.2) | ✅* | 5000000.00 |
| 23 | Crédito | Decimal (11.2) | ✅* | |
| 24 | Observaciones | Texto (300) | ⚠️ | Ejemplo |
| 25 | Base gravable libro compras/ventas | Decimal (11.2) | ⚠️ | 5000000.00 |
| 26 | Base exenta libro compras/ventas | Decimal (11.2) | ⚠️ | |
| 27 | Mes de cierre | SI/NO | ⚠️ | NO |

**Leyenda:**
- ✅ Obligatorio siempre
- ✅* Al menos uno (Débito O Crédito, no ambos)
- ⚠️ Obligatorio según condiciones

---

## 🔍 Validaciones Implementadas

### 1. **Campos Obligatorios Base**
```
✅ Tipo de comprobante (ND, NC, FV, FC, REC, CHQ, TR)
✅ Consecutivo comprobante
✅ Fecha de elaboración (DD/MM/AAAA)
✅ Sigla moneda
✅ Código cuenta contable
✅ Identificación tercero
✅ Descripción
✅ Débito O Crédito (no ambos > 0)
```

### 2. **Validaciones de Formato**
```
✅ Fechas en formato DD/MM/AAAA exacto
✅ Débito/Crédito con 2 decimales exactos
✅ Tasa de cambio con hasta 9 decimales
✅ Números positivos donde corresponde
✅ Longitudes máximas por columna
```

### 3. **Validaciones Condicionales por Tipo de Cuenta**

**Inventario (cuentas_inventario):**
```
✅ Código producto (obligatorio)
✅ Código de bodega (obligatorio)
✅ Acción (obligatoria, debe ser: Compra, Venta, Movimiento, Entrada, Salida)
✅ Cantidad producto (obligatoria, numérica)
```

**Vencimiento (cuentas_vencimiento):**
```
✅ Prefijo (obligatorio)
✅ Consecutivo (obligatorio)
✅ No. cuota (obligatorio, numérico)
✅ Fecha vencimiento (obligatoria, DD/MM/AAAA)
```

**Impuestos (cuentas_impuesto):**
```
✅ Código impuesto (obligatorio)
```

**Activos Fijos (cuentas_activo_fijo):**
```
✅ Código grupo activo fijo (obligatorio)
✅ Código activo fijo (obligatorio)
```

### 4. **Validaciones Transversales**
```
✅ No puede haber Débito y Crédito > 0 en la misma línea
✅ Tasa de cambio debe ser consistente dentro del mismo comprobante
✅ Todas las líneas del comprobante deben usar la misma moneda
✅ Mes de cierre debe ser SI o NO
```

### 5. **Validaciones Numéricas**
```
✅ Débito/Crédito: máximo 11 enteros, 2 decimales
✅ Tasa de cambio: máximo 5 enteros, 9 decimales
✅ Bases: máximo 11 enteros, 2 decimales
✅ Cantidad: máximo 11 enteros, 2 decimales
✅ Tasa > 0 si moneda diferente a COP
```

---

## 🚨 Tipos de Comprobante Válidos

```python
TIPOS_COMPROBANTE_VALIDOS = {
    "ND": "Nota Débito",
    "NC": "Nota Crédito",
    "FV": "Factura Venta",
    "FC": "Factura Compra",
    "REC": "Recibo",
    "CHQ": "Cheque",
    "TR": "Traslado",
}
```

---

## 📤 Salida: Archivo Excel

El archivo generado contiene 2 hojas:

### Hoja 1: **Plano**
Contiene todos los comprobantes con las 27 columnas del modelo.

### Hoja 2: **Errores**
Contiene los errores encontrados con estructura:
```
| fila | columna | error | valor |
|------|---------|-------|-------|
| 2 | Tipo de comprobante | Tipo no válido | XX |
```

Si no hay errores:
```
| Mensaje |
|---------|
| ✅ No se encontraron errores |
```

---

## 🔧 Personalización

### Cambiar longitudes máximas

```python
config = SiigoConfig(
    max_descripcion=150,  # Aumentar a 150 caracteres
    max_observaciones=500,  # Aumentar a 500 caracteres
)
```

### Agregar cuentas condicionales

```python
config = SiigoConfig(
    cuentas_inventario={"143505", "143510", "143515"},  # Agregar más
    cuentas_vencimiento={"130505", "220505", "220510"},
)
```

### Cambiar moneda local

```python
config = SiigoConfig(
    moneda_local="USD",  # Si la empresa maneja USD
)
```

---

## 🧪 Testing

```python
# Ejecutar archivo directamente
python generador_plano_siigo_corregido.py

# Salida esperada:
# ================================================================================
# GENERADOR DE PLANO SIIGO - VALIDACIÓN
# ================================================================================
# 
# ✅ Archivo generado: plano_siigo_generado.xlsx
# 📊 Total de filas: 2
# ❌ Total de errores detectados: 0
# 
# ✅ Validación completada sin errores
```

---

## ⚠️ Errores Comunes

### Error: "Tipo no válido"
```
Solución: Usar solo ND, NC, FV, FC, REC, CHQ, TR
```

### Error: "Formato debe ser DD/MM/AAAA"
```
Solución: Convertir fechas al formato exacto DD/MM/AAAA
Ejemplo correcto: "14/06/2026"
Incorrecto: "2026-06-14" o "06/14/2026"
```

### Error: "Debe ser mayor a cero"
```
Solución: Asegurar que Tasa de cambio > 0 si moneda es diferente a COP
```

### Error: "Debe existir Débito o Crédito mayor a cero"
```
Solución: Cada línea debe tener Débito > 0 O Crédito > 0 (no ambos)
```

### Error: "No puede haber Débito y Crédito mayores a cero simultáneamente"
```
Solución: Una línea solo puede tener débito O crédito, no ambos
```

### Error: "No se puede conectar con el backend"
```
Solución: Asegurar que el backend FastAPI esté corriendo en puerto 8000
```

---

## 📚 Integración con Backend

Si usas FastAPI:

```python
from fastapi import UploadFile
from generador_plano_siigo_corregido import (
    construir_plano_siigo,
    validar_plano_siigo,
    exportar_plano_siigo
)

@app.post("/api/generar-plano-siigo")
async def generar_plano(archivo: UploadFile = File(...)):
    df = pd.read_excel(archivo.file)
    config = SiigoConfig()
    
    plano = construir_plano_siigo(df, config)
    plano_validado, errores = validar_plano_siigo(plano, config)
    
    archivo_excel = exportar_plano_siigo(
        plano_validado,
        errores,
        "plano_siigo.xlsx"
    )
    
    return FileResponse(archivo_excel)
```

---

## 📞 Soporte

Para reportar errores o sugerencias, revisar:
- `CAMBIOS_GENERADOR_SIIGO.md` - Detalles técnicos
- `MODELO_COMPROBANTES_CONTABLES.md` - Especificación completa

---

**Versión:** 2.0  
**Última actualización:** 2026-06-14  
**Compatible con:** SIIGO 8.0+

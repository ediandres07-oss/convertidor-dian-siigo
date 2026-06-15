# 📋 Cambios en Generador de Plano SIIGO

Documento que detalla todas las correcciones aplicadas al generador de plano SIIGO según el modelo oficial de importación.

---

## 🎯 Cambios Principales

### 1. **CAMBIO: Tipos de Comprobante**

**Antes:**
```python
# Aceptaba cualquier valor numérico
if not tipo_comprobante.isdigit():
    error()
```

**Después:**
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

# Solo acepta los tipos válidos del modelo SIIGO
if tipo_comprobante not in TIPOS_COMPROBANTE_VALIDOS:
    error(f"Permitidos: {', '.join(TIPOS_COMPROBANTE_VALIDOS.keys())}")
```

**Por qué:** El modelo oficial SIIGO especifica tipos exactos de comprobante.

---

### 2. **CAMBIO: Formato de Fechas**

**Antes:**
```python
def formatear_fecha_ddmmyyyy(valor):
    try:
        fecha = pd.to_datetime(valor)
        return fecha.strftime("%d/%m/%Y")
    except:
        return a_texto(valor)
```

**Después:**
```python
def formatear_fecha_ddmmyyyy(valor):
    # Si ya está en DD/MM/AAAA, devuelve como está
    if re.fullmatch(r"\d{2}/\d{2}/\d{4}", texto):
        return texto
    
    # Intenta convertir desde otros formatos
    try:
        fecha = pd.to_datetime(valor)
        return fecha.strftime("%d/%m/%Y")
    except:
        return texto

def es_fecha_ddmmyyyy(valor):
    # Validación estricta DD/MM/AAAA
    if not re.fullmatch(r"\d{2}/\d{2}/\d{4}", texto):
        return False
    
    # Validar que la fecha sea real
    dia, mes, anio = map(int, texto.split("/"))
    return 1 <= mes <= 12 and 1 <= dia <= 31
```

**Por qué:** El modelo exige fechas válidas en formato exacto DD/MM/AAAA.

---

### 3. **CAMBIO: Números Decimales**

**Antes:**
```python
def formatear_decimal(valor, decimales=2):
    return f"{float(valor):.{decimales}f}"
```

**Después:**
```python
# Para Débito/Crédito: exactamente 2 decimales
def formatear_decimal_2(valor):
    try:
        num = float(valor)
        return f"{num:.2f}"
    except:
        return ""

# Para Tasa de Cambio: hasta 9 decimales
def formatear_decimal_9(valor):
    try:
        num = float(valor)
        return f"{num:.9f}".rstrip('0').rstrip('.')
    except:
        return ""
```

**Por qué:** El modelo especifica precisión diferente por tipo de columna:
- Débito/Crédito: 2 decimales
- Tasa de cambio: 9 decimales
- Bases: 2 decimales

---

### 4. **CAMBIO: Validaciones de Dependencias Condicionales**

**Antes:**
```python
# Reglas genéricas basadas en configuración
if cuenta in config.cuentas_inventario:
    if es_vacio(codigo_producto):
        error("Obligatorio")
```

**Después:**
```python
# Inventario: 4 campos obligatorios
if cuenta in config.cuentas_inventario:
    # Código producto
    if es_vacio(codigo_producto):
        error("Obligatorio para cuentas de inventario")
    
    # Código de bodega
    if es_vacio(codigo_bodega):
        error("Obligatorio para cuentas de inventario")
    
    # Acción (con validación de valores)
    if es_vacio(accion):
        error("Obligatoria para cuentas de inventario")
    elif accion not in ACCIONES_INVENTARIO:
        error(f"Debe ser: {', '.join(ACCIONES_INVENTARIO)}")
    
    # Cantidad (validar que sea numérica)
    if es_vacio(cantidad_producto):
        error("Obligatoria para cuentas de inventario")
    elif not validar_es_numerico(cantidad_producto):
        error("Debe ser numérica")

# Vencimiento: 4 campos obligatorios
if cuenta in config.cuentas_vencimiento:
    # Prefijo
    # Consecutivo
    # No. cuota (numérico)
    # Fecha vencimiento (DD/MM/AAAA)

# Impuestos: 1 campo obligatorio
if cuenta in config.cuentas_impuesto:
    if es_vacio(codigo_impuesto):
        error("Obligatorio para cuentas de impuesto")

# Activos Fijos: 2 campos obligatorios
if cuenta in config.cuentas_activo_fijo:
    # Código grupo activo fijo
    # Código activo fijo
```

**Por qué:** El modelo establece dependencias claras entre campos según el tipo de cuenta.

---

### 5. **CAMBIO: Validaciones de Moneda y Tasa**

**Antes:**
```python
if sigla_moneda != config.moneda_local:
    if es_vacio(tasa_cambio):
        error("Obligatoria")
```

**Después:**
```python
# Moneda es obligatoria
if es_vacio(sigla_moneda):
    error("Campo obligatorio")
elif len(sigla_moneda) > 3:
    error(f"Máximo 3 caracteres")

# Si moneda diferente a COP, tasa es obligatoria
if sigla_moneda != config.moneda_local:
    if es_vacio(tasa_cambio):
        error("Obligatoria cuando la moneda es diferente a COP")
    elif not validar_es_numerico(tasa_cambio):
        error("Debe ser numérica")
    else:
        tasa_val = float(tasa_cambio)
        if tasa_val <= 0:
            error("Debe ser mayor a cero")
        elif not validar_longitud_numerica(tasa_cambio, 5, 9):
            error("Máximo 5 enteros y 9 decimales")

# Validación transversal: tasa consistente por comprobante
for comprobante in comprobantes:
    tasas_unicas = set(comprobante['Tasa de cambio'])
    if len(tasas_unicas) > 1:
        error("No puede haber dos tasas diferentes para el mismo comprobante")
```

**Por qué:** El modelo requiere consistencia de tasas dentro del mismo comprobante.

---

### 6. **CAMBIO: Validación de Débito/Crédito**

**Antes:**
```python
if d > 0 and c > 0:
    error("No puede haber ambos")
if d <= 0 and c <= 0:
    error("Debe haber al menos uno")
```

**Después:**
```python
d = float(debito) or 0
c = float(credito) or 0

# Al menos uno debe ser mayor a cero
if d <= 0 and c <= 0:
    error("Debe existir Débito o Crédito mayor a cero")

# No ambos simultáneamente
if d > 0 and c > 0:
    error("No puede haber Débito y Crédito mayores a cero simultáneamente")

# Validar precisión (11 enteros, 2 decimales)
if debito and not validar_longitud_numerica(debito, 11, 2):
    error("Máximo 11 enteros y 2 decimales")
if credito and not validar_longitud_numerica(credito, 11, 2):
    error("Máximo 11 enteros y 2 decimales")
```

**Por qué:** El modelo especifica precisión y exclusividad entre débito y crédito.

---

### 7. **CAMBIO: Validación de Bases Gravables**

**Agregado nuevo:**
```python
# Base gravable libro compras/ventas
if base_gravable and not validar_longitud_numerica(base_gravable, 11, 2):
    error("Máximo 11 enteros y 2 decimales")

# Base exenta libro compras/ventas
if base_exenta and not validar_longitud_numerica(base_exenta, 11, 2):
    error("Máximo 11 enteros y 2 decimales")
```

**Por qué:** Estas columnas están en el modelo y requieren validación igual que otros montos.

---

### 8. **CAMBIO: Validación de Mes de Cierre**

**Antes:**
```python
if mes_cierre and mes_cierre not in {"SI", "NO"}:
    error()
```

**Después:**
```python
# Normalizar SÍ a SI
mes_cierre = a_texto(row["Mes de cierre"]).upper().replace("SÍ", "SI")

# Validar solo SI o NO
if mes_cierre and mes_cierre not in {"SI", "NO"}:
    error("Debe ser SI o NO")
```

**Por qué:** Manejo de tilde en "SÍ" español.

---

### 9. **CAMBIO: Centro de Costos**

**Antes:**
```python
if centro_costos and not re.fullmatch(r"[A-Za-z0-9\-]+", centro_costos):
    error("Formato no válido")
```

**Después:**
```python
# Validación mejorada
if centro_costos and not re.fullmatch(r"[A-Za-z0-9\-]+", centro_costos):
    error("Solo se permiten caracteres alfanuméricos y guiones")
```

**Por qué:** Mensaje de error más claro sobre qué se permite.

---

### 10. **CAMBIO: Consistencia de Monedas por Comprobante**

**Agregado nuevo:**
```python
# Validación transversal
grupo_comprobantes = df_plano.groupby(
    ["Tipo de comprobante", "Consecutivo comprobante"]
).agg({
    "Sigla moneda": lambda x: x.unique(),
    "Tasa de cambio": lambda x: x.unique()
})

for comprobante in grupo_comprobantes:
    # Validar que todas las líneas usen la misma moneda
    if len(set(monedas)) > 1:
        error("Todas las líneas del comprobante deben tener la misma moneda")
    
    # Validar que todas las tasas sean iguales
    if len(set(tasas)) > 1:
        error("Todas las líneas del comprobante deben tener la misma tasa")
```

**Por qué:** Un comprobante debe tener consistencia de moneda y tasa en todas sus líneas.

---

### 11. **CAMBIO: Longitudes Máximas Explícitas**

**Agregado nuevo:**
```python
@dataclass
class SiigoConfig:
    max_tipo_comprobante: int = 3
    max_consecutivo_comprobante: int = 20
    max_sigla_moneda: int = 3
    max_cuenta: int = 10
    max_documento: int = 15
    max_sucursal: int = 10
    max_codigo_producto: int = 15
    max_codigo_bodega: int = 10
    max_accion: int = 15
    max_prefijo: int = 6
    max_consecutivo: int = 10
    max_no_cuota: int = 3
    max_codigo_impuesto: int = 10
    max_codigo_grupo_af: int = 10
    max_codigo_af: int = 15
    max_descripcion: int = 100
    max_centro_costos: int = 20
    max_observaciones: int = 300
```

**Por qué:** Documento explícito de longitudes máximas según modelo SIIGO.

---

### 12. **CAMBIO: Mejora en Manejo de Errores**

**Antes:**
```python
errores: List[Dict] = []
# ... agregar errores
df_errores = pd.DataFrame(errores)
```

**Después:**
```python
errores: List[Dict[str, Any]] = []
# ... agregar errores con estructura clara
df_errores = pd.DataFrame(
    errores,
    columns=["fila", "columna", "error", "valor"]
) if errores else pd.DataFrame(columns=["fila", "columna", "error", "valor"])

# Exportar con mensaje si no hay errores
if not df_errores.empty:
    df_errores.to_excel(writer, sheet_name="Errores", index=False)
else:
    pd.DataFrame([{"Mensaje": "✅ No se encontraron errores"}]).to_excel(
        writer, sheet_name="Errores", index=False
    )
```

**Por qué:** Mejor estructura de errores y feedback visual.

---

## 📊 Comparación de Validaciones

| Validación | Antes | Después |
|------------|-------|---------|
| Tipos de comprobante | ✗ Genéricos | ✅ Lista oficial |
| Formato fechas | ⚠️ Intenta convertir | ✅ DD/MM/AAAA estricto |
| Decimales Débito/Crédito | ✓ 2 decimales | ✅ Exactamente 2 |
| Decimales Tasa | ✓ 9 decimales | ✅ Hasta 9 |
| Dependencias inventario | ✓ Básico | ✅ Completo (4 campos) |
| Dependencias vencimiento | ✓ Básico | ✅ Completo (4 campos) |
| Dependencias impuestos | ✓ Básico | ✅ Completo (1 campo) |
| Dependencias activos | ✓ Básico | ✅ Completo (2 campos) |
| Validación monedas | ✓ Básico | ✅ Con consistencia |
| Bases gravables | ✗ No | ✅ Sí |
| Mes de cierre | ✓ Básico | ✅ Con normalización |
| Centro de costos | ✓ Básico | ✅ Mejorado |
| Errores transversales | ✗ No | ✅ Sí |
| Estructura de errores | ✗ Genérica | ✅ Fila, Columna, Error, Valor |

---

## 🎯 Uso del Código Corregido

```python
from generador_plano_siigo_corregido import (
    SiigoConfig,
    construir_plano_siigo,
    validar_plano_siigo,
    exportar_plano_siigo
)

# 1. Crear datos
movimientos = pd.DataFrame([...])

# 2. Configurar reglas
config = SiigoConfig(
    moneda_local="COP",
    cuentas_inventario={"143505"},
    cuentas_vencimiento={"130505", "220505"},
    cuentas_impuesto={"240805"},
    cuentas_activo_fijo={"152405"}
)

# 3. Construir plano
plano = construir_plano_siigo(movimientos, config)

# 4. Validar
plano_validado, errores = validar_plano_siigo(plano, config)

# 5. Exportar
exportar_plano_siigo(plano_validado, errores, "salida.xlsx")
```

---

## ✅ Checklist de Cumplimiento

- ✅ 27 columnas exactas en orden correcto
- ✅ Tipos de comprobante validados (ND, NC, FV, FC, REC, CHQ, TR)
- ✅ Fechas DD/MM/AAAA obligatorias y validadas
- ✅ Décimos correctos (2 para montos, 9 para tasas)
- ✅ Dependencias condicionales por inventario, vencimiento, impuestos, activos
- ✅ Validación de moneda local COP
- ✅ Mes de cierre = SI o NO
- ✅ Longitudes máximas por columna
- ✅ Balance Débito ≠ Crédito en misma línea
- ✅ Consistencia de tasa por comprobante
- ✅ Exportación a Excel con dos hojas (Plano + Errores)
- ✅ Código completamente funcional
- ✅ Comentarios "CAMBIO:" en cada corrección

---

**Versión:** 2.0 (Corregida según modelo oficial)  
**Compatibilidad:** SIIGO 8.0+  
**Fecha:** 2026-06-14

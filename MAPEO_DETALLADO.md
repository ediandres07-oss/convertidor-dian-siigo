# Mapeo Detallado: Exógena → Ayuda Renta 2025

## 📊 Resumen de Categorías Encontradas

Del análisis del reporte de Información Exógena 2024 de Elizabeth Giraldo García, se identificaron las siguientes categorías principales:

| # | Categoría Exógena | Valor Total | Registros | Destino Sugerido |
|---|---|---|---|---|
| 1 | **R132 Retenciones año gravable** | $1,362,514 | 10 | Hoja Retenciones |
| 2 | **Tope 2. Patrimonio (CDT)** | $335,626,272 | 1 | Hoja Patrimonio → Inversiones |
| 3 | **Tope 2. Patrimonio bruto (Catastral)** | $69,318,000 | 3 | Hoja Patrimonio → Bienes Raíces |
| 4 | **Tope 2. Patrimonio (Cuentas Bancarias)** | $49,539,342 | 2 | Hoja Efectivo_Bancos_Cuentas |
| 5 | **Tope 1. Ingresos Laborales** | $82,744,800 | 3 | Hoja Salarios_Demas_Pagos_Laborales |
| 6 | **Tope 1. Ingresos de Capital (CDT)** | $33,810,314 | 9 | Hoja Inter_Rend_Finan |
| 7 | **Tope 1. Retiros Pensión Voluntaria** | $4,431,976 | 2 | Hoja Inter_Rend_Finan o Pensiones |
| 8 | **Aportes Pensión** | $7,074,488 | 1 | Hoja AY_PENSIONES |
| 9 | **Aportes Salud** | $1,897,503 | 1 | Hoja Ingresos_No_Constitutivos |
| 10 | **Cesantías** | $3,695,907 | 2 | Hoja cesantias |
| 11 | **Facturas Electrónicas** | $8,128,113 | 1 | Hoja Inter_Rend_Finan o Ventas |
| 12 | **Consumo Tarjeta Crédito/Débito** | $15,666,577 | 3 | Hoja TOPES (para referencia) |
| 13 | **Inversiones Totales (Tope 4)** | $1,297,938,192 | 5 | Hoja Inversiones |
| 14 | **Deudas** | $658,958 | 1 | Hoja Deudas_Moneda_Nacional |

---

## 🎯 Mapeo Configurado en el Script

### 1. RETENCIONES (R132)

**Exógena → Ayuda Renta**

```
Categoría: R132 Retenciones año gravable a declarar
Valor Total: $1,362,514
Detalles:
  • CDT Retención práctica: $1,352,411 (9 registros)
  • Retención retiros pensión voluntaria: $10,103 (1 registro)

Destino:
  Hoja: Retenciones
  Celda: C32 (Total automático)
  Tipo: SUM (se calcula automáticamente)
```

**Nota:** El valor se suma automáticamente en la celda C32 de la hoja Retenciones.

---

### 2. PATRIMONIO - CDTs e Inversiones

**Exógena → Ayuda Renta**

```
Categoría: Tope 2. Patrimonio | R29 Patrimonio bruto
Valor Total: $335,626,272
Detalles:
  • Saldo CDT (Titular Principal): $335,626,272
  
Destino:
  Hoja: Patrimonio
  Celda: D14 (Total Inversiones)
  Tipo: DIRECT (valor directo)
```

**Ubicación en Ayuda Renta:**
- Abre la hoja "Patrimonio"
- Ve a celda D14 (columna D, fila 14)
- Allí se inyectará el valor $335,626,272

---

### 3. PATRIMONIO - Bienes Raíces (Catastral)

**Exógena → Ayuda Renta**

```
Categoría: Tope 2. Patrimonio bruto | R29 Patrimonio bruto
Valor Total: $69,318,000
Detalles:
  • Valor avalúo catastral: $69,318,000 (3 propiedades diferentes)
  
Destino:
  Hoja: Patrimonio
  Celda: D18 (Total Bienes Raíces)
  Tipo: DIRECT (valor directo)
```

**Ubicación en Ayuda Renta:**
- Abre la hoja "Patrimonio"
- Ve a celda D18 (columna D, fila 18)
- Allí se inyectará el valor $69,318,000

---

### 4. CUENTAS BANCARIAS

**Exógena → Ayuda Renta**

```
Categoría: Tope 2. Patrimonio| R29 Patrimonio bruto
Valor Total: $49,539,342
Detalles:
  • Saldo cuentas bancarias (Titular Principal): $9,111,198
  • Ahorro voluntario Saldo Final: $40,428,144
  
Destino:
  Hoja: Efectivo_Bancos_Cuentas
  Celda Inicial: E7 (primera fila de datos)
  Tipo: ITEM_LIST (múltiples items)
```

**Ubicación en Ayuda Renta:**
- Abre la hoja "Efectivo_Bancos_Cuentas"
- Las filas 7+ están designadas para ingresar cuentas
- Columna E es donde va el saldo
- Columna F redondea automáticamente

**Estructura esperada:**
```
Fila 7, Columna E: 9,111,198 (Bancolombia - Cuenta de ahorro)
Fila 8, Columna E: 40,428,144 (Fondo de Pensiones - Ahorro voluntario)
```

---

### 5. INGRESOS DE TRABAJO (R32)

**Exógena → Ayuda Renta**

```
Categoría: Tope 1: ingresos brutos | R32 Ingresos brutos por rentas de trabajo
Valor Total: $82,744,800
Detalles:
  • Certificado - Pagos por salarios: $43,939,896
  • Certificado - Otros pagos Rentas de trabajo y pensión: $31,353,954
  • Certificado - Pagos por prestaciones sociales: $7,450,950
  
Destino:
  Hoja: Salarios_Demas_Pagos_Laborales
  Celda Inicial: E7
  Tipo: ITEM_LIST (múltiples items)
```

**Ubicación en Ayuda Renta:**
- Abre la hoja "Salarios_Demas_Pagos_Laborales"
- Fila 7 en adelante para ingresar los pagos mensuales/periódicos

---

### 6. RENDIMIENTOS DE CDT (R59)

**Exógena → Ayuda Renta**

```
Categoría: Tope 1: ingresos brutos | R58 Ingresos brutos por rentas de capital | R59 Ingresos no constitutivos por rentas de capital
Valor Total: $33,810,314
Detalles:
  • CDT Rendimientos Pagados: $33,810,314 (9 CDTs diferentes)
  
Destino:
  Hoja: Inter_Rend_Finan (Intereses y Rendimientos Financieros)
  Celda Inicial: E7
  Tipo: ITEM_LIST (múltiples items)
```

**Ubicación en Ayuda Renta:**
- Abre la hoja "Inter_Rend_Finan"
- Fila 7 en adelante para los diferentes CDTs
- Cada CDT va en una fila diferente

---

### 7. INVERSIONES TOTALES (Tope 4)

**Exógena → Ayuda Renta**

```
Categoría: TOPE 4. Consignaciones e inversiones
Valor Total: $1,297,938,192
Detalles:
  • CDT inversión efectuada: $1,162,565,712 (4 CDTs)
  • Movimientos bancarios: $135,372,480 (1 entrada)
  
Destino:
  Hoja: Inversiones
  Celda Inicial: E7
  Tipo: ITEM_LIST (múltiples items)
```

**Ubicación en Ayuda Renta:**
- Abre la hoja "Inversiones"
- Fila 7 en adelante para cada inversión/CDT

---

## 🔧 Cómo Ajustar el Mapeo Manualmente

### Si necesitas cambiar una celda destino:

**Ejemplo:** Cambiar dónde van las retenciones

1. Abre el script `exogena_to_ayuda_renta.py` en un editor
2. Busca la línea con `"R132 Retenciones año gravable a declarar"`
3. Cambia la celda:
   ```python
   "R132 Retenciones año gravable a declarar": {
       "hoja": "Retenciones",
       "celda": "C32",  # ← Cambiar este valor
       "type": "sum",
       "descripcion": "Retenciones practicadas CDT y retiros pensión"
   },
   ```

### Para encontrar la celda correcta en Ayuda Renta:

1. Abre el archivo `AyudaRenta 2025 V1.0 .xlsm` en Excel
2. Ve a la hoja deseada (ej: "Retenciones")
3. Haz clic en la celda donde quieres inyectar el valor
4. Mira en la esquina superior izquierda de Excel → allí aparece la referencia (ej: "C32")
5. Usa esa referencia en el script

---

## 📋 Checklist de Mapeo

Antes de ejecutar, verifica que:

- [ ] **R132 Retenciones**: Destino = Retenciones!C32
- [ ] **Patrimonio CDT**: Destino = Patrimonio!D14
- [ ] **Patrimonio Catastral**: Destino = Patrimonio!D18
- [ ] **Cuentas Bancarias**: Destino = Efectivo_Bancos_Cuentas!E7
- [ ] **Ingresos Laborales**: Destino = Salarios_Demas_Pagos_Laborales!E7
- [ ] **Rendimientos CDT**: Destino = Inter_Rend_Finan!E7
- [ ] **Inversiones**: Destino = Inversiones!E7
- [ ] Todos los archivos existen en las rutas correctas
- [ ] pandas y openpyxl están instalados
- [ ] Python 3.7+ está disponible

---

## 💡 Tips Importantes

1. **Macros preservadas**: El script usa `keep_vba=True`, así que las macros NO se borran

2. **Valores redondeados**: Si ves valores como $1,362,514 en lugar de decimales, es normal. El Exógena usa moneda colombiana (COP) sin decimales

3. **Multiple items**: Cuando el tipo es "item_list", el script inyecta múltiples valores en filas consecutivas. Asegúrate de que haya suficientes filas vacías

4. **Cálculos automáticos**: Las celdas con fórmulas (SUM, ROUND, etc.) se recalculan automáticamente cuando abres el archivo

5. **Validación**: Siempre abre el archivo generado en Excel para verificar que los datos se vieron correctamente

---

## 📞 Preguntas Frecuentes

**P: ¿Qué pasa con los valores que no están mapeados?**
R: Se ignoran. Si hay categorías del Exógena que no están en el mapeo, simplemente no se inyectan. Puedes agregarlas editando `CONFIG["data_mapping"]`.

**P: ¿Puedo ejecutar el script múltiples veces?**
R: Sí. Cada ejecución sobrescribe el archivo anterior con los nuevos datos del Exógena.

**P: ¿Se pierden las fórmulas del Ayuda Renta?**
R: No. El script solo modifica valores en celdas específicas. Las fórmulas se mantienen intactas.

**P: ¿Qué pasa si el valor es muy grande?**
R: Excel soporta números hasta 999,999,999,999,999.99. Los valores en tu Exógena están dentro de ese rango.

---

**¡Listo! Ahora tienes un mapeo completo y detallado.** ✓

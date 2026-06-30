# 📊 Liquidador de Formulario 210 - DIAN

## ¿Qué hace?

Automatiza el proceso de **mapear datos de Exógena** y **calcular liquidaciones tributarias** del Formulario 210 (Declaración de Renta) en Colombia.

### Características

✅ **Lectura de Exógena** - Lee reportes de información reportada por terceros  
✅ **Mapeo Automático** - Clasifica conceptos a categorías del Formulario 210  
✅ **Cálculo IRPF** - Calcula impuesto según rangos tributarios 2024-2025  
✅ **Aporte Solidario** - Incluye cálculo de aporte sobre rentas altas  
✅ **Generación Excel** - Crea Formulario 210 con fórmulas dinámicas  
✅ **Interfaz Web** - Streamlit para uso fácil sin código

---

## Instalación

### 1. Requisitos
- Python 3.9+
- pip

### 2. Instalar dependencias

```bash
pip install streamlit pandas openpyxl xlrd
```

### 3. Archivos necesarios

- **reporteExogena2024Elizabeth.xlsx** - Reporte exógena (obligatorio)
- **VA23-Formulario-210-AG2022-PN-SIMONVELASQUEZ.xlsx** - Template base (opcional)

---

## Uso

### Opción 1: App Web (Recomendado)

```bash
streamlit run app_liquidador_renta.py
```

Luego:
1. 📁 Carga el archivo de Exógena en pestaña "Cargar Archivos"
2. 🔗 Mapea los conceptos en "Mapear Datos"
3. 💰 Calcula en "Liquidación"
4. 📈 Descarga resultados en "Resultados"

### Opción 2: Desde Python

```python
from liquidador_renta import procesar_liquidacion

resultado = procesar_liquidacion(
    ruta_exogena="/ruta/al/reporte_exogena.xlsx",
    ruta_formulario_base="/ruta/al/formulario_210.xlsx",
    ano_gravable=2024
)

print(resultado)
```

---

## Mapeo de Campos

### Exógena → Formulario 210

| Exógena | Formulario 210 | Línea |
|---------|---|---|
| Honorarios y Comisiones | Ingresos por Servicios | 200 |
| Rendimientos Financieros | Rendimientos | 300 |
| Ingresos por Arrendamiento | Arrendamientos | 400 |
| Ganancia en Venta de Bienes | Ganancias | 500 |
| Otros Ingresos | Otros | 600 |

### Retenciones

| Concepto | Línea |
|----------|-------|
| Retención en la Fuente | 110 |
| Impuesto a Dividendos | 111 |
| IVA Retenido | 112 |

---

## Cálculos Incluidos

### IRPF 2024

Rangos de tarifa progresiva:

| Base Líquida | Tarifa |
|--------------|--------|
| Hasta $66.950.000 | 0% |
| $66.950.001 - $134.900.000 | 5% |
| $134.900.001 - $404.700.000 | 12% |
| $404.700.001 - $673.500.000 | 25% |
| $673.500.001 - $1.347.000.000 | 32% |
| Más de $1.347.000.000 | 37% |

### Aporte Solidario

- **Aplicable:** Rentas > 16.000 UVT
- **Tarifa:** 1%
- **Fórmula:** (Base Líquida - 16.000 × UVT) × 0.01

### Deducción Estándar

- Empleados: Hasta 10% de ingresos laborales
- Independientes: Gastos comprobados (con sopor documentario)

---

## Estructura de Resultados

### Salida JSON

```json
{
  "exito": true,
  "contribuyente": {
    "cedula": "44004730",
    "nombre": "GIRALDO GARCIA ELIZABETH",
    "ano": 2024
  },
  "calculos": {
    "total_ingresos": 50000000,
    "deducciones": 5000000,
    "base_liquida": 45000000,
    "irpf": 2247500,
    "aporte_solidario": 0,
    "total_impuesto": 2247500,
    "retenciones": 1000000,
    "saldo_pagar": 1247500,
    "acreencia": 0
  },
  "archivo": "formulario_210_liquidado_20240627_193400.xlsx"
}
```

---

## Archivos Generados

### Excel (Formulario 210)

- ✅ Datos del contribuyente
- ✅ Detalle de ingresos por concepto
- ✅ Cálculos de deducciones
- ✅ IRPF y aporte solidario
- ✅ Saldo a pagar / Acreencia
- ✅ Formato profesional con fórmulas dinámicas

---

## Validaciones

⚠️ **IMPORTANTE**: Antes de presentar a DIAN:

1. ✅ Verifica que tu cedencia esté en el rango correcto
2. ✅ Comprueba retenciones con certificados FORMUL-2649
3. ✅ Valida deducciones con contador
4. ✅ Confirma año gravable (típicamente año anterior)

---

## Limitaciones y Extensiones

### ❌ Actualmente NO incluye:
- Ingresos por dividendos
- Pérdidas de ejercicios anteriores
- Activos y pasivos (Formulario 131)
- Impuesto a Ganar Más (IEG)
- UVT por rangos especiales

### 📌 Mejoras futuras:
- Integración con API DIAN
- Validación en tiempo real
- Cálculo de estimados mensuales
- Exportación a PDF firmado
- Sincronización con Siigo/Contabilidad

---

## Troubleshooting

### "No se detectaron ingresos"
→ Verifica que el archivo Exógena tenga la estructura correcta (check fila 13+)

### "Error al leer Excel"
→ El archivo puede estar corrupto. Descarga nuevamente de DIAN

### "Fórmulas con errores"
→ Si ves #REF! o #DIV/0!, recalcula con LibreOffice/Excel

---

## Soporte

📧 Contacta al equipo de desarrollo  
📚 [Documentación DIAN](https://www.dian.gov.co)  
💬 Reporta issues en el repositorio

---

**Versión:** 1.0  
**Última actualización:** Junio 2024  
**Estado:** ✅ Producción

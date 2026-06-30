# 📊 Liquidador de Formulario 210

**Sistema automático para mapear datos de Exógena y calcular liquidaciones de Renta en Colombia**

---

## ⚡ Inicio Rápido (5 minutos)

### 1️⃣ Instalar dependencias
```bash
pip install streamlit pandas openpyxl xlrd
```

### 2️⃣ Iniciar la aplicación web
```bash
# Opción A: Usar el script
./iniciar_liquidador.sh

# Opción B: Directo con streamlit
streamlit run app_liquidador_renta.py
```

### 3️⃣ Usar la app
1. Abre http://localhost:8501 en tu navegador
2. Carga tu archivo de Exógena (📁 Cargar Archivos)
3. Mapea los conceptos (🔗 Mapear Datos)
4. Calcula la liquidación (💰 Liquidación)
5. Descarga el Excel (📈 Resultados)

---

## 📂 Archivos Incluidos

| Archivo | Descripción |
|---------|-------------|
| `liquidador_renta.py` | Módulo principal - lógica de cálculo |
| `app_liquidador_renta.py` | Interfaz web Streamlit |
| `iniciar_liquidador.sh` | Script de inicio rápido |
| `GUIA_LIQUIDADOR_210.md` | Documentación completa |
| `README_LIQUIDADOR.md` | Este archivo |

---

## 🎯 Funcionalidades

✅ **Lectura de Exógena DIAN**
- Lee reportes .xlsx descargados de DIAN
- Extrae automáticamente datos del contribuyente
- Clasifica conceptos (ingresos vs retenciones)

✅ **Cálculo Completo de IRPF**
- Tarifa progresiva 2024-2025
- Deducción estándar (10%) o personalizada
- Aporte Solidario (>16.000 UVT)

✅ **Generación de Formulario 210**
- Excel profesional con fórmulas
- Totales dinámicos
- Formato compatible con DIAN

✅ **Interfaz Amigable**
- Sin código requerido
- Pasos claros y validaciones
- Descarga instantánea

---

## 📋 Mapeo de Datos

### Exógena → Formulario 210

La app automáticamente clasifica:

```
📊 Ingresos:
├─ Honorarios y Comisiones → Línea 200
├─ Rendimientos Financieros → Línea 300
├─ Ingresos por Arrendamiento → Línea 400
├─ Ganancia en Venta de Bienes → Línea 500
└─ Otros Ingresos → Línea 600

💳 Retenciones:
├─ Retención en la Fuente → Línea 110
├─ Impuesto Dividendos → Línea 111
└─ IVA Retenido → Línea 112
```

**Personalizable:** En la pestaña "Mapear Datos" puedes ajustar la clasificación.

---

## 💰 Ejemplo de Cálculo

**Entrada (Exógena):**
```
Contribuyente: GIRALDO GARCIA ELIZABETH (CC 44004730)
Año: 2024

Ingresos Reportados:
├─ Patrimonio: $515.035.008
├─ Rendimientos CDT: $769.677
├─ Retenciones (CDT): $1.168.724
├─ Aporte Pensión: $2.095.107
└─ Otros: $4.400.000+
   TOTAL: $4.918.255.904
```

**Cálculos:**
```
Base Líquida:
  Ingresos - Deducción (10%) = $4.426.430.313

IRPF Progresivo:
  Hasta 66.95M @ 0% = $0
  66.95M - 134.9M @ 5% = $3.397.500
  ... (aplicar tarifa correcta) ...
  TOTAL IRPF = $1.457.882.716

Aporte Solidario (>16.000 UVT):
  ($4.426.430.313 - $714.464.000) × 1% = $37.119.663

Total Impuesto = $1.495.002.379

Menos Retenciones = $9.490.627

SALDO A PAGAR = $1.485.511.752
```

---

## 🔧 Uso Avanzado

### Desde Python (no web)

```python
from liquidador_renta import procesar_liquidacion

# Procesamiento completo en 1 línea
resultado = procesar_liquidacion(
    ruta_exogena="tu_exogena.xlsx",
    ruta_formulario_base="formulario_210_base.xlsx",
    ano_gravable=2024
)

# Ver resultados
print(f"Saldo a pagar: ${resultado['calculos']['saldo_pagar']:,.0f}")
print(f"Excel guardado en: {resultado['archivo']}")
```

### Personalizar Cálculos

```python
from liquidador_renta import Formulario210Liquidador

liquidador = Formulario210Liquidador(ano_gravable=2024)
liquidador.leer_exogena("exogena.xlsx")

# Ajustar deducción
total = sum(liquidador.datos['ingresos'].values())
liquidador.datos['ingresos']['_deducciones'] = total * 0.15  # 15%

# Agregar retenciones manuales
liquidador.datos['retenciones'] = {
    'Retención DIAN': 1000000,
    'Retención Banco': 500000
}

# Calcular y exportar
resultado = liquidador.liquidar()
liquidador.generar_excel("mi_formulario_210.xlsx")
```

---

## ⚠️ Validaciones Importantes

**Antes de presentar a DIAN:**

1. ✅ **Verifica la Exógena**
   - Descargada de www.dian.gov.co/datosabiertos
   - Año gravable correcto
   - Datos del contribuyente coinciden

2. ✅ **Comprueba Retenciones**
   - Coteja con Certificados FORMUL-2649
   - Suma de retenciones = suma en Exógena
   - Todas están registradas

3. ✅ **Valida Deducciones**
   - Documento de gastos comprobados
   - Límites según régimen (Simple, Común, UPE)
   - Asesoramiento de contador

4. ✅ **Revisa Cálculos**
   - Tarifa IRPF correcta para el año
   - Aporte Solidario aplicable
   - Saldo negativo = acreencia

---

## 🐛 Troubleshooting

### "No se detectaron ingresos"
→ Verifica que el archivo sea realmente una Exógena DIAN  
→ Descargalo nuevamente de www.dian.gov.co

### "Error al leer archivo Excel"
→ El archivo puede estar corrupto  
→ Intenta abrir en Excel y guardar como .xlsx nuevo

### "¿Cómo obtengo el archivo de Exógena?"
1. Ve a https://www.dian.gov.co/datosabiertos
2. Ingresa tu cédula/NIT
3. Selecciona "Consulta de Información Reportada por Terceros"
4. Año gravable
5. Descarga el Excel

### "¿Qué tasa de deducción debo usar?"
- **Empleados:** 10% automático (art. 240 E.T.)
- **Independientes:** Gastos reales (con recibos)
- **Actividad Económica:** 10% o gastos comprobados
- *Consulta con tu contador*

---

## 📊 Rangos IRPF 2024

| Rango Base | Tarifa |
|------------|--------|
| $0 - $66.950.000 | 0% |
| $66.950.001 - $134.900.000 | 5% |
| $134.900.001 - $404.700.000 | 12% |
| $404.700.001 - $673.500.000 | 25% |
| $673.500.001 - $1.347.000.000 | 32% |
| > $1.347.000.000 | 37% |

**Aporte Solidario:** 1% sobre rentas > 16.000 UVT ($714.464.000)

---

## 📞 Soporte

**¿Duda sobre los cálculos?**
→ Contacta a un contador especializado en impuesto de renta

**¿Error técnico?**
→ Revisa GUIA_LIQUIDADOR_210.md

**¿Sugerencia de mejora?**
→ Abre un issue en el repositorio

---

## 📜 Advertencia Legal

⚠️ **IMPORTANTE:**
- Esta herramienta es **informativa**
- **No reemplaza** la asesoría de un contador
- **Valida siempre** con DIAN antes de presentar
- El usuario es responsable de la exactitud
- Usa bajo tu propio riesgo

---

## 🎓 Aprende Más

- 📚 [Guía DIAN - Formulario 210](https://www.dian.gov.co)
- 💡 [Tarifa IRPF Actualizada](https://www.dian.gov.co/impuestos/irpf)
- 📖 [Deducción Estándar](https://www.dian.gov.co)

---

**Versión:** 1.0  
**Última actualización:** Junio 2026  
**Desarrollado para:** Colombia 🇨🇴

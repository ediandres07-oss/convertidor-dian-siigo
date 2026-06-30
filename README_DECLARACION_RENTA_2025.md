# 📋 App Declaración de Renta 2025 - Colombia

Aplicación integrada para procesar declaraciones de renta de personas naturales.

## 🎯 Características

✅ **Carga de Exógena DIAN** - Importa archivos exógena directamente
✅ **Cálculo Cedular** - Distribuye rentas según cédulas oficiales
✅ **Generación Formulario 210** - Crea Excel con formulario 210 completo
✅ **Clasificación Automática** - Clasifica rentas según DIAN

## 🚀 Inicio Rápido

### 1. Requisitos
```bash
pip install streamlit pandas openpyxl
```

### 2. Ejecutar la App
```bash
streamlit run app_declaracion_renta_2025.py
```

### 3. Usar la App

**Paso 1: Cargar Exógena**
- Selecciona tu archivo Excel con datos de la exógena DIAN
- La app detectará automáticamente cédula, nombre y rentas

**Paso 2: Calcular Cédulas**
- Distribuye rentas según tipo (General, Trabajo, etc.)
- Muestra ingresos, deducciones y renta líquida

**Paso 3: Generar Formulario 210**
- Descarga Excel listo para presentar

## 📊 Archivos

- `app_declaracion_renta_2025.py` - App principal Streamlit
- `cedulas_2025.py` - Módulo de cálculo de cédulas
- `ejemplo_exogena.xlsx` - Archivo de ejemplo para probar

## 🔢 Valores 2025

- **UVT**: $47,065
- **SMLV**: $1,320,000

## 📄 Sistema Cedular

| Cédula | Rentas |
|--------|--------|
| General | Dividendos, Intereses, Arrendamiento |
| Trabajo | Salarios, Honorarios, Comisiones |
| Pensiones | Jubilación |
| Ocasionales | Ganancias de capital |


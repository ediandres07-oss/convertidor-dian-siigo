# 🇨🇴 Automatizador: Información Exógena DIAN → Ayuda Renta 2025

**Automatiza la inyección de datos de tu reporte de Información Exógena en el formulario oficial de Ayuda Renta de la DIAN.**

---

## 📌 Descripción General

Este proyecto contiene un **script Python** que:

1. ✅ Lee tu reporte de Información Exógena descargado de la DIAN
2. ✅ Agrupa y procesa los datos por categoría tributaria
3. ✅ Inyecta automáticamente los valores en el archivo `AyudaRenta 2025 V1.0 .xlsm`
4. ✅ **Preserva las macros** del documento original (crítico para que funcione)
5. ✅ Genera un nuevo archivo listo para presentación

---

## 🚀 Inicio Rápido

### 1️⃣ Verificar configuración
```bash
cd /Users/edison/Desktop/proyecto-subir\ info\ a\ siigo\ nube/
python3 verificar_config.py
```

### 2️⃣ Instalar dependencias (si es necesario)
```bash
pip3 install pandas openpyxl
```

### 3️⃣ Ejecutar el automatizador
```bash
python3 exogena_to_ayuda_renta.py
```

### 4️⃣ Abrir el resultado
```bash
open AyudaRenta_Diligenciado.xlsm
```

---

## 📁 Archivos del Proyecto

| Archivo | Descripción |
|---------|-------------|
| `exogena_to_ayuda_renta.py` | **Script principal** - Automatiza la inyección de datos |
| `verificar_config.py` | Verifica que todo esté bien configurado antes de ejecutar |
| `INSTRUCCIONES_EJECUCION.md` | Guía paso a paso para instalar y ejecutar |
| `MAPEO_DETALLADO.md` | Explicación detallada de cada categoría y dónde va |
| `README_AUTOMATIZADOR_EXOGENA.md` | Este archivo (descripción general) |

---

## 📊 PASO 1: ANÁLISIS DE DATOS

### Resumen del Exógena 2024 - Elizabeth Giraldo García

**Total de registros:** 59
**Categorías identificadas:** 14 categorías tributarias

### Valores principales encontrados:

```
TOPE 1 - Ingresos Brutos
├─ Ingresos Laborales: $82,744,800
├─ Ingresos de Capital (CDTs): $33,810,314
└─ Retiros Pensión: $4,431,976
                    TOTAL: ~$121,987,090

TOPE 2 - Patrimonio Bruto
├─ CDTs e Inversiones: $335,626,272
├─ Bienes Raíces: $69,318,000
└─ Cuentas Bancarias: $49,539,342
                    TOTAL: ~$454,483,614

TOPE 3 - Consumos T.C.
└─ Total consumos: $15,666,577
                    TOTAL: $15,666,577

TOPE 4 - Inversiones/Cuentas
├─ CDTs (inversiones): $1,162,565,712
└─ Movimientos bancarios: $135,372,480
                    TOTAL: $1,297,938,192

RETENCIONES Y APORTES
├─ R132 Retenciones: $1,362,514
├─ Aportes Pensión: $7,074,488
└─ Aportes Salud: $1,897,503
                    TOTAL: $10,334,505
```

---

## 🎯 PASO 2: MAPEO DE DATOS

El script mapea automáticamente cada categoría del Exógena a las hojas y celdas correspondientes del Ayuda Renta:

| Categoría Exógena | Destino | Hoja | Celda |
|---|---|---|---|
| R132 Retenciones | Retenciones practicadas | `Retenciones` | `C32` |
| Patrimonio CDT | Inversiones | `Patrimonio` | `D14` |
| Patrimonio Catastral | Bienes raíces | `Patrimonio` | `D18` |
| Cuentas Bancarias | Saldos bancarios | `Efectivo_Bancos_Cuentas` | `E7+` |
| Ingresos Laborales | Salarios | `Salarios_Demas_Pagos_Laborales` | `E7+` |
| Rendimientos CDT | Intereses | `Inter_Rend_Finan` | `E7+` |
| Inversiones Totales | Consignaciones | `Inversiones` | `E7+` |

**Ver `MAPEO_DETALLADO.md` para descripción completa de cada mapeo.**

---

## 💻 PASO 3: DESARROLLO DEL SCRIPT

### Tecnologías utilizadas:

- **Python 3.7+** - Lenguaje de programación
- **pandas** - Procesamiento y análisis de datos
- **openpyxl** - Lectura/escritura de archivos Excel con soporte a macros

### Características principales:

✅ **Preserva macros**: Usa `keep_vba=True` para no borrar las macros del archivo original
✅ **Modular**: Configuración centralizada en la sección `CONFIG`
✅ **Robusto**: Manejo de errores y logging detallado
✅ **Flexible**: Fácil de ajustar celdas y mapeos

### Estructura del código:

```python
CONFIG                          # Configuración centralizada
├─ exogena_file               # Ruta del archivo Exógena
├─ ayuda_renta_file           # Ruta del Ayuda Renta
├─ output_file                # Dónde guardar el resultado
├─ exogena_config             # Config de lectura del Exógena
└─ data_mapping               # Mapeo de categorías → celdas

FUNCIONES
├─ leer_exogena()             # Lee el archivo CSV/XLSX
├─ procesar_datos_exogena()   # Agrupa y suma por categoría
├─ inyectar_en_ayuda_renta()  # Inyecta datos en el XLSM
└─ guardar_resultado()        # Guarda preservando macros
```

---

## 📝 PASO 4: INSTRUCCIONES DE EJECUCIÓN

### Requisitos previos:

- ✅ Python 3.7 o superior
- ✅ Archivo Exógena: `reporteExogena2024Elizabeth.xlsx`
- ✅ Archivo Ayuda Renta: `AyudaRenta 2025 V1.0 .xlsm`
- ✅ Librerías Python: `pandas`, `openpyxl`

### Instalación paso a paso:

#### 1. Instalar dependencias
```bash
pip3 install pandas openpyxl
```

#### 2. Verificar configuración
```bash
python3 verificar_config.py
```

#### 3. Ejecutar el script
```bash
python3 exogena_to_ayuda_renta.py
```

#### 4. Resultado
Se genera automáticamente: `AyudaRenta_Diligenciado.xlsm`

**Ver `INSTRUCCIONES_EJECUCION.md` para guía completa con screenshots y solución de problemas.**

---

## 🔧 Personalización

### Cambiar rutas de archivos:

Edita la sección `CONFIG` en `exogena_to_ayuda_renta.py`:

```python
CONFIG = {
    "exogena_file": "/nueva/ruta/reporte_exogena.xlsx",
    "ayuda_renta_file": "/nueva/ruta/AyudaRenta.xlsm",
    "output_file": "/nueva/ruta/AyudaRenta_Resultado.xlsm",
    ...
}
```

### Cambiar celdas destino:

Edita el mapeo en `CONFIG["data_mapping"]`:

```python
"R132 Retenciones año gravable a declarar": {
    "hoja": "Retenciones",
    "celda": "C32",  # ← Cambiar aquí
    "type": "sum",
    "descripcion": "..."
},
```

### Agregar nuevas categorías:

```python
"Nueva categoría del Exógena": {
    "hoja": "NombreHoja",
    "celda": "D15",
    "type": "direct",  # o "sum", "item_list"
    "descripcion": "Descripción"
},
```

---

## 🐛 Solución de Problemas

### Error: "ModuleNotFoundError: No module named 'pandas'"
```bash
pip3 install pandas openpyxl
```

### Error: "File not found"
- Verifica que las rutas en `CONFIG` sean correctas
- Usa rutas absolutas (no relativas)

### Advertencia: "Data Validation extension is not supported"
- No es un error, es normal
- El archivo se guardará correctamente

### Las macros desaparecieron
- Asegúrate de que el script usa `keep_vba=True`
- Excel a veces remueve macros al abrir (comportamiento normal)

---

## 📚 Documentación Completa

- 📖 **INSTRUCCIONES_EJECUCION.md** - Guía paso a paso
- 🗺️ **MAPEO_DETALLADO.md** - Explicación de cada categoría
- 💻 **exogena_to_ayuda_renta.py** - Código fuente comentado

---

## ✅ Verificaciones Previas

Ejecuta esto antes de usar por primera vez:

```bash
python3 verificar_config.py
```

Debería ver algo como:
```
========================================================================
  VERIFICADOR DE CONFIGURACIÓN - EXÓGENA → AYUDA RENTA
========================================================================

✓ Python 3.9.7 (OK)
✓ pandas 1.5.3
✓ openpyxl 3.10.0
✓ Archivo Exógena: ... (2.45 MB)
✓ Archivo Ayuda Renta: ... (3.67 MB)
✓ Script Principal: ... (7.89 KB)

========================================================================
  RESUMEN DE VERIFICACIÓN
========================================================================

✓ OK     Python
✓ OK     Dependencias
✓ OK     Archivos
✓ OK     Exógena
✓ OK     Ayuda Renta

✓ ¡TODAS LAS VERIFICACIONES PASARON!
```

---

## 🎓 Cómo Funciona (Resumido)

```
1. Leer Exógena
   ↓
2. Procesar datos (agrupar por categoría)
   ↓
3. Abrir Ayuda Renta (preservando macros)
   ↓
4. Para cada categoría en el mapeo:
   ├─ Encontrar la celda destino
   ├─ Inyectar el valor
   └─ Repetir para todas las categorías
   ↓
5. Guardar con macros intactas
   ↓
6. Archivo listo para presentación
```

---

## 📞 Contacto / Ayuda

Si necesitas ajustar algo específico:

1. Abre `MAPEO_DETALLADO.md` para ver el mapeo completo
2. Busca tu categoría en el documento
3. Edita el script según lo necesites
4. Ejecuta `verificar_config.py` para validar
5. Corre el script principal

---

## ⚖️ Notas Legales / Tributarias

- ✅ Este script **no reemplaza** la consulta con un asesor tributario
- ✅ Los valores se inyectan **automáticamente**, pero debes verificarlos
- ✅ **Responsabilidad del usuario**: Revisar que los datos sean correctos antes de presentar
- ✅ Funciona con datos reales del Exógena DIAN 2024-2025
- ✅ Compatible con Ayuda Renta 2025 V1.0

---

## 🚀 Próximas Mejoras Posibles

- [ ] Interfaz gráfica (GUI)
- [ ] Soporte para múltiples contribuyentes
- [ ] Validación automática de datos
- [ ] Generación de reportes de inconsistencias
- [ ] Cálculo automático de impuestos

---

**Versión:** 1.0  
**Última actualización:** Junio 2025  
**Autor:** Claude Code (Automatización Tributaria)  
**Python:** 3.7+  
**Licencia:** MIT

---

**¡Listo para automatizar tu declaración de renta! ✓**

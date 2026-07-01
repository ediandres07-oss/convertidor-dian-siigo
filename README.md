# 💼 Sistema de Liquidaciones de Nómina

Un sistema completo de gestión de liquidaciones de nómina basado en Python con FastAPI y Streamlit.

## ✨ Características

### Backend (FastAPI)
- ✅ Carga de archivos Excel con múltiples hojas
- ✅ Cálculo automático de:
  - Cesantías
  - Intereses de cesantías
  - Prima de servicios
  - Vacaciones
  - Aportes a salud (4%)
  - Aportes a pensión (4%)
  - Fondo de solidaridad (1%)
  - Retenciones personalizadas
- ✅ Exportación de Excel consolidado
- ✅ Generación de PDFs individuales
- ✅ Empaquetamiento en ZIP de múltiples PDFs

### Frontend (Streamlit)
- ✅ Interfaz intuitiva y amigable
- ✅ Carga y procesamiento de archivos
- ✅ Visualización de resultados
- ✅ Descargas de Excel, PDF individual y ZIP
- ✅ Métricas y estadísticas globales
- ✅ Búsqueda de empleados

## 🚀 Inicio Rápido

### 1. Instalar dependencias automáticamente

```bash
python3 -m pip install -r requirements.txt
```

### 2. Ejecutar el sistema

#### Opción A: Script automático (recomendado)
```bash
python3 run.py
```

#### Opción B: Ejecutar manualmente

**Terminal 1 - Backend:**
```bash
python3 -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

**Terminal 2 - Frontend:**
```bash
python3 -m streamlit run frontend/app.py --server.port=8501 --server.address=127.0.0.1
```

### 3. Acceder a la aplicación

- **Frontend Streamlit**: http://127.0.0.1:8501
- **Backend API**: http://127.0.0.1:8000
- **Documentación API**: http://127.0.0.1:8000/docs

## 📁 Estructura del Archivo Excel

Tu archivo Excel debe contener al menos estas hojas:

### Hoja: Empleados (Requerida)
| Columna | Tipo | Descripción |
|---------|------|-------------|
| nombre | Texto | Nombre del empleado |
| documento | Texto/Número | Número de documento |
| salario_mensual | Número | Salario mensual |
| dias_laborados | Número | Días trabajados en el período |
| cesantias_acum | Número | Cesantías acumuladas (opcional) |
| vacaciones_acum | Número | Vacaciones acumuladas (opcional) |

### Hoja: Parametros (Opcional)
| Columna | Descripción |
|---------|-------------|
| parametro | Nombre del parámetro (ej: salud, pension) |
| valor | Valor del porcentaje |

### Hoja: Novedades (Opcional)
| Columna | Descripción |
|---------|-------------|
| documento | Documento del empleado |
| tipo_novedad | Tipo de novedad (ej: retencion) |
| valor | Valor de la novedad |

## 📋 Ejemplo de Uso

1. **Cargar archivo**: Descarga `ejemplo_liquidacion.xlsx` o crea uno con tu estructura
2. **Procesar**: Clic en "Procesar Archivo"
3. **Descargar resultados**:
   - Excel consolidado: contiene todas las liquidaciones
   - ZIP de PDFs: un PDF por empleado
   - PDF individual: descarga un PDF específico

## 📊 Cálculos Realizados

```
DEVENGOS:
- Salario Prorratead: Salario × (Días / 30)
- Cesantías: (Salario × Días) / 360
- Intereses Cesantías: Cesantías × 12%
- Prima de Servicios: (Salario × Días) / 360
- Vacaciones: (Salario × Días) / 720

DEDUCCIONES:
- Salud: Salario × 4%
- Pensión: Salario × 4%
- Fondo Solidaridad: Salario × 1% (si aplica)
- Retenciones: Según novedades

NETO A PAGAR: Total Devengos - Total Deducciones
```

## 🛠️ Estructura del Proyecto

```
proyecto-liquidaciones/
├── backend/
│   ├── __init__.py
│   ├── main.py                 # Aplicación FastAPI
│   ├── utils.py                # Funciones de cálculo
│   └── routers/
│       ├── __init__.py
│       └── payroll.py          # Endpoints de nómina
├── frontend/
│   └── app.py                  # Aplicación Streamlit
├── run.py                      # Script para ejecutar todo
├── generar_ejemplo.py          # Genera archivo de ejemplo
├── ejemplo_liquidacion.xlsx    # Archivo de prueba
└── requirements.txt            # Dependencias
```

## 🔗 Endpoints API

### POST /api/procesar-completo
Procesa un archivo Excel y retorna los resultados

```bash
curl -X POST "http://127.0.0.1:8000/api/procesar-completo" \
  -F "file=@archivo.xlsx"
```

**Respuesta:**
```json
{
  "success": true,
  "total_empleados": 5,
  "total_neto": 16045344.43,
  "empleados": [...]
}
```

### POST /api/exportar-excel-desde-excel
Exporta un Excel consolidado

```bash
curl -X POST "http://127.0.0.1:8000/api/exportar-excel-desde-excel" \
  -F "file=@archivo.xlsx" \
  -o liquidacion.xlsx
```

### POST /api/exportar-pdf-individual-desde-excel
Exporta un PDF individual

```bash
curl -X POST "http://127.0.0.1:8000/api/exportar-pdf-individual-desde-excel" \
  -F "file=@archivo.xlsx" \
  -G -d "documento=1234567890" \
  -o empleado.pdf
```

### POST /api/exportar-pdf-zip-desde-excel
Exporta un ZIP con todos los PDFs

```bash
curl -X POST "http://127.0.0.1:8000/api/exportar-pdf-zip-desde-excel" \
  -F "file=@archivo.xlsx" \
  -o liquidaciones.zip
```

## 📦 Dependencias

- **fastapi**: Framework web API
- **uvicorn**: Servidor ASGI
- **pandas**: Procesamiento de datos
- **openpyxl**: Lectura/escritura de Excel
- **reportlab**: Generación de PDFs
- **streamlit**: Framework para interfaz web
- **requests**: Cliente HTTP

## 🔒 Notas de Seguridad

- Los archivos se procesan en memoria
- No se almacenan archivos en el servidor
- Los datos se envían entre frontend y backend sin encriptación
- Para uso en producción, implementar HTTPS y autenticación

## 📞 Soporte

Si tienes problemas:

1. Verifica que ambas aplicaciones estén ejecutándose
2. Comprueba que los puertos 8000 y 8501 estén disponibles
3. Revisa los logs en `/tmp/backend.log` y `/tmp/frontend.log`
4. Asegúrate que el archivo Excel tenga la estructura correcta

## 📝 Licencia

Este proyecto es de código abierto y está disponible para uso libre.

---

**¡Disfruta del sistema de liquidaciones! 💼**
# Tue Jun 30 22:55:15 -05 2026

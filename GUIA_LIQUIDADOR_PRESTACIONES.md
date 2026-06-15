# 💼 Guía Completa: Sistema de Liquidación de Prestaciones Sociales

## 🎯 Descripción General

Sistema profesional en Python para calcular y generar reportes PDF de prestaciones sociales colombianas. Incluye:

✅ Cálculo automático de cesantías, prima, vacaciones e intereses  
✅ Interfaz web intuitiva con Streamlit  
✅ Generación de PDF profesional y legalizado  
✅ Validaciones integradas  
✅ Descarga directa del documento  

---

## 📦 Requisitos

### Dependencias Python

```bash
pip install streamlit reportlab pytz
```

O usa el archivo `requirements.txt`:

```bash
pip install -r requirements.txt
```

### Archivos Necesarios

```
.
├── app_prestaciones.py              # Aplicación principal (Streamlit)
├── calculadora_prestaciones.py      # Lógica de cálculos
├── generador_pdf_prestaciones.py    # Generación de PDF
├── ejemplo_uso.py                   # Ejemplo de uso programático
└── GUIA_LIQUIDADOR_PRESTACIONES.md  # Esta documentación
```

---

## 🚀 Inicio Rápido

### Opción 1: Interfaz Web (Recomendado)

```bash
streamlit run app_prestaciones.py
```

Se abrirá automáticamente en: http://localhost:8501

**Pasos:**
1. Completa los datos del empleado
2. Ingresa salario y fechas
3. Haz clic en "✅ LIQUIDAR PRESTACIONES"
4. Descarga el PDF con "⬇️ Descargar PDF Profesional"

### Opción 2: Uso Programático

```python
from calculadora_prestaciones import DatosEmpleado, CalculadoraPrestaciones
from generador_pdf_prestaciones import GeneradorPDFPrestaciones
from datetime import datetime

# Crear datos del empleado
datos = DatosEmpleado(
    nombre="Juan García Pérez",
    documento="1234567890",
    cargo="Gerente",
    salario_mensual=2600000,
    auxilio_transporte=140000,
    fecha_ingreso=datetime(2023, 1, 1),
    fecha_retiro=datetime(2024, 6, 30),
    empresa="Mi Empresa S.A.S"
)

# Calcular prestaciones
calculadora = CalculadoraPrestaciones()
resultados = calculadora.calcular_prestaciones(datos)

# Generar PDF
generador = GeneradorPDFPrestaciones()
generador.generar_pdf(datos, resultados, "liquidacion.pdf")

print(f"Total a pagar: ${resultados.neto_pagar:,.2f}")
```

---

## 📋 Estructura de Módulos

### 1. `calculadora_prestaciones.py`

**Clases principales:**
- `DatosEmpleado`: Estructura con datos del empleado
- `ResultadosPrestaciones`: Resultado de cálculos
- `CalculadoraPrestaciones`: Lógica de cálculo

**Métodos principales:**
```python
calcular_dias_laborados(fecha_ingreso, fecha_retiro)
calcular_cesantias(base_calculo, dias)
calcular_prima(base_calculo, dias)
calcular_vacaciones(salario, dias)
calcular_prestaciones(datos)  # Calcula todo
```

### 2. `generador_pdf_prestaciones.py`

**Clase principal:**
- `GeneradorPDFPrestaciones`: Generación de PDF

**Método principal:**
```python
generar_pdf(datos, resultados, ruta_salida=None)
```

Retorna: BytesIO (si ruta_salida es None) o ruta del archivo

### 3. `app_prestaciones.py`

Interfaz Streamlit con:
- Formulario de entrada
- Validaciones
- Visualización de resultados
- Descarga de PDF

---

## 🧮 Fórmulas Colombianas Implementadas

### Cesantías
```
Cesantías = (Salario + Auxilio) × Días / 360
```
- Se debe pagar al retiro del empleado
- No aplica si ha recibido crédito de cesantías

### Intereses sobre Cesantías
```
Intereses = Cesantías × 12% × Días / 360
```
- 12% anual sobre el monto de cesantías
- Se paga al retiro junto con las cesantías

### Prima de Servicios (Bono de Servicios)
```
Prima = (Salario + Auxilio) × Días / 360
```
- Se paga en dos cuotas (junio 30 y diciembre 31)
- Liquidación proporcional al retiro

### Vacaciones Proporcionales
```
Vacaciones = Salario × Días / 720
```
- 720 = 2 × 360 (equivale a 15 días anuales)
- Solo el salario, sin auxilio

---

## 📥 Entrada de Datos

### Campos Requeridos

| Campo | Tipo | Validación | Ejemplo |
|-------|------|-----------|---------|
| Nombre | Texto | Obligatorio | Juan García Pérez |
| Documento | Texto | Obligatorio | 1234567890 |
| Cargo | Texto | Obligatorio | Gerente General |
| Salario | Número | > 0 | 2600000 |
| Auxilio | Número | ≥ 0 | 140000 |
| Fecha Ingreso | Fecha | Obligatoria | 2023-01-15 |
| Fecha Retiro | Fecha | Posterior a ingreso | 2024-06-30 |
| Empresa | Texto | Opcional | Mi Empresa S.A.S |

---

## 📤 Salida del PDF

### Contenido del PDF

✅ **Encabezado**
- Nombre de la empresa
- Título "LIQUIDACIÓN DE PRESTACIONES SOCIALES"

✅ **Datos del Empleado**
- Nombre, documento, cargo
- Empresa, fechas de ingreso y retiro
- Días laborados, salario mensual

✅ **Tabla de Prestaciones**
- Cesantías
- Intereses sobre cesantías
- Prima de servicios
- Vacaciones proporcionales
- Total devengado
- Descuentos (si aplica)
- **NETO A PAGAR**

✅ **Total en Letras**
- Conversión a palabras en español
- Formato legal

✅ **Sección de Firmas**
- Firma del empleado
- Firma de la empresa
- Fechas de autorización

✅ **Pie de página**
- Leyenda de validez legal
- Información de archivo automático

---

## ✅ Validaciones Implementadas

### En Interfaz Streamlit

- ✅ Nombre: Obligatorio, no vacío
- ✅ Documento: Obligatorio, no vacío
- ✅ Cargo: Obligatorio, no vacío
- ✅ Salario: Debe ser > 0
- ✅ Fechas: Retiro debe ser ≥ Ingreso
- ✅ Empresa: Opcional (usa default)

### En Calculadora

- ✅ Salario debe ser positivo
- ✅ Fecha retiro > fecha ingreso
- ✅ Redondeo a 2 decimales
- ✅ Cálculo correcto de días (inclusive)

### En PDF

- ✅ Todos los valores con formato monetario
- ✅ Tablas con bordes y colores
- ✅ Conversión a letras correcta
- ✅ Espacios para firmas

---

## 🎨 Personalización

### Cambiar Nombre de Empresa

En la interfaz, el campo "Nombre de la empresa" es editable.

Programáticamente:
```python
datos = DatosEmpleado(
    ...
    empresa="Mi Empresa Personalizada S.A.S"
)
```

### Cambiar Colores del PDF

En `generador_pdf_prestaciones.py`, línea ~33:

```python
COLOR_ENCABEZADO = colors.HexColor('#1f4788')  # Azul
COLOR_TOTAL = colors.HexColor('#FFE6E6')       # Rosa suave
COLOR_ALTERNADO = colors.HexColor('#F5F5F5')   # Gris claro
```

### Agregar Logo

Modifica `GeneradorPDFPrestaciones._crear_estilos_personalizados()`:

```python
# Agregar imagen del logo
from reportlab.platypus import Image

logo = Image('logo.png', width=1*inch, height=1*inch)
story.insert(0, logo)
```

---

## 🔧 Ejemplos Avanzados

### Calcular múltiples empleados

```python
from calculadora_prestaciones import DatosEmpleado, CalculadoraPrestaciones
from generador_pdf_prestaciones import GeneradorPDFPrestaciones
from datetime import datetime
import pandas as pd

empleados_data = [
    {
        'nombre': 'Juan García',
        'documento': '1234567890',
        'cargo': 'Gerente',
        'salario': 2600000,
        'auxilio': 140000,
        'ingreso': datetime(2023, 1, 1),
        'retiro': datetime(2024, 6, 30)
    },
    {
        'nombre': 'María López',
        'documento': '0987654321',
        'cargo': 'Contador',
        'salario': 2200000,
        'auxilio': 140000,
        'ingreso': datetime(2022, 6, 15),
        'retiro': datetime(2024, 6, 30)
    }
]

calculadora = CalculadoraPrestaciones()
generador = GeneradorPDFPrestaciones()

for emp in empleados_data:
    datos = DatosEmpleado(
        nombre=emp['nombre'],
        documento=emp['documento'],
        cargo=emp['cargo'],
        salario_mensual=emp['salario'],
        auxilio_transporte=emp['auxilio'],
        fecha_ingreso=emp['ingreso'],
        fecha_retiro=emp['retiro']
    )
    
    resultado = calculadora.calcular_prestaciones(datos)
    generador.generar_pdf(
        datos,
        resultado,
        f"liquidacion_{emp['documento']}.pdf"
    )
    
    print(f"✅ {emp['nombre']}: ${resultado.neto_pagar:,.2f}")
```

### Exportar a Excel

```python
import pandas as pd

datos_tabla = []
for emp in empleados:
    datos = crear_datos_empleado(emp)
    resultado = calculadora.calcular_prestaciones(datos)
    
    datos_tabla.append({
        'Nombre': emp['nombre'],
        'Documento': emp['documento'],
        'Salario': emp['salario'],
        'Días': resultado.dias_laborados,
        'Cesantías': resultado.cesantias,
        'Prima': resultado.prima_servicios,
        'Vacaciones': resultado.vacaciones,
        'Intereses': resultado.intereses_cesantias,
        'Total': resultado.neto_pagar
    })

df = pd.DataFrame(datos_tabla)
df.to_excel('liquidaciones.xlsx', index=False)
```

---

## 🐛 Solución de Problemas

### Error: "ModuleNotFoundError: No module named 'streamlit'"

**Solución:**
```bash
pip install streamlit reportlab pytz
```

### Error: "Fecha de retiro no puede ser anterior"

**Solución:** Verifica que la fecha de retiro sea posterior a la de ingreso

### PDF generado pero no se ve correctamente

**Solución:** Actualiza reportlab:
```bash
pip install --upgrade reportlab
```

### Valores calculados incorrectos

**Solución:** Verifica:
1. El salario sea positivo
2. Las fechas sean correctas
3. Los días laborados sean > 0

---

## 📞 Soporte y Reportes

Para:
- **Bugs:** Reporta en el sistema de tickets
- **Mejoras:** Sugiere en las reuniones de equipo
- **Preguntas:** Contacta a Recursos Humanos

---

## 📊 Cambios y Versionado

**Versión Actual:** 2.0  
**Fecha:** 2026-06-14  

### Historial de Cambios

**v2.0** - Release Completo
- ✅ Sistema completo de cálculo
- ✅ Interfaz web profesional
- ✅ PDF legalizado
- ✅ Validaciones robustas
- ✅ Documentación completa

**v1.0** - Versión Inicial
- Cálculos básicos
- PDF simple

---

## 📖 Recursos Adicionales

### Documentación Oficial
- [Reportlab Documentation](https://www.reportlab.com/docs/reportlab-userguide.pdf)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [Ministerio de Trabajo Colombia](https://www.mintrabajo.gov.co/)

### Normativa Colombiana
- Código Sustantivo del Trabajo
- Decreto 1072 de 2015
- Resoluciones de Recursos Humanos

---

## ⚖️ Notas Legales

Este sistema:
- ✅ Cumple con normativa colombiana
- ✅ Genera documentos válidos legalmente
- ✅ Requiere firma del empleado y empresa
- ✅ Debe conservarse por mínimo 2 años

**Descargo de responsabilidad:**
Este software se proporciona "tal cual" sin garantía de ningún tipo.
El usuario es responsable de verificar la exactitud de los cálculos
según la legislación vigente en el momento de su uso.

---

**¿Necesitas ayuda?** Contacta con el área de Recursos Humanos.

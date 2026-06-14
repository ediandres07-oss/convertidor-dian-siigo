# 💼 Funciones de Prima y Vacaciones - Colombia

Funciones Python para calcular **Prima de Servicios** y **Vacaciones Proporcionales** según la legislación laboral colombiana.

## 📋 Contenido

- `prima_servicios.py` - Cálculo de Prima de Servicios
- `vacaciones_proporcionales.py` - Cálculo de Vacaciones Proporcionales
- `ejemplo_uso_avanzado.py` - Ejemplos de uso y casos especiales

---

## 🎯 PRIMA DE SERVICIOS

### Fórmula
```
Prima = (Salario Mensual + Auxilio Transporte) × Días Trabajados ÷ 360
```

### Características
✅ Incluye auxilio de transporte en la base  
✅ Validación de datos negativa  
✅ Redondeo a 2 decimales  
✅ Compatible con listas y DataFrames  

### Parámetros Entrada

| Parámetro | Tipo | Requerido | Descripción |
|-----------|------|-----------|-------------|
| nombre | str | ✅ | Nombre del empleado |
| salario_mensual | float | ✅ | Salario mensual en pesos |
| dias_trabajados | float | ✅ | Días trabajados (0-360) |
| auxilio_transporte | float | ❌ | Subsidio de transporte (default: 0) |

### Salida

| Campo | Descripción |
|-------|-------------|
| nombre | Nombre del empleado |
| salario_mensual | Salario ingresado |
| auxilio_transporte | Auxilio ingresado |
| dias_trabajados | Días ingresados |
| base_prima | Salario + Auxilio |
| valor_prima | Prima calculada |

### Uso Básico

```python
from prima_servicios import calcular_prima

# Opción 1: Con listas
empleados = [
    {
        'nombre': 'Juan García',
        'salario_mensual': 2_500_000,
        'auxilio_transporte': 140_000,
        'dias_trabajados': 30
    }
]

df = calcular_prima(empleados)
print(df)

# Opción 2: Con DataFrames
import pandas as pd

df_empleados = pd.read_csv('empleados.csv')
df_prima = calcular_prima(df_empleados)
```

### Ejemplos de Cálculo

**Ejemplo 1: Mes completo con auxilio**
```
Salario: $2,500,000
Auxilio: $140,000
Días: 30

Base = 2,500,000 + 140,000 = $2,640,000
Prima = 2,640,000 × 30 ÷ 360 = $220,000
```

**Ejemplo 2: Medio mes, sin auxilio**
```
Salario: $3,000,000
Auxilio: $0
Días: 15

Base = 3,000,000 + 0 = $3,000,000
Prima = 3,000,000 × 15 ÷ 360 = $125,000
```

---

## 🏖️ VACACIONES PROPORCIONALES

### Fórmula
```
Vacaciones = Salario Mensual × Días Trabajados ÷ 720
```

**Nota:** 720 = 360 × 2 (un empleado tiene 30 días de vacaciones al año)

### Características
✅ Base solo con salario (sin auxilio)  
✅ Validación de datos negativa  
✅ Redondeo a 2 decimales  
✅ Compatible con listas y DataFrames  

### Parámetros Entrada

| Parámetro | Tipo | Requerido | Descripción |
|-----------|------|-----------|-------------|
| nombre | str | ✅ | Nombre del empleado |
| salario_mensual | float | ✅ | Salario mensual en pesos |
| dias_trabajados | float | ✅ | Días trabajados (0-360) |

### Salida

| Campo | Descripción |
|-------|-------------|
| nombre | Nombre del empleado |
| salario_mensual | Salario ingresado |
| dias_trabajados | Días ingresados |
| base_vacaciones | Base para cálculo (= salario) |
| valor_vacaciones | Vacaciones calculadas |

### Uso Básico

```python
from vacaciones_proporcionales import calcular_vacaciones

# Opción 1: Con listas
empleados = [
    {
        'nombre': 'María Rodríguez',
        'salario_mensual': 3_200_000,
        'dias_trabajados': 30
    }
]

df = calcular_vacaciones(empleados)
print(df)

# Opción 2: Con DataFrames
import pandas as pd

df_empleados = pd.read_csv('empleados.csv')
df_vaca = calcular_vacaciones(df_empleados)
```

### Ejemplos de Cálculo

**Ejemplo 1: Mes completo**
```
Salario: $2,500,000
Días: 30

Vacaciones = 2,500,000 × 30 ÷ 720 = $104,166.67
```

**Ejemplo 2: Año completo (360 días)**
```
Salario: $2,500,000
Días: 360

Vacaciones = 2,500,000 × 360 ÷ 720 = $1,250,000
(equivalente a 30 días pagos: 2,500,000 ÷ 30 = 83,333.33 × 15 días = 1,250,000)
```

**Ejemplo 3: Ingreso tardío (10 días)**
```
Salario: $2,500,000
Días: 10

Vacaciones = 2,500,000 × 10 ÷ 720 = $34,722.22
```

---

## 🔄 Combinación Prima + Vacaciones

Para obtener un resumen completo:

```python
from prima_servicios import calcular_prima
from vacaciones_proporcionales import calcular_vacaciones

empleados = [
    {
        'nombre': 'Empleado Prueba',
        'salario_mensual': 2_500_000,
        'auxilio_transporte': 140_000,
        'dias_trabajados': 30
    }
]

# Calcular prima
df_prima = calcular_prima(empleados)

# Calcular vacaciones
df_vaca = calcular_vacaciones(empleados)

# Combinar
df_total = pd.DataFrame({
    'Nombre': df_prima['nombre'],
    'Salario': df_prima['salario_mensual'],
    'Prima': df_prima['valor_prima'],
    'Vacaciones': df_vaca['valor_vacaciones'],
    'Total': df_prima['valor_prima'] + df_vaca['valor_vacaciones']
})

print(df_total)
```

---

## 📊 Exportar a Excel

```python
from prima_servicios import calcular_prima
from vacaciones_proporcionales import calcular_vacaciones
import pandas as pd

empleados = [...]

df_prima = calcular_prima(empleados)
df_vaca = calcular_vacaciones(empleados)

# Exportar a Excel con múltiples hojas
with pd.ExcelWriter('liquidacion.xlsx', engine='openpyxl') as writer:
    df_prima.to_excel(writer, sheet_name='Prima', index=False)
    df_vaca.to_excel(writer, sheet_name='Vacaciones', index=False)

print("✅ Archivo guardado: liquidacion.xlsx")
```

---

## ⚙️ Ejecución Directa

Ambos archivos pueden ejecutarse directamente:

```bash
# Prima
python3 prima_servicios.py

# Vacaciones
python3 vacaciones_proporcionales.py

# Ejemplos avanzados
python3 ejemplo_uso_avanzado.py
```

---

## 🛡️ Validaciones

Ambas funciones validan automáticamente:

✅ Campos requeridos presentes  
✅ Salario no negativo  
✅ Días no negativos  
✅ Días no excedan 360  

Ejemplo de error:

```python
empleado = {
    'nombre': 'Prueba',
    'salario_mensual': -1000,  # ❌ Error: salario negativo
    'dias_trabajados': 30
}

calcular_vacaciones([empleado])
# ValueError: Empleado Prueba: El salario no puede ser negativo
```

---

## 📈 Casos de Uso

### 1. Liquidación por Renuncia
```python
# Empleado que renuncia el 15 del mes
empleado = {
    'nombre': 'Empleado',
    'salario_mensual': 2_500_000,
    'dias_trabajados': 15,  # Solo 15 días del mes
    'auxilio_transporte': 140_000
}

df = calcular_prima([empleado])
df = calcular_vacaciones([empleado])
```

### 2. Ingreso Tardío
```python
# Empleado que ingresa el 20 del mes
empleado = {
    'nombre': 'Nuevo',
    'salario_mensual': 2_500_000,
    'dias_trabajados': 10,  # 10 días del mes (20 al 30)
    'auxilio_transporte': 140_000
}
```

### 3. Procesar Nómina Completa
```python
df_empleados = pd.read_csv('nómina.csv')

prima = calcular_prima(df_empleados)
vacaciones = calcular_vacaciones(df_empleados)

total_prima = prima['valor_prima'].sum()
total_vaca = vacaciones['valor_vacaciones'].sum()

print(f"Total Prima: ${total_prima:,.2f}")
print(f"Total Vacaciones: ${total_vaca:,.2f}")
```

---

## 📋 Requisitos

```
pandas >= 1.0.0
openpyxl >= 3.0.0 (para exportar a Excel)
```

Instalar:
```bash
pip install pandas openpyxl
```

---

## ✨ Características Especiales

### Manejo de Decimales
- Todos los cálculos mantienen precisión decimal
- Redondeo automático a 2 decimales
- Ideal para valores en pesos colombianos

### Flexibilidad de Entrada
- ✅ Listas de diccionarios
- ✅ DataFrames de pandas
- ✅ Archivos CSV
- ✅ APIs/JSON

### Salida Estructura
- ✅ DataFrames (fácil de manipular)
- ✅ Exportable a Excel
- ✅ Legible en tablas
- ✅ Compatible con reportes

---

## 📚 Ejemplos Completos

Ejecuta para ver todos los ejemplos:
```bash
python3 ejemplo_uso_avanzado.py
```

Incluye:
1. Listas de diccionarios
2. DataFrames
3. Resumen combinado
4. Exportación a Excel
5. Casos especiales

---

## 📞 Notas

- Las fórmulas siguen la legislación laboral colombiana
- Compatible con años 2024 en adelante
- Validaciones automáticas de integridad de datos
- Código modular y reutilizable

---

**Versión 1.0** | © 2024 | Liquidación de Nómina

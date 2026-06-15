# 🗓️ Feature: Cálculo Automático de Días Laborados desde Fechas

## ¿Qué es?

Feature que calcula automáticamente los días laborados (días_laborados) a partir de dos fechas:
- **Fecha de Entrada** (fecha_entrada, fecha_inicio, fecha_ingreso, etc.)
- **Fecha de Retiro** (fecha_retiro, fecha_fin, fecha_salida, etc.)

## ¿Por qué?

En lugar de ingresar manualmente los días trabajados por cada empleado, el sistema puede calcularlo automáticamente:

```
días_laborados = fecha_retiro - fecha_entrada
```

---

## Cómo Funciona

### 1. Detección de Columnas

El sistema busca automáticamente cualquiera de estos nombres (sin distinción de mayúsculas):

**Fecha de Entrada:**
- `fecha_entrada` ← Recomendado
- `fecha_inicio`
- `fecha_ingreso`
- `start_date`
- `fecha_inicio_periodo`

**Fecha de Retiro:**
- `fecha_retiro` ← Recomendado
- `fecha_fin`
- `fecha_salida`
- `end_date`
- `fecha_fin_periodo`
- `fecha_termino`

### 2. Prioridad de Cálculo

El sistema intenta calcular días en este orden:

1. ✅ Si existe columna `dias_laborados` → **Usa ese valor**
2. ✅ Si existen ambas fechas → **Calcula automáticamente**
3. ✅ Si faltan todas → **Usa 30 días por defecto**

```
if tiene_dias:
    días = valor_columna_dias
elif tiene_fecha_inicio AND tiene_fecha_fin:
    días = (fecha_fin - fecha_inicio).days
else:
    días = 30
```

### 3. Manejo de Errores

Si las fechas no se pueden parsear correctamente:
- Intenta diferentes formatos automáticamente
- Si fallan todas: usa 30 días como fallback
- No genera error, continúa el cálculo

```python
try:
    fecha_inicio = pd.to_datetime(valor)
    fecha_fin = pd.to_datetime(valor)
    dias = (fecha_fin - fecha_inicio).days
except Exception:
    dias = 30  # Fallback seguro
```

---

## Ejemplo de Uso

### Entrada (Excel)
```
documento | nombre              | salario_mensual | fecha_entrada | fecha_retiro
1020304050| Juan García Pérez   | 2500000        | 2025-01-01   | 2025-06-30
1020304051| María Rodríguez G.  | 3000000        | 2024-06-01   | 2025-06-14
```

### Proceso
```
Juan García:     2025-06-30 - 2025-01-01 = 180 días ✓
María Rodríguez: 2025-06-14 - 2024-06-01 = 378 días ✓
```

### Salida (Cálculo)
```
Juan García:
  • Días Laborados: 180
  • Cesantías: $1,250,000
  • Prima: $1,250,000
  • Vacaciones: $625,000
  • Total: $3,750,000

María Rodríguez:
  • Días Laborados: 378
  • Cesantías: $3,150,000
  • Prima: $3,150,000
  • Vacaciones: $1,575,000
  • Total: $11,182,500
```

---

## Validación en Frontend

La pantalla de Prestaciones ahora valida:

✅ **Si tienes:**
- Columna `dias_laborados` → Calcula automáticamente
- Columnas `fecha_entrada` Y `fecha_retiro` → Calcula automáticamente
- Ninguna de las anteriores → Usa 30 días por defecto

⚠️ **Si falta ALGUNA de las fechas:**
- Si tienes `fecha_entrada` pero NO `fecha_retiro`
- Si tienes `fecha_retiro` pero NO `fecha_entrada`
- → Muestra advertencia y usa 30 días por defecto

---

## Cambios de Código

### 1. liquidacion_prestaciones.py
**Líneas 36-38:** Agregadas más opciones de nombres para columnas de fecha
```python
columnas_fecha_inicio = ['fecha_inicio', 'fecha_ingreso', 'start_date', 
                         'fecha_inicio_periodo', 'fecha entrada', 'fecha_entrada']
columnas_fecha_fin = ['fecha_fin', 'fecha_salida', 'end_date', 
                      'fecha_fin_periodo', 'fecha_termino', 'fecha retiro', 'fecha_retiro']
```

**Líneas 70-77:** Lógica de cálculo desde fechas
```python
elif col_fecha_inicio and col_fecha_fin:
    try:
        fecha_inicio = pd.to_datetime(emp.get(col_fecha_inicio))
        fecha_fin = pd.to_datetime(emp.get(col_fecha_fin))
        dias = (fecha_fin - fecha_inicio).days
    except Exception as e:
        dias = 30
```

### 2. frontend/app.py
**Líneas 620-621:** Detección de columnas de fecha
```python
columnas_fecha_inicio = ['fecha_inicio', 'fecha_ingreso', 'start_date', ...]
columnas_fecha_fin = ['fecha_fin', 'fecha_salida', 'end_date', ...]
```

**Líneas 628-629:** Validación de disponibilidad
```python
tiene_fecha_inicio = any(col in df_empleados.columns for col in columnas_fecha_inicio)
tiene_fecha_fin = any(col in df_empleados.columns for col in columnas_fecha_fin)
```

**Línea 642:** Bug Fix - Condición correcta
```python
# ANTES (incorrecto):
if not tiene_dias and (not tiene_fecha_inicio and not tiene_fecha_fin):

# AHORA (correcto):
if not tiene_dias and (not tiene_fecha_inicio or not tiene_fecha_fin):
```

---

## Testing

### Archivo de Prueba Incluido
Descarga: `empleados_con_fechas.xlsx`

```
documento,nombre,salario_mensual,fecha_entrada,fecha_retiro
1020304050,Juan García Pérez,2500000,2025-01-01,2025-06-30
1020304051,María Rodríguez García,3000000,2024-06-01,2025-06-14
```

### Ejecutar Prueba
```bash
python3 test_liquidacion_dates.py     # Test módulo
python3 test_frontend_dates.py        # Test workflow completo
```

### Resultados Esperados
```
✅ Prestaciones calculadas correctamente
✅ PDF generado exitosamente
✅ Totales: $14,932,500 en prestaciones
```

---

## Compatibilidad

| Feature | Versión |
|---------|---------|
| Cálculo de días desde fechas | v2.0+ |
| Detección flexible de columnas | v2.0+ |
| Fallback a 30 días | v2.0+ |
| PDF de prestaciones | v2.0+ |

---

## Limitaciones Conocidas

1. ❌ No valida que fecha_retiro > fecha_entrada
2. ❌ No maneja feriados (usa días calendario)
3. ❌ No soporta períodos parciales complejos
4. ⚠️ Usa 30 días si alguna fecha es inválida

---

## Preguntas Frecuentes

**P: ¿Puedo mezclar días y fechas en el mismo archivo?**
A: Sí. Para cada empleado:
- Si tiene `dias_laborados` → usa ese
- Si no pero tiene fechas → calcula desde fechas
- Si no tiene nada → usa 30 días

**P: ¿Qué formatos de fecha soporta?**
A: Pandas soporta automáticamente casi todos:
- ISO: 2025-06-30
- Corta: 30/06/2025, 06/30/2025
- Larga: 30 de Junio de 2025
- Timestamp de Excel

**P: ¿Qué pasa si la fecha de retiro es anterior a la entrada?**
A: El cálculo usa la diferencia como está (puede ser negativo). 
Recomendación: Validar datos antes de cargar.

**P: ¿Debo actualizar el backend FastAPI?**
A: No. El cambio es en frontend (app.py) y módulo de cálculo (liquidacion_prestaciones.py). 
El backend ya tiene las rutas necesarias.

---

## Soporte

Para reportar bugs o sugerir mejoras:
1. Verifica que uses los nombres correctos de columnas
2. Ejecuta los scripts de prueba para aislar el problema
3. Revisa el archivo `TEMPLATE_EMPLEADOS_CON_FECHAS.md` para ejemplos

---

**Versión:** 2.0  
**Fecha:** 2026-06-14  
**Status:** ✅ Funcional y Probado

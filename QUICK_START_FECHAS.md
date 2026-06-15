# ⚡ Quick Start: Cálculo de Prestaciones con Fechas

## ¿Qué fue arreglado?
✅ La feature de cálculo automático de días desde fechas ahora funciona correctamente.

## 🚀 Opción 1: Prueba Rápida (2 minutos)

### 1. Descarga el archivo de ejemplo
Usa el archivo incluido: **`empleados_con_fechas.xlsx`**

```
documento      | nombre                    | salario_mensual | fecha_entrada | fecha_retiro
1020304050     | Juan García Pérez         | 2500000        | 2025-01-01   | 2025-06-30
1020304051     | María Rodríguez García    | 3000000        | 2024-06-01   | 2025-06-14
```

### 2. Abre la aplicación
```bash
streamlit run frontend/app.py
```

### 3. Prueba en 3 pasos:
1. Pestaña "📄 Cargar Archivo" → carga `empleados_con_fechas.xlsx`
2. Pestaña "🎓 Prestaciones" → click "🧮 Liquidar Prestaciones"
3. Descarga el PDF con los cálculos

**Resultado esperado:** $14,932,500 en prestaciones totales

---

## 🎯 Opción 2: Usa Tu Propio Archivo

### Paso 1: Crea un Excel con estas columnas
```
documento | nombre | salario_mensual | fecha_entrada | fecha_retiro
----------|--------|-----------------|---------------|-------------
1020304050| Juan   | 2500000        | 2025-01-01   | 2025-06-30
```

**Nombres válidos para las columnas:**

**Entrada:**
- `fecha_entrada` ✅
- `fecha_inicio`
- `fecha_ingreso`
- `start_date`

**Retiro:**
- `fecha_retiro` ✅
- `fecha_fin`
- `fecha_salida`
- `end_date`

### Paso 2: Carga y calcula
1. App → "📄 Cargar Archivo" → carga tu archivo
2. "🎓 Prestaciones" → "🧮 Liquidar Prestaciones"
3. Descarga el PDF

---

## 🔧 Opción 3: Tests Automatizados

Verifica que todo funciona con los tests incluidos:

```bash
# Test completo (6 escenarios)
python3 test_all_scenarios.py

# Test específico con archivo ejemplo
python3 test_liquidacion_dates.py
```

---

## ⚙️ Cambios Técnicos (Para Desarrolladores)

### Bug Fix - frontend/app.py:642
```diff
- if not tiene_dias and (not tiene_fecha_inicio and not tiene_fecha_fin):
+ if not tiene_dias and (not tiene_fecha_inicio or not tiene_fecha_fin):
```

**Por qué:** Validación correcta de que AMBAS fechas existan (OR en lugar de AND).

### Soporte de Columnas
Archivo `liquidacion_prestaciones.py` (líneas 36-38) soporta múltiples nombres:

```python
columnas_fecha_inicio = [
    'fecha_entrada', 'fecha_inicio', 'fecha_ingreso', 
    'start_date', 'fecha_inicio_periodo'
]
columnas_fecha_fin = [
    'fecha_retiro', 'fecha_fin', 'fecha_salida',
    'end_date', 'fecha_fin_periodo', 'fecha_termino'
]
```

---

## ❓ FAQ Rápido

**P: Mi archivo no tiene fechas, solo días. ¿Funciona?**
A: ✅ Sí. Si tienes columna `dias_laborados`, la usa directamente.

**P: ¿Qué pasa sin días ni fechas?**
A: ✅ Usa 30 días automáticamente.

**P: ¿Puedo mezclar algunos con días y otros con fechas?**
A: ✅ Sí. Cada empleado usa lo disponible.

**P: Las fechas deben estar en formato específico?**
A: ✅ Excel lo maneja - YYYY-MM-DD, DD/MM/YYYY, etc.

**P: ¿Debo actualizar el backend?**
A: ❌ No. Solo cambió el frontend (app.py).

---

## 📂 Archivos Nuevos

| Archivo | Uso |
|---------|-----|
| `empleados_con_fechas.xlsx` | Ejemplo listo para usar |
| `test_all_scenarios.py` | Suite de 6 tests |
| `TEMPLATE_EMPLEADOS_CON_FECHAS.md` | Guía de columnas |
| `FEATURE_FECHA_DIAS_LABORADOS.md` | Docs técnica completa |
| `RESOLUCION_FECHA_DIAS.md` | Detalles de la fix |

---

## ✅ Verificación

**¿Cómo sé si está funcionando?**

1. Carga `empleados_con_fechas.xlsx`
2. Calcula prestaciones
3. Deberías ver:
   - Juan García: 180 días
   - María Rodríguez: 378 días

4. Totales: $14,932,500

Si lo ves, ✅ **¡Está funcionando!**

---

## 🎓 Fórmulas Utilizadas

```
Cesantías = (Salario × Días) / 360
Prima = (Salario × Días) / 360
Vacaciones = (Salario × Días) / 720
Intereses Cesantías = (Cesantías × Días) / 360
```

---

**¿Dudas?** Revisa:
- `TEMPLATE_EMPLEADOS_CON_FECHAS.md` para estructura del archivo
- `FEATURE_FECHA_DIAS_LABORADOS.md` para detalles técnicos
- `RESOLUCION_FECHA_DIAS.md` para entender qué se arregló

✨ **¡Listo para usar!**

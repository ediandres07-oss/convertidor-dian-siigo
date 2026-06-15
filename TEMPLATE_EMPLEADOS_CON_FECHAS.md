# 📋 Template: Cómo Crear un Archivo para Calcular Prestaciones

## Opción 1: Usando Columna de Días (Más Simple)

Si ya sabes cuántos días trabajó cada empleado, crea un archivo con estas columnas:

| documento | nombre | salario_mensual | dias_laborados |
|-----------|--------|-----------------|----------------|
| 1020304050 | Juan García | 2500000 | 180 |
| 1020304051 | María Rodríguez | 3000000 | 200 |

**Nombres alternativos para la columna de días:**
- `dias_laborados` ✅ (recomendado)
- `dias`
- `dias_trabajados`
- `dias_trabajo`
- `days`

---

## Opción 2: Usando Fechas de Entrada y Retiro (Automático)

El sistema calcula automáticamente los días entre dos fechas:

| documento | nombre | salario_mensual | fecha_entrada | fecha_retiro |
|-----------|--------|-----------------|---------------|--------------|
| 1020304050 | Juan García | 2500000 | 2025-01-01 | 2025-06-30 |
| 1020304051 | María Rodríguez | 3000000 | 2024-06-01 | 2025-06-14 |

**Nombres alternativos para fecha de entrada:**
- `fecha_entrada` ✅ (recomendado)
- `fecha_inicio`
- `fecha_ingreso`
- `start_date`
- `fecha_inicio_periodo`

**Nombres alternativos para fecha de retiro:**
- `fecha_retiro` ✅ (recomendado)
- `fecha_fin`
- `fecha_salida`
- `end_date`
- `fecha_fin_periodo`
- `fecha_termino`

---

## Opción 3: Columna de Nombre (Variaciones)

El sistema acepta diferentes nombres para la columna de empleado:
- `nombre` ✅ (recomendado)
- `name`
- `empleado`

---

## Opción 4: Columna de Documento (Variaciones)

El sistema acepta diferentes nombres para la cédula/identificación:
- `documento` ✅ (recomendado)
- `doc`
- `cedula`
- `id`

---

## Opción 5: Columna de Salario (Variaciones)

El sistema acepta diferentes nombres para el salario:
- `salario_mensual` ✅ (recomendado)
- `salario`
- `salary`
- `sueldo`

---

## Si Falta Información: Usa Default de 30 Días

Si tu archivo **NO tiene**:
- ❌ Columna de días laborados
- ❌ Ambas columnas de fechas (entrada y retiro)

El sistema usará automáticamente **30 días por defecto** para cada empleado.

**Ejemplo:**

| documento | nombre | salario_mensual |
|-----------|--------|-----------------|
| 1020304050 | Juan García | 2500000 |
| 1020304051 | María Rodríguez | 3000000 |

→ Se calcularán prestaciones para **30 días** cada uno

---

## Ejemplo Completo: Archivo descargable

Descarga el archivo de ejemplo aquí:
📥 [`empleados_con_fechas.xlsx`](empleados_con_fechas.xlsx)

**Contenido:**
```
documento,nombre,salario_mensual,fecha_entrada,fecha_retiro
1020304050,Juan García Pérez,2500000,2025-01-01,2025-06-30
1020304051,María Rodríguez García,3000000,2024-06-01,2025-06-14
```

---

## Pasos para Usar:

1. **Descarga** el template o crea tu archivo siguiendo una de las opciones arriba
2. **Llena los datos** de tus empleados
3. **Carga el archivo** en la aplicación (pestaña "📄 Cargar Archivo")
4. **Haz clic** en "🧮 Liquidar Prestaciones"
5. **Descarga el PDF** con el cálculo de cesantías, prima, vacaciones, etc.

---

## Fórmulas Usadas (Colombia)

```
Cesantías = (Salario × Días) / 360
Intereses = (Cesantías × Días) / 360
Prima = (Salario × Días) / 360
Vacaciones = (Salario × Días) / 720
```

---

## Preguntas Frecuentes

**P: ¿Qué pasa si mezclo fechas y días en el mismo archivo?**
A: El sistema prioriza la columna de días si existe. Si no existe, busca las fechas.

**P: ¿Las fechas deben estar en un formato específico?**
A: Excel maneja automáticamente el formato. Puedes usar YYYY-MM-DD o DD/MM/YYYY.

**P: ¿Puedo dejar vacías algunas celdas?**
A: Las columnas obligatorias son: documento, nombre, salario_mensual. Las otras pueden estar vacías (usarán defaults).

**P: ¿Cómo sé si mi archivo es correcto?**
A: Si cargas el archivo y el sistema muestra datos en la tabla, es correcto. Si muestra una advertencia, sigue las instrucciones.

---

**Versión:** 1.0  
**Última actualización:** 2026-06-14  
**Compatible con:** Liquidador de Prestaciones v2.0+

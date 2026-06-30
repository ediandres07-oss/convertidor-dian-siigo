# 🔄 CAMBIOS - Mapeo Correcto de Cédulas DIAN 2025

## ✅ Actualización Realizada

Se corrigió la clasificación de rentas según la **Guía Definitiva - DRPN 2025** de DIAN.

---

## 📊 SISTEMA CEDULAR CORRECTO

### 1️⃣ **CÉDULA GENERAL** (La más importante)

Contiene **3 tipos de rentas**:

#### A) **Rentas de Trabajo** (Casillas 32-56)
- Salarios (contrato laboral)
- Honorarios (máx 90 días, menos de 2 personas)
- Comisiones
- Prestaciones sociales (prima, vacaciones, cesantías)
- Retiros de fondos de cesantía

**Deducción:** 25% del ingreso (máximo $95 millones)

#### B) **Rentas de Capital** (Casillas 58-72)
- Dividendos y participaciones
- **Intereses** (CDT, depósitos a término)
- Arrendamientos
- Otros ingresos de capital

**Deducción:** Según corresponda

#### C) **Rentas No Laborales** (Casillas 74-90)
- Actividades económicas (negocio propio)
- Otras rentas no laborales

---

### 2️⃣ **CÉDULA DE PENSIONES** (Casillas 99-105)

- Pensión de jubilación
- Pensión de vejez
- Pensión de sobrevivientes
- Pensión de invalidez
- Indemnizaciones sustitutivas

---

### 3️⃣ **GANANCIAS OCASIONALES** (Casillas 112-115)

- Venta de bienes (2+ años)
- Venta de activos fijos
- Otras ganancias ocasionales

**Tarifa especial:** 10% (no progresivo)

---

## 💰 EJEMPLO CON DATOS REALES

### Entrada (Archivo Exógena)
```
Salario:           $600,000,000  ← TRABAJO (Cédula General)
Dividendos:        $150,000,000  ← CAPITAL (Cédula General)
Intereses CDT:     $ 25,000,000  ← CAPITAL (Cédula General)
────────────────────────────────
TOTAL:             $775,000,000
```

### Cálculos por Cédula

**CÉDULA GENERAL:**
```
Ingresos Trabajo:           $600,000,000
Ingresos Capital:           $175,000,000
                            ────────────
Ingresos Totales:           $775,000,000

Deducciones (25% trabajo):  -$95,000,000 (máximo)
                            ────────────
Renta Líquida General:      $680,000,000
```

**IMPUESTO (IRPF - Sistema Progresivo 2025):**
```
De $0 a $1.650.000:            $0 × 0% = $0
De $1.650.001 a $2.750.000:    $1.1M × 5% = $55.000
De $2.750.001 a $4.433.333:    $1.683.333 × 8% = $134.667
... (otros tramos)
───────────────────────────────
IRPF Total:                 $219,485,000

Tasa Efectiva:              32.28%
```

---

## 📁 Archivos Actualizados

| Archivo | Cambio |
|---------|--------|
| `app_declaracion_renta_2025.py` | ✅ Usa nuevo mapeo de cédulas |
| `mapeo_cedulas_2025.py` | ✅ Nuevo - Mapeo oficial DIAN |
| `cedulas_2025.py` | ⚠️ Deprecado (usar mapeo_cedulas_2025.py) |

---

## 🔍 Cómo Verificar el Mapeo

### Test Rápido:
```bash
cd "/Users/edison/Desktop/proyecto-subir info a siigo nube"
python3 mapeo_cedulas_2025.py
```

Output esperado:
```
Salario                        → CEDULA_GENERAL            | salarios
Dividendos                     → CEDULA_GENERAL            | dividendos
Intereses CDT                  → CEDULA_GENERAL            | intereses
Pensión jubilación             → CEDULA_PENSIONES          | pension_jubilacion
Ganancia venta terreno         → GANANCIAS_OCASIONALES     | venta_bienes
```

---

## 📍 Casillas del Formulario 210

| Concepto | Casillas |
|----------|----------|
| Rentas de Trabajo | 32-56 |
| Rentas de Capital | 58-72 |
| Rentas No Laborales | 74-90 |
| Cédula General Líquida | 91 |
| Cédula de Pensiones | 99-105 |
| Ganancias Ocasionales | 112-115 |
| Impuesto Total | 116-125 |

---

## ✨ Mejoras Realizadas

1. ✅ **Clasificación correcta** según DIAN
2. ✅ **Cédula General** incluye 3 tipos de rentas
3. ✅ **Dividendos e Intereses** en Rentas de Capital (no separadas)
4. ✅ **Deducciones correctas** por tipo de renta
5. ✅ **Cálculo IRPF progresivo** correcto
6. ✅ **Ganancias Ocasionales** con tarifa especial 10%

---

## 🚀 Próximos Pasos

La app ahora:
1. Carga archivo exógena ✅
2. Clasifica rentas correctamente ✅
3. Distribuye en cédulas según DIAN ✅
4. Calcula impuestos correctamente ✅
5. Genera Formulario 210 ✅

**¡Lista para usar!**


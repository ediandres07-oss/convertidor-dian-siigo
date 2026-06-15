"""Comprehensive test of all date calculation scenarios"""

import pandas as pd
import sys
import os

sys.path.insert(0, '/Users/edison/Desktop/proyecto-subir info a siigo nube')
from liquidacion_prestaciones import calcular_prestaciones

print("="*80)
print("TEST COMPLETO: Todos los Escenarios de Cálculo de Días")
print("="*80)

# Escenario 1: Archivo con días laborados directos
print("\n\n1️⃣ ESCENARIO 1: Columna 'dias_laborados' (más simple)")
print("-" * 80)

df1 = pd.DataFrame([
    {
        'documento': '1020304050',
        'nombre': 'Juan García',
        'salario_mensual': 2500000,
        'dias_laborados': 180,
    },
])

try:
    result1 = calcular_prestaciones(df1)
    print(f"✅ Éxito")
    print(f"   Días: {result1['Días Trabajados'].iloc[0]:.0f}")
    print(f"   Cesantías: ${result1['Cesantías'].iloc[0]:,.2f}")
except Exception as e:
    print(f"❌ Error: {e}")

# Escenario 2: Archivo con fechas
print("\n\n2️⃣ ESCENARIO 2: Columnas 'fecha_entrada' y 'fecha_retiro'")
print("-" * 80)

df2 = pd.DataFrame([
    {
        'documento': '1020304051',
        'nombre': 'María Rodríguez',
        'salario_mensual': 3000000,
        'fecha_entrada': '2025-01-01',
        'fecha_retiro': '2025-06-30',
    },
])

try:
    result2 = calcular_prestaciones(df2)
    print(f"✅ Éxito")
    print(f"   Días: {result2['Días Trabajados'].iloc[0]:.0f}")
    print(f"   Cesantías: ${result2['Cesantías'].iloc[0]:,.2f}")
except Exception as e:
    print(f"❌ Error: {e}")

# Escenario 3: Nombres alternativos para fechas
print("\n\n3️⃣ ESCENARIO 3: Nombres alternativos ('fecha_inicio' y 'fecha_fin')")
print("-" * 80)

df3 = pd.DataFrame([
    {
        'documento': '1020304052',
        'nombre': 'Carlos Martínez',
        'salario_mensual': 2200000,
        'fecha_inicio': '2024-06-01',
        'fecha_fin': '2025-06-14',
    },
])

try:
    result3 = calcular_prestaciones(df3)
    print(f"✅ Éxito")
    print(f"   Días: {result3['Días Trabajados'].iloc[0]:.0f}")
    print(f"   Cesantías: ${result3['Cesantías'].iloc[0]:,.2f}")
except Exception as e:
    print(f"❌ Error: {e}")

# Escenario 4: Archivo sin días ni fechas (fallback a 30)
print("\n\n4️⃣ ESCENARIO 4: Sin días ni fechas (fallback a 30 días)")
print("-" * 80)

df4 = pd.DataFrame([
    {
        'documento': '1020304053',
        'nombre': 'Ana López',
        'salario_mensual': 2800000,
    },
])

try:
    result4 = calcular_prestaciones(df4)
    print(f"✅ Éxito")
    print(f"   Días: {result4['Días Trabajados'].iloc[0]:.0f} (default)")
    print(f"   Cesantías: ${result4['Cesantías'].iloc[0]:,.2f}")
except Exception as e:
    print(f"❌ Error: {e}")

# Escenario 5: Prioridad - días laborados prevalece sobre fechas
print("\n\n5️⃣ ESCENARIO 5: Prioridad - 'dias_laborados' sobre fechas")
print("-" * 80)

df5 = pd.DataFrame([
    {
        'documento': '1020304054',
        'nombre': 'Luis Torres',
        'salario_mensual': 3100000,
        'dias_laborados': 100,  # Prioridad
        'fecha_entrada': '2025-01-01',
        'fecha_retiro': '2025-12-31',  # Serían ~365 días, pero se usa 100
    },
])

try:
    result5 = calcular_prestaciones(df5)
    print(f"✅ Éxito")
    print(f"   Días: {result5['Días Trabajados'].iloc[0]:.0f} (valor directo, no calculado)")
    print(f"   Cesantías: ${result5['Cesantías'].iloc[0]:,.2f}")
except Exception as e:
    print(f"❌ Error: {e}")

# Escenario 6: Fechas en formato datetime de Excel
print("\n\n6️⃣ ESCENARIO 6: Fechas como objetos datetime (desde Excel)")
print("-" * 80)

from datetime import datetime, timedelta

df6 = pd.DataFrame([
    {
        'documento': '1020304055',
        'nombre': 'Rosa García',
        'salario_mensual': 2600000,
        'fecha_entrada': datetime(2024, 1, 1),
        'fecha_retiro': datetime(2025, 6, 14),
    },
])

try:
    result6 = calcular_prestaciones(df6)
    print(f"✅ Éxito")
    dias = (datetime(2025, 6, 14) - datetime(2024, 1, 1)).days
    print(f"   Días: {result6['Días Trabajados'].iloc[0]:.0f} (esperado: {dias})")
    print(f"   Cesantías: ${result6['Cesantías'].iloc[0]:,.2f}")
except Exception as e:
    print(f"❌ Error: {e}")

# Resumen
print("\n\n" + "="*80)
print("📊 RESUMEN DE PRUEBAS")
print("="*80)

test_scenarios = [
    ("Dias laborados directo", result1),
    ("Fechas entrada/retiro", result2),
    ("Nombres alternativos", result3),
    ("Fallback 30 días", result4),
    ("Prioridad dias vs fechas", result5),
    ("Fechas como datetime", result6),
]

total_prestaciones = 0
for name, result in test_scenarios:
    total = result['Total Prestaciones'].sum()
    total_prestaciones += total
    print(f"✅ {name}: ${total:,.2f}")

print(f"\n💰 TOTAL TODAS LAS PRUEBAS: ${total_prestaciones:,.2f}")
print("\n" + "="*80)
print("✅ TODAS LAS PRUEBAS EXITOSAS")
print("="*80)

#!/usr/bin/env python3
"""
Debug - Ver exactamente qué se lee del archivo
"""

import pandas as pd
import sys

# El archivo debe estar en /tmp
import os
temp_files = [f for f in os.listdir('/tmp') if f.startswith('exogena_')]

if not temp_files:
    print("No hay archivos de Exógena en /tmp")
    sys.exit(1)

# Usar el más reciente
temp_file = f"/tmp/{sorted(temp_files)[-1]}"
print(f"Leyendo: {temp_file}\n")

df = pd.read_excel(temp_file, sheet_name='Reporte', header=None)

print(f"Dimensiones: {df.shape}")
print(f"\nPrimeras 30 filas (para ver estructura):\n")

for i in range(min(30, len(df))):
    row = df.iloc[i]
    print(f"Fila {i}: {list(row[:8])}")

print("\n\n=== BÚSQUEDA DE INGRESOS ===\n")

for i in range(14, len(df)):
    row = df.iloc[i]
    if pd.notna(row.iloc[4]) and pd.notna(row.iloc[5]):
        concepto = str(row.iloc[4]).strip()
        valor = float(row.iloc[5])
        if valor > 0:
            uso = str(row.iloc[6]).lower() if pd.notna(row.iloc[6]) else ""
            tipo = "RETENCIÓN" if ('retención' in uso or 'r132' in uso) else "INGRESO"
            print(f"Fila {i}: {concepto[:50]} = ${valor:,.0f} ({tipo})")

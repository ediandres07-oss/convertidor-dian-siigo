"""
Script para generar un archivo Excel de ejemplo
"""
import pandas as pd
from openpyxl import Workbook

# Crear datos de ejemplo
empleados = pd.DataFrame({
    'nombre': ['Juan García López', 'María Rodríguez', 'Carlos Martínez', 'Ana Pérez', 'Luis Sánchez'],
    'documento': ['1234567890', '9876543210', '5555666777', '4444333222', '7777888999'],
    'salario_mensual': [2_500_000, 3_000_000, 2_200_000, 4_000_000, 2_800_000],
    'dias_laborados': [30, 30, 28, 30, 30],
    'cesantias_acum': [0, 500_000, 0, 1_000_000, 250_000],
    'vacaciones_acum': [0, 200_000, 0, 500_000, 0]
})

# Crear datos de parámetros
parametros = pd.DataFrame({
    'parametro': ['salud', 'pension', 'fondo_solidaridad'],
    'valor': [4, 4, 1]
})

# Crear datos de novedades
novedades = pd.DataFrame({
    'documento': ['1234567890', '4444333222'],
    'tipo_novedad': ['retencion', 'retencion'],
    'valor': [50_000, 100_000]
})

# Guardar en Excel
with pd.ExcelWriter('ejemplo_liquidacion.xlsx', engine='openpyxl') as writer:
    empleados.to_excel(writer, sheet_name='Empleados', index=False)
    parametros.to_excel(writer, sheet_name='Parametros', index=False)
    novedades.to_excel(writer, sheet_name='Novedades', index=False)

print("✅ Archivo 'ejemplo_liquidacion.xlsx' creado exitosamente")

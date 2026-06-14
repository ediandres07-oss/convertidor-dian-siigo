"""
Ejemplos de uso avanzado de las funciones de Prima y Vacaciones
Demuestra cómo usar con DataFrames, JSON, etc.
"""

import pandas as pd
from prima_servicios import calcular_prima
from vacaciones_proporcionales import calcular_vacaciones


def ejemplo_1_listas():
    """Ejemplo 1: Usando listas de diccionarios"""
    print("\n" + "=" * 90)
    print("EJEMPLO 1: Cálculo con LISTAS de diccionarios")
    print("=" * 90)

    empleados = [
        {'nombre': 'Ana Gómez', 'salario_mensual': 1_500_000, 'auxilio_transporte': 140_000, 'dias_trabajados': 30},
        {'nombre': 'Pedro Ruiz', 'salario_mensual': 2_800_000, 'auxilio_transporte': 140_000, 'dias_trabajados': 28},
    ]

    print("\n📌 Prima de Servicios:")
    df_prima = calcular_prima(empleados)
    print(df_prima.to_string(index=False))

    print("\n📌 Vacaciones:")
    df_vaca = calcular_vacaciones(empleados)
    print(df_vaca.to_string(index=False))


def ejemplo_2_dataframe():
    """Ejemplo 2: Usando DataFrames directamente"""
    print("\n" + "=" * 90)
    print("EJEMPLO 2: Cálculo con DATAFRAME")
    print("=" * 90)

    # Crear DataFrame desde archivo CSV simulado
    df_empleados = pd.DataFrame({
        'nombre': ['Sofía López', 'Diego Martín', 'Carla Soto'],
        'salario_mensual': [3_500_000, 2_000_000, 2_700_000],
        'auxilio_transporte': [140_000, 140_000, 140_000],
        'dias_trabajados': [30, 30, 20]
    })

    print("\n📌 Datos de entrada:")
    print(df_empleados.to_string(index=False))

    print("\n📌 Prima de Servicios:")
    df_prima = calcular_prima(df_empleados)
    print(df_prima.to_string(index=False))

    print("\n📌 Vacaciones:")
    df_vaca = calcular_vacaciones(df_empleados)
    print(df_vaca.to_string(index=False))


def ejemplo_3_combinado():
    """Ejemplo 3: Cálculo combinado de Prima y Vacaciones"""
    print("\n" + "=" * 90)
    print("EJEMPLO 3: RESUMEN COMBINADO (Prima + Vacaciones)")
    print("=" * 90)

    empleados = [
        {'nombre': 'Roberto Silva', 'salario_mensual': 2_200_000, 'auxilio_transporte': 140_000, 'dias_trabajados': 30},
        {'nombre': 'Juana Morales', 'salario_mensual': 3_800_000, 'auxilio_transporte': 140_000, 'dias_trabajados': 25},
    ]

    # Calcular prima y vacaciones
    df_prima = calcular_prima(empleados)
    df_vaca = calcular_vacaciones(empleados)

    # Combinar resultados
    df_resumen = pd.DataFrame({
        'Nombre': df_prima['nombre'],
        'Salario': df_prima['salario_mensual'],
        'Días': df_prima['dias_trabajados'],
        'Prima': df_prima['valor_prima'],
        'Vacaciones': df_vaca['valor_vacaciones'],
        'Total Liquidación': df_prima['valor_prima'] + df_vaca['valor_vacaciones']
    })

    print("\n📊 Resumen de liquidación:")
    print(df_resumen.to_string(index=False))

    print("\n💰 TOTALES:")
    print(f"   Total Prima: ${df_prima['valor_prima'].sum():,.2f}")
    print(f"   Total Vacaciones: ${df_vaca['valor_vacaciones'].sum():,.2f}")
    print(f"   GRAN TOTAL: ${(df_prima['valor_prima'].sum() + df_vaca['valor_vacaciones'].sum()):,.2f}")


def ejemplo_4_exportar():
    """Ejemplo 4: Exportar resultados a Excel"""
    print("\n" + "=" * 90)
    print("EJEMPLO 4: EXPORTAR RESULTADOS A EXCEL")
    print("=" * 90)

    empleados = [
        {'nombre': 'Mariana Ríos', 'salario_mensual': 2_600_000, 'auxilio_transporte': 140_000, 'dias_trabajados': 30},
        {'nombre': 'Nicolás Vega', 'salario_mensual': 3_100_000, 'auxilio_transporte': 140_000, 'dias_trabajados': 30},
    ]

    # Calcular
    df_prima = calcular_prima(empleados)
    df_vaca = calcular_vacaciones(empleados)

    # Exportar a Excel
    archivo = 'resultados_liquidacion.xlsx'

    with pd.ExcelWriter(archivo, engine='openpyxl') as writer:
        df_prima.to_excel(writer, sheet_name='Prima', index=False)
        df_vaca.to_excel(writer, sheet_name='Vacaciones', index=False)

        # Hoja de resumen
        df_resumen = pd.DataFrame({
            'Concepto': ['Prima', 'Vacaciones', 'Total'],
            'Valor Total': [
                df_prima['valor_prima'].sum(),
                df_vaca['valor_vacaciones'].sum(),
                df_prima['valor_prima'].sum() + df_vaca['valor_vacaciones'].sum()
            ]
        })
        df_resumen.to_excel(writer, sheet_name='Resumen', index=False)

    print(f"\n✅ Archivo exportado: {archivo}")
    print("\nContenido del archivo:")
    print("\n📌 Hoja 'Prima':")
    print(df_prima.to_string(index=False))
    print("\n📌 Hoja 'Vacaciones':")
    print(df_vaca.to_string(index=False))


def ejemplo_5_casos_especiales():
    """Ejemplo 5: Casos especiales y validaciones"""
    print("\n" + "=" * 90)
    print("EJEMPLO 5: CASOS ESPECIALES Y VALIDACIONES")
    print("=" * 90)

    empleados = [
        # Caso normal
        {'nombre': 'caso Normal', 'salario_mensual': 2_000_000, 'dias_trabajados': 30},

        # Caso: sin auxilio (solo salario)
        {'nombre': 'Sin Auxilio', 'salario_mensual': 2_500_000, 'auxilio_transporte': 0, 'dias_trabajados': 30},

        # Caso: medio mes
        {'nombre': 'Medio Mes', 'salario_mensual': 3_000_000, 'dias_trabajados': 15},

        # Caso: ingreso tardío
        {'nombre': 'Ingreso Tardío', 'salario_mensual': 2_200_000, 'dias_trabajados': 10},

        # Caso: año completo
        {'nombre': 'Año Completo', 'salario_mensual': 2_800_000, 'dias_trabajados': 360},
    ]

    print("\n📌 Prima de Servicios:")
    df_prima = calcular_prima(empleados)
    print(df_prima.to_string(index=False))

    print("\n📌 Vacaciones:")
    df_vaca = calcular_vacaciones(empleados)
    print(df_vaca.to_string(index=False))

    # Análisis
    print("\n" + "-" * 90)
    print("ANÁLISIS:")
    print("-" * 90)
    print(f"Empleado con mayor prima: {df_prima.loc[df_prima['valor_prima'].idxmax(), 'nombre']} (${df_prima['valor_prima'].max():,.2f})")
    print(f"Empleado con menor prima: {df_prima.loc[df_prima['valor_prima'].idxmin(), 'nombre']} (${df_prima['valor_prima'].min():,.2f})")
    print(f"Empleado con mayor vacaciones: {df_vaca.loc[df_vaca['valor_vacaciones'].idxmax(), 'nombre']} (${df_vaca['valor_vacaciones'].max():,.2f})")
    print(f"Empleado con menor vacaciones: {df_vaca.loc[df_vaca['valor_vacaciones'].idxmin(), 'nombre']} (${df_vaca['valor_vacaciones'].min():,.2f})")


if __name__ == "__main__":
    print("\n")
    print("╔" + "=" * 88 + "╗")
    print("║" + "EJEMPLOS DE USO AVANZADO - PRIMA Y VACACIONES".center(88) + "║")
    print("╚" + "=" * 88 + "╝")

    ejemplo_1_listas()
    ejemplo_2_dataframe()
    ejemplo_3_combinado()
    ejemplo_4_exportar()
    ejemplo_5_casos_especiales()

    print("\n" + "=" * 90)
    print("✅ EJEMPLOS COMPLETADOS")
    print("=" * 90 + "\n")

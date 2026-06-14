"""
Cálculo de Prima de Servicios para empleados en Colombia
Prima = (salario_mensual + auxilio_transporte) * dias_trabajados / 360
"""

import pandas as pd
from typing import List, Dict, Union


def validar_empleado(empleado: Dict) -> tuple[bool, str]:
    """
    Valida los datos de un empleado.

    Args:
        empleado: Diccionario con datos del empleado

    Returns:
        Tupla (válido, mensaje_error)
    """
    campos_requeridos = ['nombre', 'salario_mensual', 'dias_trabajados']

    # Validar campos requeridos
    for campo in campos_requeridos:
        if campo not in empleado:
            return False, f"Campo '{campo}' faltante"

    # Validar que salario sea positivo
    if empleado['salario_mensual'] < 0:
        return False, "El salario no puede ser negativo"

    # Validar que días sea positivo
    if empleado['dias_trabajados'] < 0:
        return False, "Los días trabajados no pueden ser negativos"

    # Validar que días no exceda 360
    if empleado['dias_trabajados'] > 360:
        return False, "Los días trabajados no pueden exceder 360"

    # Validar auxilio_transporte si existe
    if 'auxilio_transporte' in empleado and empleado['auxilio_transporte'] < 0:
        return False, "El auxilio de transporte no puede ser negativo"

    return True, "Válido"


def calcular_prima_empleado(empleado: Dict) -> Dict:
    """
    Calcula la prima de servicios para un empleado.

    Args:
        empleado: Diccionario con:
            - nombre (str)
            - salario_mensual (float)
            - dias_trabajados (float)
            - auxilio_transporte (float, opcional, default=0)

    Returns:
        Diccionario con:
            - nombre
            - salario_mensual
            - auxilio_transporte
            - dias_trabajados
            - base_prima
            - valor_prima
    """
    # Validar
    valido, mensaje = validar_empleado(empleado)
    if not valido:
        raise ValueError(f"Empleado {empleado.get('nombre', 'desconocido')}: {mensaje}")

    # Obtener datos (con valores por defecto)
    nombre = empleado['nombre']
    salario = float(empleado['salario_mensual'])
    dias = float(empleado['dias_trabajados'])
    auxilio = float(empleado.get('auxilio_transporte', 0))

    # Calcular base (salario + auxilio)
    base_prima = salario + auxilio

    # Calcular prima: (salario + auxilio) * días / 360
    valor_prima = (base_prima * dias) / 360

    # Redondear a 2 decimales
    valor_prima = round(valor_prima, 2)
    base_prima = round(base_prima, 2)

    return {
        'nombre': nombre,
        'salario_mensual': round(salario, 2),
        'auxilio_transporte': round(auxilio, 2),
        'dias_trabajados': dias,
        'base_prima': base_prima,
        'valor_prima': valor_prima
    }


def calcular_prima(empleados: Union[List[Dict], pd.DataFrame]) -> pd.DataFrame:
    """
    Calcula la prima de servicios para una lista de empleados.

    Args:
        empleados: Lista de diccionarios o DataFrame con datos de empleados

    Returns:
        DataFrame con resultados

    Ejemplo:
        >>> empleados = [
        ...     {'nombre': 'Juan', 'salario_mensual': 2000000, 'dias_trabajados': 30},
        ...     {'nombre': 'María', 'salario_mensual': 2500000, 'dias_trabajados': 30, 'auxilio_transporte': 120000}
        ... ]
        >>> resultado = calcular_prima(empleados)
    """
    # Convertir DataFrame a lista de diccionarios si es necesario
    if isinstance(empleados, pd.DataFrame):
        empleados = empleados.to_dict('records')

    if not empleados:
        raise ValueError("La lista de empleados está vacía")

    resultados = []

    for empleado in empleados:
        try:
            resultado = calcular_prima_empleado(empleado)
            resultados.append(resultado)
        except ValueError as e:
            print(f"⚠️  Error: {str(e)}")
            continue

    # Convertir a DataFrame
    df_resultado = pd.DataFrame(resultados)

    return df_resultado[['nombre', 'salario_mensual', 'auxilio_transporte', 'dias_trabajados', 'base_prima', 'valor_prima']]


if __name__ == "__main__":
    print("=" * 90)
    print("CÁLCULO DE PRIMA DE SERVICIOS - COLOMBIA")
    print("=" * 90)
    print()

    # Crear lista de empleados de ejemplo
    empleados = [
        {
            'nombre': 'Juan García López',
            'salario_mensual': 2_500_000,
            'auxilio_transporte': 140_000,
            'dias_trabajados': 30
        },
        {
            'nombre': 'María Rodríguez Pérez',
            'salario_mensual': 3_200_000,
            'auxilio_transporte': 140_000,
            'dias_trabajados': 30
        },
        {
            'nombre': 'Carlos Martínez',
            'salario_mensual': 1_800_000,
            'auxilio_transporte': 140_000,
            'dias_trabajados': 25  # Medio mes
        },
        {
            'nombre': 'Ana Sánchez',
            'salario_mensual': 4_000_000,
            'dias_trabajados': 15  # 15 días (sin auxilio)
        }
    ]

    # Calcular prima
    try:
        df_prima = calcular_prima(empleados)

        print("📊 RESULTADOS DEL CÁLCULO DE PRIMA\n")
        print(df_prima.to_string(index=False))

        print("\n" + "=" * 90)
        print("TOTALES")
        print("=" * 90)

        total_base = df_prima['base_prima'].sum()
        total_prima = df_prima['valor_prima'].sum()
        promedio_prima = df_prima['valor_prima'].mean()

        print(f"Total de empleados procesados: {len(df_prima)}")
        print(f"Suma total de bases prima: ${total_base:,.2f}")
        print(f"Suma total de prima: ${total_prima:,.2f}")
        print(f"Promedio de prima: ${promedio_prima:,.2f}")

        print("\n" + "=" * 90)
        print("FÓRMULA UTILIZADA")
        print("=" * 90)
        print("Prima = (Salario Mensual + Auxilio Transporte) × Días Trabajados ÷ 360")
        print()
        print("Donde:")
        print("  • Salario Mensual: valor acordado en el contrato")
        print("  • Auxilio Transporte: subsidio de transporte (opcional)")
        print("  • Días Trabajados: días laborados en el período")
        print()

    except ValueError as e:
        print(f"❌ Error: {str(e)}")

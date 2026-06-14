"""
Cálculo de Vacaciones Proporcionales para empleados en Colombia
Vacaciones = salario_mensual * dias_trabajados / 720
"""

import pandas as pd
from typing import List, Dict, Union


def validar_empleado_vacaciones(empleado: Dict) -> tuple[bool, str]:
    """
    Valida los datos de un empleado para cálculo de vacaciones.

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

    # Validar que días no exceda 360 (un año completo)
    if empleado['dias_trabajados'] > 360:
        return False, "Los días trabajados no pueden exceder 360 días"

    return True, "Válido"


def calcular_vacaciones_empleado(empleado: Dict) -> Dict:
    """
    Calcula las vacaciones proporcionales para un empleado.

    En Colombia, las vacaciones se calculan como:
    Vacaciones = salario_mensual * dias_trabajados / 720

    Nota: 720 = 2 × 360 (porque los empleados tienen derecho a 30 días de vacaciones por año)

    Args:
        empleado: Diccionario con:
            - nombre (str)
            - salario_mensual (float)
            - dias_trabajados (float)

    Returns:
        Diccionario con:
            - nombre
            - salario_mensual
            - dias_trabajados
            - base_vacaciones
            - valor_vacaciones
    """
    # Validar
    valido, mensaje = validar_empleado_vacaciones(empleado)
    if not valido:
        raise ValueError(f"Empleado {empleado.get('nombre', 'desconocido')}: {mensaje}")

    # Obtener datos
    nombre = empleado['nombre']
    salario = float(empleado['salario_mensual'])
    dias = float(empleado['dias_trabajados'])

    # En vacaciones, la base es solo el salario (sin auxilio)
    base_vacaciones = salario

    # Calcular vacaciones: salario * días / 720
    # (720 porque 30 días de vacaciones / 12 meses * 360 días = 30 * 12 = 360, entonces 720 = 360*2)
    valor_vacaciones = (base_vacaciones * dias) / 720

    # Redondear a 2 decimales
    valor_vacaciones = round(valor_vacaciones, 2)
    base_vacaciones = round(base_vacaciones, 2)

    return {
        'nombre': nombre,
        'salario_mensual': round(salario, 2),
        'dias_trabajados': dias,
        'base_vacaciones': base_vacaciones,
        'valor_vacaciones': valor_vacaciones
    }


def calcular_vacaciones(empleados: Union[List[Dict], pd.DataFrame]) -> pd.DataFrame:
    """
    Calcula las vacaciones proporcionales para una lista de empleados.

    Args:
        empleados: Lista de diccionarios o DataFrame con datos de empleados

    Returns:
        DataFrame con resultados

    Ejemplo:
        >>> empleados = [
        ...     {'nombre': 'Juan', 'salario_mensual': 2000000, 'dias_trabajados': 30},
        ...     {'nombre': 'María', 'salario_mensual': 2500000, 'dias_trabajados': 30}
        ... ]
        >>> resultado = calcular_vacaciones(empleados)
    """
    # Convertir DataFrame a lista de diccionarios si es necesario
    if isinstance(empleados, pd.DataFrame):
        empleados = empleados.to_dict('records')

    if not empleados:
        raise ValueError("La lista de empleados está vacía")

    resultados = []

    for empleado in empleados:
        try:
            resultado = calcular_vacaciones_empleado(empleado)
            resultados.append(resultado)
        except ValueError as e:
            print(f"⚠️  Error: {str(e)}")
            continue

    # Convertir a DataFrame
    df_resultado = pd.DataFrame(resultados)

    return df_resultado[['nombre', 'salario_mensual', 'dias_trabajados', 'base_vacaciones', 'valor_vacaciones']]


if __name__ == "__main__":
    print("=" * 90)
    print("CÁLCULO DE VACACIONES PROPORCIONALES - COLOMBIA")
    print("=" * 90)
    print()

    # Crear lista de empleados de ejemplo
    empleados = [
        {
            'nombre': 'Juan García López',
            'salario_mensual': 2_500_000,
            'dias_trabajados': 30
        },
        {
            'nombre': 'María Rodríguez Pérez',
            'salario_mensual': 3_200_000,
            'dias_trabajados': 30
        },
        {
            'nombre': 'Carlos Martínez',
            'salario_mensual': 1_800_000,
            'dias_trabajados': 25  # Medio mes
        },
        {
            'nombre': 'Ana Sánchez',
            'salario_mensual': 4_000_000,
            'dias_trabajados': 15  # 15 días
        },
        {
            'nombre': 'Luis Fernández',
            'salario_mensual': 2_200_000,
            'dias_trabajados': 360  # Año completo
        }
    ]

    # Calcular vacaciones
    try:
        df_vacaciones = calcular_vacaciones(empleados)

        print("📊 RESULTADOS DEL CÁLCULO DE VACACIONES\n")
        print(df_vacaciones.to_string(index=False))

        print("\n" + "=" * 90)
        print("TOTALES")
        print("=" * 90)

        total_base = df_vacaciones['base_vacaciones'].sum()
        total_vacaciones = df_vacaciones['valor_vacaciones'].sum()
        promedio_vacaciones = df_vacaciones['valor_vacaciones'].mean()

        print(f"Total de empleados procesados: {len(df_vacaciones)}")
        print(f"Suma total de bases: ${total_base:,.2f}")
        print(f"Suma total de vacaciones: ${total_vacaciones:,.2f}")
        print(f"Promedio de vacaciones: ${promedio_vacaciones:,.2f}")

        print("\n" + "=" * 90)
        print("FÓRMULA UTILIZADA")
        print("=" * 90)
        print("Vacaciones = Salario Mensual × Días Trabajados ÷ 720")
        print()
        print("Donde:")
        print("  • Salario Mensual: valor acordado en el contrato (SIN auxilio de transporte)")
        print("  • Días Trabajados: días laborados en el período")
        print("  • 720: constante que representa (360 días × 2)")
        print("         porque un empleado tiene derecho a 30 días de vacaciones al año")
        print()
        print("Ejemplos:")
        print("  • 30 días de trabajo = 30 × 2 / 12 = 5 días de vacaciones")
        print("  • 60 días de trabajo = 30 × 2 / 12 = 10 días de vacaciones")
        print("  • 360 días de trabajo = 30 × 2 / 12 = 60 días de vacaciones (un mes)")
        print()

    except ValueError as e:
        print(f"❌ Error: {str(e)}")

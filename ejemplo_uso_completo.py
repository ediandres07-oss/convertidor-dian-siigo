"""
Ejemplo Completo: Cómo Usar el Sistema de Liquidación de Prestaciones
Sin necesidad de la interfaz web de Streamlit
"""

from datetime import datetime
from calculadora_prestaciones import DatosEmpleado, CalculadoraPrestaciones
from generador_pdf_prestaciones import GeneradorPDFPrestaciones


def ejemplo_simple():
    """Ejemplo simple: Un empleado"""
    print("=" * 80)
    print("EJEMPLO 1: Liquidación Simple - Un Empleado")
    print("=" * 80)

    # Crear datos del empleado
    datos = DatosEmpleado(
        nombre="Juan García Pérez",
        documento="1234567890",
        cargo="Gerente General",
        salario_mensual=2600000,
        auxilio_transporte=140000,
        fecha_ingreso=datetime(2023, 1, 15),
        fecha_retiro=datetime(2024, 6, 30),
        empresa="Mi Empresa S.A.S"
    )

    print(f"\n📋 Datos del Empleado:")
    print(f"  Nombre: {datos.nombre}")
    print(f"  Documento: {datos.documento}")
    print(f"  Cargo: {datos.cargo}")
    print(f"  Salario: ${datos.salario_mensual:,.0f}")
    print(f"  Auxilio: ${datos.auxilio_transporte:,.0f}")
    print(f"  Ingreso: {datos.fecha_ingreso.date()}")
    print(f"  Retiro: {datos.fecha_retiro.date()}")

    # Calcular prestaciones
    calculadora = CalculadoraPrestaciones()
    resultado = calculadora.calcular_prestaciones(datos)

    print(f"\n💰 Resultados:")
    print(f"  Días Laborados: {resultado.dias_laborados}")
    print(f"  Cesantías: ${resultado.cesantias:,.2f}")
    print(f"  Intereses: ${resultado.intereses_cesantias:,.2f}")
    print(f"  Prima: ${resultado.prima_servicios:,.2f}")
    print(f"  Vacaciones: ${resultado.vacaciones:,.2f}")
    print(f"  Total Devengado: ${resultado.total_devengado:,.2f}")
    print(f"  Neto a Pagar: ${resultado.neto_pagar:,.2f}")

    # Generar PDF
    print(f"\n📄 Generando PDF...")
    generador = GeneradorPDFPrestaciones()
    archivo_pdf = f"liquidacion_{datos.documento}.pdf"
    generador.generar_pdf(datos, resultado, archivo_pdf)

    print(f"✅ PDF guardado: {archivo_pdf}")
    print("=" * 80)

    return datos, resultado, archivo_pdf


def ejemplo_multiples_empleados():
    """Ejemplo: Múltiples empleados"""
    print("\n\n")
    print("=" * 80)
    print("EJEMPLO 2: Liquidación de Múltiples Empleados")
    print("=" * 80)

    empleados = [
        {
            'nombre': 'Juan García Pérez',
            'documento': '1001234567',
            'cargo': 'Gerente General',
            'salario': 2600000,
            'auxilio': 140000,
            'ingreso': datetime(2023, 1, 15),
            'retiro': datetime(2024, 6, 30),
        },
        {
            'nombre': 'María López Rodríguez',
            'documento': '1098765432',
            'cargo': 'Contadora',
            'salario': 2200000,
            'auxilio': 140000,
            'ingreso': datetime(2022, 6, 1),
            'retiro': datetime(2024, 6, 30),
        },
        {
            'nombre': 'Carlos Martínez Silva',
            'documento': '1111222333',
            'cargo': 'Asesor Técnico',
            'salario': 2000000,
            'auxilio': 140000,
            'ingreso': datetime(2024, 1, 1),
            'retiro': datetime(2024, 6, 30),
        },
    ]

    calculadora = CalculadoraPrestaciones()
    generador = GeneradorPDFPrestaciones()

    total_general = 0
    resultados_todos = []

    print("\n📋 Procesando empleados...\n")

    for i, emp in enumerate(empleados, 1):
        # Crear datos
        datos = DatosEmpleado(
            nombre=emp['nombre'],
            documento=emp['documento'],
            cargo=emp['cargo'],
            salario_mensual=emp['salario'],
            auxilio_transporte=emp['auxilio'],
            fecha_ingreso=emp['ingreso'],
            fecha_retiro=emp['retiro'],
            empresa="Mi Empresa S.A.S"
        )

        # Calcular
        resultado = calculadora.calcular_prestaciones(datos)
        total_general += resultado.neto_pagar

        # Generar PDF
        archivo = f"liquidacion_{emp['documento']}.pdf"
        generador.generar_pdf(datos, resultado, archivo)

        # Mostrar
        print(f"{i}. {emp['nombre']}")
        print(f"   Días: {resultado.dias_laborados} | "
              f"Total: ${resultado.neto_pagar:,.2f} | "
              f"PDF: {archivo}")

        resultados_todos.append({
            'nombre': emp['nombre'],
            'documento': emp['documento'],
            'dias': resultado.dias_laborados,
            'cesantias': resultado.cesantias,
            'prima': resultado.prima_servicios,
            'vacaciones': resultado.vacaciones,
            'intereses': resultado.intereses_cesantias,
            'total': resultado.neto_pagar
        })

    print(f"\n💰 Resumen General:")
    print(f"  Total Empleados: {len(empleados)}")
    print(f"  Total a Pagar: ${total_general:,.2f}")
    print("=" * 80)

    return resultados_todos


def ejemplo_con_validaciones():
    """Ejemplo: Manejo de errores y validaciones"""
    print("\n\n")
    print("=" * 80)
    print("EJEMPLO 3: Validaciones y Manejo de Errores")
    print("=" * 80)

    calculadora = CalculadoraPrestaciones()

    # Test 1: Salario inválido
    print("\n🔍 Test 1: Salario = 0 (debe fallar)")
    try:
        datos_invalido = DatosEmpleado(
            nombre="Test",
            documento="0000000000",
            cargo="Prueba",
            salario_mensual=0,
            auxilio_transporte=0,
            fecha_ingreso=datetime(2024, 1, 1),
            fecha_retiro=datetime(2024, 6, 30),
        )
        calculadora.calcular_prestaciones(datos_invalido)
    except ValueError as e:
        print(f"  ✅ Validación correcta: {e}")

    # Test 2: Fechas invertidas
    print("\n🔍 Test 2: Fecha retiro anterior a ingreso (debe fallar)")
    try:
        datos_fechas = DatosEmpleado(
            nombre="Test",
            documento="0000000000",
            cargo="Prueba",
            salario_mensual=2000000,
            auxilio_transporte=140000,
            fecha_ingreso=datetime(2024, 6, 30),
            fecha_retiro=datetime(2024, 1, 1),  # Invertido
        )
        calculadora.calcular_prestaciones(datos_fechas)
    except ValueError as e:
        print(f"  ✅ Validación correcta: {e}")

    # Test 3: Datos válidos
    print("\n🔍 Test 3: Datos válidos (debe funcionar)")
    try:
        datos_valido = DatosEmpleado(
            nombre="Test Válido",
            documento="9999999999",
            cargo="Prueba",
            salario_mensual=2000000,
            auxilio_transporte=140000,
            fecha_ingreso=datetime(2024, 1, 1),
            fecha_retiro=datetime(2024, 6, 30),
        )
        resultado = calculadora.calcular_prestaciones(datos_valido)
        print(f"  ✅ Cálculo exitoso: ${resultado.neto_pagar:,.2f}")
    except Exception as e:
        print(f"  ❌ Error: {e}")

    print("=" * 80)


def ejemplo_analisis_comparativo():
    """Ejemplo: Comparar prestaciones con diferentes salarios"""
    print("\n\n")
    print("=" * 80)
    print("EJEMPLO 4: Análisis Comparativo - Diferentes Salarios")
    print("=" * 80)

    calculadora = CalculadoraPrestaciones()

    salarios = [1000000, 2000000, 3000000, 5000000]
    dias_empleado = 365  # 1 año completo

    print("\n📊 Comparativa de Prestaciones (1 año de trabajo):\n")
    print(f"{'Salario':<15} {'Cesantías':<15} {'Prima':<15} {'Vacaciones':<15} {'Total':<15}")
    print("-" * 75)

    for salario in salarios:
        datos = DatosEmpleado(
            nombre="Empleado Test",
            documento="0000000000",
            cargo="Cargo",
            salario_mensual=salario,
            auxilio_transporte=140000,
            fecha_ingreso=datetime(2023, 6, 30),
            fecha_retiro=datetime(2024, 6, 30),
        )

        resultado = calculadora.calcular_prestaciones(datos)

        print(
            f"${salario:<14,} "
            f"${resultado.cesantias:<14,.0f} "
            f"${resultado.prima_servicios:<14,.0f} "
            f"${resultado.vacaciones:<14,.0f} "
            f"${resultado.total_devengado:<14,.0f}"
        )

    print("=" * 80)


def ejemplo_calculo_dias():
    """Ejemplo: Cálculo correcto de días laborados"""
    print("\n\n")
    print("=" * 80)
    print("EJEMPLO 5: Verificación de Cálculo de Días")
    print("=" * 80)

    calculadora = CalculadoraPrestaciones()

    casos = [
        {
            'nombre': 'Un mes (30 días aproximado)',
            'ingreso': datetime(2024, 1, 1),
            'retiro': datetime(2024, 1, 31),
            'dias_esperados': 31,
        },
        {
            'nombre': 'Tres meses',
            'ingreso': datetime(2024, 1, 1),
            'retiro': datetime(2024, 3, 31),
            'dias_esperados': 91,
        },
        {
            'nombre': 'Seis meses',
            'ingreso': datetime(2024, 1, 1),
            'retiro': datetime(2024, 6, 30),
            'dias_esperados': 182,
        },
        {
            'nombre': 'Un año completo',
            'ingreso': datetime(2023, 6, 30),
            'retiro': datetime(2024, 6, 30),
            'dias_esperados': 366,
        },
    ]

    print("\n📅 Verificación de Cálculo de Días:\n")

    for caso in casos:
        dias = calculadora.calcular_dias_laborados(caso['ingreso'], caso['retiro'])

        estado = "✅" if dias == caso['dias_esperados'] else "⚠️"
        print(
            f"{estado} {caso['nombre']:<30} "
            f"Calculado: {dias} días | "
            f"Esperado: {caso['dias_esperados']} días"
        )

    print("=" * 80)


def main():
    """Ejecuta todos los ejemplos"""
    print("\n")
    print("╔" + "═" * 78 + "╗")
    print("║" + " " * 78 + "║")
    print("║" + "SISTEMA DE LIQUIDACIÓN DE PRESTACIONES - EJEMPLOS COMPLETOS".center(78) + "║")
    print("║" + " " * 78 + "║")
    print("╚" + "═" * 78 + "╝")

    # Ejecutar ejemplos
    ejemplo_simple()
    ejemplo_multiples_empleados()
    ejemplo_con_validaciones()
    ejemplo_calculo_dias()
    ejemplo_analisis_comparativo()

    print("\n\n")
    print("╔" + "═" * 78 + "╗")
    print("║" + "✅ TODOS LOS EJEMPLOS COMPLETADOS EXITOSAMENTE".center(78) + "║")
    print("╚" + "═" * 78 + "╝")
    print("\n💡 Revisa los archivos PDF generados en la carpeta actual")
    print("📖 Consulta GUIA_LIQUIDADOR_PRESTACIONES.md para más información\n")


if __name__ == "__main__":
    main()

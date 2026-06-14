"""
Generador de Archivo Plano Compatible con SIIGO
Convierte liquidación de nómina a asientos contables para SIIGO
"""

import pandas as pd
from typing import List, Dict, Tuple
from datetime import datetime
from pathlib import Path


class ConfiguracionCuentas:
    """Configuración de cuentas contables"""

    CUENTAS = {
        'salarios': '5105',
        'cesantias': '510530',
        'intereses_cesantias': '510533',
        'prima': '510536',
        'vacaciones': '510539',
        'salud': '237005',
        'pension': '238030',
        'fondo_solidaridad': '238095',
        'retencion_fuente': '236540',
        'bancos': '111005',
    }

    CENTRO_COSTOS_DEFAULT = '01'

    @classmethod
    def obtener_cuenta(cls, concepto: str) -> str:
        """Obtiene cuenta contable para un concepto"""
        return cls.CUENTAS.get(concepto, '0000')

    @classmethod
    def actualizar_cuentas(cls, nuevas_cuentas: Dict[str, str]):
        """Permite actualizar cuentas personalizadas"""
        cls.CUENTAS.update(nuevas_cuentas)


def leer_excel(ruta_archivo: str) -> pd.DataFrame:
    """
    Lee el archivo Excel con datos de liquidación de nómina

    Args:
        ruta_archivo: Ruta al archivo Excel

    Returns:
        DataFrame con datos de empleados
    """
    try:
        df = pd.read_excel(ruta_archivo, sheet_name='Liquidacion')

        # Validar columnas requeridas
        columnas_requeridas = [
            'documento', 'nombre', 'salario_mensual',
            'cesantias', 'intereses_cesantias', 'prima', 'vacaciones',
            'salud', 'pension', 'fondo_solidaridad', 'retencion_fuente', 'neto_pagar'
        ]

        columnas_faltantes = [col for col in columnas_requeridas if col not in df.columns]
        if columnas_faltantes:
            raise ValueError(f"Columnas faltantes: {columnas_faltantes}")

        # Convertir documento a string
        df['documento'] = df['documento'].astype(str)

        # Rellenar NaN con 0
        df = df.fillna(0)

        # Redondear a 2 decimales
        columnas_numericas = df.columns.difference(['documento', 'nombre'])
        df[columnas_numericas] = df[columnas_numericas].round(2)

        return df

    except FileNotFoundError:
        raise FileNotFoundError(f"Archivo no encontrado: {ruta_archivo}")
    except Exception as e:
        raise Exception(f"Error leyendo Excel: {str(e)}")


def validar_datos(df: pd.DataFrame) -> Tuple[bool, str]:
    """
    Valida los datos de entrada

    Args:
        df: DataFrame con datos

    Returns:
        Tupla (válido, mensaje)
    """
    if df.empty:
        return False, "El archivo no contiene datos"

    # Validar valores negativos
    columnas_numericas = df.select_dtypes(include=['float64', 'int64']).columns
    for col in columnas_numericas:
        if (df[col] < 0).any():
            return False, f"Valores negativos encontrados en columna {col}"

    # Validar documento
    if df['documento'].isnull().any() or df['documento'].eq('').any():
        return False, "Hay documentos vacíos"

    # Validar nombre
    if df['nombre'].isnull().any() or df['nombre'].eq('').any():
        return False, "Hay nombres vacíos"

    # Validar y corregir neto_pagar
    for idx, row in df.iterrows():
        devengos = (row['salario_mensual'] + row['cesantias'] + row['intereses_cesantias'] +
                   row['prima'] + row['vacaciones'])
        deducciones = (row['salud'] + row['pension'] + row['fondo_solidaridad'] + row['retencion_fuente'])
        neto_calculado = devengos - deducciones

        if abs(row['neto_pagar'] - neto_calculado) > 0.01:
            df.at[idx, 'neto_pagar'] = round(neto_calculado, 2)

    return True, "Datos válidos"


def generar_asientos(df: pd.DataFrame, centro_costos: str = None) -> List[Dict]:
    """
    Genera asientos contables a partir de la liquidación

    Args:
        df: DataFrame con datos de liquidación
        centro_costos: Centro de costos (default: 01)

    Returns:
        Lista de asientos contables
    """
    if centro_costos is None:
        centro_costos = ConfiguracionCuentas.CENTRO_COSTOS_DEFAULT

    asientos = []

    for _, empleado in df.iterrows():
        documento = str(empleado['documento'])
        nombre = str(empleado['nombre'])

        # DEVENGOS (Débito)
        devengos = [
            {
                'tipo': 'NOMINA',
                'cuenta': ConfiguracionCuentas.obtener_cuenta('salarios'),
                'documento': documento,
                'nombre': nombre,
                'valor': float(empleado['salario_mensual']),
                'debito_credito': 'D',
                'centro_costos': centro_costos,
                'concepto': 'SALARIO'
            }
        ]

        # Cesantías
        if empleado['cesantias'] > 0:
            devengos.append({
                'tipo': 'NOMINA',
                'cuenta': ConfiguracionCuentas.obtener_cuenta('cesantias'),
                'documento': documento,
                'nombre': nombre,
                'valor': float(empleado['cesantias']),
                'debito_credito': 'D',
                'centro_costos': centro_costos,
                'concepto': 'CESANTIAS'
            })

        # Intereses cesantías
        if empleado['intereses_cesantias'] > 0:
            devengos.append({
                'tipo': 'NOMINA',
                'cuenta': ConfiguracionCuentas.obtener_cuenta('intereses_cesantias'),
                'documento': documento,
                'nombre': nombre,
                'valor': float(empleado['intereses_cesantias']),
                'debito_credito': 'D',
                'centro_costos': centro_costos,
                'concepto': 'INTERESES CESANTIAS'
            })

        # Prima
        if empleado['prima'] > 0:
            devengos.append({
                'tipo': 'NOMINA',
                'cuenta': ConfiguracionCuentas.obtener_cuenta('prima'),
                'documento': documento,
                'nombre': nombre,
                'valor': float(empleado['prima']),
                'debito_credito': 'D',
                'centro_costos': centro_costos,
                'concepto': 'PRIMA SERVICIOS'
            })

        # Vacaciones
        if empleado['vacaciones'] > 0:
            devengos.append({
                'tipo': 'NOMINA',
                'cuenta': ConfiguracionCuentas.obtener_cuenta('vacaciones'),
                'documento': documento,
                'nombre': nombre,
                'valor': float(empleado['vacaciones']),
                'debito_credito': 'D',
                'centro_costos': centro_costos,
                'concepto': 'VACACIONES'
            })

        asientos.extend(devengos)

        # DEDUCCIONES (Crédito)
        deducciones = []

        # Salud
        if empleado['salud'] > 0:
            deducciones.append({
                'tipo': 'NOMINA',
                'cuenta': ConfiguracionCuentas.obtener_cuenta('salud'),
                'documento': documento,
                'nombre': nombre,
                'valor': float(empleado['salud']),
                'debito_credito': 'C',
                'centro_costos': centro_costos,
                'concepto': 'APORTE SALUD'
            })

        # Pensión
        if empleado['pension'] > 0:
            deducciones.append({
                'tipo': 'NOMINA',
                'cuenta': ConfiguracionCuentas.obtener_cuenta('pension'),
                'documento': documento,
                'nombre': nombre,
                'valor': float(empleado['pension']),
                'debito_credito': 'C',
                'centro_costos': centro_costos,
                'concepto': 'APORTE PENSION'
            })

        # Fondo solidaridad
        if empleado['fondo_solidaridad'] > 0:
            deducciones.append({
                'tipo': 'NOMINA',
                'cuenta': ConfiguracionCuentas.obtener_cuenta('fondo_solidaridad'),
                'documento': documento,
                'nombre': nombre,
                'valor': float(empleado['fondo_solidaridad']),
                'debito_credito': 'C',
                'centro_costos': centro_costos,
                'concepto': 'FONDO SOLIDARIDAD'
            })

        # Retención en la fuente
        if empleado['retencion_fuente'] > 0:
            deducciones.append({
                'tipo': 'NOMINA',
                'cuenta': ConfiguracionCuentas.obtener_cuenta('retencion_fuente'),
                'documento': documento,
                'nombre': nombre,
                'valor': float(empleado['retencion_fuente']),
                'debito_credito': 'C',
                'centro_costos': centro_costos,
                'concepto': 'RETENCION FUENTE'
            })

        asientos.extend(deducciones)

        # NETO A PAGAR (Crédito - Cuenta Bancos)
        if empleado['neto_pagar'] > 0:
            asientos.append({
                'tipo': 'NOMINA',
                'cuenta': ConfiguracionCuentas.obtener_cuenta('bancos'),
                'documento': documento,
                'nombre': nombre,
                'valor': float(empleado['neto_pagar']),
                'debito_credito': 'C',
                'centro_costos': centro_costos,
                'concepto': 'NETO A PAGAR'
            })

    return asientos


def validar_balance(asientos: List[Dict]) -> Tuple[bool, float, float, float]:
    """
    Valida que débitos = créditos

    Args:
        asientos: Lista de asientos contables

    Returns:
        Tupla (balanceado, total_debitos, total_creditos, diferencia)
    """
    total_debitos = sum(a['valor'] for a in asientos if a['debito_credito'] == 'D')
    total_creditos = sum(a['valor'] for a in asientos if a['debito_credito'] == 'C')

    diferencia = abs(total_debitos - total_creditos)
    balanceado = diferencia < 0.01  # Tolerancia por redondeo

    return balanceado, total_debitos, total_creditos, diferencia


def exportar_plano_txt(asientos: List[Dict], ruta_salida: str = 'plano_siigo.txt') -> str:
    """
    Exporta asientos a archivo plano TXT

    Args:
        asientos: Lista de asientos contables
        ruta_salida: Ruta del archivo de salida

    Returns:
        Ruta del archivo generado
    """
    try:
        with open(ruta_salida, 'w', encoding='utf-8') as f:
            for asiento in asientos:
                linea = (
                    f"{asiento['tipo']};"
                    f"{asiento['cuenta']};"
                    f"{asiento['documento']};"
                    f"{asiento['nombre']};"
                    f"{asiento['valor']:.2f};"
                    f"{asiento['debito_credito']};"
                    f"{asiento['centro_costos']}\n"
                )
                f.write(linea)

        return ruta_salida

    except Exception as e:
        raise Exception(f"Error exportando TXT: {str(e)}")


def exportar_plano_excel(asientos: List[Dict], ruta_salida: str = 'plano_siigo.xlsx') -> str:
    """
    Exporta asientos a archivo Excel

    Args:
        asientos: Lista de asientos contables
        ruta_salida: Ruta del archivo de salida

    Returns:
        Ruta del archivo generado
    """
    try:
        df_asientos = pd.DataFrame(asientos)

        # Reordenar columnas
        columnas_orden = [
            'tipo', 'cuenta', 'documento', 'nombre', 'valor', 'debito_credito', 'centro_costos', 'concepto'
        ]
        df_asientos = df_asientos[columnas_orden]

        # Crear Excel con múltiples hojas
        with pd.ExcelWriter(ruta_salida, engine='openpyxl') as writer:
            # Hoja de asientos
            df_asientos.to_excel(writer, sheet_name='Asientos', index=False)

            # Hoja de resumen
            debitos = df_asientos[df_asientos['debito_credito'] == 'D']['valor'].sum()
            creditos = df_asientos[df_asientos['debito_credito'] == 'C']['valor'].sum()

            resumen = pd.DataFrame({
                'Concepto': ['Total Débitos', 'Total Créditos', 'Diferencia'],
                'Valor': [debitos, creditos, abs(debitos - creditos)]
            })
            resumen.to_excel(writer, sheet_name='Resumen', index=False)

            # Hoja por cuenta
            df_por_cuenta = df_asientos.groupby('cuenta')['valor'].sum().reset_index()
            df_por_cuenta.columns = ['Cuenta', 'Total']
            df_por_cuenta.to_excel(writer, sheet_name='Por Cuenta', index=False)

        return ruta_salida

    except Exception as e:
        raise Exception(f"Error exportando Excel: {str(e)}")


def generar_reporte(asientos: List[Dict], df_original: pd.DataFrame) -> str:
    """
    Genera reporte de generación

    Args:
        asientos: Lista de asientos contables
        df_original: DataFrame original

    Returns:
        Texto del reporte
    """
    balanceado, debitos, creditos, diferencia = validar_balance(asientos)

    reporte = []
    reporte.append("=" * 80)
    reporte.append("REPORTE DE GENERACIÓN - ARCHIVO PLANO SIIGO")
    reporte.append("=" * 80)
    reporte.append("")

    # Datos de entrada
    reporte.append("📊 DATOS DE ENTRADA")
    reporte.append("-" * 80)
    reporte.append(f"Total empleados procesados: {len(df_original)}")
    reporte.append(f"Total salario a pagar: ${df_original['neto_pagar'].sum():,.2f}")
    reporte.append("")

    # Asientos generados
    reporte.append("📋 ASIENTOS GENERADOS")
    reporte.append("-" * 80)
    reporte.append(f"Total asientos: {len(asientos)}")
    reporte.append(f"Asientos débito: {len([a for a in asientos if a['debito_credito'] == 'D'])}")
    reporte.append(f"Asientos crédito: {len([a for a in asientos if a['debito_credito'] == 'C'])}")
    reporte.append("")

    # Balance contable
    reporte.append("⚖️ BALANCE CONTABLE")
    reporte.append("-" * 80)
    reporte.append(f"Total Débitos:   ${debitos:,.2f}")
    reporte.append(f"Total Créditos:  ${creditos:,.2f}")
    reporte.append(f"Diferencia:      ${diferencia:,.2f}")
    reporte.append("")

    if balanceado:
        reporte.append("✅ ESTADO: BALANCEADO")
    else:
        reporte.append("❌ ESTADO: DESBALANCEADO")
    reporte.append("")

    # Resumen por cuenta
    reporte.append("📈 RESUMEN POR CUENTA")
    reporte.append("-" * 80)

    df_asientos = pd.DataFrame(asientos)
    resumen_cuentas = df_asientos.groupby('cuenta')['valor'].sum().reset_index()
    resumen_cuentas.columns = ['Cuenta', 'Valor']
    resumen_cuentas = resumen_cuentas.sort_values('Valor', ascending=False)

    for _, row in resumen_cuentas.iterrows():
        reporte.append(f"Cuenta {row['Cuenta']:6s}: ${row['Valor']:>12,.2f}")

    reporte.append("")
    reporte.append("=" * 80)
    reporte.append(f"Generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    reporte.append("=" * 80)

    return "\n".join(reporte)


def procesar_liquidacion(
    ruta_excel: str,
    ruta_plano: str = 'plano_siigo.txt',
    ruta_excel_salida: str = 'plano_siigo.xlsx',
    centro_costos: str = None,
    cuentas_personalizadas: Dict = None
) -> Dict:
    """
    Función principal que procesa la liquidación y genera archivos

    Args:
        ruta_excel: Ruta al archivo Excel con liquidación
        ruta_plano: Ruta de salida para archivo TXT
        ruta_excel_salida: Ruta de salida para archivo Excel
        centro_costos: Centro de costos a utilizar
        cuentas_personalizadas: Diccionario con cuentas personalizadas

    Returns:
        Diccionario con resultados
    """
    try:
        # Actualizar cuentas si se proporcionan
        if cuentas_personalizadas:
            ConfiguracionCuentas.actualizar_cuentas(cuentas_personalizadas)

        # Leer datos
        print("📖 Leyendo archivo Excel...")
        df = leer_excel(ruta_excel)

        # Validar datos
        print("✓ Validando datos...")
        valido, mensaje = validar_datos(df)
        if not valido:
            raise ValueError(mensaje)

        # Generar asientos
        print("📝 Generando asientos contables...")
        asientos = generar_asientos(df, centro_costos)

        # Validar balance
        print("⚖️ Validando balance...")
        balanceado, debitos, creditos, diferencia = validar_balance(asientos)

        # Exportar archivos
        print(f"💾 Exportando a {ruta_plano}...")
        exportar_plano_txt(asientos, ruta_plano)

        print(f"💾 Exportando a {ruta_excel_salida}...")
        exportar_plano_excel(asientos, ruta_excel_salida)

        # Generar reporte
        reporte = generar_reporte(asientos, df)
        print("")
        print(reporte)

        # Guardar reporte
        ruta_reporte = ruta_plano.replace('.txt', '_reporte.txt')
        with open(ruta_reporte, 'w', encoding='utf-8') as f:
            f.write(reporte)

        return {
            'exito': True,
            'total_empleados': len(df),
            'total_asientos': len(asientos),
            'balanceado': balanceado,
            'total_debitos': debitos,
            'total_creditos': creditos,
            'diferencia': diferencia,
            'archivo_plano': ruta_plano,
            'archivo_excel': ruta_excel_salida,
            'archivo_reporte': ruta_reporte
        }

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return {
            'exito': False,
            'error': str(e)
        }


if __name__ == "__main__":
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + "GENERADOR DE ARCHIVO PLANO COMPATIBLE CON SIIGO".center(78) + "║")
    print("╚" + "=" * 78 + "╝")
    print()

    # Archivo de entrada
    archivo_entrada = 'plano_siigo_entrada.xlsx'

    # Verificar si existe el archivo
    if not Path(archivo_entrada).exists():
        print(f"❌ Archivo no encontrado: {archivo_entrada}")
        print("\nCrea un archivo Excel con las siguientes columnas:")
        print("  - documento")
        print("  - nombre")
        print("  - salario_mensual")
        print("  - cesantias")
        print("  - intereses_cesantias")
        print("  - prima")
        print("  - vacaciones")
        print("  - salud")
        print("  - pension")
        print("  - fondo_solidaridad")
        print("  - retencion_fuente")
        print("  - neto_pagar")
        print(f"\nEn una hoja llamada 'Liquidacion'")
    else:
        # Procesar
        resultado = procesar_liquidacion(
            ruta_excel=archivo_entrada,
            ruta_plano='plano_siigo.txt',
            ruta_excel_salida='plano_siigo.xlsx',
            centro_costos='01'
        )

        if resultado['exito']:
            print("\n✅ PROCESAMIENTO COMPLETADO")
            print(f"\n📁 Archivos generados:")
            print(f"   • {resultado['archivo_plano']}")
            print(f"   • {resultado['archivo_excel']}")
            print(f"   • {resultado['archivo_reporte']}")

"""
Mapeo de Datos de Nómina al Modelo SIIGO de 27 Columnas
Convierte liquidación de nómina a formato exacto del modelo oficial
"""

import pandas as pd
from datetime import datetime


# ================================================================
# MAPEO DE COLUMNAS - Orden exacto del modelo SIIGO
# ================================================================
COLUMNAS_SIIGO = [
    "Tipo de comprobante",
    "Consecutivo comprobante",
    "Fecha de elaboración ",
    "Sigla moneda",
    "Tasa de cambio",
    "Código cuenta contable",
    "Identificación tercero",
    "Sucursal",
    "Código producto",
    "Código de bodega",
    "Acción",
    "Cantidad producto",
    "Prefijo",
    "Consecutivo",
    "No. cuota",
    "Fecha vencimiento",
    "Código impuesto",
    "Código grupo activo fijo",
    "Código activo fijo",
    "Descripción",
    "Código centro/subcentro de costos",
    "Débito",
    "Crédito",
    "Observaciones",
    "Base gravable libro compras/ventas  ",
    "Base exenta libro compras/ventas",
    "Mes de cierre",
]

# ================================================================
# CONFIGURACIÓN DE CUENTAS PARA NÓMINA
# ================================================================
CUENTAS_NOMINA = {
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

# ================================================================
# MAPEO DE CONCEPTOS DE NÓMINA A FILAS DEL PLANO
# ================================================================
CONCEPTOS_NOMINA = {
    'salario_prorr': {
        'cuenta': 'salarios',
        'descripcion': 'Salario',
        'tipo': 'devengos',
        'naturaleza': 'D'
    },
    'cesantias': {
        'cuenta': 'cesantias',
        'descripcion': 'Cesantías',
        'tipo': 'devengos',
        'naturaleza': 'D'
    },
    'intereses_cesantias': {
        'cuenta': 'intereses_cesantias',
        'descripcion': 'Intereses Cesantías',
        'tipo': 'devengos',
        'naturaleza': 'D'
    },
    'prima': {
        'cuenta': 'prima',
        'descripcion': 'Prima de Servicios',
        'tipo': 'devengos',
        'naturaleza': 'D'
    },
    'vacaciones': {
        'cuenta': 'vacaciones',
        'descripcion': 'Vacaciones',
        'tipo': 'devengos',
        'naturaleza': 'D'
    },
    'salud': {
        'cuenta': 'salud',
        'descripcion': 'Aporte Salud',
        'tipo': 'deducciones',
        'naturaleza': 'C'
    },
    'pension': {
        'cuenta': 'pension',
        'descripcion': 'Aporte Pensión',
        'tipo': 'deducciones',
        'naturaleza': 'C'
    },
    'fondo_solidaridad': {
        'cuenta': 'fondo_solidaridad',
        'descripcion': 'Fondo Solidaridad',
        'tipo': 'deducciones',
        'naturaleza': 'C'
    },
    'retencion': {
        'cuenta': 'retencion_fuente',
        'descripcion': 'Retención en la Fuente',
        'tipo': 'deducciones',
        'naturaleza': 'C'
    },
    'neto_pagar': {
        'cuenta': 'bancos',
        'descripcion': 'Neto a Pagar',
        'tipo': 'pago',
        'naturaleza': 'C'
    }
}


def convertir_nomina_a_siigo(empleados_resultados, fecha_comprobante=None):
    """
    Convierte resultados de liquidación de nómina al formato SIIGO

    Args:
        empleados_resultados: Lista de resultados de liquidación por empleado
        fecha_comprobante: Fecha en formato DD/MM/YYYY (por defecto: hoy)

    Returns:
        DataFrame con 27 columnas exactas del modelo SIIGO
    """

    if fecha_comprobante is None:
        fecha_comprobante = datetime.now().strftime("%d/%m/%Y")

    filas = []

    # Por cada empleado
    for emp in empleados_resultados:
        documento = str(emp.get('documento', '')).strip()
        nombre = str(emp.get('nombre', '')).strip()

        # Usar documento como consecutivo único
        consecutivo_comprobante = f"NOM-{documento}"

        # Por cada concepto de nómina
        for concepto, config in CONCEPTOS_NOMINA.items():
            # Solo si el valor es > 0
            valor = float(emp.get(concepto, 0) or 0)
            if valor <= 0:
                continue

            # Obtener información de la cuenta
            cuenta_clave = config['cuenta']
            cuenta = CUENTAS_NOMINA.get(cuenta_clave, '0000')
            naturaleza = config['naturaleza']

            # Crear fila con todas las 27 columnas
            fila = {
                # 1. Tipo de comprobante - FC para nómina
                "Tipo de comprobante": "FC",

                # 2. Consecutivo comprobante - Único por nómina
                "Consecutivo comprobante": consecutivo_comprobante,

                # 3. Fecha de elaboración - DD/MM/YYYY
                "Fecha de elaboración ": fecha_comprobante,

                # 4. Sigla moneda - COP para Colombia
                "Sigla moneda": "COP",

                # 5. Tasa de cambio - Vacío para moneda local
                "Tasa de cambio": "",

                # 6. Código cuenta contable
                "Código cuenta contable": cuenta,

                # 7. Identificación tercero - Documento del empleado
                "Identificación tercero": documento,

                # 8. Sucursal - Vacío (no aplicable para nómina)
                "Sucursal": "",

                # 9. Código producto - Vacío (no aplica)
                "Código producto": "",

                # 10. Código de bodega - Vacío (no aplica)
                "Código de bodega": "",

                # 11. Acción - Vacío (no aplica para nómina)
                "Acción": "",

                # 12. Cantidad producto - Vacío (no aplica)
                "Cantidad producto": "",

                # 13. Prefijo - Vacío (no aplica para nómina)
                "Prefijo": "",

                # 14. Consecutivo - Vacío (no aplica para nómina)
                "Consecutivo": "",

                # 15. No. cuota - Vacío (no aplica para nómina)
                "No. cuota": "",

                # 16. Fecha vencimiento - Vacío (no aplica para nómina)
                "Fecha vencimiento": "",

                # 17. Código impuesto - Vacío (no aplica para nómina)
                "Código impuesto": "",

                # 18. Código grupo activo fijo - Vacío (no aplica)
                "Código grupo activo fijo": "",

                # 19. Código activo fijo - Vacío (no aplica)
                "Código activo fijo": "",

                # 20. Descripción - Nombre concepto + empleado
                "Descripción": f"{config['descripcion']} - {nombre}",

                # 21. Código centro/subcentro de costos
                "Código centro/subcentro de costos": "1-1",

                # 22. Débito - Si es devengos o pago
                "Débito": f"{valor:.2f}" if naturaleza == 'D' else "",

                # 23. Crédito - Si es deducción o pago
                "Crédito": f"{valor:.2f}" if naturaleza == 'C' else "",

                # 24. Observaciones - Período de nómina
                "Observaciones": "Liquidación de nómina",

                # 25. Base gravable libro compras/ventas
                "Base gravable libro compras/ventas  ": "",

                # 26. Base exenta libro compras/ventas
                "Base exenta libro compras/ventas": "",

                # 27. Mes de cierre - NO (no es cierre)
                "Mes de cierre": "NO",
            }

            filas.append(fila)

    # Crear DataFrame con columnas en orden exacto
    df = pd.DataFrame(filas)

    # Asegurar que todas las columnas existen en el orden correcto
    for col in COLUMNAS_SIIGO:
        if col not in df.columns:
            df[col] = ""

    # Reordenar columnas exactamente como el modelo
    df = df[COLUMNAS_SIIGO]

    return df


def exportar_a_siigo_excel(df_siigo, ruta_salida="plano_siigo.xlsx"):
    """
    Exporta el DataFrame a Excel con formato del modelo SIIGO

    Args:
        df_siigo: DataFrame con 27 columnas SIIGO
        ruta_salida: Ruta del archivo Excel

    Returns:
        Ruta del archivo generado
    """
    with pd.ExcelWriter(ruta_salida, engine='openpyxl') as writer:
        df_siigo.to_excel(writer, sheet_name='Datos', index=False)

    return ruta_salida


def exportar_a_siigo_txt(df_siigo, ruta_salida="plano_siigo.txt"):
    """
    Exporta a formato plano TXT compatible con SIIGO
    Formato: TIPO;CUENTA;DOCUMENTO;DESCRIPCIÓN;VALOR;D/C

    Args:
        df_siigo: DataFrame con 27 columnas SIIGO
        ruta_salida: Ruta del archivo TXT

    Returns:
        Ruta del archivo generado
    """
    with open(ruta_salida, 'w', encoding='utf-8') as f:
        for idx, row in df_siigo.iterrows():
            # Obtener valores
            tipo = row['Tipo de comprobante']
            cuenta = row['Código cuenta contable']
            documento = row['Identificación tercero']
            descripcion = row['Descripción']
            debito = row['Débito']
            credito = row['Crédito']

            # Determinar valor y naturaleza
            if debito and float(debito) > 0:
                valor = debito
                naturaleza = 'D'
            else:
                valor = credito
                naturaleza = 'C'

            # Escribir línea
            linea = f"{tipo};{cuenta};{documento};{descripcion};{valor};{naturaleza}\n"
            f.write(linea)

    return ruta_salida


# ================================================================
# EJEMPLO DE USO
# ================================================================
if __name__ == "__main__":
    # Datos de ejemplo de liquidación
    empleados_ejemplo = [
        {
            'documento': '1020304050',
            'nombre': 'JUAN GARCÍA',
            'salario_prorr': 2500000,
            'cesantias': 250000,
            'intereses_cesantias': 12500,
            'prima': 208333.33,
            'vacaciones': 104166.67,
            'salud': 100000,
            'pension': 150000,
            'fondo_solidaridad': 0,
            'retencion': 50000,
            'neto_pagar': 2683000,
        },
        {
            'documento': '1020304051',
            'nombre': 'MARÍA RODRÍGUEZ',
            'salario_prorr': 3000000,
            'cesantias': 300000,
            'intereses_cesantias': 15000,
            'prima': 250000,
            'vacaciones': 125000,
            'salud': 120000,
            'pension': 180000,
            'fondo_solidaridad': 0,
            'retencion': 75000,
            'neto_pagar': 3115000,
        }
    ]

    # Convertir a formato SIIGO
    print("📋 Convirtiendo nómina a formato SIIGO...")
    df_siigo = convertir_nomina_a_siigo(empleados_ejemplo)

    print(f"\n✅ Total de líneas generadas: {len(df_siigo)}")
    print(f"✅ Columnas: {len(df_siigo.columns)}")

    # Exportar a Excel
    excel_file = exportar_a_siigo_excel(df_siigo, "ejemplo_nomina_siigo.xlsx")
    print(f"\n📄 Excel generado: {excel_file}")

    # Exportar a TXT
    txt_file = exportar_a_siigo_txt(df_siigo, "ejemplo_nomina_siigo.txt")
    print(f"📝 TXT generado: {txt_file}")

    # Mostrar preview
    print("\n📊 Preview de datos:")
    print(df_siigo.head(5).to_string(index=False))

    print("\n✅ Mapeo completado exitosamente")

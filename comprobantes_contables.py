"""
Procesador de Comprobantes Contables para SIIGO
Importa y valida comprobantes contables según el modelo SIIGO
"""

import pandas as pd
from datetime import datetime
from pathlib import Path

# ================================
# MODELO DE COMPROBANTES
# ================================
COLUMNAS_COMPROBANTE = [
    "Tipo de comprobante",
    "Consecutivo comprobante",
    "Fecha de elaboración",
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
    "Base gravable libro compras/ventas",
    "Base exenta libro compras/ventas",
    "Mes de cierre"
]

TIPOS_COMPROBANTE = {
    "ND": "Nota Débito",
    "NC": "Nota Crédito",
    "FV": "Factura Venta",
    "FC": "Factura Compra",
    "REC": "Recibo",
    "CHQ": "Cheque",
    "TR": "Traslado"
}

# ================================
# PROCESAMIENTO DE COMPROBANTES
# ================================
def importar_comprobantes(ruta_archivo):
    """
    Importa comprobantes contables desde Excel

    Args:
        ruta_archivo: Ruta del archivo .xlsx

    Returns:
        DataFrame con los comprobantes y validaciones
    """

    try:
        df = pd.read_excel(ruta_archivo, sheet_name="Datos")

        # Validar que tenga las columnas esperadas
        columnas_faltantes = [col for col in COLUMNAS_COMPROBANTE if col not in df.columns]
        if columnas_faltantes:
            raise ValueError(f"Columnas faltantes: {', '.join(columnas_faltantes)}")

        # Convertir tipos de datos
        df["Fecha de elaboración"] = pd.to_datetime(df["Fecha de elaboración"], errors="coerce")
        df["Fecha vencimiento"] = pd.to_datetime(df["Fecha vencimiento"], errors="coerce")
        df["Tasa de cambio"] = pd.to_numeric(df["Tasa de cambio"], errors="coerce").fillna(1)
        df["Débito"] = pd.to_numeric(df["Débito"], errors="coerce").fillna(0)
        df["Crédito"] = pd.to_numeric(df["Crédito"], errors="coerce").fillna(0)
        df["Cantidad producto"] = pd.to_numeric(df["Cantidad producto"], errors="coerce").fillna(0)

        return df, None

    except Exception as e:
        return None, str(e)


def validar_comprobantes(df):
    """
    Valida los comprobantes contables

    Returns:
        Diccionario con resultados de validación
    """

    validaciones = {
        "total_comprobantes": len(df),
        "errores": [],
        "advertencias": [],
        "balance": {}
    }

    # Validar tipos de comprobante
    tipos_invalidos = df[~df["Tipo de comprobante"].isin(TIPOS_COMPROBANTE.keys())]
    if len(tipos_invalidos) > 0:
        validaciones["errores"].append(
            f"❌ {len(tipos_invalidos)} comprobantes con tipo inválido"
        )

    # Validar que cada comprobante tenga cuenta contable
    sin_cuenta = df[df["Código cuenta contable"].isna()]
    if len(sin_cuenta) > 0:
        validaciones["errores"].append(
            f"❌ {len(sin_cuenta)} comprobantes sin código de cuenta"
        )

    # Validar que cada línea tenga débito o crédito
    sin_monto = df[(df["Débito"] == 0) & (df["Crédito"] == 0)]
    if len(sin_monto) > 0:
        validaciones["advertencias"].append(
            f"⚠️ {len(sin_monto)} líneas sin débito ni crédito"
        )

    # Validar fechas
    fechas_invalidas = df[df["Fecha de elaboración"].isna()]
    if len(fechas_invalidas) > 0:
        validaciones["advertencias"].append(
            f"⚠️ {len(fechas_invalidas)} comprobantes sin fecha válida"
        )

    # Balance por comprobante
    balance_comprobante = df.groupby("Consecutivo comprobante").agg({
        "Débito": "sum",
        "Crédito": "sum"
    }).reset_index()

    desbalanceados = balance_comprobante[
        (balance_comprobante["Débito"] - balance_comprobante["Crédito"]).abs() > 0.01
    ]

    if len(desbalanceados) > 0:
        validaciones["errores"].append(
            f"❌ {len(desbalanceados)} comprobantes desbalanceados"
        )

    # Balance total
    total_debitos = df["Débito"].sum()
    total_creditos = df["Crédito"].sum()
    diferencia = abs(total_debitos - total_creditos)

    validaciones["balance"] = {
        "total_debitos": round(total_debitos, 2),
        "total_creditos": round(total_creditos, 2),
        "diferencia": round(diferencia, 2),
        "balanceado": diferencia < 0.01
    }

    return validaciones


def generar_resumen_comprobantes(df):
    """
    Genera resumen de comprobantes por tipo y cuenta
    """

    resumen = {
        "por_tipo": {},
        "por_cuenta": {},
        "por_tercero": {}
    }

    # Resumen por tipo
    tipo_count = df["Tipo de comprobante"].value_counts()
    for tipo, count in tipo_count.items():
        resumen["por_tipo"][TIPOS_COMPROBANTE.get(tipo, tipo)] = count

    # Resumen por cuenta
    cuenta_resumen = df.groupby("Código cuenta contable").agg({
        "Débito": "sum",
        "Crédito": "sum",
        "Descripción": "count"
    }).reset_index()
    cuenta_resumen.columns = ["Cuenta", "Débito", "Crédito", "Líneas"]
    resumen["por_cuenta"] = cuenta_resumen.to_dict('records')

    # Resumen por tercero
    tercero_resumen = df.groupby("Identificación tercero").agg({
        "Débito": "sum",
        "Crédito": "sum"
    }).reset_index()
    tercero_resumen.columns = ["Tercero", "Débito", "Crédito"]
    resumen["por_tercero"] = tercero_resumen.to_dict('records')

    return resumen


def generar_plano_siigo_desde_comprobantes(df, nombre_archivo=None):
    """
    Genera archivo plano SIIGO desde comprobantes contables

    Args:
        df: DataFrame con comprobantes
        nombre_archivo: Nombre del archivo de salida (opcional)

    Returns:
        Ruta del archivo generado
    """

    if nombre_archivo is None:
        fecha = datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre_archivo = f"plano_comprobantes_{fecha}.txt"

    # Preparar datos para plano SIIGO
    plano_data = []

    for idx, row in df.iterrows():
        # Línea para débito
        if row["Débito"] > 0:
            plano_data.append({
                "tipo_movimiento": "01",  # Comprobante contable
                "cuenta": str(row["Código cuenta contable"]),
                "consecutivo": str(row["Consecutivo comprobante"]),
                "descripcion": str(row["Descripción"])[:50],
                "valor": row["Débito"],
                "naturaleza": "D",
                "documento": str(row["Identificación tercero"]),
                "centro_costo": str(row["Código centro/subcentro de costos"]) if pd.notna(row["Código centro/subcentro de costos"]) else ""
            })

        # Línea para crédito
        if row["Crédito"] > 0:
            plano_data.append({
                "tipo_movimiento": "01",
                "cuenta": str(row["Código cuenta contable"]),
                "consecutivo": str(row["Consecutivo comprobante"]),
                "descripcion": str(row["Descripción"])[:50],
                "valor": row["Crédito"],
                "naturaleza": "C",
                "documento": str(row["Identificación tercero"]),
                "centro_costo": str(row["Código centro/subcentro de costos"]) if pd.notna(row["Código centro/subcentro de costos"]) else ""
            })

    # Crear DataFrame con formato plano
    df_plano = pd.DataFrame(plano_data)

    # Guardar archivo TXT
    with open(nombre_archivo, 'w', encoding='utf-8') as f:
        for idx, row in df_plano.iterrows():
            linea = f"{row['tipo_movimiento']};{row['cuenta']};{row['documento']};{row['descripcion']};{row['valor']};{row['naturaleza']}"
            f.write(linea + "\n")

    return nombre_archivo


def generar_excel_comprobantes(df, nombre_archivo=None):
    """
    Genera Excel con comprobantes y validaciones
    """

    if nombre_archivo is None:
        fecha = datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre_archivo = f"comprobantes_contables_{fecha}.xlsx"

    validaciones = validar_comprobantes(df)

    with pd.ExcelWriter(nombre_archivo, engine='openpyxl') as writer:
        # Hoja 1: Comprobantes completos
        df.to_excel(writer, sheet_name="Comprobantes", index=False)

        # Hoja 2: Validación
        validacion_df = pd.DataFrame([{
            "Total Comprobantes": validaciones["total_comprobantes"],
            "Total Débitos": validaciones["balance"]["total_debitos"],
            "Total Créditos": validaciones["balance"]["total_creditos"],
            "Diferencia": validaciones["balance"]["diferencia"],
            "Estado": "✅ BALANCEADO" if validaciones["balance"]["balanceado"] else "❌ DESBALANCEADO",
            "Errores": len(validaciones["errores"]),
            "Advertencias": len(validaciones["advertencias"])
        }])
        validacion_df.to_excel(writer, sheet_name="Validacion", index=False)

        # Hoja 3: Resumen
        resumen = generar_resumen_comprobantes(df)

        resumen_cuenta = pd.DataFrame(resumen["por_cuenta"])
        resumen_cuenta.to_excel(writer, sheet_name="Por Cuenta", index=False)

        resumen_tercero = pd.DataFrame(resumen["por_tercero"])
        resumen_tercero.to_excel(writer, sheet_name="Por Tercero", index=False)

    return nombre_archivo

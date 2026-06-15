"""
Generador de Plano SIIGO - Corregido según Modelo de Importación Oficial
Genera y valida archivos de comprobantes contables compatibles con SIIGO
"""

import re
from dataclasses import dataclass, field
from typing import Dict, List, Any, Tuple, Optional

import pandas as pd


# =========================================================
# CONFIGURACIÓN DEL MODELO (según archivo de importación)
# =========================================================
# CAMBIO: Lista exacta de columnas en orden correcto del modelo
COLUMNAS_MODELO = [
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
    "Mes de cierre",
]

# CAMBIO: Tipos de comprobante válidos según modelo SIIGO
TIPOS_COMPROBANTE_VALIDOS = {
    "ND": "Nota Débito",
    "NC": "Nota Crédito",
    "FV": "Factura Venta",
    "FC": "Factura Compra",
    "REC": "Recibo",
    "CHQ": "Cheque",
    "TR": "Traslado",
}

# CAMBIO: Acciones válidas para movimientos de inventario
ACCIONES_INVENTARIO = {"Compra", "Venta", "Movimiento", "Entrada", "Salida"}


@dataclass
class SiigoConfig:
    """
    Configuración parametrizable para reglas condicionales
    que el modelo menciona de forma dependiente de la cuenta.
    """
    moneda_local: str = "COP"

    # CAMBIO: Cuentas que requieren campos de inventario
    cuentas_inventario: set = field(default_factory=set)
    # CAMBIO: Cuentas que requieren vencimiento
    cuentas_vencimiento: set = field(default_factory=set)
    # CAMBIO: Cuentas que requieren código de impuesto
    cuentas_impuesto: set = field(default_factory=set)
    # CAMBIO: Cuentas que requieren activos fijos
    cuentas_activo_fijo: set = field(default_factory=set)

    # CAMBIO: Longitudes máximas según modelo
    max_tipo_comprobante: int = 3
    max_consecutivo_comprobante: int = 20
    max_sigla_moneda: int = 3
    max_cuenta: int = 10
    max_documento: int = 15
    max_sucursal: int = 10
    max_codigo_producto: int = 15
    max_codigo_bodega: int = 10
    max_accion: int = 15
    max_prefijo: int = 6
    max_consecutivo: int = 10
    max_no_cuota: int = 3
    max_codigo_impuesto: int = 10
    max_codigo_grupo_af: int = 10
    max_codigo_af: int = 15
    max_descripcion: int = 100
    max_centro_costos: int = 20
    max_observaciones: int = 300

    # CAMBIO: Precisión decimal según modelo
    # Tasa de cambio: 5 enteros, 9 decimales
    # Débito/Crédito: 11 enteros, 2 decimales
    # Bases: 11 enteros, 2 decimales


# =========================================================
# UTILIDADES
# =========================================================
def es_vacio(valor: Any) -> bool:
    """CAMBIO: Función mejorada para detectar valores vacíos"""
    if valor is None:
        return True
    if pd.isna(valor):
        return True
    texto = str(valor).strip()
    return texto == "" or texto.upper() in {"", "NAN", "NONE"}


def a_texto(valor: Any) -> str:
    """CAMBIO: Conversión a texto con trim"""
    if es_vacio(valor):
        return ""
    return str(valor).strip()


def truncar_texto(valor: Any, max_len: int) -> str:
    """CAMBIO: Truncar texto a longitud máxima"""
    texto = a_texto(valor)
    if len(texto) > max_len:
        return texto[:max_len]
    return texto


def formatear_fecha_ddmmyyyy(valor: Any) -> str:
    """
    CAMBIO: Conversión a DD/MM/AAAA con mejor manejo de errores
    Soporta múltiples formatos de entrada.
    """
    if es_vacio(valor):
        return ""

    texto = a_texto(valor)

    # Si ya está en formato DD/MM/AAAA, devolver como está
    if re.fullmatch(r"\d{2}/\d{2}/\d{4}", texto):
        return texto

    # Intentar convertir desde otros formatos
    try:
        fecha = pd.to_datetime(valor, errors="coerce")
        if pd.isna(fecha):
            return texto  # Devolver original si no se puede convertir
        return fecha.strftime("%d/%m/%Y")
    except Exception:
        return texto


def es_fecha_ddmmyyyy(valor: str) -> bool:
    """CAMBIO: Validar formato DD/MM/AAAA exacto"""
    if es_vacio(valor):
        return False
    texto = a_texto(valor)
    if not re.fullmatch(r"\d{2}/\d{2}/\d{4}", texto):
        return False

    # CAMBIO: Validar que la fecha sea real
    try:
        dia, mes, anio = map(int, texto.split("/"))
        if mes < 1 or mes > 12:
            return False
        if dia < 1 or dia > 31:
            return False
        return True
    except Exception:
        return False


def formatear_decimal_2(valor: Any) -> str:
    """CAMBIO: Formatear con exactamente 2 decimales para Débito/Crédito"""
    if es_vacio(valor):
        return ""
    try:
        num = float(valor)
        return f"{num:.2f}"
    except Exception:
        return ""


def formatear_decimal_9(valor: Any) -> str:
    """CAMBIO: Formatear con hasta 9 decimales para Tasa de Cambio"""
    if es_vacio(valor):
        return ""
    try:
        num = float(valor)
        # Limitar a 9 decimales
        return f"{num:.9f}".rstrip('0').rstrip('.')
    except Exception:
        return ""


def a_float_cero(valor: Any) -> float:
    """CAMBIO: Conversión segura a float con valor por defecto 0"""
    if es_vacio(valor):
        return 0.0
    try:
        return float(valor)
    except Exception:
        return 0.0


def validar_longitud_numerica(texto: str, enteros: int, decimales: int) -> bool:
    """
    CAMBIO: Validación mejorada de tamaño numérico
    Ej.: 11 enteros y 2 decimales para Débito/Crédito
    """
    if es_vacio(texto):
        return True

    texto = a_texto(texto)

    # Patrón: 1 a N enteros, opcionalmente punto, 1 a M decimales
    patron = rf"^\d{{1,{enteros}}}(\.\d{{1,{decimales}}})?$"
    return bool(re.fullmatch(patron, texto))


def validar_es_numerico(texto: str) -> bool:
    """CAMBIO: Validar que sea numérico"""
    if es_vacio(texto):
        return True
    try:
        float(texto)
        return True
    except Exception:
        return False


# =========================================================
# CONSTRUCCIÓN DEL PLANO
# =========================================================
def construir_plano_siigo(
    movimientos: pd.DataFrame,
    config: Optional[SiigoConfig] = None
) -> pd.DataFrame:
    """
    CAMBIO: Construye DataFrame con EXACTAMENTE las columnas del modelo
    Normaliza todos los datos según especificación SIIGO
    """
    if config is None:
        config = SiigoConfig()

    df = movimientos.copy()

    # CAMBIO: Crear columnas vacías si no existen
    for col in COLUMNAS_MODELO:
        if col not in df.columns:
            df[col] = ""

    # CAMBIO: Reordenar exactamente como exige el modelo
    df = df[COLUMNAS_MODELO].copy()

    # CAMBIO: Normalizar texto en todas las columnas de texto
    columnas_texto = [
        "Tipo de comprobante",
        "Consecutivo comprobante",
        "Sigla moneda",
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
        "Código impuesto",
        "Código grupo activo fijo",
        "Código activo fijo",
        "Descripción",
        "Código centro/subcentro de costos",
        "Observaciones",
        "Mes de cierre",
    ]

    for col in columnas_texto:
        df[col] = df[col].apply(a_texto)

    # CAMBIO: Convertir fechas a formato DD/MM/AAAA
    df["Fecha de elaboración"] = df["Fecha de elaboración"].apply(formatear_fecha_ddmmyyyy)
    df["Fecha vencimiento"] = df["Fecha vencimiento"].apply(formatear_fecha_ddmmyyyy)

    # CAMBIO: Convertir moneda a mayúsculas y validar
    df["Sigla moneda"] = df["Sigla moneda"].apply(lambda x: a_texto(x).upper())

    # CAMBIO: Limitar textos según longitudes máximas del modelo
    df["Tipo de comprobante"] = df["Tipo de comprobante"].apply(
        lambda x: truncar_texto(x, config.max_tipo_comprobante)
    )
    df["Consecutivo comprobante"] = df["Consecutivo comprobante"].apply(
        lambda x: truncar_texto(x, config.max_consecutivo_comprobante)
    )
    df["Código cuenta contable"] = df["Código cuenta contable"].apply(
        lambda x: truncar_texto(x, config.max_cuenta)
    )
    df["Identificación tercero"] = df["Identificación tercero"].apply(
        lambda x: truncar_texto(x, config.max_documento)
    )
    df["Sucursal"] = df["Sucursal"].apply(lambda x: truncar_texto(x, config.max_sucursal))
    df["Código producto"] = df["Código producto"].apply(
        lambda x: truncar_texto(x, config.max_codigo_producto)
    )
    df["Código de bodega"] = df["Código de bodega"].apply(
        lambda x: truncar_texto(x, config.max_codigo_bodega)
    )
    df["Acción"] = df["Acción"].apply(lambda x: truncar_texto(x, config.max_accion))
    df["Prefijo"] = df["Prefijo"].apply(lambda x: truncar_texto(x, config.max_prefijo))
    df["Consecutivo"] = df["Consecutivo"].apply(
        lambda x: truncar_texto(x, config.max_consecutivo)
    )
    df["No. cuota"] = df["No. cuota"].apply(lambda x: truncar_texto(x, config.max_no_cuota))
    df["Código impuesto"] = df["Código impuesto"].apply(
        lambda x: truncar_texto(x, config.max_codigo_impuesto)
    )
    df["Código grupo activo fijo"] = df["Código grupo activo fijo"].apply(
        lambda x: truncar_texto(x, config.max_codigo_grupo_af)
    )
    df["Código activo fijo"] = df["Código activo fijo"].apply(
        lambda x: truncar_texto(x, config.max_codigo_af)
    )
    df["Descripción"] = df["Descripción"].apply(
        lambda x: truncar_texto(x, config.max_descripcion)
    )
    df["Código centro/subcentro de costos"] = df["Código centro/subcentro de costos"].apply(
        lambda x: truncar_texto(x, config.max_centro_costos)
    )
    df["Observaciones"] = df["Observaciones"].apply(
        lambda x: truncar_texto(x, config.max_observaciones)
    )

    # CAMBIO: Validar Mes de cierre = SI o NO
    df["Mes de cierre"] = df["Mes de cierre"].apply(
        lambda x: "SI" if a_texto(x).upper() in {"SI", "SÍ"} else ("NO" if not es_vacio(x) else "")
    )

    # CAMBIO: Formato numérico con 2 decimales para Débito/Crédito
    df["Débito"] = df["Débito"].apply(formatear_decimal_2)
    df["Crédito"] = df["Crédito"].apply(formatear_decimal_2)

    # CAMBIO: Formato numérico con 2 decimales para Bases
    df["Base gravable libro compras/ventas"] = df["Base gravable libro compras/ventas"].apply(
        formatear_decimal_2
    )
    df["Base exenta libro compras/ventas"] = df["Base exenta libro compras/ventas"].apply(
        formatear_decimal_2
    )

    # CAMBIO: Formato numérico con hasta 9 decimales para Tasa de Cambio
    df["Tasa de cambio"] = df["Tasa de cambio"].apply(formatear_decimal_9)

    # CAMBIO: Formato numérico para Cantidad producto
    df["Cantidad producto"] = df["Cantidad producto"].apply(
        lambda x: a_texto(x) if es_vacio(x) else formatear_decimal_2(x)
    )

    return df


# =========================================================
# VALIDACIÓN DEL PLANO
# =========================================================
def validar_plano_siigo(
    df_plano: pd.DataFrame,
    config: Optional[SiigoConfig] = None
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    CAMBIO: Validación completa según modelo SIIGO
    Devuelve: df_validado, df_errores
    """
    if config is None:
        config = SiigoConfig()

    errores: List[Dict[str, Any]] = []

    for idx, row in df_plano.iterrows():
        fila_excel = idx + 2  # Considerando encabezado en fila 1

        # CAMBIO: Extraer valores normalizados
        tipo_comprobante = a_texto(row["Tipo de comprobante"]).upper()
        consecutivo_comprobante = a_texto(row["Consecutivo comprobante"])
        fecha_elaboracion = a_texto(row["Fecha de elaboración"])
        sigla_moneda = a_texto(row["Sigla moneda"]).upper()
        tasa_cambio = a_texto(row["Tasa de cambio"])
        cuenta = a_texto(row["Código cuenta contable"])
        tercero = a_texto(row["Identificación tercero"])
        sucursal = a_texto(row["Sucursal"])
        codigo_producto = a_texto(row["Código producto"])
        codigo_bodega = a_texto(row["Código de bodega"])
        accion = a_texto(row["Acción"])
        cantidad_producto = a_texto(row["Cantidad producto"])
        prefijo = a_texto(row["Prefijo"])
        consecutivo_doc = a_texto(row["Consecutivo"])
        no_cuota = a_texto(row["No. cuota"])
        fecha_vencimiento = a_texto(row["Fecha vencimiento"])
        codigo_impuesto = a_texto(row["Código impuesto"])
        codigo_grupo_af = a_texto(row["Código grupo activo fijo"])
        codigo_af = a_texto(row["Código activo fijo"])
        descripcion = a_texto(row["Descripción"])
        centro_costos = a_texto(row["Código centro/subcentro de costos"])
        debito = a_texto(row["Débito"])
        credito = a_texto(row["Crédito"])
        observaciones = a_texto(row["Observaciones"])
        base_gravable = a_texto(row["Base gravable libro compras/ventas"])
        base_exenta = a_texto(row["Base exenta libro compras/ventas"])
        mes_cierre = a_texto(row["Mes de cierre"]).upper()

        # =====================================================
        # CAMBIO: Validaciones de campos obligatorios
        # =====================================================

        # Tipo de comprobante: obligatorio y debe ser válido
        if es_vacio(tipo_comprobante):
            errores.append({
                "fila": fila_excel,
                "columna": "Tipo de comprobante",
                "error": "Campo obligatorio",
                "valor": tipo_comprobante
            })
        elif tipo_comprobante not in TIPOS_COMPROBANTE_VALIDOS:
            # CAMBIO: Validar contra tipos válidos
            errores.append({
                "fila": fila_excel,
                "columna": "Tipo de comprobante",
                "error": f"Tipo no válido. Permitidos: {', '.join(TIPOS_COMPROBANTE_VALIDOS.keys())}",
                "valor": tipo_comprobante
            })

        # Consecutivo comprobante: obligatorio
        if es_vacio(consecutivo_comprobante):
            errores.append({
                "fila": fila_excel,
                "columna": "Consecutivo comprobante",
                "error": "Campo obligatorio",
                "valor": consecutivo_comprobante
            })

        # Fecha de elaboración: obligatoria y formato DD/MM/AAAA
        if es_vacio(fecha_elaboracion):
            errores.append({
                "fila": fila_excel,
                "columna": "Fecha de elaboración",
                "error": "Campo obligatorio",
                "valor": fecha_elaboracion
            })
        elif not es_fecha_ddmmyyyy(fecha_elaboracion):
            # CAMBIO: Validar formato exacto DD/MM/AAAA
            errores.append({
                "fila": fila_excel,
                "columna": "Fecha de elaboración",
                "error": "Formato debe ser DD/MM/AAAA",
                "valor": fecha_elaboracion
            })

        # Código cuenta contable: obligatorio
        if es_vacio(cuenta):
            errores.append({
                "fila": fila_excel,
                "columna": "Código cuenta contable",
                "error": "Campo obligatorio",
                "valor": cuenta
            })

        # Identificación tercero: obligatorio
        if es_vacio(tercero):
            errores.append({
                "fila": fila_excel,
                "columna": "Identificación tercero",
                "error": "Campo obligatorio",
                "valor": tercero
            })

        # Descripción: obligatoria
        if es_vacio(descripcion):
            errores.append({
                "fila": fila_excel,
                "columna": "Descripción",
                "error": "Campo obligatorio",
                "valor": descripcion
            })

        # Débito y Crédito: al menos uno es obligatorio
        d = a_float_cero(debito)
        c = a_float_cero(credito)
        if d <= 0 and c <= 0:
            # CAMBIO: Validar que existe al menos Débito o Crédito
            errores.append({
                "fila": fila_excel,
                "columna": "Débito/Crédito",
                "error": "Debe existir Débito o Crédito mayor a cero",
                "valor": f"D={debito} C={credito}"
            })

        # =====================================================
        # CAMBIO: Validaciones de moneda y tasa de cambio
        # =====================================================
        if es_vacio(sigla_moneda):
            errores.append({
                "fila": fila_excel,
                "columna": "Sigla moneda",
                "error": "Campo obligatorio",
                "valor": sigla_moneda
            })
        elif len(sigla_moneda) > config.max_sigla_moneda:
            errores.append({
                "fila": fila_excel,
                "columna": "Sigla moneda",
                "error": f"Máximo {config.max_sigla_moneda} caracteres",
                "valor": sigla_moneda
            })

        # CAMBIO: Tasa de cambio obligatoria si moneda es diferente a la local
        if sigla_moneda and sigla_moneda != config.moneda_local:
            if es_vacio(tasa_cambio):
                errores.append({
                    "fila": fila_excel,
                    "columna": "Tasa de cambio",
                    "error": "Obligatoria cuando la moneda es diferente a COP",
                    "valor": tasa_cambio
                })
            else:
                # CAMBIO: Validar que sea numérica
                if not validar_es_numerico(tasa_cambio):
                    errores.append({
                        "fila": fila_excel,
                        "columna": "Tasa de cambio",
                        "error": "Debe ser numérica",
                        "valor": tasa_cambio
                    })
                else:
                    tasa_val = a_float_cero(tasa_cambio)
                    if tasa_val <= 0:
                        # CAMBIO: Validar que sea mayor a cero
                        errores.append({
                            "fila": fila_excel,
                            "columna": "Tasa de cambio",
                            "error": "Debe ser mayor a cero",
                            "valor": tasa_cambio
                        })
                    # CAMBIO: Validar longitud numérica (5 enteros, 9 decimales máximo)
                    elif not validar_longitud_numerica(tasa_cambio, 5, 9):
                        errores.append({
                            "fila": fila_excel,
                            "columna": "Tasa de cambio",
                            "error": "Máximo 5 enteros y 9 decimales",
                            "valor": tasa_cambio
                        })

        # =====================================================
        # CAMBIO: Validaciones de dependencias por inventario
        # =====================================================
        if cuenta in config.cuentas_inventario:
            # Código producto: obligatorio para inventario
            if es_vacio(codigo_producto):
                errores.append({
                    "fila": fila_excel,
                    "columna": "Código producto",
                    "error": "Obligatorio para cuentas de inventario",
                    "valor": codigo_producto
                })

            # Código bodega: obligatorio para inventario
            if es_vacio(codigo_bodega):
                errores.append({
                    "fila": fila_excel,
                    "columna": "Código de bodega",
                    "error": "Obligatorio para cuentas de inventario",
                    "valor": codigo_bodega
                })

            # Acción: obligatoria y validar valores
            if es_vacio(accion):
                errores.append({
                    "fila": fila_excel,
                    "columna": "Acción",
                    "error": "Obligatoria para cuentas de inventario",
                    "valor": accion
                })
            elif accion not in ACCIONES_INVENTARIO:
                # CAMBIO: Validar contra acciones permitidas
                errores.append({
                    "fila": fila_excel,
                    "columna": "Acción",
                    "error": f"Debe ser una de: {', '.join(ACCIONES_INVENTARIO)}",
                    "valor": accion
                })

            # Cantidad producto: obligatoria para inventario
            if es_vacio(cantidad_producto):
                errores.append({
                    "fila": fila_excel,
                    "columna": "Cantidad producto",
                    "error": "Obligatoria para cuentas de inventario",
                    "valor": cantidad_producto
                })
            elif not validar_es_numerico(cantidad_producto):
                # CAMBIO: Validar que sea numérica
                errores.append({
                    "fila": fila_excel,
                    "columna": "Cantidad producto",
                    "error": "Debe ser numérica",
                    "valor": cantidad_producto
                })

        # =====================================================
        # CAMBIO: Validaciones de dependencias por vencimiento
        # =====================================================
        if cuenta in config.cuentas_vencimiento:
            # Prefijo: obligatorio
            if es_vacio(prefijo):
                errores.append({
                    "fila": fila_excel,
                    "columna": "Prefijo",
                    "error": "Obligatorio para cuentas con vencimiento",
                    "valor": prefijo
                })

            # Consecutivo: obligatorio
            if es_vacio(consecutivo_doc):
                errores.append({
                    "fila": fila_excel,
                    "columna": "Consecutivo",
                    "error": "Obligatorio para cuentas con vencimiento",
                    "valor": consecutivo_doc
                })

            # No. cuota: obligatorio
            if es_vacio(no_cuota):
                errores.append({
                    "fila": fila_excel,
                    "columna": "No. cuota",
                    "error": "Obligatorio para cuentas con vencimiento",
                    "valor": no_cuota
                })
            elif not validar_es_numerico(no_cuota):
                # CAMBIO: Validar que sea numérico
                errores.append({
                    "fila": fila_excel,
                    "columna": "No. cuota",
                    "error": "Debe ser numérico",
                    "valor": no_cuota
                })

            # Fecha vencimiento: obligatoria y formato DD/MM/AAAA
            if es_vacio(fecha_vencimiento):
                errores.append({
                    "fila": fila_excel,
                    "columna": "Fecha vencimiento",
                    "error": "Obligatoria para cuentas con vencimiento",
                    "valor": fecha_vencimiento
                })
            elif not es_fecha_ddmmyyyy(fecha_vencimiento):
                # CAMBIO: Validar formato exacto DD/MM/AAAA
                errores.append({
                    "fila": fila_excel,
                    "columna": "Fecha vencimiento",
                    "error": "Formato debe ser DD/MM/AAAA",
                    "valor": fecha_vencimiento
                })

        # =====================================================
        # CAMBIO: Validaciones de dependencias por impuesto
        # =====================================================
        if cuenta in config.cuentas_impuesto:
            if es_vacio(codigo_impuesto):
                errores.append({
                    "fila": fila_excel,
                    "columna": "Código impuesto",
                    "error": "Obligatorio para cuentas de impuesto",
                    "valor": codigo_impuesto
                })

        # =====================================================
        # CAMBIO: Validaciones de dependencias por activos fijos
        # =====================================================
        if cuenta in config.cuentas_activo_fijo:
            # Código grupo activo fijo: obligatorio
            if es_vacio(codigo_grupo_af):
                errores.append({
                    "fila": fila_excel,
                    "columna": "Código grupo activo fijo",
                    "error": "Obligatorio para cuentas de activo fijo",
                    "valor": codigo_grupo_af
                })

            # Código activo fijo: obligatorio
            if es_vacio(codigo_af):
                errores.append({
                    "fila": fila_excel,
                    "columna": "Código activo fijo",
                    "error": "Obligatorio para cuentas de activo fijo",
                    "valor": codigo_af
                })

        # =====================================================
        # CAMBIO: Validaciones de formatos numéricos
        # =====================================================
        if debito and not validar_longitud_numerica(debito, 11, 2):
            errores.append({
                "fila": fila_excel,
                "columna": "Débito",
                "error": "Máximo 11 enteros y 2 decimales",
                "valor": debito
            })

        if credito and not validar_longitud_numerica(credito, 11, 2):
            errores.append({
                "fila": fila_excel,
                "columna": "Crédito",
                "error": "Máximo 11 enteros y 2 decimales",
                "valor": credito
            })

        if base_gravable and not validar_longitud_numerica(base_gravable, 11, 2):
            # CAMBIO: Validar Base gravable
            errores.append({
                "fila": fila_excel,
                "columna": "Base gravable libro compras/ventas",
                "error": "Máximo 11 enteros y 2 decimales",
                "valor": base_gravable
            })

        if base_exenta and not validar_longitud_numerica(base_exenta, 11, 2):
            # CAMBIO: Validar Base exenta
            errores.append({
                "fila": fila_excel,
                "columna": "Base exenta libro compras/ventas",
                "error": "Máximo 11 enteros y 2 decimales",
                "valor": base_exenta
            })

        # =====================================================
        # CAMBIO: No debe haber Débito y Crédito simultáneamente
        # =====================================================
        if d > 0 and c > 0:
            errores.append({
                "fila": fila_excel,
                "columna": "Débito/Crédito",
                "error": "No puede haber Débito y Crédito mayores a cero simultáneamente",
                "valor": f"D={debito} C={credito}"
            })

        # =====================================================
        # CAMBIO: Validación de Mes de cierre
        # =====================================================
        if mes_cierre and mes_cierre not in {"SI", "NO"}:
            errores.append({
                "fila": fila_excel,
                "columna": "Mes de cierre",
                "error": "Debe ser SI o NO",
                "valor": mes_cierre
            })

        # =====================================================
        # CAMBIO: Centro de costos - validar formato
        # =====================================================
        if centro_costos and not re.fullmatch(r"[A-Za-z0-9\-]+", centro_costos):
            errores.append({
                "fila": fila_excel,
                "columna": "Código centro/subcentro de costos",
                "error": "Solo se permiten caracteres alfanuméricos y guiones",
                "valor": centro_costos
            })

    # =====================================================
    # CAMBIO: Validación transversal - Tasa de cambio consistente por comprobante
    # =====================================================
    grupo_comprobantes = df_plano.groupby(
        ["Tipo de comprobante", "Consecutivo comprobante"]
    ).agg({
        "Sigla moneda": lambda x: x.unique(),
        "Tasa de cambio": lambda x: x.unique()
    }).reset_index()

    for idx, row_grupo in grupo_comprobantes.iterrows():
        monedas = [m for m in row_grupo["Sigla moneda"] if not es_vacio(m)]
        tasas = [t for t in row_grupo["Tasa de cambio"] if not es_vacio(t)]

        # Si hay diferentes monedas en el mismo comprobante
        if len(set(monedas)) > 1:
            # CAMBIO: Validar que todas las monedas sean la misma
            filas_comprobante = df_plano[
                (df_plano["Tipo de comprobante"] == row_grupo["Tipo de comprobante"]) &
                (df_plano["Consecutivo comprobante"] == row_grupo["Consecutivo comprobante"])
            ].index

            for fila_idx in filas_comprobante:
                errores.append({
                    "fila": fila_idx + 2,
                    "columna": "Sigla moneda",
                    "error": "Todas las líneas del comprobante deben tener la misma moneda",
                    "valor": df_plano.loc[fila_idx, "Sigla moneda"]
                })

        # Si hay diferentes tasas para la misma moneda en el mismo comprobante
        if len(set(tasas)) > 1 and any(m != config.moneda_local for m in monedas):
            # CAMBIO: Validar consistencia de tasa por comprobante
            filas_comprobante = df_plano[
                (df_plano["Tipo de comprobante"] == row_grupo["Tipo de comprobante"]) &
                (df_plano["Consecutivo comprobante"] == row_grupo["Consecutivo comprobante"])
            ].index

            for fila_idx in filas_comprobante:
                errores.append({
                    "fila": fila_idx + 2,
                    "columna": "Tasa de cambio",
                    "error": "Todas las líneas del comprobante deben tener la misma tasa de cambio",
                    "valor": df_plano.loc[fila_idx, "Tasa de cambio"]
                })

    # =====================================================
    # Convertir a DataFrame
    # =====================================================
    df_errores = pd.DataFrame(
        errores,
        columns=["fila", "columna", "error", "valor"]
    ) if errores else pd.DataFrame(columns=["fila", "columna", "error", "valor"])

    return df_plano.copy(), df_errores


# =========================================================
# EXPORTACIÓN
# =========================================================
def exportar_plano_siigo(
    df_plano: pd.DataFrame,
    df_errores: pd.DataFrame,
    ruta_excel: str = "plano_siigo_generado.xlsx",
    ruta_csv: Optional[str] = None
) -> str:
    """
    CAMBIO: Exporta a Excel con hojas Plano y Errores
    """
    with pd.ExcelWriter(ruta_excel, engine="openpyxl") as writer:
        # CAMBIO: Hoja Plano con todas las columnas del modelo
        df_plano.to_excel(writer, sheet_name="Plano", index=False)

        # CAMBIO: Hoja Errores con detalle de validaciones
        if not df_errores.empty:
            df_errores.to_excel(writer, sheet_name="Errores", index=False)
        else:
            # CAMBIO: Si no hay errores, crear hoja con mensaje
            pd.DataFrame([{"Mensaje": "✅ No se encontraron errores"}]).to_excel(
                writer, sheet_name="Errores", index=False
            )

    # CAMBIO: Exportar CSV opcional
    if ruta_csv:
        df_plano.to_csv(ruta_csv, index=False, encoding="utf-8-sig")

    return ruta_excel


# =========================================================
# EJEMPLO DE USO
# =========================================================
if __name__ == "__main__":
    # =====================================================
    # CAMBIO: Datos de ejemplo actualizados
    # =====================================================
    movimientos = pd.DataFrame([
        {
            # CAMBIO: Tipo de comprobante debe ser válido (ND, NC, FV, FC, REC, CHQ, TR)
            "Tipo de comprobante": "FC",
            "Consecutivo comprobante": "COM-001",
            "Fecha de elaboración": "2026-06-14",
            "Sigla moneda": "COP",
            "Tasa de cambio": "",
            "Código cuenta contable": "2205",
            "Identificación tercero": "800123456",
            "Sucursal": "BOGOTA",
            "Código producto": "",
            "Código de bodega": "",
            "Acción": "",
            "Cantidad producto": "",
            "Prefijo": "PUP",
            "Consecutivo": "1001",
            "No. cuota": "1",
            "Fecha vencimiento": "2026-07-14",
            "Código impuesto": "IVA",
            "Código grupo activo fijo": "",
            "Código activo fijo": "",
            "Descripción": "Factura de compra de mercancía",
            "Código centro/subcentro de costos": "1-1",
            "Débito": "",
            "Crédito": "5000000.00",
            "Observaciones": "Comprobante de ejemplo",
            "Base gravable libro compras/ventas": "5000000.00",
            "Base exenta libro compras/ventas": "",
            "Mes de cierre": "NO",
        },
        {
            # CAMBIO: Segunda línea con débito
            "Tipo de comprobante": "FC",
            "Consecutivo comprobante": "COM-001",
            "Fecha de elaboración": "14/06/2026",
            "Sigla moneda": "COP",
            "Tasa de cambio": "",
            "Código cuenta contable": "1105",
            "Identificación tercero": "800123456",
            "Sucursal": "BOGOTA",
            "Código producto": "",
            "Código de bodega": "",
            "Acción": "",
            "Cantidad producto": "",
            "Prefijo": "PUP",
            "Consecutivo": "1001",
            "No. cuota": "1",
            "Fecha vencimiento": "14/07/2026",
            "Código impuesto": "",
            "Código grupo activo fijo": "",
            "Código activo fijo": "",
            "Descripción": "Pago de la factura",
            "Código centro/subcentro de costos": "1-1",
            "Débito": "5000000.00",
            "Crédito": "",
            "Observaciones": "Pago por cheque",
            "Base gravable libro compras/ventas": "",
            "Base exenta libro compras/ventas": "",
            "Mes de cierre": "NO",
        },
    ])

    # =====================================================
    # CAMBIO: Configurar reglas condicionales
    # =====================================================
    config = SiigoConfig(
        moneda_local="COP",
        # CAMBIO: Cuentas que requieren inventario
        cuentas_inventario={"143505", "143510"},
        # CAMBIO: Cuentas que requieren vencimiento
        cuentas_vencimiento={"130505", "220505", "2205"},
        # CAMBIO: Cuentas que requieren impuesto
        cuentas_impuesto={"240805"},
        # CAMBIO: Cuentas que requieren activos fijos
        cuentas_activo_fijo={"152405"},
    )

    # =====================================================
    # CAMBIO: Construcción del plano
    # =====================================================
    plano = construir_plano_siigo(movimientos, config=config)

    # =====================================================
    # CAMBIO: Validación del plano
    # =====================================================
    plano_validado, errores = validar_plano_siigo(plano, config=config)

    # =====================================================
    # CAMBIO: Exportación
    # =====================================================
    archivo = exportar_plano_siigo(
        df_plano=plano_validado,
        df_errores=errores,
        ruta_excel="plano_siigo_generado.xlsx",
        ruta_csv="plano_siigo_generado.csv"
    )

    print("=" * 80)
    print("GENERADOR DE PLANO SIIGO - VALIDACIÓN")
    print("=" * 80)
    print(f"\n✅ Archivo generado: {archivo}")
    print(f"📊 Total de filas: {len(plano_validado)}")
    print(f"❌ Total de errores detectados: {len(errores)}")

    if not errores.empty:
        print("\n⚠️ ERRORES ENCONTRADOS:")
        print(errores.to_string(index=False))
    else:
        print("\n✅ Validación completada sin errores")

    print("\n" + "=" * 80)
    print("PLANO GENERADO:")
    print("=" * 80)
    print(plano_validado.to_string(index=False))

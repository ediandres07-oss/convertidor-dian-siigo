import io
import openpyxl
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side, numbers
from openpyxl.utils import get_column_letter

# NIT del proveedor de inventario — sus facturas van a COMPRAS
NIT_PROVEEDOR_INVENTARIO = "830040709"

# ========================================
# MAPEO CONCEPTO -> CUENTA DE GASTO
# ========================================
CONCEPTO_CUENTA_MAP = {
    "PIEZAS VEHICULOS": "52454001",
    "COMBUSTIBLE":      "52953501",
    "PROCESAMIENTO DE DATOS": "52352001",
    "SEGUROS":          "52304001",
    "FLETES":           "52953001",
    "GASTOS LEGALES":   "52509501",
    "ADECUACIONES":     "52055101",
    "UTILES":           "52355001",
}

# ========================================
# MAPEO NIT -> (CUENTA DE GASTO, CUENTA IVA, COD_IMPUESTO)
# Construido desde el histórico de la hoja GASTOS manual.
# cod_imp: 1 = IVA descontable bienes, None = IVA descontable servicios
# ========================================
NIT_DETAIL_MAP = {
    # --- Personas naturales / sin IVA conocido → default ---
    "1022092204": ("52454001", "24081001", 1),
    "1038333727": ("52454001", "24081001", 1),
    "1038334816": ("52454001", "24081001", 1),
    "1098757457": ("52454001", "24081001", 1),
    "15400875":   ("52509501", "24081501", None),   # GASTOS LEGALES + IVA servicios
    "15404656":   ("52454001", "24081001", 1),
    "21667787":   ("52454001", "24081001", 1),
    "32349185":   ("52454001", "24081001", 1),       # PIEZAS VEHICULOS
    "3603022":    ("52953501", "24081001", 1),       # COMBUSTIBLE
    "43161428":   ("52454001", "24081001", 1),       # PIEZAS VEHICULOS
    "70051912":   ("52509501", "24081001", 1),       # override manual
    "70162940":   ("52956501", "24081001", 1),       # override manual (combustible especial)
    "70602269":   ("52454001", "24081001", 1),
    "800048847":  ("52953501", "24081001", 1),       # JCR COMBUSTIBLE
    "800153993":  ("52353501", "24081501", None),    # COMCEL — override manual
    "800242106":  ("52454001", "24081001", 1),
    "800251569":  ("52953001", "24081501", None),    # INTER RAPIDISIMO FLETES
    "805012610":  ("52454001", "24081001", 1),
    "805018674":  ("52352001", "24081501", None),    # ECOM procesamiento datos
    "811004112":  ("52454001", "24081001", 1),       # DISPARTES PIEZAS
    "811015158":  ("52953501", "24081001", 1),       # ZUPETROL COMBUSTIBLE
    "811019874":  ("52454001", "24081001", 1),
    "811023037":  ("52355001", "24081001", 1),       # PAPELERIA UTILES
    "811027052":  ("52454001", "24081001", 1),
    "811027786":  ("52454001", "24081001", 1),       # ECOLLANTAS PIEZAS
    "811036875":  ("53052001", "24081001", 1),       # override manual
    "811039882":  ("52454001", "24081001", 1),
    "811044263":  ("52454001", "24081001", 1),       # CARPAS Y LUBRICANTES
    "830059699":  ("52352001", "24081501", None),    # Satrack procesamiento datos
    "860002400":  ("52304001", "24081501", None),    # LA PREVISORA SEGUROS
    "890900081":  ("52454001", "24081001", 1),       # AUTOLARTE PIEZAS
    "890902872":  ("52454001", "24081001", 1),
    "890903407":  ("52304001", "24081501", None),    # SURAMERICANA SEGUROS — override manual
    "890904996":  ("52454001", "24081001", 1),
    "890984843":  ("52454001", "24081001", 1),
    "900116036":  ("52454001", "24081001", 1),
    "900160139":  ("52953501", "24081001", 1),       # EDS LA VARIANTE COMBUSTIBLE
    "900344127":  ("52454001", "24081001", 1),
    "900459737":  ("52953501", "24081001", 1),       # GRUPO EDS AUTOGAS COMBUSTIBLE
    "900491889":  ("52953501", "24081001", 1),       # EDS TERPEL COMBUSTIBLE
    "900541746":  ("52454001", "24081001", 1),
    "900704090":  ("52454001", "24081001", 1),       # RINCARD PIEZAS
    "900758571":  ("52454001", "24081001", 1),
    "901031400":  ("52454001", "24081001", 1),       # FERROPARTES PIEZAS
    "901076394":  ("52953501", "24081001", 1),       # NEOINVERCALO COMBUSTIBLE
    "901105704":  ("52454001", "24081001", 1),
    "901113085":  ("52454001", "24081001", 1),
    "901113902":  ("52454001", "24081001", 1),       # ELECTRICOS LA CABANA PIEZAS
    "901118254":  ("52454001", "24081001", 1),
    "901124504":  ("52953001", "24081501", None),    # Harinas del Sinu FLETES
    "901150329":  ("52454001", "24081001", 1),
    "901218235":  ("52454001", "24081001", 1),       # HIDRAULICAS Y REPUESTOS PIEZAS
    "901253560":  ("52454001", "24081001", 1),       # TORNIRACORES PIEZAS
    "901259705":  ("52454001", "24081001", 1),
    "901269431":  ("52454001", "24081001", 1),       # LUBRIMEDELLIN PIEZAS
    "901335972":  ("52454001", "24081001", 1),
    "901340988":  ("52454001", "24081001", 1),       # CAJAS FUERTES PIEZAS
    "901351826":  ("52454001", "24081001", 1),
    "901553102":  ("52055101", "24081001", 1),       # JOSAOS ADECUACIONES
    "901565059":  ("52454001", "24081001", 1),       # ELECTRILUJOS PIEZAS
    "901575667":  ("52454001", "24081001", 1),       # CDA OCCIDENTE PIEZAS
    "901644399":  ("52454001", "24081001", 1),       # CDA SAN GERMAN PIEZAS
    "901783612":  ("52454001", "24081001", 1),
    "901826538":  ("52355001", "24081001", 1),       # PAPELERIA MUNDIAL UTILES
    "901903899":  ("52454001", "24081001", 1),       # RINES Y LLANTAS PIEZAS
    "98585449":   ("52454001", "24081001", 1),
}

# Defaults para proveedores nuevos no mapeados
DEFAULT_CUENTA_GASTO = "52454001"
DEFAULT_IVA_CUENTA   = "24081001"
DEFAULT_COD_IMP      = 1

# ========================================
# ENCABEZADOS DEL PLANO SIIGO
# ========================================
HEADERS = [
    'Tipo de comprobante', 'Consecutivo comprobante', 'Fecha de elaboración ',
    'Sigla moneda', 'Tasa de cambio', 'Código cuenta contable',
    'Identificación tercero', 'Sucursal', 'Código producto',
    'Código de bodega', 'Acción', 'Cantidad producto',
    'Prefijo', 'Consecutivo', 'No. cuota',
    'Fecha vencimiento', 'Código impuesto', 'Código grupo activo fijo',
    'Código activo fijo', 'Descripción', 'Código centro/subcentro de costos',
    'Débito', 'Crédito', 'Observaciones',
    'Base gravable libro compras/ventas  ', 'Base exenta libro compras/ventas',
    'Mes de cierre'
]


def make_row(tipo_comp, consec, fecha, cuenta, nit, cod_imp, descripcion, debito, credito):
    return [
        tipo_comp, consec, fecha, None, None, cuenta,
        str(nit) if nit else None, None, None, None, None, None,
        None, None, None, None, cod_imp, None, None, descripcion, None,
        debito, credito, None, None, None, None
    ]


def _write_headers(ws):
    for col, header in enumerate(HEADERS, 1):
        ws.cell(row=1, column=col, value=header)


# ========================================
# LECTURA DE LA HOJA REPORTE
# ========================================

def _detect_mi_nit(ws, fmt):
    """
    Detecta automáticamente el NIT del negocio (receptor más frecuente,
    excluyendo NITs genéricos de venta ocasional).
    """
    from collections import Counter
    col_receptor = 8 if fmt == 'reporte' else 12
    EXCLUIDOS = {'222222222222', '0', '', 'None'}
    conteo = Counter()
    for r in range(2, ws.max_row + 1):
        nit = str(ws.cell(r, col_receptor).value or '').strip()
        if nit not in EXCLUIDOS:
            conteo[nit] += 1
    if not conteo:
        raise ValueError("No se encontró ningún NIT receptor en el archivo.")
    return conteo.most_common(1)[0][0]


def _detect_format(wb_src):
    """
    Detecta el formato del archivo DIAN.
    Retorna ('reporte', ws) para el formato antiguo (hoja REPORTE)
    o ('nuevo', ws) para el formato nuevo (hoja Rp_Doc_XXXXXXXX).
    """
    if 'REPORTE' in wb_src.sheetnames:
        return 'reporte', wb_src['REPORTE']
    # Buscar hoja con prefijo Rp_Doc_
    for name in wb_src.sheetnames:
        if name.startswith('Rp_Doc_') or name.startswith('Rp_'):
            return 'nuevo', wb_src[name]
    # Usar la primera hoja como fallback
    ws = wb_src[wb_src.sheetnames[0]]
    header = str(ws.cell(1, 1).value or '').strip()
    if header == 'Tipo de documento':
        return 'nuevo', ws
    raise ValueError(
        f"No se reconoce el formato del archivo. "
        f"Hojas encontradas: {wb_src.sheetnames}. "
        f"Se esperaba una hoja llamada 'REPORTE' o 'Rp_Doc_...'."
    )


def read_reporte(wb_src):
    """Lee el reporte DIAN (formato antiguo o nuevo) y clasifica en tres listas."""
    fmt, ws = _detect_format(wb_src)
    mi_nit = _detect_mi_nit(ws, fmt)

    facturas_compras = []
    facturas_gastos  = []
    notas_credito    = []

    for row_idx in range(2, ws.max_row + 1):
        if fmt == 'reporte':
            # Formato antiguo: hoja REPORTE
            tipo         = ws.cell(row_idx, 1).value
            folio        = ws.cell(row_idx, 3).value
            fecha        = ws.cell(row_idx, 5).value
            nit_emisor   = str(ws.cell(row_idx, 6).value or '').strip()
            nit_receptor = str(ws.cell(row_idx, 8).value or '').strip()
            no_gravado   = float(ws.cell(row_idx, 10).value or 0)
            gravado      = float(ws.cell(row_idx, 11).value or 0)
            iva          = float(ws.cell(row_idx, 12).value or 0)
            total        = float(ws.cell(row_idx, 13).value or 0)
        else:
            # Formato nuevo: hoja Rp_Doc_XXXXXXXX
            # Col 1: Tipo, 3: Folio, 8: Fecha Emisión, 10: NIT Emisor,
            # 12: NIT Receptor, 14: IVA, 30: Total
            tipo         = ws.cell(row_idx, 1).value
            folio        = ws.cell(row_idx, 3).value
            fecha        = ws.cell(row_idx, 8).value
            nit_emisor   = str(ws.cell(row_idx, 10).value or '').strip()
            nit_receptor = str(ws.cell(row_idx, 12).value or '').strip()
            iva          = float(ws.cell(row_idx, 14).value or 0)
            total        = float(ws.cell(row_idx, 30).value or 0)
            # Calcular base gravable: iva / 0.19 si iva > 0
            gravado      = round(iva / 0.19, 2) if iva > 0 else 0.0
            no_gravado   = round(total - gravado - iva, 2)
            if no_gravado < 0:
                no_gravado = 0.0

        # Solo documentos recibidos por el negocio
        if nit_receptor != mi_nit:
            continue
        if folio is None:
            continue

        tipo_str = str(tipo or '').lower()
        if 'nota de crédito' in tipo_str or 'nota de credito' in tipo_str:
            notas_credito.append({
                'folio': folio, 'fecha': fecha, 'nit': nit_emisor,
                'no_gravado': no_gravado, 'gravado': gravado,
                'iva': iva, 'total': total,
            })
        elif nit_emisor == NIT_PROVEEDOR_INVENTARIO:
            facturas_compras.append({
                'folio': folio, 'fecha': fecha, 'nit': nit_emisor,
                'gravado': gravado, 'iva': iva, 'total': total,
            })
        else:
            facturas_gastos.append({
                'folio': folio, 'fecha': fecha, 'nit': nit_emisor,
                'no_gravado': no_gravado, 'gravado': gravado,
                'iva': iva, 'total': total,
            })

    return facturas_compras, facturas_gastos, notas_credito


# ========================================
# GENERACIÓN DE PLANOS
# ========================================

def convert_compras(facturas, wb_dst, consec_inicio):
    ws_dst = wb_dst.create_sheet('COMPRAS')
    _write_headers(ws_dst)

    row_out = 2

    # Bloque 1: cuenta por cobrar cartera (crédito — CxP proveedor)
    consec = consec_inicio
    for f in facturas:
        row = make_row(9, consec, f['fecha'], '14350103', f['nit'], None,
                       f"FC: {f['folio']}", 0, 0)
        for col, val in enumerate(row, 1):
            ws_dst.cell(row=row_out, column=col, value=val)
        row_out += 1
        consec += 1

    # Bloque 2: mercancía gravada (débito)
    consec = consec_inicio
    for f in facturas:
        row = make_row(9, consec, f['fecha'], '14350101', f['nit'], None,
                       f"FC: {f['folio']}", f['gravado'], 0)
        for col, val in enumerate(row, 1):
            ws_dst.cell(row=row_out, column=col, value=val)
        row_out += 1
        consec += 1

    # Bloque 3: IVA descontable (débito)
    consec = consec_inicio
    for f in facturas:
        row = make_row(9, consec, f['fecha'], '24081001', f['nit'], 1,
                       f"FC: {f['folio']}", f['iva'], 0)
        for col, val in enumerate(row, 1):
            ws_dst.cell(row=row_out, column=col, value=val)
        row_out += 1
        consec += 1

    # Bloque 4: CxP proveedor (crédito)
    consec = consec_inicio
    for f in facturas:
        row = make_row(9, consec, f['fecha'], '22050501', f['nit'], None,
                       f"FC: {f['folio']}", 0, f['total'])
        for col, val in enumerate(row, 1):
            ws_dst.cell(row=row_out, column=col, value=val)
        row_out += 1
        consec += 1

    return consec_inicio + len(facturas)


def convert_nc_compras(notas, wb_dst, consec_inicio):
    if not notas:
        return consec_inicio

    ws_dst = wb_dst.create_sheet('NC COMPRAS')
    _write_headers(ws_dst)

    row_out = 2

    consec = consec_inicio
    for n in notas:
        credito_14350103 = n['no_gravado'] if n['no_gravado'] > 0 and n['gravado'] == 0 else 0
        row = make_row(10, consec, n['fecha'], '14350103', n['nit'], None,
                       f"NC: {n['folio']}", 0, credito_14350103)
        for col, val in enumerate(row, 1):
            ws_dst.cell(row=row_out, column=col, value=val)
        row_out += 1
        consec += 1

    consec = consec_inicio
    for n in notas:
        row = make_row(10, consec, n['fecha'], '14350101', n['nit'], None,
                       f"NC: {n['folio']}", 0, n['gravado'])
        for col, val in enumerate(row, 1):
            ws_dst.cell(row=row_out, column=col, value=val)
        row_out += 1
        consec += 1

    consec = consec_inicio
    for n in notas:
        row = make_row(10, consec, n['fecha'], '24081002', n['nit'], 1,
                       f"NC: {n['folio']}", 0, n['iva'])
        for col, val in enumerate(row, 1):
            ws_dst.cell(row=row_out, column=col, value=val)
        row_out += 1
        consec += 1

    consec = consec_inicio
    for n in notas:
        row = make_row(10, consec, n['fecha'], '22050501', n['nit'], None,
                       f"NC: {n['folio']}", n['total'], 0)
        for col, val in enumerate(row, 1):
            ws_dst.cell(row=row_out, column=col, value=val)
        row_out += 1
        consec += 1

    return consec_inicio + len(notas)


def convert_gastos(gastos, wb_dst, consec_inicio):
    ws_dst = wb_dst.create_sheet('GASTOS')
    _write_headers(ws_dst)

    row_out = 2

    # Bloque 1: cuenta de gasto (débito)
    consec = consec_inicio
    for g in gastos:
        nit_str = str(g['nit'])
        cuenta, _, _ = NIT_DETAIL_MAP.get(nit_str,
                       (DEFAULT_CUENTA_GASTO, DEFAULT_IVA_CUENTA, DEFAULT_COD_IMP))
        debito_gasto = int(g['gravado'] + g['no_gravado'])
        row = make_row(12, consec, g['fecha'], cuenta, g['nit'], None,
                       f"G: {g['folio']}", debito_gasto, 0)
        for col, val in enumerate(row, 1):
            ws_dst.cell(row=row_out, column=col, value=val)
        row_out += 1
        consec += 1

    # Bloque 2: IVA descontable (débito)
    consec = consec_inicio
    for g in gastos:
        nit_str = str(g['nit'])
        _, cuenta_iva, cod_imp = NIT_DETAIL_MAP.get(nit_str,
                                 (DEFAULT_CUENTA_GASTO, DEFAULT_IVA_CUENTA, DEFAULT_COD_IMP))
        row = make_row(12, consec, g['fecha'], cuenta_iva, g['nit'], cod_imp,
                       f"G: {g['folio']}", int(g['iva']), 0)
        for col, val in enumerate(row, 1):
            ws_dst.cell(row=row_out, column=col, value=val)
        row_out += 1
        consec += 1

    # Bloque 3: CxP proveedor (crédito)
    consec = consec_inicio
    for g in gastos:
        row = make_row(12, consec, g['fecha'], '23359501', g['nit'], None,
                       f"G: {g['folio']}", 0, int(g['total']))
        for col, val in enumerate(row, 1):
            ws_dst.cell(row=row_out, column=col, value=val)
        row_out += 1
        consec += 1

    return consec_inicio + len(gastos)


# ========================================
# PUNTO DE ENTRADA PRINCIPAL — PLANOS SIIGO
# ========================================

def process_file(input_stream, consec_compras=371, consec_nc=271, consec_gastos=798):
    """Lee el archivo DIAN (solo hoja REPORTE) y genera los tres planos Siigo."""
    wb_src = openpyxl.load_workbook(input_stream, data_only=True)

    facturas_compras, facturas_gastos, notas_credito = read_reporte(wb_src)

    wb_dst = Workbook()
    if wb_dst.active:
        wb_dst.remove(wb_dst.active)

    convert_compras(facturas_compras, wb_dst, consec_compras)
    convert_nc_compras(notas_credito, wb_dst, consec_nc)
    convert_gastos(facturas_gastos, wb_dst, consec_gastos)

    output_stream = io.BytesIO()
    wb_dst.save(output_stream)
    output_stream.seek(0)
    return output_stream


# ========================================
# LIQUIDACIÓN DE IVA — LECTURA VENTAS
# ========================================

def read_ventas_iva(wb_src):
    """
    Lee ventas y NC ventas (donde NIT_emisor = NIT del negocio).
    Soporta formato antiguo (hoja REPORTE) y nuevo (hoja Rp_Doc_...).
    Retorna (base_ventas, iva_ventas, base_nc_ventas, iva_nc_ventas, fecha_inicio, fecha_fin).
    """
    fmt, ws = _detect_format(wb_src)
    mi_nit = _detect_mi_nit(ws, fmt)
    base_ventas    = 0.0
    iva_ventas     = 0.0
    base_nc_ventas = 0.0
    iva_nc_ventas  = 0.0
    fechas = []

    for r in range(2, ws.max_row + 1):
        if fmt == 'reporte':
            tipo       = str(ws.cell(r, 1).value or '').lower()
            nit_emisor = str(ws.cell(r, 6).value or '').strip()
            fecha      = ws.cell(r, 5).value
            gravado    = float(ws.cell(r, 11).value or 0)
            iva        = float(ws.cell(r, 12).value or 0)
        else:
            tipo       = str(ws.cell(r, 1).value or '').lower()
            nit_emisor = str(ws.cell(r, 10).value or '').strip()
            fecha      = ws.cell(r, 8).value
            iva        = float(ws.cell(r, 14).value or 0)
            gravado    = round(iva / 0.19, 2) if iva > 0 else 0.0

        if nit_emisor != mi_nit:
            continue
        if fecha:
            fechas.append(fecha)
        if 'nota de crédito' in tipo or 'nota de credito' in tipo:
            base_nc_ventas += gravado
            iva_nc_ventas  += iva
        elif 'factura' in tipo:
            base_ventas += gravado
            iva_ventas  += iva

    fecha_inicio = min(fechas) if fechas else None
    fecha_fin    = max(fechas) if fechas else None
    return base_ventas, iva_ventas, base_nc_ventas, iva_nc_ventas, fecha_inicio, fecha_fin


# ========================================
# LIQUIDACIÓN DE IVA — GENERACIÓN ARCHIVO
# ========================================

def _fmt_date(d):
    if d is None:
        return ''
    if hasattr(d, 'strftime'):
        return d.strftime('%d/%m/%Y')
    return str(d)


def _make_border():
    thin = Side(style='thin', color='BFBFBF')
    return Border(left=thin, right=thin, top=thin, bottom=thin)


def _apply_cell(ws, row, col, value, bold=False, fill_hex=None, number_format=None,
                align='left', font_color='000000', font_size=10):
    cell = ws.cell(row=row, column=col, value=value)
    cell.font = Font(bold=bold, color=font_color, size=font_size)
    cell.alignment = Alignment(horizontal=align, vertical='center', wrap_text=False)
    cell.border = _make_border()
    if fill_hex:
        cell.fill = PatternFill(fill_type='solid', fgColor=fill_hex)
    if number_format:
        cell.number_format = number_format
    return cell


def generate_liquidacion_iva_file(facturas_compras, facturas_gastos, notas_credito,
                                  base_ventas, iva_ventas,
                                  base_nc_ventas, iva_nc_ventas,
                                  fecha_inicio, fecha_fin):
    """Genera un Excel con una hoja RESUMEN de liquidación de IVA."""

    # ── Cálculos ────────────────────────────────────────────────────────────
    base_compras_inv = sum(f['gravado'] for f in facturas_compras)
    iva_compras_inv  = sum(f['iva']     for f in facturas_compras)

    base_gastos_bienes    = 0.0;  iva_gastos_bienes    = 0.0
    base_gastos_servicios = 0.0;  iva_gastos_servicios = 0.0
    for g in facturas_gastos:
        _, cuenta_iva, _ = NIT_DETAIL_MAP.get(
            str(g['nit']), (DEFAULT_CUENTA_GASTO, DEFAULT_IVA_CUENTA, DEFAULT_COD_IMP))
        if cuenta_iva == '24081501':
            base_gastos_servicios += g['gravado']
            iva_gastos_servicios  += g['iva']
        else:
            base_gastos_bienes += g['gravado']
            iva_gastos_bienes  += g['iva']

    base_nc_compras = sum(n['gravado'] for n in notas_credito)
    iva_nc_compras  = sum(n['iva']     for n in notas_credito)

    base_generado_neto    = base_ventas - base_nc_ventas
    iva_generado_neto     = iva_ventas  - iva_nc_ventas

    base_descontable_neto = (base_compras_inv + base_gastos_bienes
                             + base_gastos_servicios - base_nc_compras)
    iva_descontable_neto  = (iva_compras_inv + iva_gastos_bienes
                             + iva_gastos_servicios - iva_nc_compras)

    saldo = iva_generado_neto - iva_descontable_neto  # > 0: a pagar

    periodo = (f"{_fmt_date(fecha_inicio)} – {_fmt_date(fecha_fin)}"
               if fecha_inicio else "N/D")

    wb = Workbook()
    wb.remove(wb.active)
    ws = wb.create_sheet('RESUMEN')

    C_AZUL        = '1E3A5F'
    C_AZUL_MED    = '2E5FA3'
    C_VERDE       = '1A6B3C'
    C_ROJO        = '8B0000'
    C_AZUL_CLARO  = 'DCE6F1'
    C_VERDE_CLARO = 'E2EFDA'
    C_ROJO_CLARO  = 'FCE4D6'
    C_BLANCO      = 'FFFFFF'
    FMT_PESO      = '"$"#,##0.00'

    ws.column_dimensions['A'].width = 36
    ws.column_dimensions['B'].width = 14
    ws.column_dimensions['C'].width = 22
    ws.column_dimensions['D'].width = 22

    # ── Título ──
    ws.merge_cells('A1:D1')
    t = ws['A1']
    t.value = 'LIQUIDACIÓN DE IVA — PERÍODO FISCAL'
    t.font = Font(bold=True, color='FFFFFF', size=14)
    t.fill = PatternFill(fill_type='solid', fgColor=C_AZUL)
    t.alignment = Alignment(horizontal='center', vertical='center')
    ws.row_dimensions[1].height = 30

    ws.merge_cells('A2:D2')
    p = ws['A2']
    p.value = f'Período: {periodo}   |   NIT: {MI_NIT}'
    p.font = Font(italic=True, color='FFFFFF', size=10)
    p.fill = PatternFill(fill_type='solid', fgColor=C_AZUL_MED)
    p.alignment = Alignment(horizontal='center', vertical='center')
    ws.row_dimensions[2].height = 18

    # ── Helpers ──
    def section_header(row, title, color, ncols=4):
        ws.merge_cells(f'A{row}:{get_column_letter(ncols)}{row}')
        c = ws[f'A{row}']
        c.value = title
        c.font = Font(bold=True, color='FFFFFF', size=11)
        c.fill = PatternFill(fill_type='solid', fgColor=color)
        c.alignment = Alignment(horizontal='left', vertical='center', indent=1)
        c.border = _make_border()
        ws.row_dimensions[row].height = 22

    def col_headers(row):
        for col, txt in enumerate(['Concepto', 'Cuenta', 'Base Gravable', 'IVA (19%)'], 1):
            _apply_cell(ws, row, col, txt, bold=True, fill_hex='D9D9D9',
                        align='center', font_size=9)
        ws.row_dimensions[row].height = 16

    def data_row(row, concepto, cuenta, base, iva_val, fill=None,
                 color_val=None, bold=False, indent=1):
        label = ('   ' * indent) + concepto
        _apply_cell(ws, row, 1, label, bold=bold, fill_hex=fill, font_size=10)
        _apply_cell(ws, row, 2, cuenta, fill_hex=fill, align='center',
                    font_size=9, font_color='555555')
        _apply_cell(ws, row, 3, base, bold=bold, fill_hex=fill,
                    number_format=FMT_PESO, align='right',
                    font_color=color_val or '000000')
        _apply_cell(ws, row, 4, iva_val, bold=bold, fill_hex=fill,
                    number_format=FMT_PESO, align='right',
                    font_color=color_val or '000000')
        ws.row_dimensions[row].height = 17

    def subtotal_row(row, label, base, iva_val, fill, color_val='000000'):
        ws.merge_cells(f'A{row}:B{row}')
        c = ws[f'A{row}']
        c.value = label
        c.font = Font(bold=True, size=10)
        c.fill = PatternFill(fill_type='solid', fgColor=fill)
        c.alignment = Alignment(horizontal='right', vertical='center')
        c.border = _make_border()
        ws[f'B{row}'].border = _make_border()
        _apply_cell(ws, row, 3, base, bold=True, fill_hex=fill,
                    number_format=FMT_PESO, align='right', font_color=color_val)
        _apply_cell(ws, row, 4, iva_val, bold=True, fill_hex=fill,
                    number_format=FMT_PESO, align='right', font_color=color_val)
        ws.row_dimensions[row].height = 18

    r = 4

    # ── IVA GENERADO ──
    section_header(r, '▶  IVA GENERADO (Ventas)', C_AZUL_MED); r += 1
    col_headers(r); r += 1
    data_row(r, 'Ventas gravadas', '24080501', base_ventas, iva_ventas,
             fill=C_BLANCO); r += 1
    data_row(r, 'Menos: notas crédito ventas', '24080501',
             -base_nc_ventas, -iva_nc_ventas,
             fill=C_BLANCO,
             color_val='8B0000' if iva_nc_ventas > 0 else None); r += 1
    subtotal_row(r, 'IVA GENERADO NETO',
                 base_generado_neto, iva_generado_neto, C_AZUL_CLARO); r += 1

    r += 1

    # ── IVA DESCONTABLE ──
    section_header(r, '▶  IVA DESCONTABLE (Compras y Gastos)', C_VERDE); r += 1
    col_headers(r); r += 1
    data_row(r, 'Compras inventario — bienes (19%)', '24081001',
             base_compras_inv, iva_compras_inv, fill=C_BLANCO); r += 1
    data_row(r, 'Gastos — bienes (19%)', '24081001',
             base_gastos_bienes, iva_gastos_bienes, fill=C_BLANCO); r += 1
    data_row(r, 'Gastos — servicios (19%)', '24081501',
             base_gastos_servicios, iva_gastos_servicios, fill=C_BLANCO); r += 1
    data_row(r, 'Menos: notas crédito compras', '24081002',
             -base_nc_compras, -iva_nc_compras,
             fill=C_BLANCO,
             color_val='8B0000' if iva_nc_compras > 0 else None); r += 1
    subtotal_row(r, 'IVA DESCONTABLE NETO',
                 base_descontable_neto, iva_descontable_neto, C_VERDE_CLARO); r += 1

    r += 1

    # ── SALDO ──
    es_a_pagar   = saldo >= 0
    saldo_label  = 'IVA A PAGAR' if es_a_pagar else 'IVA A FAVOR (saldo próximo período)'
    saldo_fill   = C_ROJO_CLARO  if es_a_pagar else C_VERDE_CLARO
    saldo_color  = C_ROJO        if es_a_pagar else C_VERDE

    section_header(r, '▶  SALDO IVA', C_ROJO if es_a_pagar else C_VERDE); r += 1

    # Fila de saldo — solo columna IVA, base en blanco
    ws.merge_cells(f'A{r}:B{r}')
    c = ws[f'A{r}']
    c.value = saldo_label
    c.font = Font(bold=True, size=11, color=saldo_color)
    c.fill = PatternFill(fill_type='solid', fgColor=saldo_fill)
    c.alignment = Alignment(horizontal='right', vertical='center')
    c.border = _make_border()
    ws[f'B{r}'].border = _make_border()
    _apply_cell(ws, r, 3, None, fill_hex=saldo_fill)
    _apply_cell(ws, r, 4, abs(saldo), bold=True, fill_hex=saldo_fill,
                number_format=FMT_PESO, align='right', font_color=saldo_color,
                font_size=11)
    ws.row_dimensions[r].height = 22; r += 1

    r += 1
    ws.merge_cells(f'A{r}:D{r}')
    nota = ws[f'A{r}']
    nota.value = ('* Valores calculados desde la hoja REPORTE del archivo DIAN. '
                  'Verifique contra su declaración de IVA (Formulario 300).')
    nota.font = Font(italic=True, size=8, color='777777')
    nota.alignment = Alignment(horizontal='left', vertical='center')

    out = io.BytesIO()
    wb.save(out)
    out.seek(0)
    return out


def process_liquidacion_iva(input_stream):
    """Lee el REPORTE DIAN y genera el archivo de liquidación de IVA."""
    wb_src = openpyxl.load_workbook(input_stream, data_only=True)

    facturas_compras, facturas_gastos, notas_credito = read_reporte(wb_src)
    (base_ventas, iva_ventas,
     base_nc_ventas, iva_nc_ventas,
     fecha_ini, fecha_fin) = read_ventas_iva(wb_src)

    return generate_liquidacion_iva_file(
        facturas_compras, facturas_gastos, notas_credito,
        base_ventas, iva_ventas,
        base_nc_ventas, iva_nc_ventas,
        fecha_ini, fecha_fin,
    )

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

def _detect_format_name(wb_src):
    """Detecta el nombre de la hoja y el formato ('reporte' o 'nuevo')."""
    if 'REPORTE' in wb_src.sheetnames:
        return 'reporte', 'REPORTE'
    for name in wb_src.sheetnames:
        if name.startswith('Rp_'):
            return 'nuevo', name
    # Fallback: primera hoja
    name = wb_src.sheetnames[0]
    return 'nuevo', name


def _parse_rows(wb_src):
    """
    Lee todas las filas de la hoja DIAN en un solo paso con iter_rows.
    Retorna (fmt, mi_nit, filas) donde filas es lista de dicts normalizados.
    """
    from collections import Counter
    fmt, sheet_name = _detect_format_name(wb_src)
    ws = wb_src[sheet_name]

    EXCLUIDOS = {'222222222222', '0', '', 'None', 'none'}
    col_receptor = 8 if fmt == 'reporte' else 12

    conteo_nit = Counter()
    raw_rows   = []

    for row in ws.iter_rows(min_row=2, values_only=True):
        if fmt == 'reporte':
            if len(row) < 13:
                continue
            tipo         = row[0]
            folio        = row[2]
            fecha        = row[4]
            nit_emisor   = str(row[5] or '').strip()
            nit_receptor = str(row[7] or '').strip()
            no_gravado   = float(row[9]  or 0)
            gravado      = float(row[10] or 0)
            iva          = float(row[11] or 0)
            total        = float(row[12] or 0)
        else:
            if len(row) < 30:
                continue
            tipo         = row[0]
            folio        = row[2]
            fecha        = row[7]
            nit_emisor   = str(row[9]  or '').strip()
            nit_receptor = str(row[11] or '').strip()
            iva          = float(row[13] or 0)
            total        = float(row[29] or 0)
            gravado      = 0.0
            no_gravado   = 0.0

        if nit_receptor not in EXCLUIDOS:
            conteo_nit[nit_receptor] += 1

        raw_rows.append((tipo, folio, fecha, nit_emisor, nit_receptor,
                         no_gravado, gravado, iva, total))

    if not conteo_nit:
        raise ValueError("No se encontró ningún NIT receptor en el archivo.")

    mi_nit = conteo_nit.most_common(1)[0][0]

    # Segunda pasada sobre los datos ya en memoria (lista Python, muy rápida)
    filas = []
    for (tipo, folio, fecha, nit_emisor, nit_receptor,
         no_gravado, gravado, iva, total) in raw_rows:

        if nit_receptor != mi_nit:
            continue
        if folio is None:
            continue

        if fmt == 'nuevo':
            # Calcular base a partir de total e iva
            iva_r      = round(iva, 2)
            total_r    = round(total, 2)
            gravado    = round(total_r - iva_r, 2)
            no_gravado = 0.0

        filas.append({
            'tipo': str(tipo or '').lower(),
            'folio': folio, 'fecha': fecha,
            'nit_emisor': nit_emisor,
            'no_gravado': no_gravado, 'gravado': gravado,
            'iva': iva, 'total': total,
        })

    return fmt, mi_nit, filas


def read_reporte(wb_src):
    """Lee el reporte DIAN y clasifica en facturas_compras, facturas_gastos, notas_credito."""
    fmt, mi_nit, filas = _parse_rows(wb_src)

    facturas_compras = []
    facturas_gastos  = []
    notas_credito    = []

    for f in filas:
        tipo_str = f['tipo']
        doc = {
            'folio': f['folio'], 'fecha': f['fecha'], 'nit': f['nit_emisor'],
            'no_gravado': f['no_gravado'], 'gravado': f['gravado'],
            'iva': f['iva'], 'total': f['total'],
        }
        if 'nota de cr' in tipo_str:
            notas_credito.append(doc)
        elif f['nit_emisor'] == NIT_PROVEEDOR_INVENTARIO:
            facturas_compras.append(doc)
        else:
            facturas_gastos.append(doc)

    return facturas_compras, facturas_gastos, notas_credito


def _detect_format(wb_src):
    """Compatibilidad: retorna (fmt, ws) para funciones que aún lo usan."""
    fmt, sheet_name = _detect_format_name(wb_src)
    return fmt, wb_src[sheet_name]


def _detect_mi_nit(ws, fmt):
    """Compatibilidad: detecta NIT desde una hoja ya abierta."""
    from collections import Counter
    col_receptor = 7 if fmt == 'reporte' else 11  # índice 0-based en iter_rows
    EXCLUIDOS = {'222222222222', '0', '', 'None'}
    conteo = Counter()
    for row in ws.iter_rows(min_row=2, values_only=True):
        if len(row) > col_receptor:
            nit = str(row[col_receptor] or '').strip()
            if nit not in EXCLUIDOS:
                conteo[nit] += 1
    if not conteo:
        raise ValueError("No se encontró ningún NIT receptor en el archivo.")
    return conteo.most_common(1)[0][0]


# ========================================
# GENERACIÓN DE PLANOS
# ========================================

def convert_compras(facturas, wb_dst, consec_inicio):
    ws_dst = wb_dst.create_sheet('COMPRAS')
    _write_headers(ws_dst)

    row_out = 2

    # Pre-calcular para garantizar balance: deb_mercancia + deb_iva = cred_cxp
    fact_calc = []
    for f in facturas:
        cred_cxp     = round(f['total'], 2)
        deb_iva      = round(f['iva'], 2)
        deb_mercancia = round(cred_cxp - deb_iva, 2)   # total - iva = base exacta
        fact_calc.append({**f, 'deb_mercancia': deb_mercancia,
                          'deb_iva': deb_iva, 'cred_cxp': cred_cxp})

    # Bloque 1: mercancía gravada (débito)
    consec = consec_inicio
    for f in fact_calc:
        row = make_row(9, consec, f['fecha'], '14350101', f['nit'], None,
                       f"FC: {f['folio']}", f['deb_mercancia'], 0)
        for col, val in enumerate(row, 1):
            ws_dst.cell(row=row_out, column=col, value=val)
        row_out += 1
        consec += 1

    # Bloque 2: IVA descontable (débito)
    consec = consec_inicio
    for f in fact_calc:
        row = make_row(9, consec, f['fecha'], '24081001', f['nit'], 1,
                       f"FC: {f['folio']}", f['deb_iva'], 0)
        for col, val in enumerate(row, 1):
            ws_dst.cell(row=row_out, column=col, value=val)
        row_out += 1
        consec += 1

    # Bloque 3: CxP proveedor (crédito = suma exacta de débitos)
    consec = consec_inicio
    for f in fact_calc:
        row = make_row(9, consec, f['fecha'], '22050501', f['nit'], None,
                       f"FC: {f['folio']}", 0, f['cred_cxp'])
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

    # Pre-calcular para garantizar balance: deb_22050501 = cred_14350101 + cred_24081002
    notas_calc = []
    for n in notas:
        deb_cxp      = round(n['total'], 2)
        cred_iva     = round(n['iva'], 2)
        cred_mercancia = round(deb_cxp - cred_iva, 2)   # total - iva = base exacta
        notas_calc.append({**n, 'deb_cxp': deb_cxp,
                           'cred_mercancia': cred_mercancia, 'cred_iva': cred_iva})

    # Bloque 1: mercancía (crédito)
    consec = consec_inicio
    for n in notas_calc:
        row = make_row(10, consec, n['fecha'], '14350101', n['nit'], None,
                       f"NC: {n['folio']}", 0, n['cred_mercancia'])
        for col, val in enumerate(row, 1):
            ws_dst.cell(row=row_out, column=col, value=val)
        row_out += 1
        consec += 1

    # Bloque 2: IVA descontable NC (crédito)
    consec = consec_inicio
    for n in notas_calc:
        row = make_row(10, consec, n['fecha'], '24081002', n['nit'], 1,
                       f"NC: {n['folio']}", 0, n['cred_iva'])
        for col, val in enumerate(row, 1):
            ws_dst.cell(row=row_out, column=col, value=val)
        row_out += 1
        consec += 1

    # Bloque 3: CxP proveedor (débito = suma exacta de créditos)
    consec = consec_inicio
    for n in notas_calc:
        row = make_row(10, consec, n['fecha'], '22050501', n['nit'], None,
                       f"NC: {n['folio']}", n['deb_cxp'], 0)
        for col, val in enumerate(row, 1):
            ws_dst.cell(row=row_out, column=col, value=val)
        row_out += 1
        consec += 1

    return consec_inicio + len(notas)


def convert_gastos(gastos, wb_dst, consec_inicio):
    ws_dst = wb_dst.create_sheet('GASTOS')
    _write_headers(ws_dst)

    row_out = 2

    # Pre-calcular débitos redondeados para garantizar balance exacto
    gastos_calc = []
    for g in gastos:
        nit_str = str(g['nit'])
        cuenta, cuenta_iva, cod_imp = NIT_DETAIL_MAP.get(
            nit_str, (DEFAULT_CUENTA_GASTO, DEFAULT_IVA_CUENTA, DEFAULT_COD_IMP))
        deb_gasto = round(g['gravado'] + g['no_gravado'], 2)
        deb_iva   = round(g['iva'], 2)
        cred_cxp  = round(deb_gasto + deb_iva, 2)   # crédito = suma exacta de débitos
        gastos_calc.append({**g, 'cuenta': cuenta, 'cuenta_iva': cuenta_iva,
                            'cod_imp': cod_imp, 'deb_gasto': deb_gasto,
                            'deb_iva': deb_iva, 'cred_cxp': cred_cxp})

    # Bloque 1: cuenta de gasto (débito)
    consec = consec_inicio
    for g in gastos_calc:
        row = make_row(12, consec, g['fecha'], g['cuenta'], g['nit'], None,
                       f"G: {g['folio']}", g['deb_gasto'], 0)
        for col, val in enumerate(row, 1):
            ws_dst.cell(row=row_out, column=col, value=val)
        row_out += 1
        consec += 1

    # Bloque 2: IVA descontable (débito)
    consec = consec_inicio
    for g in gastos_calc:
        row = make_row(12, consec, g['fecha'], g['cuenta_iva'], g['nit'], g['cod_imp'],
                       f"G: {g['folio']}", g['deb_iva'], 0)
        for col, val in enumerate(row, 1):
            ws_dst.cell(row=row_out, column=col, value=val)
        row_out += 1
        consec += 1

    # Bloque 3: CxP proveedor (crédito = suma exacta de débitos)
    consec = consec_inicio
    for g in gastos_calc:
        row = make_row(12, consec, g['fecha'], '23359501', g['nit'], None,
                       f"G: {g['folio']}", 0, g['cred_cxp'])
        for col, val in enumerate(row, 1):
            ws_dst.cell(row=row_out, column=col, value=val)
        row_out += 1
        consec += 1

    return consec_inicio + len(gastos)


# ========================================
# LECTURA DE VENTAS
# ========================================

def read_ventas(wb_src):
    """
    Lee ventas y NC ventas emitidas por el negocio en un solo paso.
    Retorna (ventas, nc_ventas).
    """
    from collections import Counter
    fmt, sheet_name = _detect_format_name(wb_src)
    ws = wb_src[sheet_name]

    EXCLUIDOS = {'222222222222', '0', '', 'None'}
    col_receptor = 7 if fmt == 'reporte' else 11  # 0-based

    # Primer paso: detectar mi_nit y recolectar filas crudas
    conteo = Counter()
    raw = []
    for row in ws.iter_rows(min_row=2, values_only=True):
        if fmt == 'reporte':
            if len(row) < 13: continue
            nit_receptor = str(row[7] or '').strip()
        else:
            if len(row) < 30: continue
            nit_receptor = str(row[11] or '').strip()
        if nit_receptor not in EXCLUIDOS:
            conteo[nit_receptor] += 1
        raw.append(row)

    if not conteo:
        raise ValueError("No se encontró ningún NIT receptor.")
    mi_nit = conteo.most_common(1)[0][0]

    ventas    = []
    nc_ventas = []

    for row in raw:
        if fmt == 'reporte':
            tipo         = str(row[0] or '').lower()
            folio        = row[2]
            fecha        = row[4]
            nit_emisor   = str(row[5] or '').strip()
            nit_cliente  = str(row[7] or '').strip()
            nombre       = ''
            iva          = float(row[11] or 0)
            total        = float(row[12] or 0)
        else:
            tipo         = str(row[0] or '').lower()
            folio        = row[2]
            fecha        = row[7]
            nit_emisor   = str(row[9]  or '').strip()
            nit_cliente  = str(row[11] or '').strip()
            nombre       = str(row[12] or '').strip()
            iva          = float(row[13] or 0)
            total        = float(row[29] or 0)

        if nit_emisor != mi_nit or folio is None:
            continue

        iva_r   = round(iva, 2)
        total_r = round(total, 2)
        gravado = round(total_r - iva_r, 2)

        doc = {'folio': folio, 'fecha': fecha, 'nit': nit_cliente,
               'nombre': nombre, 'gravado': gravado, 'iva': iva_r, 'total': total_r}

        if 'nota de cr' in tipo:
            nc_ventas.append(doc)
        elif 'factura' in tipo:
            ventas.append(doc)

    return ventas, nc_ventas


def sheet_venta_nc_ventas(ventas, nc_ventas, wb_dst):
    """Crea la hoja VENTA Y NC VENTAS con detalle completo."""
    ws = wb_dst.create_sheet('VENTA Y NC VENTAS')

    # Encabezados
    headers = ['Tipo', 'Folio', 'Fecha', 'NIT/Cédula Cliente',
               'Nombre Cliente', 'Base Gravable', 'IVA', 'Total']
    for col, h in enumerate(headers, 1):
        ws.cell(row=1, column=col, value=h)

    row_out = 2
    for v in ventas:
        ws.cell(row_out, 1, 'VENTA')
        ws.cell(row_out, 2, v['folio'])
        ws.cell(row_out, 3, v['fecha'])
        ws.cell(row_out, 4, v['nit'])
        ws.cell(row_out, 5, v['nombre'])
        ws.cell(row_out, 6, v['gravado'])
        ws.cell(row_out, 7, v['iva'])
        ws.cell(row_out, 8, v['total'])
        row_out += 1

    for n in nc_ventas:
        ws.cell(row_out, 1, 'NC VENTA')
        ws.cell(row_out, 2, n['folio'])
        ws.cell(row_out, 3, n['fecha'])
        ws.cell(row_out, 4, n['nit'])
        ws.cell(row_out, 5, n['nombre'])
        ws.cell(row_out, 6, -n['gravado'])
        ws.cell(row_out, 7, -n['iva'])
        ws.cell(row_out, 8, -n['total'])
        row_out += 1


def convert_ventas(ventas, nc_ventas, wb_dst, consec_inicio):
    """
    Genera la hoja VENTAS con el plano Siigo consolidado por NIT cliente.
    Cada NIT cliente → una fila por bloque contable (CxC, Ingresos, IVA).
    """
    from collections import defaultdict

    ws_dst = wb_dst.create_sheet('VENTAS')
    _write_headers(ws_dst)
    row_out = 2

    # Consolidar ventas por NIT cliente
    consolidado = defaultdict(lambda: {'gravado': 0.0, 'iva': 0.0, 'total': 0.0, 'fecha': None})
    for v in ventas:
        k = str(v['nit'])
        consolidado[k]['gravado'] += v['gravado']
        consolidado[k]['iva']     += v['iva']
        consolidado[k]['total']   += v['total']
        if consolidado[k]['fecha'] is None:
            consolidado[k]['fecha'] = v['fecha']

    # Restar NC ventas por NIT cliente
    for n in nc_ventas:
        k = str(n['nit'])
        consolidado[k]['gravado'] -= n['gravado']
        consolidado[k]['iva']     -= n['iva']
        consolidado[k]['total']   -= n['total']

    # Filtrar NITs con total > 0
    clientes = [(nit, d) for nit, d in consolidado.items() if abs(d['total']) > 0.01]

    # Pre-calcular créditos para garantizar balance exacto por consecutivo
    # débito CxC = total; crédito ingreso = total - iva; crédito IVA = iva
    clientes_calc = []
    for nit, d in clientes:
        cred_iva     = round(d['iva'], 2)
        cred_ingreso = round(d['total'], 2) - cred_iva   # garantiza débito = crédito1 + crédito2
        clientes_calc.append((nit, d, cred_ingreso, cred_iva))

    consec = consec_inicio

    # Bloque 1: CxC clientes (débito)
    for nit, d, _, _ in clientes_calc:
        row = make_row(1, consec, d['fecha'], '13050501', nit, None,
                       'VENTA CONSOLIDADA', round(d['total'], 2), 0)
        for col, val in enumerate(row, 1):
            ws_dst.cell(row=row_out, column=col, value=val)
        row_out += 1
        consec += 1

    # Bloque 2: Ingresos por ventas (crédito = total - iva)
    consec = consec_inicio
    for nit, d, cred_ingreso, _ in clientes_calc:
        row = make_row(1, consec, d['fecha'], '41009501', nit, None,
                       'VENTA CONSOLIDADA', 0, cred_ingreso)
        for col, val in enumerate(row, 1):
            ws_dst.cell(row=row_out, column=col, value=val)
        row_out += 1
        consec += 1

    # Bloque 3: IVA generado (crédito)
    consec = consec_inicio
    for nit, d, _, cred_iva in clientes_calc:
        row = make_row(1, consec, d['fecha'], '24080501', nit, 1,
                       'VENTA CONSOLIDADA', 0, cred_iva)
        for col, val in enumerate(row, 1):
            ws_dst.cell(row=row_out, column=col, value=val)
        row_out += 1
        consec += 1

    return consec_inicio + len(clientes)


# ========================================
# PUNTO DE ENTRADA PRINCIPAL — PLANOS SIIGO
# ========================================

def _leer_todo(wb_src):
    """
    Lee el archivo DIAN en UN SOLO PASO y devuelve todas las listas necesarias.
    Evita múltiples iteraciones sobre el mismo archivo grande.
    """
    from collections import Counter
    fmt, sheet_name = _detect_format_name(wb_src)
    ws = wb_src[sheet_name]

    EXCLUIDOS = {'222222222222', '0', '', 'None', 'none'}

    # Primera pasada: detectar mi_nit y acumular filas crudas en memoria
    conteo = Counter()
    raw = []
    for row in ws.iter_rows(min_row=2, values_only=True):
        if fmt == 'reporte':
            if len(row) < 13: continue
            nit_receptor = str(row[7] or '').strip()
        else:
            if len(row) < 30: continue
            nit_receptor = str(row[11] or '').strip()
        if nit_receptor not in EXCLUIDOS:
            conteo[nit_receptor] += 1
        raw.append(row)

    if not conteo:
        raise ValueError("No se encontró ningún NIT receptor en el archivo.")
    mi_nit = conteo.most_common(1)[0][0]

    # Segunda pasada sobre lista Python (muy rápida, ya en memoria)
    facturas_compras = []; facturas_gastos = []; notas_credito = []
    ventas = []; nc_ventas = []
    base_ventas = 0.0; iva_ventas = 0.0
    base_nc_ventas = 0.0; iva_nc_ventas = 0.0
    fechas_venta = []

    for row in raw:
        if fmt == 'reporte':
            tipo         = str(row[0] or '').lower()
            folio        = row[2]
            fecha        = row[4]
            nit_emisor   = str(row[5] or '').strip()
            nit_receptor = str(row[7] or '').strip()
            no_gravado   = float(row[9]  or 0)
            gravado_raw  = float(row[10] or 0)
            iva          = float(row[11] or 0)
            total        = float(row[12] or 0)
            nit_cliente  = nit_receptor
            nombre       = ''
        else:
            tipo         = str(row[0] or '').lower()
            folio        = row[2]
            fecha        = row[7]
            nit_emisor   = str(row[9]  or '').strip()
            nit_receptor = str(row[11] or '').strip()
            nombre       = str(row[12] or '').strip()
            iva          = float(row[13] or 0)
            total        = float(row[29] or 0)
            no_gravado   = 0.0
            gravado_raw  = 0.0
            nit_cliente  = nit_receptor

        iva_r   = round(iva,   2)
        total_r = round(total, 2)
        base_r  = round(total_r - iva_r, 2)   # base exacta para balancear

        es_nc      = 'nota de cr' in tipo
        es_factura = 'factura'    in tipo

        # ── Compras / gastos (recibidos por mi_nit) ──
        if nit_receptor == mi_nit and folio is not None:
            if fmt == 'reporte':
                grav = gravado_raw; nograv = no_gravado
            else:
                grav = base_r; nograv = 0.0

            doc = {'folio': folio, 'fecha': fecha, 'nit': nit_emisor,
                   'no_gravado': nograv, 'gravado': grav, 'iva': iva_r, 'total': total_r}

            if es_nc:
                notas_credito.append(doc)
            elif nit_emisor == NIT_PROVEEDOR_INVENTARIO:
                facturas_compras.append(doc)
            else:
                facturas_gastos.append(doc)

        # ── Ventas (emitidas por mi_nit) ──
        if nit_emisor == mi_nit and folio is not None:
            vdoc = {'folio': folio, 'fecha': fecha, 'nit': nit_cliente,
                    'nombre': nombre, 'gravado': base_r, 'iva': iva_r, 'total': total_r}
            if es_nc:
                nc_ventas.append(vdoc)
                base_nc_ventas += base_r; iva_nc_ventas += iva_r
                if fecha: fechas_venta.append(fecha)
            elif es_factura:
                ventas.append(vdoc)
                base_ventas += base_r; iva_ventas += iva_r
                if fecha: fechas_venta.append(fecha)

    fecha_ini = min(fechas_venta) if fechas_venta else None
    fecha_fin = max(fechas_venta) if fechas_venta else None

    return (mi_nit,
            facturas_compras, facturas_gastos, notas_credito,
            ventas, nc_ventas,
            base_ventas, iva_ventas, base_nc_ventas, iva_nc_ventas,
            fecha_ini, fecha_fin)


def process_file(input_stream, consec_compras=371, consec_nc=271, consec_gastos=798, consec_ventas=1):
    """Lee el archivo DIAN y genera los planos Siigo (compras, NC, gastos y ventas)."""
    wb_src = openpyxl.load_workbook(input_stream, data_only=True, read_only=True)

    (mi_nit, facturas_compras, facturas_gastos, notas_credito,
     ventas, nc_ventas, _, _, _, _, _, _) = _leer_todo(wb_src)

    wb_dst = Workbook()
    if wb_dst.active:
        wb_dst.remove(wb_dst.active)

    convert_compras(facturas_compras, wb_dst, consec_compras)
    convert_nc_compras(notas_credito, wb_dst, consec_nc)
    convert_gastos(facturas_gastos, wb_dst, consec_gastos)
    sheet_venta_nc_ventas(ventas, nc_ventas, wb_dst)
    convert_ventas(ventas, nc_ventas, wb_dst, consec_ventas)

    output_stream = io.BytesIO()
    wb_dst.save(output_stream)
    output_stream.seek(0)
    return output_stream


# ========================================
# LIQUIDACIÓN DE IVA — LECTURA VENTAS
# ========================================

def read_ventas_iva(wb_src):
    """
    Lee ventas y NC ventas emitidas por el negocio en un solo paso.
    Retorna (base_ventas, iva_ventas, base_nc_ventas, iva_nc_ventas, fecha_inicio, fecha_fin).
    """
    # Reutiliza _parse_rows que ya hizo el trabajo pesado
    fmt, mi_nit, filas = _parse_rows(wb_src)

    base_ventas    = 0.0;  iva_ventas     = 0.0
    base_nc_ventas = 0.0;  iva_nc_ventas  = 0.0
    fechas = []

    for f in filas:
        # filas contiene documentos recibidos por mi_nit (compras/gastos)
        # Para ventas necesitamos documentos EMITIDOS por mi_nit
        pass

    # Segunda lectura enfocada en emisor = mi_nit
    fmt2, sheet_name = _detect_format_name(wb_src)
    ws2 = wb_src[sheet_name]
    for row in ws2.iter_rows(min_row=2, values_only=True):
        if fmt2 == 'reporte':
            if len(row) < 13: continue
            tipo       = str(row[0] or '').lower()
            nit_emisor = str(row[5] or '').strip()
            fecha      = row[4]
            iva        = float(row[11] or 0)
            total      = float(row[12] or 0)
        else:
            if len(row) < 30: continue
            tipo       = str(row[0] or '').lower()
            nit_emisor = str(row[9] or '').strip()
            fecha      = row[7]
            iva        = float(row[13] or 0)
            total      = float(row[29] or 0)

        if nit_emisor != mi_nit:
            continue
        gravado = round(total - iva, 2)
        if fecha:
            fechas.append(fecha)
        if 'nota de cr' in tipo:
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
                                  fecha_inicio, fecha_fin, mi_nit=''):
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
    p.value = f'Período: {periodo}   |   NIT: {mi_nit}'
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
    wb_src = openpyxl.load_workbook(input_stream, data_only=True, read_only=True)

    (mi_nit, facturas_compras, facturas_gastos, notas_credito,
     _, _, base_ventas, iva_ventas, base_nc_ventas, iva_nc_ventas,
     fecha_ini, fecha_fin) = _leer_todo(wb_src)

    return generate_liquidacion_iva_file(
        facturas_compras, facturas_gastos, notas_credito,
        base_ventas, iva_ventas,
        base_nc_ventas, iva_nc_ventas,
        fecha_ini, fecha_fin,
        mi_nit=mi_nit,
    )

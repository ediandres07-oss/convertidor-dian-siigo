"""
Generador de Planos para Contai-Ilimitada desde el reporte DIAN.

Toma el mismo archivo DIAN que usa el convertidor Siigo y genera el plano de
ventas, compras y notas crédito de compras en formato Contai-Ilimitada
(contabilidad de partida doble por documento).

Nota: el reporte DIAN solo trae el IVA total y el total por documento, por lo
que todo se contabiliza al 19% (no se separa 19%/5%) y no se incluyen
retenciones en la fuente. Si un documento no trae IVA, se omite la línea de IVA.

Gastos/servicios NO están incluidos: a diferencia de compras (que van a una
única cuenta de inventario), cada proveedor de gastos usa una cuenta contable
distinta (arriendo, honorarios, servicios públicos, etc.) y ese mapeo
NIT→cuenta específico de Contai aún no está definido.
"""

import io
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

from converter import _leer_todo, _fecha


# ========================================
# Cuentas contables Contai (INVERPLAS)
# ========================================
CTA_INGRESO_19 = '412054'      # Ingresos gravados 19%
CTA_IVA_19     = '24080104'    # IVA generado 19%
CTA_CLIENTES   = '130505'      # Clientes (CxC)
CTA_DEV_VENTAS = '417502'      # Devoluciones en ventas
CTA_IVA_DEV    = '24080207'    # IVA en devoluciones 19%

CTA_COMPRAS_19    = '143504'   # Compras gravadas 19% (inventario)
CTA_IVA_DESCONTAB = '240802'   # IVA descontable 19%
CTA_PROVEEDORES   = '220505'   # Proveedores nacionales (CxP)
CTA_DEV_COMPRAS   = '143521'   # Devolución en compras gravadas 19%

COMP_VENTA   = 4               # Comprobante de venta
COMP_DEVOL   = 16              # Comprobante de devolución (NC ventas)
COMP_COMPRA  = 1               # Comprobante de compra
COMP_NC_COMPRA = 2             # Comprobante de NC de compra

TIPO_DEBITO  = 1
TIPO_CREDITO = 2

HEADERS_CONTAI = [
    'Cuenta', 'Comprobante', 'Fecha(mm/dd/yyyy)', 'Comprobante', 'Documento Ref.',
    'Nit', 'Detalle', 'Tipo', 'VALORES', 'BASE', 'Centro de Costo',
    'Trans. Ext', 'Plazo'
]

_HEADER_FILL = PatternFill(fill_type='solid', fgColor='1a3a5c')
_HEADER_FONT = Font(bold=True, color='FFFFFF', name='Calibri', size=10)
_THIN_BORDER = Border(
    left=Side(style='thin', color='BFCCD8'),
    right=Side(style='thin', color='BFCCD8'),
    top=Side(style='thin', color='BFCCD8'),
    bottom=Side(style='thin', color='BFCCD8')
)


def _fmt_fecha(val):
    """Devuelve la fecha en formato dd-mm-yyyy (como en el plano Contai)."""
    f = _fecha(val)
    try:
        return f.strftime('%d-%m-%Y')
    except AttributeError:
        return str(val) if val is not None else ''


def _fila_contai(cuenta, comp, fecha, folio, nit, detalle, tipo, valores, base=None):
    """Construye una fila del plano Contai (13 columnas)."""
    return [
        cuenta, comp, fecha, folio, folio,
        str(nit) if nit else None, detalle, tipo, round(valores, 2),
        round(base, 2) if base is not None else None,
        None, None, None
    ]


def _escribir_headers(ws):
    for col, header in enumerate(HEADERS_CONTAI, 1):
        cell = ws.cell(row=1, column=col, value=header)
        cell.fill = _HEADER_FILL
        cell.font = _HEADER_FONT
        cell.alignment = Alignment(horizontal='center', vertical='center')
        cell.border = _THIN_BORDER
    ws.row_dimensions[1].height = 20


def _escribir_fila(ws, row_idx, fila):
    for col, val in enumerate(fila, 1):
        cell = ws.cell(row=row_idx, column=col, value=val)
        cell.border = _THIN_BORDER
        # Formato numérico para VALORES (col 9) y BASE (col 10)
        if col in (9, 10) and isinstance(val, (int, float)):
            cell.number_format = '#,##0.00'


def _escribir_ventas(ws, row_idx, ventas, nc_ventas):
    """Escribe las líneas de facturas de venta y sus notas crédito."""
    # --- Facturas de venta (Comprobante 4) ---
    for v in ventas:
        if abs(v['total']) < 0.01:
            continue
        fecha  = _fmt_fecha(v['fecha'])
        folio  = v['folio']
        nit    = v['nit']
        base   = v['gravado']
        iva    = v['iva']
        total  = v['total']

        # Ingreso gravado 19% (crédito)
        _escribir_fila(ws, row_idx, _fila_contai(
            CTA_INGRESO_19, COMP_VENTA, fecha, folio, nit, 'VENTAS',
            TIPO_CREDITO, base))
        row_idx += 1

        # IVA generado 19% (crédito) — solo si hay IVA
        if abs(iva) > 0.01:
            _escribir_fila(ws, row_idx, _fila_contai(
                CTA_IVA_19, COMP_VENTA, fecha, folio, nit, 'VENTAS',
                TIPO_CREDITO, iva, base=base))
            row_idx += 1

        # Clientes / CxC (débito) por el total
        _escribir_fila(ws, row_idx, _fila_contai(
            CTA_CLIENTES, COMP_VENTA, fecha, folio, nit, 'VENTAS',
            TIPO_DEBITO, total))
        row_idx += 1

    # --- Notas crédito / devoluciones (Comprobante 16) ---
    for nc in nc_ventas:
        if abs(nc['total']) < 0.01:
            continue
        fecha  = _fmt_fecha(nc['fecha'])
        folio  = nc['folio']
        nit    = nc['nit']
        base   = nc['gravado']
        iva    = nc['iva']
        total  = nc['total']

        # Devolución en ventas (débito)
        _escribir_fila(ws, row_idx, _fila_contai(
            CTA_DEV_VENTAS, COMP_DEVOL, fecha, folio, nit, 'DEV. VENTAS',
            TIPO_DEBITO, base))
        row_idx += 1

        # IVA en devoluciones (débito) — solo si hay IVA
        if abs(iva) > 0.01:
            _escribir_fila(ws, row_idx, _fila_contai(
                CTA_IVA_DEV, COMP_DEVOL, fecha, folio, nit, 'DEV. VENTAS',
                TIPO_DEBITO, iva, base=base))
            row_idx += 1

        # Clientes / CxC (crédito) por el total
        _escribir_fila(ws, row_idx, _fila_contai(
            CTA_CLIENTES, COMP_DEVOL, fecha, folio, nit, 'DEV. VENTAS',
            TIPO_CREDITO, total))
        row_idx += 1

    return row_idx


def _escribir_compras(ws, row_idx, compras):
    """Escribe las líneas de facturas de compra (mercancía/inventario)."""
    for c in compras:
        if abs(c['total']) < 0.01:
            continue
        fecha  = _fmt_fecha(c['fecha'])
        folio  = c['folio']
        nit    = c['nit']
        base   = c['gravado']
        iva    = c['iva']
        total  = c['total']

        # Compras gravadas 19% (débito)
        _escribir_fila(ws, row_idx, _fila_contai(
            CTA_COMPRAS_19, COMP_COMPRA, fecha, folio, nit, 'COMPRAS',
            TIPO_DEBITO, base))
        row_idx += 1

        # IVA descontable 19% (débito) — solo si hay IVA
        if abs(iva) > 0.01:
            _escribir_fila(ws, row_idx, _fila_contai(
                CTA_IVA_DESCONTAB, COMP_COMPRA, fecha, folio, nit, 'COMPRAS',
                TIPO_DEBITO, iva, base=base))
            row_idx += 1

        # Proveedores / CxP (crédito) por el total
        _escribir_fila(ws, row_idx, _fila_contai(
            CTA_PROVEEDORES, COMP_COMPRA, fecha, folio, nit, 'COMPRAS',
            TIPO_CREDITO, total))
        row_idx += 1

    return row_idx


def _escribir_nc_compras(ws, row_idx, nc_compras):
    """Escribe las líneas de notas crédito de compra (devoluciones a proveedor)."""
    for nc in nc_compras:
        if abs(nc['total']) < 0.01:
            continue
        fecha  = _fmt_fecha(nc['fecha'])
        folio  = nc['folio']
        nit    = nc['nit']
        base   = nc['gravado']
        iva    = nc['iva']
        total  = nc['total']

        # Devolución en compras (crédito)
        _escribir_fila(ws, row_idx, _fila_contai(
            CTA_DEV_COMPRAS, COMP_NC_COMPRA, fecha, folio, nit, 'DEV. COMPRAS',
            TIPO_CREDITO, base))
        row_idx += 1

        # IVA descontable en devolución (crédito) — solo si hay IVA
        if abs(iva) > 0.01:
            _escribir_fila(ws, row_idx, _fila_contai(
                CTA_IVA_DESCONTAB, COMP_NC_COMPRA, fecha, folio, nit, 'DEV. COMPRAS',
                TIPO_CREDITO, iva, base=base))
            row_idx += 1

        # Proveedores / CxP (débito) por el total
        _escribir_fila(ws, row_idx, _fila_contai(
            CTA_PROVEEDORES, COMP_NC_COMPRA, fecha, folio, nit, 'DEV. COMPRAS',
            TIPO_DEBITO, total))
        row_idx += 1

    return row_idx


def generar_plano_contai(input_stream, incluir=('ventas', 'compras', 'nc_compras')):
    """
    Lee el reporte DIAN y genera el plano contable completo en formato Contai
    (ventas, compras y notas crédito de compras, según lo solicitado en
    'incluir'). Retorna un BytesIO con el archivo Excel listo para descargar.
    """
    wb_src = openpyxl.load_workbook(input_stream, data_only=True, read_only=True)
    (_, facturas_compras, _, notas_credito,
     ventas, nc_ventas, _, _, _, _, _, _) = _leer_todo(wb_src)

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = 'ARCHIVO PLANO'
    _escribir_headers(ws)

    row_idx = 2
    if 'ventas' in incluir:
        row_idx = _escribir_ventas(ws, row_idx, ventas, nc_ventas)
    if 'compras' in incluir:
        row_idx = _escribir_compras(ws, row_idx, facturas_compras)
    if 'nc_compras' in incluir:
        row_idx = _escribir_nc_compras(ws, row_idx, notas_credito)

    # Ajustar ancho de columnas
    anchos = [10, 12, 16, 12, 14, 14, 14, 6, 14, 14, 14, 12, 8]
    for col_idx, ancho in enumerate(anchos, 1):
        ws.column_dimensions[openpyxl.utils.get_column_letter(col_idx)].width = ancho

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    return output


def generar_plano_ventas_contai(input_stream):
    """Compatibilidad: genera solo el plano de ventas en formato Contai."""
    return generar_plano_contai(input_stream, incluir=('ventas',))

"""
Generador de Planos para Contai-Ilimitada desde el reporte DIAN.

Toma el mismo archivo DIAN que usa el convertidor Siigo y genera el plano de
ventas, compras y notas crédito de compras en formato Contai-Ilimitada
(contabilidad de partida doble por documento).

Nota: el reporte DIAN solo trae el IVA total y el total por documento, por lo
que todo se contabiliza al 19% (no se separa 19%/5%) y no se incluyen
retenciones en la fuente. Si un documento no trae IVA, se omite la línea de IVA.

Gastos/servicios: cada proveedor usa una cuenta contable distinta (arriendo,
honorarios, servicios públicos, etc.), así que se resuelven con el mapeo
NIT_CUENTA_GASTO extraído del balance de prueba de INVERPLAS. Los NITs que
en el balance aparecen en más de una cuenta (compras mixtas, ej. HOMCENTER)
o que no están en el mapeo van a la cuenta genérica CTA_GASTO_DEFAULT
('Diversos') para reclasificar manualmente.
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

CTA_GASTO_DEFAULT = '5195'     # Diversos: destino de NITs ambiguos o no mapeados

# NIT (solo dígitos) -> cuenta de gasto, extraído del balance de prueba
# INVERPLAS (mayo 2026). Excluye NITs de nómina y NITs que en el balance
# aparecen en más de una cuenta de gasto (esos van a CTA_GASTO_DEFAULT).
NIT_CUENTA_GASTO = {
    '10061835363': '513550',   # JHON MARIO SALAZAR SANCHEZ
    '10064074258': '519560',   # LEZLY JULIANA DEL PILAR DIAZ
    '10396875120': '519560',   # NATALY PRADA RAMIREZ
    '10403804926': '519560',   # KATERINE JOHANA LOPEZ SANCHEZ
    '10454279145': '515505',   # SALOME MOSALVE POLO
    '10774432324': '513550',   # JHON GABRIEL RICO RIOS
    '10774661341': '519560',   # JUAN CAMILO VELASQUEZ OSPINA
    '10774676685': '513550',   # DANIEL SEBASTIAN LONDOÑO AGUDE
    '10882780234': '513550',   # JULIAN LOPEZ
    '10883397338': '519560',   # SEBASTIAN DUQUE MARIN
    '109514998': '515505',     # PABLO ANDRES ARANGO ZAPATA
    '11284337610': '519560',   # CRISTIA CAMILO GRISALES DUQUE
    '11521992011': '519530',   # JULIAN DAVID DIOSSA GALLEGO
    '153822927': '515505',     # MIGUEL ANTONIO ALZATE LOPEZ
    '154061773': '513550',     # CARLOS ENRIQUE HIGUITA
    '155390508': '515505',     # DIEGO LEON VERGARA BUSTAMANTE
    '162181907': '519535',     # HUMBERTO DE JESUS AGUDELO BETA
    '165452835': '519560',     # LUIS ANGEL MARTINEZ CRUZ
    '168366321': '513550',     # JUAN FERNANDO CARDONA MARTINEZ
    '218946896': '515505',     # MARIA ROCIO MONTES DAVILA
    '222099454': '515505',     # LUZ MARLENY CARMONA VILLA
    '284874202': '515505',     # ELISA USECHE DE CASTELLANOS
    '302304030': '530535',     # LUISA FERNANDA LARGO OROZCO
    '325604151': '530535',     # SARITH YASMITH CHANCI CARMONA
    '35101480': '530535',      # GUILLERMO ALONSO GARCIA JARAMI
    '391591108': '519560',     # OBEIDA MARIA CASTRO TRIANA
    '392728337': '519560',     # NANCY DEL CARMEN MERCADO
    '429416482': '519560',     # RESTAURANTE PARRILLA Y SABOR
    '431170935': '513515',     # CLAUDIA MARCELA GONZALEZ YEPES
    '43345959': '530535',      # OSCAR AUGUSTO MEJIA GALVIS
    '43369026': '530535',      # JOSE LIBARDO HERNANDEZ
    '436041133': '519560',     # BIBIANA MARIA DUQUE RICO
    '700867517': '515505',     # GERARDO DE JESUS ADARVE ROBAYO
    '701043354': '519530',     # JOSE LIBARDO ALVAREZ RESTREPO
    '702568017': '519560',     # JOSE ALBERTO TOBON MAZO
    '704223863': '513550',     # YOINER ALEXANDER OLAYA SERNA
    '704313822': '513550',     # GERMAN ARTURO LONDOÑO SARRAZOL
    '705634241': '519560',     # LUIS ALVARO GUIZADO ZAPATA
    '707806665': '519560',     # JOSE ISRAEL CARDONA VARGAS
    '711822130': '530535',     # ARTURO DE JESUS VALENCIA
    '711862382': '515505',     # JUAN BERNARDO GOMEZ ANGEL
    '712709823': '513515',     # RUBIEL HERNANDO VELEZ MOLINA
    '713642426': '513550',     # SERGIO OROZCO GUARIN
    '713642988': '513550',     # LUIS FERNANDO VASQUEZ BALLESTE
    '715261796': '512010',     # DIEGO CASTRILLON MARIN
    '717250333': '513520',     # WILLMAR DE JESUS GAVIRIA GALLE
    '8001443551': '513505',    # TELESENTINEL DE ANTIOQUIA LTDA
    '8001475678': '515520',    # COOTRANSUROCCIDENTE
    '8001539937': '513535',    # COMCEL
    '8002248088': '530515',    # PORVENIR
    '8002279406': '530515',    # COLFONDOS
    '8002297390': '530515',    # PROTECCION
    '80144605': '513550',      # URIEL ORLEY GOMEZ ATEHORTUA
    '801853056': '519560',     # FRANCISCO ALEJANDRO DIAZ VELEZ
    '80336071': '530535',      # SERGIO PATIÑO OSORIO
    '8050074044': '514515',    # ICOMALLAS S A
    '80754471': '513550',      # DIEGO LEON MONTOYA ZAPATA
    '8110097888': '519535',    # DISTRACOM MARIA AUXILIADORA
    '8110124275': '515015',    # FERRETERIA LOS FIERROS
    '8110151582': '519535',    # SHIRLEY ZULUAGA SALAZAR Y CIA
    '8110231848': '514540',    # ASESORIA JURIDICA Y TECNICA DE
    '82035969': '519560',      # GABRIEL JAIME LLANO ALVAREZ
    '823617684': '515505',     # LEDEZMA COPETE RICARDO
    '8300450345': '513550',    # PISOTRANS S.A.S.
    '83381633': '513550',      # LIS ALEXANDER ZAPATA SEPULVEDA
    '83452275': '519535',      # JUAN GUILLERMO GARCES
    '84168137': '513550',      # FABIO TORRES TABARES
    '8600325507': '515015',    # ALFAGRES S.A.
    '860040588': '519560',     # JHON FREDY SUAREZ GIRALDO
    '8605192353': '513005',    # TALLERES AUTORIZADOS S.A
    '882486130': '513550',     # HELMER GIRALDO MEDINA
    '8902009287': '515520',    # COOPERATIVA SANTANDERIANA DETR
    '8903029887': '519535',    # DIEGO LOPEZ S.A.S
    '8909006089': '519535',    # ALMACENES EXITO S.A.
    '8909006523': '515015',    # INVENSA S.A.
    '8909008419': '530515',    # COMFAMA
    '8909014919': '515520',    # FLOTA NORDESTE S.C.A.
    '8909027601': '515520',    # SOTRAAURABA S.A.
    '8909028726': '515520',    # TRANSPORTES GOMEZ HERNANDEZ SA
    '8909034079': '513005',    # CIA SURAMERICANA DE SEGUROS S.
    '8909050803': '514010',    # CAMARA DE COMERCIO DE MEDELLIN
    '8909052111': '511505',    # MUNICIPIO DE MEDELLIN
    '8909056802': '515520',    # COONORTE
    '8909107151': '515015',    # FEROSVEL S.A.S.
    '8909130591': '513550',    # EXPRESO CISNEROS NUS LTDA
    '8909139871': '519560',    # MADRID HERMANOS S.A.S.
    '8909146058': '515520',    # SOTRANSODA
    '8914085845': '519560',    # FRISBY S.A.
    '8914086352': '530535',    # INDUSTRIAS ZENNER S.A.
    '8999991434': '515515',    # SERVICIO AEREO A TERRITORIOS N
    '9000889157': '515515',    # EMPRESA AEREA DE SERVICIOS Y F
    '9000923859': '513545',    # UNE EPM TELECOMUNICACIONES S.A
    '9000988491': '530535',    # COMERCIALIZADORA LA PALMERA S,
    '9001316321': '530535',    # PROVEEDORA MARIN SAS
    '9002078548': '519535',    # HL COMBUSTIBLES SAS
    '9003197533': '514015',    # PRICESMART COLOMBIA SAS
    '9003925544': '515015',    # CROSSWAY S.A.S
    '9004036701': '519560',    # INVERSISA S.A.S.
    '9004251617': '530535',    # AGROCCIDENTE SOPETRAN
    '9004388982': '530535',    # SUPERMERCADO SOL STORES S.A.S.
    '9005241786': '530535',    # LA ESTACION DEL AGRO S.A.S.
    '9005984448': '530535',    # ELECTRICOS SOLLA LA 49 SAS
    '9006260951': '515015',    # MATERIALES Y FERRETERIA LA CR
    '9009475326': '513520',    # RIBISOFT S.A.S.
    '9010321471': '514540',    # LLANTAS Y RINES MOGOLLA SAS
    '9010387381': '512510',    # CONJUNTO RESIDENCIAL MALAWI PH
    '9010734179': '530535',    # CUERDAS EL TITAN SAS
    '9011773479': '519560',    # C.M.S. INVERSORES S.A.S.
    '9013025441': '530535',    # AGROINSUMOS PA MI TIERRA ZOMAC
    '9013043356': '519535',    # JUANBE SANDIEGO SAS
    '9013238191': '530535',    # INVERSIONES VELEZ VILLA ZOMAC
    '9017251664': '530535',    # INVERSIONES MONSALVE VELEZ S.A
    '9019296916': '530535',    # XCAVATECH S.A.S.
    '9019750747': '530535',    # FERRETERIA LA PLAZUELA GH S.A.
    '984752674': '530535',     # AMAURY MIGUEL ZAYAS CORDERO
    '986273913': '514540',     # CARLOS BALBINO JARAMILOALVAREZ
    '986362486': '511030',     # CESAR AUGUSTO RESTREPO CIRO
    '986371737': '513550',     # JUAN FERNANDO HIGUITA CARTAGEN
    '986437368': '513550',     # JOHN ALEXANDER MEJIA VELASQUEZ
}

COMP_VENTA   = 4               # Comprobante de venta
COMP_DEVOL   = 16              # Comprobante de devolución (NC ventas)
COMP_COMPRA  = 1               # Comprobante de compra
COMP_NC_COMPRA = 2             # Comprobante de NC de compra
COMP_GASTO   = 12              # Comprobante de gasto/servicio

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


def _escribir_gastos(ws, row_idx, gastos):
    """Escribe las líneas de facturas de gastos/servicios, usando NIT_CUENTA_GASTO
    para asignar la cuenta de gasto correcta por proveedor. Los NITs sin mapeo
    único van a CTA_GASTO_DEFAULT ('Diversos') para reclasificar manualmente."""
    for g in gastos:
        if abs(g['total']) < 0.01:
            continue
        fecha  = _fmt_fecha(g['fecha'])
        folio  = g['folio']
        nit    = g['nit']
        base   = g['gravado']
        iva    = g['iva']
        total  = g['total']
        cuenta_gasto = NIT_CUENTA_GASTO.get(str(nit).strip(), CTA_GASTO_DEFAULT)

        # Cuenta de gasto (débito)
        _escribir_fila(ws, row_idx, _fila_contai(
            cuenta_gasto, COMP_GASTO, fecha, folio, nit, 'GASTOS',
            TIPO_DEBITO, base))
        row_idx += 1

        # IVA descontable (débito) — solo si hay IVA
        if abs(iva) > 0.01:
            _escribir_fila(ws, row_idx, _fila_contai(
                CTA_IVA_DESCONTAB, COMP_GASTO, fecha, folio, nit, 'GASTOS',
                TIPO_DEBITO, iva, base=base))
            row_idx += 1

        # Proveedores / CxP (crédito) por el total
        _escribir_fila(ws, row_idx, _fila_contai(
            CTA_PROVEEDORES, COMP_GASTO, fecha, folio, nit, 'GASTOS',
            TIPO_CREDITO, total))
        row_idx += 1

    return row_idx


def generar_plano_contai(input_stream, incluir=('ventas', 'compras', 'nc_compras', 'gastos')):
    """
    Lee el reporte DIAN y genera el plano contable completo en formato Contai
    (ventas, compras, notas crédito de compras y gastos, según lo solicitado
    en 'incluir'). Retorna un BytesIO con el archivo Excel listo para descargar.
    """
    wb_src = openpyxl.load_workbook(input_stream, data_only=True, read_only=True)
    (_, facturas_compras, facturas_gastos, notas_credito,
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
    if 'gastos' in incluir:
        row_idx = _escribir_gastos(ws, row_idx, facturas_gastos)
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

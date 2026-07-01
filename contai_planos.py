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

# NIT (solo dígitos, SIN dígito de verificación) -> cuenta de gasto,
# extraído del balance de prueba INVERPLAS (mayo 2026). El NIT en los
# archivos DIAN no trae el dígito de verificación, así que se compara sin él.
# Excluye NITs de nómina. Los NITs ambiguos (más de una cuenta posible en el
# balance) están en NITS_GASTO_AMBIGUOS: se reconocen como gasto pero usan
# CTA_GASTO_DEFAULT para reclasificar manualmente.
NIT_CUENTA_GASTO = {
    '1006183536': '513550',   # JHON MARIO SALAZAR SANCHEZ
    '1006407425': '519560',   # LEZLY JULIANA DEL PILAR DIAZ
    '1039687512': '519560',   # NATALY PRADA RAMIREZ
    '1040380492': '519560',   # KATERINE JOHANA LOPEZ SANCHEZ
    '1045427914': '515505',   # SALOME MOSALVE POLO
    '1077443232': '513550',   # JHON GABRIEL RICO RIOS
    '1077466134': '519560',   # JUAN CAMILO VELASQUEZ OSPINA
    '1077467668': '513550',   # DANIEL SEBASTIAN LONDOÑO AGUDE
    '1088278023': '513550',   # JULIAN LOPEZ
    '1088339733': '519560',   # SEBASTIAN DUQUE MARIN
    '10951499': '515505',   # PABLO ANDRES ARANGO ZAPATA
    '1128433761': '519560',   # CRISTIA CAMILO GRISALES DUQUE
    '1152199201': '519530',   # JULIAN DAVID DIOSSA GALLEGO
    '15382292': '515505',   # MIGUEL ANTONIO ALZATE LOPEZ
    '15406177': '513550',   # CARLOS ENRIQUE HIGUITA
    '15539050': '515505',   # DIEGO LEON VERGARA BUSTAMANTE
    '16218190': '519535',   # HUMBERTO DE JESUS AGUDELO BETA
    '16545283': '519560',   # LUIS ANGEL MARTINEZ CRUZ
    '16836632': '513550',   # JUAN FERNANDO CARDONA MARTINEZ
    '21894689': '515505',   # MARIA ROCIO MONTES DAVILA
    '22209945': '515505',   # LUZ MARLENY CARMONA VILLA
    '28487420': '515505',   # ELISA USECHE DE CASTELLANOS
    '30230403': '530535',   # LUISA FERNANDA LARGO OROZCO
    '32560415': '530535',   # SARITH YASMITH CHANCI CARMONA
    '3510148': '530535',   # GUILLERMO ALONSO GARCIA JARAMI
    '39159110': '519560',   # OBEIDA MARIA CASTRO TRIANA
    '39272833': '519560',   # NANCY DEL CARMEN MERCADO
    '42941648': '519560',   # RESTAURANTE PARRILLA Y SABOR
    '43117093': '513515',   # CLAUDIA MARCELA GONZALEZ YEPES
    '4334595': '530535',   # OSCAR AUGUSTO MEJIA GALVIS
    '4336902': '530535',   # JOSE LIBARDO HERNANDEZ
    '43604113': '519560',   # BIBIANA MARIA DUQUE RICO
    '70086751': '515505',   # GERARDO DE JESUS ADARVE ROBAYO
    '70104335': '519530',   # JOSE LIBARDO ALVAREZ RESTREPO
    '70256801': '519560',   # JOSE ALBERTO TOBON MAZO
    '70422386': '513550',   # YOINER ALEXANDER OLAYA SERNA
    '70431382': '513550',   # GERMAN ARTURO LONDOÑO SARRAZOL
    '70563424': '519560',   # LUIS ALVARO GUIZADO ZAPATA
    '70780666': '519560',   # JOSE ISRAEL CARDONA VARGAS
    '71182213': '530535',   # ARTURO DE JESUS VALENCIA
    '71186238': '515505',   # JUAN BERNARDO GOMEZ ANGEL
    '71270982': '513515',   # RUBIEL HERNANDO VELEZ MOLINA
    '71364242': '513550',   # SERGIO OROZCO GUARIN
    '71364298': '513550',   # LUIS FERNANDO VASQUEZ BALLESTE
    '71526179': '512010',   # DIEGO CASTRILLON MARIN
    '71725033': '513520',   # WILLMAR DE JESUS GAVIRIA GALLE
    '800144355': '513505',   # TELESENTINEL DE ANTIOQUIA LTDA
    '800147567': '515520',   # COOTRANSUROCCIDENTE
    '800153993': '513535',   # COMCEL
    '800224808': '530515',   # PORVENIR
    '800227940': '530515',   # COLFONDOS
    '800229739': '530515',   # PROTECCION
    '8014460': '513550',   # URIEL ORLEY GOMEZ ATEHORTUA
    '80185305': '519560',   # FRANCISCO ALEJANDRO DIAZ VELEZ
    '8033607': '530535',   # SERGIO PATIÑO OSORIO
    '805007404': '514515',   # ICOMALLAS S A
    '8075447': '513550',   # DIEGO LEON MONTOYA ZAPATA
    '811009788': '519535',   # DISTRACOM MARIA AUXILIADORA
    '811012427': '515015',   # FERRETERIA LOS FIERROS
    '811015158': '519535',   # SHIRLEY ZULUAGA SALAZAR Y CIA
    '811023184': '514540',   # ASESORIA JURIDICA Y TECNICA DE
    '8203596': '519560',   # GABRIEL JAIME LLANO ALVAREZ
    '82361768': '515505',   # LEDEZMA COPETE RICARDO
    '830045034': '513550',   # PISOTRANS S.A.S.
    '8338163': '513550',   # LIS ALEXANDER ZAPATA SEPULVEDA
    '8345227': '519535',   # JUAN GUILLERMO GARCES
    '8416813': '513550',   # FABIO TORRES TABARES
    '860032550': '515015',   # ALFAGRES S.A.
    '86004058': '519560',   # JHON FREDY SUAREZ GIRALDO
    '860519235': '513005',   # TALLERES AUTORIZADOS S.A
    '88248613': '513550',   # HELMER GIRALDO MEDINA
    '890200928': '515520',   # COOPERATIVA SANTANDERIANA DETR
    '890302988': '519535',   # DIEGO LOPEZ S.A.S
    '890900608': '519535',   # ALMACENES EXITO S.A.
    '890900652': '515015',   # INVENSA S.A.
    '890900841': '530515',   # COMFAMA
    '890901491': '515520',   # FLOTA NORDESTE S.C.A.
    '890902760': '515520',   # SOTRAAURABA S.A.
    '890902872': '515520',   # TRANSPORTES GOMEZ HERNANDEZ SA
    '890903407': '513005',   # CIA SURAMERICANA DE SEGUROS S.
    '890905080': '514010',   # CAMARA DE COMERCIO DE MEDELLIN
    '890905211': '511505',   # MUNICIPIO DE MEDELLIN
    '890905680': '515520',   # COONORTE
    '890910715': '515015',   # FEROSVEL S.A.S.
    '890913059': '513550',   # EXPRESO CISNEROS NUS LTDA
    '890913987': '519560',   # MADRID HERMANOS S.A.S.
    '890914605': '515520',   # SOTRANSODA
    '891408584': '519560',   # FRISBY S.A.
    '891408635': '530535',   # INDUSTRIAS ZENNER S.A.
    '899999143': '515515',   # SERVICIO AEREO A TERRITORIOS N
    '900088915': '515515',   # EMPRESA AEREA DE SERVICIOS Y F
    '900092385': '513545',   # UNE EPM TELECOMUNICACIONES S.A
    '900098849': '530535',   # COMERCIALIZADORA LA PALMERA S,
    '900131632': '530535',   # PROVEEDORA MARIN SAS
    '900207854': '519535',   # HL COMBUSTIBLES SAS
    '900319753': '514015',   # PRICESMART COLOMBIA SAS
    '900392554': '515015',   # CROSSWAY S.A.S
    '900403670': '519560',   # INVERSISA S.A.S.
    '900425161': '530535',   # AGROCCIDENTE SOPETRAN
    '900438898': '530535',   # SUPERMERCADO SOL STORES S.A.S.
    '900524178': '530535',   # LA ESTACION DEL AGRO S.A.S.
    '900598444': '530535',   # ELECTRICOS SOLLA LA 49 SAS
    '900626095': '515015',   # MATERIALES Y FERRETERIA LA CR
    '900947532': '513520',   # RIBISOFT S.A.S.
    '901032147': '514540',   # LLANTAS Y RINES MOGOLLA SAS
    '901038738': '512510',   # CONJUNTO RESIDENCIAL MALAWI PH
    '901073417': '530535',   # CUERDAS EL TITAN SAS
    '901177347': '519560',   # C.M.S. INVERSORES S.A.S.
    '901302544': '530535',   # AGROINSUMOS PA MI TIERRA ZOMAC
    '901304335': '519535',   # JUANBE SANDIEGO SAS
    '901323819': '530535',   # INVERSIONES VELEZ VILLA ZOMAC
    '901725166': '530535',   # INVERSIONES MONSALVE VELEZ S.A
    '901929691': '530535',   # XCAVATECH S.A.S.
    '901975074': '530535',   # FERRETERIA LA PLAZUELA GH S.A.
    '98475267': '530535',   # AMAURY MIGUEL ZAYAS CORDERO
    '98627391': '514540',   # CARLOS BALBINO JARAMILOALVAREZ
    '98636248': '511030',   # CESAR AUGUSTO RESTREPO CIRO
    '98637173': '513550',   # JUAN FERNANDO HIGUITA CARTAGEN
    '98643736': '513550',   # JOHN ALEXANDER MEJIA VELASQUEZ
}

# NITs de gasto AMBIGUOS (2+ cuentas posibles en el balance): se
# reconocen como gasto pero van a CTA_GASTO_DEFAULT para reclasificar.
NITS_GASTO_AMBIGUOS = {
    '35589143',   # CLAUDIA PATRICIA VALDERRAMA SA -> ['519525', '519560']
    '71703542',   # JAIRO ANDRES GOMEZ OCAMPO -> ['515505', '519560']
    '71798765',   # WILMER HENAO NIETO -> ['515015', '531520']
    '800242106',   # HOMCENTER -> ['513550', '515015']
    '811044263',   # CARPAS Y LUBRICANTES LUFER S.A -> ['514540', '519535']
    '890902878',   # TRANSPORTES SEGOVIA Y CIA SCA -> ['513550', '515520']
    '890904996',   # EMPRESAS PUBLICAS DE MEDELLIN -> ['513525', '513530', '513560']
    '890935774',   # INVERSIONES ACEVEDO Y CIA SAS -> ['514540', '519535']
    '900219834',   # FLY PASS F2X  S.A.S. -> ['515530', '519565']
    '900276962',   # D1 S.A.S. -> ['519525', '519560']
    '900461512',   # MUEBLES PLASTICOS DUMMI SAS -> ['513550', '519540']
    '900480569',   # JERONIMO MARTINS COLOMBIA SAS -> ['515505', '519560']
    '900854874',   # NEX CAPITAL S.A.S. -> ['530505', '530520']
    '901300741',   # COESCO COLOMBIA S.A.S. -> ['513515', '519535']
    '901870310',   # RESTAURANTE ANGOLA NOVEL -> ['519525', '519560']
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


def _es_nit_gasto_conocido(nit):
    """True si el NIT es un proveedor de servicios/gastos identificado en el
    balance (con cuenta única en NIT_CUENTA_GASTO o ambiguo en
    NITS_GASTO_AMBIGUOS). El NIT se compara SIN dígito de verificación."""
    nit = str(nit).strip()
    return nit in NIT_CUENTA_GASTO or nit in NITS_GASTO_AMBIGUOS


def _reclasificar_recibidas(compras_raw, gastos_raw):
    """
    converter.py clasifica compras vs. gastos comparando el NIT emisor contra
    un único NIT_PROVEEDOR_INVENTARIO (regla pensada para otro cliente con un
    solo proveedor de mercancía). Para INVERPLAS, que compra mercancía a
    decenas de proveedores distintos, se reclasifica por NIT: si el NIT es un
    proveedor de servicios conocido (o ambiguo) → gasto; si no → compra de
    mercancía.
    """
    compras, gastos = [], []
    for doc in compras_raw + gastos_raw:
        (gastos if _es_nit_gasto_conocido(doc['nit']) else compras).append(doc)
    return compras, gastos


def _reclasificar_nc(notas_credito):
    """Igual que _reclasificar_recibidas, para notas crédito recibidas."""
    nc_compras, nc_gastos = [], []
    for doc in notas_credito:
        (nc_gastos if _es_nit_gasto_conocido(doc['nit']) else nc_compras).append(doc)
    return nc_compras, nc_gastos


def _escribir_nc_gastos(ws, row_idx, nc_gastos):
    """Escribe notas crédito de gastos/servicios (devolución al proveedor)."""
    for nc in nc_gastos:
        if abs(nc['total']) < 0.01:
            continue
        fecha  = _fmt_fecha(nc['fecha'])
        folio  = nc['folio']
        nit    = nc['nit']
        base   = nc['gravado']
        iva    = nc['iva']
        total  = nc['total']
        cuenta_gasto = NIT_CUENTA_GASTO.get(str(nit).strip(), CTA_GASTO_DEFAULT)

        # Reverso de la cuenta de gasto (crédito)
        _escribir_fila(ws, row_idx, _fila_contai(
            cuenta_gasto, COMP_NC_COMPRA, fecha, folio, nit, 'DEV. GASTOS',
            TIPO_CREDITO, base))
        row_idx += 1

        # Reverso IVA descontable (crédito) — solo si hay IVA
        if abs(iva) > 0.01:
            _escribir_fila(ws, row_idx, _fila_contai(
                CTA_IVA_DESCONTAB, COMP_NC_COMPRA, fecha, folio, nit, 'DEV. GASTOS',
                TIPO_CREDITO, iva, base=base))
            row_idx += 1

        # Proveedores / CxP (débito) por el total
        _escribir_fila(ws, row_idx, _fila_contai(
            CTA_PROVEEDORES, COMP_NC_COMPRA, fecha, folio, nit, 'DEV. GASTOS',
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
    (_, facturas_compras_raw, facturas_gastos_raw, notas_credito_raw,
     ventas, nc_ventas, _, _, _, _, _, _) = _leer_todo(wb_src)

    # Reclasificar por NIT real del proveedor (ver _reclasificar_recibidas):
    # la clasificación de converter.py usa una regla de otro cliente.
    facturas_compras, facturas_gastos = _reclasificar_recibidas(
        facturas_compras_raw, facturas_gastos_raw)
    nc_compras, nc_gastos = _reclasificar_nc(notas_credito_raw)

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
        row_idx = _escribir_nc_compras(ws, row_idx, nc_compras)
        row_idx = _escribir_nc_gastos(ws, row_idx, nc_gastos)

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

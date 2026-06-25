"""
Módulo para cálculo de retenciones colombianas según tabla oficial DIAN 2026
Tabla de tarifas de retención en la fuente - UVT 2026: $52.374
"""

# Tabla oficial de retenciones 2026 por concepto
RETENCIONES_2026 = {
    # COMPRAS
    'compras_generales_declarantes': 2.5,
    'compras_generales_no_declarantes': 3.5,
    'compras_tarjeta_debito_credito': 1.5,
    'compras_agricolas_sin_procesamiento': 1.5,
    'compras_agricolas_con_procesamiento_declarantes': 2.5,
    'compras_agricolas_con_procesamiento_no_declarantes': 3.5,
    'compras_cafe_pergamino': 0.5,
    'compras_combustibles': 0.1,
    'compras_vehiculos': 1.0,
    'compras_oro': 2.5,
    'compras_bienes_raices_vivienda_hasta_10000uvt': 1.0,
    'compras_bienes_raices_vivienda_exceso': 2.5,
    'compras_bienes_raices_otro_uso': 2.5,

    # SERVICIOS
    'servicios_generales_declarantes': 4.0,
    'servicios_generales_no_declarantes': 6.0,
    'servicios_transporte_carga': 1.0,
    'servicios_transporte_pasajeros_terrestre': 3.5,
    'servicios_transporte_pasajeros_aereo_maritimo': 1.0,
    'servicios_temporales_aiu': 1.0,
    'servicios_vigilancia_aseo_aiu': 2.0,
    'servicios_salud_ips': 2.0,
    'servicios_hoteles_restaurantes': 3.5,
    'servicios_software_licenciamiento': 3.5,

    # ARRENDAMIENTO
    'arrendamiento_muebles': 4.0,
    'arrendamiento_inmuebles_declarantes': 3.5,
    'arrendamiento_inmuebles_no_declarantes': 3.5,

    # HONORARIOS Y COMISIONES
    'honorarios_comisiones_juridicas': 11.0,
    'honorarios_comisiones_naturales': 11.0,
    'honorarios_comisiones_no_declarantes': 10.0,

    # INGRESOS TRIBUTARIOS
    'otros_ingresos_declarantes': 2.5,
    'otros_ingresos_no_declarantes': 3.5,

    # RENDIMIENTOS FINANCIEROS
    'intereses_financieros': 7.0,
    'rendimientos_renta_fija': 4.0,

    # RETENCIÓN IVA
    'retencion_iva_servicios': 15.0,
    'retencion_iva_compras': 15.0,

    # CONSTRUCCIÓN
    'construccion_urbanizacion': 2.0,

    # VENTAS (autoretención)
    'ventas_autorretencion': 1.2,
}

# Mapeo de actividades económicas (CIIU)
ACTIVIDADES_ECONOMICAS = {
    '4631': 'Comercio al por mayor',
    '4632': 'Comercio al por menor',
    '7820': 'Servicios de TI',
    '6820': 'Arrendamiento de bienes',
}

# Mapeo de NITs especiales con retenciones específicas
NITS_ESPECIALES = {
    # 'NIT': {'concepto': 'servicios_software_licenciamiento', 'tasa': 3.5}
}

def obtener_tasa_por_tipo(tipo_documento, es_declarante=True):
    """
    Obtiene la tasa de retención según el tipo de documento.

    Args:
        tipo_documento: Tipo de documento ('compras', 'servicios', 'honorarios', etc.)
        es_declarante: Si es declarante de renta (afecta tasa)

    Returns:
        Tasa de retención en porcentaje
    """

    tipo_lower = tipo_documento.lower().replace(' ', '_')

    # Mapeo de tipos generales a conceptos específicos
    tipo_map = {
        'compras': 'compras_generales_declarantes' if es_declarante else 'compras_generales_no_declarantes',
        'servicios': 'servicios_generales_declarantes' if es_declarante else 'servicios_generales_no_declarantes',
        'software': 'servicios_software_licenciamiento',
        'arrendamiento': 'arrendamiento_inmuebles_declarantes' if es_declarante else 'arrendamiento_inmuebles_no_declarantes',
        'honorarios': 'honorarios_comisiones_no_declarantes' if not es_declarante else 'honorarios_comisiones_naturales',
        'ventas': 'ventas_autorretencion',
    }

    # Intentar encontrar mapeo exacto
    if tipo_lower in RETENCIONES_2026:
        return RETENCIONES_2026[tipo_lower]

    # Intentar mapeo por palabra clave
    for clave, concepto in tipo_map.items():
        if clave in tipo_lower:
            return RETENCIONES_2026.get(concepto, 2.5)

    # Por defecto según tipo
    if 'compra' in tipo_lower:
        return RETENCIONES_2026['compras_generales_declarantes']
    elif 'venta' in tipo_lower:
        return RETENCIONES_2026['ventas_autorretencion']
    elif 'servicio' in tipo_lower or 'software' in tipo_lower:
        return RETENCIONES_2026['servicios_software_licenciamiento']

    # Default: compras genéricas declarantes
    return 2.5

def calcular_retencion(base_gravable, tipo_operacion='compras', nit_proveedor='', actividad='4631', es_declarante=True):
    """
    Calcula la retención aplicable según la operación.

    Args:
        base_gravable: Base sobre la cual se calcula
        tipo_operacion: 'ventas', 'compras', 'servicios', 'software', etc.
        nit_proveedor: NIT del proveedor (para buscar en tabla especial)
        actividad: Actividad económica (ej: '4631')
        es_declarante: Si es declarante de renta

    Returns:
        dict con: base, tasa, valor_retencion
    """

    # Buscar tasa especial por NIT
    if nit_proveedor in NITS_ESPECIALES:
        concepto = NITS_ESPECIALES[nit_proveedor].get('concepto')
        tasa = RETENCIONES_2026.get(concepto, obtener_tasa_por_tipo(tipo_operacion, es_declarante))
    else:
        # Usar tasa según tipo de operación
        tasa = obtener_tasa_por_tipo(tipo_operacion, es_declarante)

    valor_retencion = round(base_gravable * tasa / 100, 2)

    return {
        'base': round(base_gravable, 2),
        'tasa': tasa,
        'valor': valor_retencion,
        'tipo': tipo_operacion,
        'actividad': actividad,
        'es_declarante': es_declarante
    }

def generar_reporte_retenciones_excel(planos_data, actividad='4631', es_declarante=True):
    """
    Genera reporte de retenciones a partir de datos de planos.
    Utiliza tabla oficial 2026 DIAN.

    Args:
        planos_data: Dict con datos de planos {'compras': [...], 'ventas': [...]}
        actividad: Actividad económica
        es_declarante: Si es declarante de renta

    Returns:
        Excel workbook con retenciones calculadas
    """

    try:
        from openpyxl import Workbook
        from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    except ImportError:
        return None

    wb = Workbook()
    ws = wb.active
    ws.title = 'Retenciones'

    # Encabezados
    headers = ['Tipo', 'Documento', 'Fecha', 'NIT', 'Tercero', 'Base Gravable', 'Tasa %', 'Valor Retención']

    # Estilo encabezado
    header_fill = PatternFill(start_color='1F4E78', end_color='1F4E78', fill_type='solid')
    header_font = Font(bold=True, color='FFFFFF')

    for col, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col, value=header)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal='center', vertical='center')

    # Ancho de columnas
    ws.column_dimensions['A'].width = 12
    ws.column_dimensions['B'].width = 12
    ws.column_dimensions['C'].width = 12
    ws.column_dimensions['D'].width = 12
    ws.column_dimensions['E'].width = 20
    ws.column_dimensions['F'].width = 14
    ws.column_dimensions['G'].width = 10
    ws.column_dimensions['H'].width = 14

    row = 2
    totales = {'base': 0, 'retencion': 0}

    # Procesar compras
    for doc in planos_data.get('compras', []):
        base = doc.get('total', 0) - doc.get('iva', 0)
        ret = calcular_retencion(base, 'compras', doc.get('nit', ''), actividad, es_declarante)

        ws.cell(row=row, column=1, value='Compra')
        ws.cell(row=row, column=2, value=doc.get('folio', ''))
        ws.cell(row=row, column=3, value=doc.get('fecha', ''))
        ws.cell(row=row, column=4, value=doc.get('nit', ''))
        ws.cell(row=row, column=5, value=doc.get('nombre', ''))
        ws.cell(row=row, column=6, value=ret['base'])
        ws.cell(row=row, column=7, value=ret['tasa'])
        ws.cell(row=row, column=8, value=ret['valor'])

        totales['base'] += ret['base']
        totales['retencion'] += ret['valor']
        row += 1

    # Procesar ventas
    for doc in planos_data.get('ventas', []):
        base = doc.get('total', 0) - doc.get('iva', 0)
        ret = calcular_retencion(base, 'ventas', doc.get('nit', ''), actividad, es_declarante)

        ws.cell(row=row, column=1, value='Venta')
        ws.cell(row=row, column=2, value=doc.get('folio', ''))
        ws.cell(row=row, column=3, value=doc.get('fecha', ''))
        ws.cell(row=row, column=4, value=doc.get('nit', ''))
        ws.cell(row=row, column=5, value=doc.get('nombre', ''))
        ws.cell(row=row, column=6, value=ret['base'])
        ws.cell(row=row, column=7, value=ret['tasa'])
        ws.cell(row=row, column=8, value=ret['valor'])

        totales['base'] += ret['base']
        totales['retencion'] += ret['valor']
        row += 1

    # Fila de totales
    total_fill = PatternFill(start_color='D9E1F2', end_color='D9E1F2', fill_type='solid')
    total_font = Font(bold=True)

    row += 1
    ws.cell(row=row, column=5, value='TOTAL').font = total_font
    ws.cell(row=row, column=6, value=totales['base']).font = total_font
    ws.cell(row=row, column=6).fill = total_fill
    ws.cell(row=row, column=8, value=totales['retencion']).font = total_font
    ws.cell(row=row, column=8).fill = total_fill

    return wb

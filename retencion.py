"""
Módulo para cálculo de retenciones colombianas según tabla 2026
"""

# Tasas de retención por actividad económica y tipo de operación
RETENCIONES = {
    'ventas': {
        'autorretencion': 1.20,  # Autoretención sobre ventas
        'default': 1.20
    },
    'compras': {
        'default': 2.5,  # Retención en la fuente compras genéricas
        'software': 3.5,  # Licenciamiento de software
    },
    'gastos': {
        'default': 2.5,
        'software': 3.5,
    }
}

# Mapeo de actividades económicas
ACTIVIDADES_ECONOMICAS = {
    '4631': 'Comercio al por mayor',
    '4632': 'Comercio al por menor',
}

# Mapeo de NITs especiales con retenciones específicas
NITS_ESPECIALES = {
    # 'NIT': {'tipo': 'software', 'tasa': 3.5}
}

def calcular_retencion(base_gravable, tipo_operacion='compras', nit_proveedor='', actividad='4631'):
    """
    Calcula la retención aplicable según la operación.
    
    Args:
        base_gravable: Base sobre la cual se calcula
        tipo_operacion: 'ventas', 'compras', 'gastos'
        nit_proveedor: NIT del proveedor (para buscar en tabla especial)
        actividad: Actividad económica (ej: '4631')
    
    Returns:
        dict con: base, tasa, valor_retencion
    """
    
    # Buscar tasa especial por NIT
    if nit_proveedor in NITS_ESPECIALES:
        tasa = NITS_ESPECIALES[nit_proveedor].get('tasa', RETENCIONES[tipo_operacion].get('default', 0))
    else:
        # Usar tasa por defecto según tipo de operación
        tasa = RETENCIONES[tipo_operacion].get('default', 0)
    
    valor_retencion = round(base_gravable * tasa / 100, 2)
    
    return {
        'base': round(base_gravable, 2),
        'tasa': tasa,
        'valor': valor_retencion,
        'tipo': tipo_operacion,
        'actividad': actividad
    }

def generar_reporte_retenciones(planos_data, actividad='4631'):
    """
    Genera reporte de retenciones a partir de datos de planos.
    
    Args:
        planos_data: Dict con datos de planos {'compras': [...], 'ventas': [...]}
        actividad: Actividad económica
    
    Returns:
        Dict con resumen de retenciones
    """
    
    retenciones = {
        'ventas': [],
        'compras': [],
        'gastos': [],
        'totales': {
            'base_ventas': 0,
            'retencion_ventas': 0,
            'base_compras': 0,
            'retencion_compras': 0,
            'base_gastos': 0,
            'retencion_gastos': 0,
        }
    }
    
    # Procesar ventas
    for venta in planos_data.get('ventas', []):
        base = venta.get('total', 0) - venta.get('iva', 0)
        ret = calcular_retencion(base, 'ventas', venta.get('nit', ''), actividad)
        retenciones['ventas'].append({**venta, **ret})
        retenciones['totales']['base_ventas'] += ret['base']
        retenciones['totales']['retencion_ventas'] += ret['valor']
    
    # Procesar compras
    for compra in planos_data.get('compras', []):
        base = compra.get('total', 0) - compra.get('iva', 0)
        ret = calcular_retencion(base, 'compras', compra.get('nit', ''), actividad)
        retenciones['compras'].append({**compra, **ret})
        retenciones['totales']['base_compras'] += ret['base']
        retenciones['totales']['retencion_compras'] += ret['valor']
    
    # Procesar gastos
    for gasto in planos_data.get('gastos', []):
        base = gasto.get('total', 0) - gasto.get('iva', 0)
        ret = calcular_retencion(base, 'gastos', gasto.get('nit', ''), actividad)
        retenciones['gastos'].append({**gasto, **ret})
        retenciones['totales']['base_gastos'] += ret['base']
        retenciones['totales']['retencion_gastos'] += ret['valor']
    
    return retenciones

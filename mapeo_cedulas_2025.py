#!/usr/bin/env python3
"""
MAPEO DE CÉDULAS 2025 - Según DIAN
Basado en Guía Definitiva - Declaración de Renta Persona Natural 2025
"""

CEDULAS_DIAN = {
    'CEDULA_GENERAL': {
        'nombre': 'Cédula General',
        'casillas': {
            'trabajo': {'inicio': 32, 'fin': 56},
            'capital': {'inicio': 58, 'fin': 72},
            'no_laborales': {'inicio': 74, 'fin': 90},
        },
        'componentes': [
            'Rentas de Trabajo',
            'Rentas de Capital',
            'Rentas No Laborales'
        ],
        'deduccion_especial': 0.25,  # 25% del ingreso
        'deduccion_maxima': 95000000,  # $95 millones
    },
    'CEDULA_PENSIONES': {
        'nombre': 'Cédula de Pensiones',
        'casillas': {'inicio': 99, 'fin': 105},
        'tipos': [
            'Pensión de jubilación',
            'Pensión de vejez',
            'Pensión de sobrevivientes',
            'Pensión de invalidez',
            'Indemnizaciones sustitutivas',
        ]
    },
    'GANANCIAS_OCASIONALES': {
        'nombre': 'Ganancias Ocasionales',
        'casillas': {'inicio': 112, 'fin': 115},
        'tarifa_especial': 0.10,  # 10%
        'tipos': [
            'Venta de bienes (2+ años)',
            'Venta de activos fijos',
            'Otras ganancias ocasionales'
        ]
    }
}

CLASIFICACION_RENTAS = {
    # RENTAS DE TRABAJO (CÉDULA GENERAL)
    'TRABAJO': {
        'salarios': {
            'palabras_clave': ['salario', 'sueldo', 'contrato laboral', 'nómina'],
            'casilla': 32,
            'descripcion': 'Salarios y contratos laborales'
        },
        'honorarios': {
            'palabras_clave': ['honorario', 'profesional', 'consultoría'],
            'casilla': 43,
            'descripcion': 'Honorarios (máx 90 días, menos de 2 personas)'
        },
        'comisiones': {
            'palabras_clave': ['comisión', 'commission', 'corretaje'],
            'casilla': 43,
            'descripcion': 'Comisiones y prestación de servicios'
        },
        'prestaciones_sociales': {
            'palabras_clave': ['prima', 'vacaciones', 'cesantías', 'liquidación'],
            'casilla': 32,
            'descripcion': 'Prestaciones sociales'
        },
    },

    # RENTAS DE CAPITAL (CÉDULA GENERAL)
    'CAPITAL': {
        'dividendos': {
            'palabras_clave': ['dividendo', 'dividend', 'utilidad', 'participación'],
            'casilla': 58,
            'descripcion': 'Dividendos y participaciones de utilidades'
        },
        'intereses': {
            'palabras_clave': ['interés', 'interest', 'rendimiento', 'cdt', 'depósito término'],
            'casilla': 58,
            'descripcion': 'Intereses y rendimientos financieros'
        },
        'arrendamiento': {
            'palabras_clave': ['arrendamiento', 'rent', 'alquiler', 'canon'],
            'casilla': 58,
            'descripcion': 'Ingresos por arrendamiento'
        },
        'otros_ingresos_capital': {
            'palabras_clave': ['ingreso capital', 'renta capital'],
            'casilla': 58,
            'descripcion': 'Otros ingresos de capital'
        }
    },

    # RENTAS NO LABORALES (CÉDULA GENERAL)
    'NO_LABORALES': {
        'actividades_economicas': {
            'palabras_clave': ['negocio propio', 'actividad económica', 'empresa'],
            'casilla': 74,
            'descripcion': 'Rentas de actividades económicas'
        },
        'otros_conceptos': {
            'palabras_clave': ['transferencia', 'herencia', 'donación'],
            'casilla': 74,
            'descripcion': 'Otros ingresos no laborales'
        }
    },

    # CÉDULA DE PENSIONES
    'PENSIONES': {
        'pension_jubilacion': {
            'palabras_clave': ['pensión jubilación', 'jubilación', 'retiro'],
            'casilla': 99,
            'descripcion': 'Pensión de jubilación'
        },
        'pension_vejez': {
            'palabras_clave': ['pensión vejez', 'vejez'],
            'casilla': 99,
            'descripcion': 'Pensión de vejez'
        },
        'pension_sobrevivientes': {
            'palabras_clave': ['pensión sobrevivientes', 'sobrevivientes'],
            'casilla': 99,
            'descripcion': 'Pensión de sobrevivientes'
        },
        'pension_invalidez': {
            'palabras_clave': ['pensión invalidez', 'invalidez'],
            'casilla': 99,
            'descripcion': 'Pensión de invalidez'
        }
    },

    # GANANCIAS OCASIONALES
    'OCASIONALES': {
        'venta_bienes': {
            'palabras_clave': ['venta bien', 'ganancia', 'plusvalía', 'venta activo'],
            'casilla': 112,
            'descripcion': 'Ganancias por venta de bienes (2+ años)',
            'tarifa': 0.10
        }
    }
}

def clasificar_renta_v2(concepto, valor):
    """
    Clasifica una renta según el sistema cedular DIAN 2025
    Retorna: (cedula, tipo, subtipo, casilla)
    """
    concepto_lower = str(concepto).lower()

    # Buscar en cada categoría
    for categoria, tipos in CLASIFICACION_RENTAS.items():
        for tipo, config in tipos.items():
            palabras_clave = config.get('palabras_clave', [])
            if any(palabra in concepto_lower for palabra in palabras_clave):
                casilla = config.get('casilla')

                # Determinar cédula
                if categoria in ['TRABAJO', 'CAPITAL', 'NO_LABORALES']:
                    cedula = 'CEDULA_GENERAL'
                elif categoria == 'PENSIONES':
                    cedula = 'CEDULA_PENSIONES'
                elif categoria == 'OCASIONALES':
                    cedula = 'GANANCIAS_OCASIONALES'
                else:
                    cedula = 'CEDULA_GENERAL'

                return {
                    'cedula': cedula,
                    'categoria': categoria,
                    'tipo': tipo,
                    'casilla': casilla,
                    'valor': valor,
                    'descripcion': config.get('descripcion', '')
                }

    # Default
    return {
        'cedula': 'CEDULA_GENERAL',
        'categoria': 'NO_LABORALES',
        'tipo': 'otros',
        'casilla': 74,
        'valor': valor,
        'descripcion': 'Renta no clasificada'
    }

# Test
if __name__ == '__main__':
    test_rentas = [
        'Salario',
        'Dividendos',
        'Intereses CDT',
        'Pensión jubilación',
        'Ganancia venta terreno',
        'Arrendamiento casa',
        'Honorarios consultoría'
    ]

    print("🔍 TEST: Clasificación de Rentas DIAN 2025\n")
    for renta in test_rentas:
        clasificacion = clasificar_renta_v2(renta, 1000000)
        print(f"{renta:30} → {clasificacion['cedula']:25} | {clasificacion['tipo']}")

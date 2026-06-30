#!/usr/bin/env python3
"""
Cálculo de Cédulas - Declaración Renta 2025
Módulo para calcular cédulas según norma DIAN
"""

class CalculadoraCedulas:
    """Calcula cédulas de renta según DIAN 2025"""

    # Valores para 2025
    UVT_2025 = 47065
    SMLV_2025 = 1320000

    # Rangos IRPF 2025
    TARIFAS_IRPF = [
        (0, 1*UVT_2025, 0),                    # 0%
        (1*UVT_2025, 1.95*UVT_2025, 0.05),     # 5%
        (1.95*UVT_2025, 3*UVT_2025, 0.08),     # 8%
        (3*UVT_2025, 4.6*UVT_2025, 0.11),      # 11%
        (4.6*UVT_2025, 6.1*UVT_2025, 0.13),    # 13%
        (6.1*UVT_2025, 9.3*UVT_2025, 0.17),    # 17%
        (9.3*UVT_2025, 18.7*UVT_2025, 0.26),   # 26%
        (18.7*UVT_2025, float('inf'), 0.33)    # 33%
    ]

    @staticmethod
    def calcular_irpf(renta_neta):
        """Calcula IRPF según tarifa 2025"""
        if renta_neta <= 0:
            return 0
        impuesto = 0
        for limite_inf, limite_sup, tarifa in CalculadoraCedulas.TARIFAS_IRPF:
            if renta_neta <= limite_inf:
                break
            base_tributaria = min(renta_neta, limite_sup) - limite_inf
            if base_tributaria > 0:
                impuesto += base_tributaria * tarifa
        return impuesto

    @staticmethod
    def calcular_aporte_solidario(renta_neta):
        """Calcula aporte solidario (1% sobre rentas > 16.000 UVT)"""
        umbral = 16000 * CalculadoraCedulas.UVT_2025
        if renta_neta > umbral:
            return (renta_neta - umbral) * 0.01
        return 0

    @staticmethod
    def calcular_cedula_general(rentas_capitales):
        """Calcula cédula general"""
        total_ingresos = sum(r.get('valor', 0) for r in rentas_capitales)
        total_deducciones = 0

        return {
            'tipo': 'Cédula General',
            'ingresos': total_ingresos,
            'deducciones': total_deducciones,
            'renta_liquida': total_ingresos - total_deducciones,
            'rentas': rentas_capitales
        }

    @staticmethod
    def calcular_cedula_trabajo(rentas_trabajo):
        """Calcula cédula de rentas de trabajo"""
        total_ingresos = sum(r.get('valor', 0) for r in rentas_trabajo)
        deduccion = min(total_ingresos * 0.25, 95000000)

        return {
            'tipo': 'Cédula de Trabajo',
            'ingresos': total_ingresos,
            'deducciones': deduccion,
            'renta_liquida': max(0, total_ingresos - deduccion),
            'rentas': rentas_trabajo
        }

    @classmethod
    def calcular_all_cedulas(cls, rentas):
        """Calcula todas las cédulas a partir de lista de rentas"""
        cédulas = {}

        rentas_general = [r for r in rentas if r.get('subtipo', '') in ['Dividendos', 'Intereses', 'Arrendamiento']]
        rentas_trabajo = [r for r in rentas if r.get('subtipo', '') in ['Salarios', 'Honorarios', 'Comisiones']]

        if rentas_general:
            cédulas['general'] = cls.calcular_cedula_general(rentas_general)

        if rentas_trabajo:
            cédulas['trabajo'] = cls.calcular_cedula_trabajo(rentas_trabajo)

        return cédulas

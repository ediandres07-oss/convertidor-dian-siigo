"""
Módulo de Liquidación de Prestaciones Sociales
Cálculos de cesantías, prima, vacaciones e intereses (Colombia)
"""

from datetime import datetime
from typing import Dict, Tuple
from dataclasses import dataclass


@dataclass
class ResultadosLiquidacion:
    """Estructura de resultados de liquidación"""
    dias_laborados: int
    cesantias: float
    intereses_cesantias: float
    prima_servicios: float
    vacaciones: float
    total_devengado: float
    descuentos: float
    neto_pagar: float


class CalculadoraLiquidacion:
    """Calcula prestaciones sociales colombianas"""

    DIAS_BASE = 360
    DIAS_VACACIONES = 720
    TASA_INTERESES = 0.12

    @staticmethod
    def calcular_dias(fecha_ingreso: str, fecha_retiro: str) -> int:
        """
        Calcula días laborados entre dos fechas

        Args:
            fecha_ingreso: Fecha formato YYYY-MM-DD
            fecha_retiro: Fecha formato YYYY-MM-DD

        Returns:
            Número de días laborados
        """
        try:
            f_inicio = datetime.strptime(fecha_ingreso, "%Y-%m-%d")
            f_fin = datetime.strptime(fecha_retiro, "%Y-%m-%d")

            if f_fin < f_inicio:
                raise ValueError("Fecha retiro debe ser posterior a fecha ingreso")

            dias = (f_fin - f_inicio).days + 1
            return max(dias, 0)

        except ValueError as e:
            raise ValueError(f"Error en formato de fechas: {str(e)}")

    @staticmethod
    def calcular_prestaciones(
        salario: float,
        auxilio: float,
        dias: int
    ) -> ResultadosLiquidacion:
        """
        Calcula todas las prestaciones sociales

        Args:
            salario: Salario mensual
            auxilio: Auxilio de transporte
            dias: Días laborados

        Returns:
            ResultadosLiquidacion con todos los valores
        """
        if salario <= 0:
            raise ValueError("Salario debe ser mayor a 0")

        if dias < 0:
            raise ValueError("Días no puede ser negativo")

        # Base de cálculo
        base = salario + auxilio

        # Cálculos individuales
        cesantias = (base * dias) / CalculadoraLiquidacion.DIAS_BASE
        intereses = (cesantias * CalculadoraLiquidacion.TASA_INTERESES * dias) / CalculadoraLiquidacion.DIAS_BASE
        prima = (base * dias) / CalculadoraLiquidacion.DIAS_BASE
        vacaciones = (salario * dias) / CalculadoraLiquidacion.DIAS_VACACIONES

        # Totales
        total_devengado = cesantias + intereses + prima + vacaciones
        descuentos = 0.0
        neto_pagar = total_devengado - descuentos

        return ResultadosLiquidacion(
            dias_laborados=dias,
            cesantias=round(cesantias, 2),
            intereses_cesantias=round(intereses, 2),
            prima_servicios=round(prima, 2),
            vacaciones=round(vacaciones, 2),
            total_devengado=round(total_devengado, 2),
            descuentos=descuentos,
            neto_pagar=round(neto_pagar, 2)
        )

    @staticmethod
    def formato_moneda(valor: float) -> str:
        """Formatea valor a moneda colombiana"""
        return f"${valor:,.2f}"

    @staticmethod
    def formato_fecha(fecha: str) -> str:
        """Convierte fecha de YYYY-MM-DD a DD/MM/YYYY"""
        try:
            f = datetime.strptime(fecha, "%Y-%m-%d")
            return f.strftime("%d/%m/%Y")
        except:
            return fecha


# Funciones compatibles con código anterior
def calcular_dias(fecha_ingreso, fecha_retiro):
    """Compatible con versión anterior"""
    return CalculadoraLiquidacion.calcular_dias(
        str(fecha_ingreso),
        str(fecha_retiro)
    )


def calcular_prestaciones(salario, auxilio, dias):
    """Compatible con versión anterior - retorna diccionario"""
    resultado = CalculadoraLiquidacion.calcular_prestaciones(salario, auxilio, dias)
    return {
        "cesantias": resultado.cesantias,
        "intereses": resultado.intereses_cesantias,
        "prima": resultado.prima_servicios,
        "vacaciones": resultado.vacaciones,
        "total": resultado.neto_pagar,
        "dias_laborados": resultado.dias_laborados,
        "total_devengado": resultado.total_devengado,
        "neto_pagar": resultado.neto_pagar
    }

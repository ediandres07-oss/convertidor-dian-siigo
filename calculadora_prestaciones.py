"""
Módulo de Cálculo de Prestaciones Sociales Colombianas
Calcula cesantías, prima, vacaciones e intereses según la ley colombiana
"""

from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import Dict, Tuple


@dataclass
class DatosEmpleado:
    """Estructura para datos del empleado"""
    nombre: str
    documento: str
    cargo: str
    salario_mensual: float
    auxilio_transporte: float
    fecha_ingreso: datetime
    fecha_retiro: datetime
    empresa: str = "EMPRESA S.A.S"


@dataclass
class ResultadosPrestaciones:
    """Estructura para resultados del cálculo"""
    dias_laborados: int
    cesantias: float
    intereses_cesantias: float
    prima_servicios: float
    vacaciones: float
    total_devengado: float
    descuentos: float
    neto_pagar: float


class CalculadoraPrestaciones:
    """Calcula prestaciones sociales según regulaciones colombianas"""

    # Constantes colombianas
    DIAS_BASE = 360  # Base de cálculo anual
    DIAS_VACACIONES = 720  # 2 × 360 para vacaciones
    TASA_INTERESES = 0.12  # 12% anual para intereses

    @staticmethod
    def calcular_dias_laborados(fecha_ingreso: datetime, fecha_retiro: datetime) -> int:
        """
        Calcula días laborados entre dos fechas

        Args:
            fecha_ingreso: Fecha de inicio laboral
            fecha_retiro: Fecha de retiro/terminación

        Returns:
            Número de días laborados (mínimo 0)
        """
        if fecha_retiro < fecha_ingreso:
            raise ValueError("Fecha de retiro no puede ser anterior a fecha de ingreso")

        dias = (fecha_retiro - fecha_ingreso).days + 1  # Incluye el último día
        return max(dias, 0)

    @staticmethod
    def calcular_cesantias(base_calculo: float, dias: int) -> Tuple[float, float]:
        """
        Calcula cesantías e intereses

        Cesantías = (Salario + Auxilio) × Días / 360
        Intereses = Cesantías × 12% × Días / 360

        Args:
            base_calculo: Salario + auxilio de transporte
            dias: Días laborados

        Returns:
            Tupla (cesantías, intereses)
        """
        cesantias = (base_calculo * dias) / CalculadoraPrestaciones.DIAS_BASE

        # Intereses sobre cesantías
        intereses = (cesantias * CalculadoraPrestaciones.TASA_INTERESES * dias) / CalculadoraPrestaciones.DIAS_BASE

        return round(cesantias, 2), round(intereses, 2)

    @staticmethod
    def calcular_prima(base_calculo: float, dias: int) -> float:
        """
        Calcula prima de servicios (bono de servicios)

        Prima = (Salario + Auxilio) × Días / 360

        Args:
            base_calculo: Salario + auxilio de transporte
            dias: Días laborados

        Returns:
            Valor de prima de servicios
        """
        prima = (base_calculo * dias) / CalculadoraPrestaciones.DIAS_BASE
        return round(prima, 2)

    @staticmethod
    def calcular_vacaciones(salario: float, dias: int) -> float:
        """
        Calcula vacaciones proporcionales

        Vacaciones = Salario × Días / 720
        (720 = 2 × 360, representa 15 días de vacaciones anuales)

        Args:
            salario: Salario mensual
            dias: Días laborados

        Returns:
            Valor de vacaciones proporcionales
        """
        vacaciones = (salario * dias) / CalculadoraPrestaciones.DIAS_VACACIONES
        return round(vacaciones, 2)

    @classmethod
    def calcular_prestaciones(cls, datos: DatosEmpleado) -> ResultadosPrestaciones:
        """
        Calcula todas las prestaciones sociales

        Args:
            datos: Datos del empleado (DatosEmpleado)

        Returns:
            ResultadosPrestaciones con todos los valores calculados
        """
        # Validaciones
        if datos.salario_mensual <= 0:
            raise ValueError("El salario debe ser mayor a 0")

        if datos.fecha_retiro < datos.fecha_ingreso:
            raise ValueError("Fecha de retiro no puede ser anterior a fecha de ingreso")

        # Cálculo de días
        dias = cls.calcular_dias_laborados(datos.fecha_ingreso, datos.fecha_retiro)

        # Base de cálculo (salario + auxilio)
        base_calculo = datos.salario_mensual + datos.auxilio_transporte

        # Cálculos individuales
        cesantias, intereses = cls.calcular_cesantias(base_calculo, dias)
        prima = cls.calcular_prima(base_calculo, dias)
        vacaciones = cls.calcular_vacaciones(datos.salario_mensual, dias)

        # Totales
        total_devengado = cesantias + intereses + prima + vacaciones

        # En este caso no hay descuentos específicos en liquidación final
        # (los descuentos de salud, pensión, etc. son durante el contrato)
        descuentos = 0.0
        neto_pagar = total_devengado - descuentos

        return ResultadosPrestaciones(
            dias_laborados=dias,
            cesantias=cesantias,
            intereses_cesantias=intereses,
            prima_servicios=prima,
            vacaciones=vacaciones,
            total_devengado=total_devengado,
            descuentos=descuentos,
            neto_pagar=round(neto_pagar, 2)
        )

    @staticmethod
    def formato_moneda(valor: float) -> str:
        """Formatea valor a moneda colombiana con separadores"""
        return f"${valor:,.2f}"

    @staticmethod
    def formato_fecha(fecha: datetime) -> str:
        """Formatea fecha a formato colombiano DD/MM/YYYY"""
        return fecha.strftime("%d/%m/%Y")

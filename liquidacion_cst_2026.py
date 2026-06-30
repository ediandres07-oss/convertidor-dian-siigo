"""
Módulo de Liquidación de Nómina según CST 2026
Implementa cálculos de cesantías, prima, vacaciones e indemnización
según Art. 64, 65, 186, 249, 306 CST y Ley 50/1990
"""

from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import Dict, Tuple
import json

# Constantes 2026
SMMLV_2026 = 1_500_000  # Salario Mínimo Mensual Legal Vigente 2026
DIAS_COMERCIALES = 360
TASA_INTERES_CESANTIAS = 0.12  # 12% anual

@dataclass
class TiempoLaborado:
    """Calcula años, meses y días de servicio"""
    fecha_ingreso: datetime
    fecha_terminacion: datetime

    def calcular(self) -> Dict:
        """Retorna años, meses, días y días totales"""
        diff = self.fecha_terminacion - self.fecha_ingreso
        dias_totales = diff.days

        # Calcular años, meses, días
        años = dias_totales // 365
        meses = (dias_totales % 365) // 30
        días = (dias_totales % 365) % 30

        return {
            'años': años,
            'meses': meses,
            'días': días,
            'días_totales': dias_totales,
            'descripción': f"{años} años, {meses} meses, {días} días"
        }


class LiquidacionCST:
    """Calcula liquidación según CST colombiano 2026"""

    def __init__(self, salario_mensual: float, fecha_ingreso: str,
                 fecha_terminacion: str, tipo_contrato: str = "indefinido",
                 tipo_terminacion: str = "sin_causa"):
        """
        Args:
            salario_mensual: Salario mensual en COP
            fecha_ingreso: YYYY-MM-DD
            fecha_terminacion: YYYY-MM-DD
            tipo_contrato: indefinido, fijo, obra_labor
            tipo_terminacion: sin_causa, con_causa, renuncia
        """
        self.salario_mensual = float(salario_mensual)
        self.fecha_ingreso = datetime.strptime(fecha_ingreso, "%Y-%m-%d")
        self.fecha_terminacion = datetime.strptime(fecha_terminacion, "%Y-%m-%d")
        self.tipo_contrato = tipo_contrato
        self.tipo_terminacion = tipo_terminacion

        # Calcular tiempo laborado
        self.tiempo = TiempoLaborado(self.fecha_ingreso, self.fecha_terminacion).calcular()
        self.dias_totales = self.tiempo['días_totales']

    def calcular_cesantias(self) -> Dict:
        """Calcula cesantías - Art. 249 CST: 8,33% del salario base"""
        # Cesantías = salario × (días_totales / 360)
        cesantias = self.salario_mensual * (self.dias_totales / DIAS_COMERCIALES)

        # Intereses = cesantías × 12% × (días_totales / 360)
        intereses = cesantias * TASA_INTERES_CESANTIAS * (self.dias_totales / DIAS_COMERCIALES)

        return {
            'cesantias': round(cesantias, 2),
            'intereses_cesantias': round(intereses, 2),
            'total': round(cesantias + intereses, 2)
        }

    def calcular_prima_servicios(self) -> Dict:
        """Calcula prima de servicios - Art. 306 CST: 30 días por año = 8,33%"""
        # Prima = salario × (días_totales / 360)
        prima = self.salario_mensual * (self.dias_totales / DIAS_COMERCIALES)

        return {
            'prima_servicios': round(prima, 2),
            'total': round(prima, 2)
        }

    def calcular_vacaciones(self) -> Dict:
        """Calcula vacaciones - Art. 186 CST: 15 días hábiles por año"""
        # Vacaciones = salario × (días_totales / 720)
        # porque 15 días / 360 = 1/24 = 720 en denominador
        vacaciones = self.salario_mensual * (self.dias_totales / 720)

        return {
            'vacaciones': round(vacaciones, 2),
            'total': round(vacaciones, 2)
        }

    def calcular_indemnizacion_art64(self) -> Dict:
        """
        Calcula indemnización por terminación sin justa causa - Art. 64 CST

        Contrato indefinido:
            - Salario < 10 SMMLV: 30 días primer año + 20 días por año adicional
            - Salario ≥ 10 SMMLV: 20 días primer año + 15 días por año adicional

        Contrato fijo: tiempo faltante para vencimiento
        Contrato obra/labor: tiempo faltante para fin de obra, mínimo 15 días
        """

        # No hay indemnización si fue por justa causa del trabajador
        if self.tipo_terminacion == "con_causa_empleador":
            return {'indemnizacion': 0, 'total': 0, 'notas': 'Sin indemnización - despido por justa causa'}

        if self.tipo_terminacion == "renuncia":
            return {'indemnizacion': 0, 'total': 0, 'notas': 'Sin indemnización - renuncia voluntaria'}

        # Por defecto: terminación sin causa
        if self.tipo_contrato == "indefinido":
            dias_indemnizacion = self._calcular_dias_indemnizacion_indefinido()
        elif self.tipo_contrato == "fijo":
            dias_indemnizacion = self._calcular_dias_indemnizacion_fijo()
        elif self.tipo_contrato == "obra_labor":
            dias_indemnizacion = max(15, self._calcular_dias_indemnizacion_obra())
        else:
            dias_indemnizacion = 0

        indemnizacion = self.salario_mensual * (dias_indemnizacion / 30)

        return {
            'dias_indemnizacion': dias_indemnizacion,
            'indemnizacion': round(indemnizacion, 2),
            'total': round(indemnizacion, 2)
        }

    def _calcular_dias_indemnizacion_indefinido(self) -> int:
        """Calcula días de indemnización para contrato indefinido - Art. 64 CST"""
        años = self.tiempo['años']

        if self.salario_mensual < (10 * SMMLV_2026):
            # Salario < 10 SMMLV: 30 días primer año + 20 días por año adicional
            if años == 0:
                return 30
            else:
                return 30 + (años - 1) * 20 if años > 1 else 30
        else:
            # Salario ≥ 10 SMMLV: 20 días primer año + 15 días por año adicional
            if años == 0:
                return 20
            else:
                return 20 + (años - 1) * 15 if años > 1 else 20

    def _calcular_dias_indemnizacion_fijo(self) -> int:
        """Calcula días para contrato de término fijo - tiempo faltante"""
        return max(0, self.dias_totales)

    def _calcular_dias_indemnizacion_obra(self) -> int:
        """Calcula días para contrato de obra o labor"""
        return self.dias_totales

    def calcular_indemnizacion_moratoria(self, dias_retardo: int = 30) -> Dict:
        """
        Calcula indemnización moratoria - Art. 65 CST
        1 día de salario por cada día de retardo (máximo 24 meses)
        """
        if dias_retardo <= 0:
            return {'indemnizacion_moratoria': 0, 'total': 0}

        # Máximo 24 meses de salario
        dias_retardo_efectivo = min(dias_retardo, 720)  # 24 meses × 30 días
        moratoria = self.salario_mensual * (dias_retardo_efectivo / 30)

        return {
            'dias_retardo': dias_retardo,
            'dias_efectivos': dias_retardo_efectivo,
            'indemnizacion_moratoria': round(moratoria, 2),
            'total': round(moratoria, 2),
            'nota': 'Aplica si no se paga oportunamente la liquidación'
        }

    def calcular_aporte_seguridad_social(self, base_prestaciones: float) -> Dict:
        """
        Calcula aportes a Seguridad Social
        Base = Cesantías + Prima + Vacaciones (NO incluye indemnización)
        """
        # Típicamente: Salud 8,5% + Pensión 12% + Riesgos 0,52-3%
        # Para este cálculo usamos porcentaje promedio
        aporte_salud = base_prestaciones * 0.085
        aporte_pension = base_prestaciones * 0.12
        aporte_riesgos = base_prestaciones * 0.02

        total_aportes = aporte_salud + aporte_pension + aporte_riesgos

        return {
            'base_prestaciones': round(base_prestaciones, 2),
            'aporte_salud': round(aporte_salud, 2),
            'aporte_pension': round(aporte_pension, 2),
            'aporte_riesgos': round(aporte_riesgos, 2),
            'total_aportes': round(total_aportes, 2)
        }

    def calcular_liquidacion_completa(self) -> Dict:
        """Calcula la liquidación completa del empleado"""

        cesantias = self.calcular_cesantias()
        prima = self.calcular_prima_servicios()
        vacaciones = self.calcular_vacaciones()
        indemnizacion = self.calcular_indemnizacion_art64()

        # Base para aportes = prestaciones (sin indemnización)
        base_prestaciones = cesantias['total'] + prima['total'] + vacaciones['total']
        aportes = self.calcular_aporte_seguridad_social(base_prestaciones)

        # Total a pagar = prestaciones + indemnización - aportes
        total_pagable = base_prestaciones + indemnizacion['total'] - aportes['total_aportes']

        return {
            'tiempo_laborado': self.tiempo,
            'cesantias': cesantias,
            'prima_servicios': prima,
            'vacaciones': vacaciones,
            'subtotal_prestaciones': round(base_prestaciones, 2),
            'indemnizacion': indemnizacion,
            'aportes_seguridad_social': aportes,
            'total_pagable': round(total_pagable, 2),
            'detalle': self._generar_detalle_liquidacion()
        }

    def _generar_detalle_liquidacion(self) -> str:
        """Genera detalle formateado de la liquidación"""
        liq = self.calcular_liquidacion_completa()

        detalle = f"""
LIQUIDACIÓN FINAL - CST 2026
{'='*60}

TIEMPO LABORADO
De {self.fecha_ingreso.strftime('%Y-%m-%d')} a {self.fecha_terminacion.strftime('%Y-%m-%d')}
{liq['tiempo_laborado']['descripción']}
Total días: {liq['tiempo_laborado']['días_totales']}

PRESTACIONES LEGALES
{'─'*60}
Concepto                          Valor (COP)
{'─'*60}
Cesantías (Art. 249)              ${liq['cesantias']['cesantias']:>15,.2f}
Intereses Cesantías (Art. 249)    ${liq['cesantias']['intereses_cesantias']:>15,.2f}
Prima de Servicios (Art. 306)     ${liq['prima_servicios']['prima_servicios']:>15,.2f}
Vacaciones (Art. 186)             ${liq['vacaciones']['vacaciones']:>15,.2f}
                                  {'─'*20}
SUBTOTAL PRESTACIONES            ${liq['subtotal_prestaciones']:>15,.2f}

INDEMNIZACIÓN (Art. 64 CST)
{'─'*60}
{self._generar_detalle_indemnizacion()}

APORTES A SEGURIDAD SOCIAL
{'─'*60}
Aporte Salud (8.5%)               ${liq['aportes_seguridad_social']['aporte_salud']:>15,.2f}
Aporte Pensión (12%)              ${liq['aportes_seguridad_social']['aporte_pension']:>15,.2f}
Aporte Riesgos (2%)               ${liq['aportes_seguridad_social']['aporte_riesgos']:>15,.2f}
                                  {'─'*20}
TOTAL APORTES                     ${liq['aportes_seguridad_social']['total_aportes']:>15,.2f}

{'='*60}
TOTAL A PAGAR AL EMPLEADO         ${liq['total_pagable']:>15,.2f}
{'='*60}

Nota: Cantidad de SMMLV 2026: ${SMMLV_2026:,}
Salario mensual: ${self.salario_mensual:,.2f}
"""
        return detalle

    def _generar_detalle_indemnizacion(self) -> str:
        """Genera detalle de indemnización"""
        indem = self.calcular_indemnizacion_art64()

        if indem['indemnizacion'] == 0:
            nota = indem.get('notas', 'No aplica indemnización')
            return f"{nota}\nIndemnización: $0"

        return f"""Días de indemnización: {indem['dias_indemnizacion']}
Indemnización (Art. 64): ${indem['indemnizacion']:,.2f}"""


def validar_datos_liquidacion(datos: Dict) -> Tuple[bool, str]:
    """Valida que los datos sean correctos antes de liquidar"""
    errores = []

    try:
        salario = float(datos.get('salario', 0))
        if salario <= 0:
            errores.append("Salario debe ser mayor a 0")
    except:
        errores.append("Salario no es un número válido")

    try:
        fecha_ingreso = datetime.strptime(datos.get('fecha_ingreso', ''), "%Y-%m-%d")
        fecha_termino = datetime.strptime(datos.get('fecha_terminacion', ''), "%Y-%m-%d")

        if fecha_ingreso >= fecha_termino:
            errores.append("Fecha de ingreso debe ser anterior a fecha de terminación")

        if fecha_termino > datetime.now():
            errores.append("Fecha de terminación no puede ser en el futuro")
    except:
        errores.append("Fechas inválidas. Use formato YYYY-MM-DD")

    if errores:
        return False, " | ".join(errores)

    return True, "OK"

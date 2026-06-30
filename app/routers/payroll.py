"""
Router de Nómina y Liquidación de Prestaciones
FastAPI endpoints para liquidación y cálculos
"""

from fastapi import APIRouter, HTTPException, File, UploadFile
from pydantic import BaseModel, Field
from typing import Optional, Dict
from datetime import datetime
from app.services.liquidacion import CalculadoraLiquidacion
from app.services.pdf import GeneradorPDFLiquidacion
import os

router = APIRouter(prefix="/api", tags=["payroll"])


# ============================================
# MODELOS PYDANTIC
# ============================================
class DatosLiquidacion(BaseModel):
    """Modelo para liquidación individual"""
    nombre: str = Field(..., min_length=1, example="Juan García")
    documento: str = Field(..., min_length=1, example="1234567890")
    cargo: str = Field(..., min_length=1, example="Gerente")
    salario: float = Field(..., gt=0, example=2600000)
    auxilio: float = Field(default=0, ge=0, example=140000)
    fecha_ingreso: str = Field(..., example="2023-01-01")
    fecha_retiro: str = Field(..., example="2024-06-30")
    empresa: Optional[str] = Field(default="EMPRESA S.A.S", example="Mi Empresa")


class RespuestaLiquidacion(BaseModel):
    """Modelo de respuesta de liquidación"""
    dias_laborados: int
    cesantias: float
    intereses_cesantias: float
    prima_servicios: float
    vacaciones: float
    total_devengado: float
    neto_pagar: float
    pdf: Optional[str] = None


# ============================================
# ENDPOINTS
# ============================================

@router.post("/liquidar-individual", response_model=RespuestaLiquidacion)
def liquidar_individual(datos: DatosLiquidacion):
    """
    Liquida prestaciones sociales para un empleado

    Args:
        datos: Información del empleado y fechas

    Returns:
        Cálculos de prestaciones y ruta del PDF
    """
    try:
        # Calcular días
        calculadora = CalculadoraLiquidacion()
        dias = calculadora.calcular_dias(datos.fecha_ingreso, datos.fecha_retiro)

        # Calcular prestaciones
        resultado = calculadora.calcular_prestaciones(
            datos.salario,
            datos.auxilio,
            dias
        )

        # Preparar datos para PDF
        datos_pdf = {
            "nombre": datos.nombre,
            "documento": datos.documento,
            "cargo": datos.cargo,
            "salario": datos.salario,
            "auxilio": datos.auxilio,
            "fecha_ingreso": datos.fecha_ingreso,
            "fecha_retiro": datos.fecha_retiro,
            "empresa": datos.empresa
        }

        # Generar PDF
        generador = GeneradorPDFLiquidacion()
        os.makedirs("outputs", exist_ok=True)
        nombre_pdf = f"outputs/{datos.nombre.replace(' ', '_')}.pdf"
        generador.generar_pdf(datos_pdf, {
            "cesantias": resultado.cesantias,
            "intereses": resultado.intereses_cesantias,
            "prima": resultado.prima_servicios,
            "vacaciones": resultado.vacaciones,
            "total": resultado.neto_pagar
        }, nombre_pdf)

        return RespuestaLiquidacion(
            dias_laborados=resultado.dias_laborados,
            cesantias=resultado.cesantias,
            intereses_cesantias=resultado.intereses_cesantias,
            prima_servicios=resultado.prima_servicios,
            vacaciones=resultado.vacaciones,
            total_devengado=resultado.total_devengado,
            neto_pagar=resultado.neto_pagar,
            pdf=nombre_pdf
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al liquidar: {str(e)}")


@router.post("/calcular-dias")
def calcular_dias(fecha_ingreso: str, fecha_retiro: str):
    """
    Calcula solo los días laborados

    Args:
        fecha_ingreso: Formato YYYY-MM-DD
        fecha_retiro: Formato YYYY-MM-DD

    Returns:
        Número de días calculados
    """
    try:
        calculadora = CalculadoraLiquidacion()
        dias = calculadora.calcular_dias(fecha_ingreso, fecha_retiro)
        return {"dias": dias}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/calcular-prestaciones")
def calcular_prestaciones(salario: float, auxilio: float = 0, dias: int = 30):
    """
    Calcula prestaciones sin generar PDF

    Args:
        salario: Salario mensual
        auxilio: Auxilio de transporte (opcional)
        dias: Días laborados (default: 30)

    Returns:
        Valores calculados
    """
    try:
        if salario <= 0:
            raise ValueError("Salario debe ser mayor a 0")

        calculadora = CalculadoraLiquidacion()
        resultado = calculadora.calcular_prestaciones(salario, auxilio, dias)

        return {
            "dias_laborados": resultado.dias_laborados,
            "cesantias": resultado.cesantias,
            "intereses_cesantias": resultado.intereses_cesantias,
            "prima_servicios": resultado.prima_servicios,
            "vacaciones": resultado.vacaciones,
            "total_devengado": resultado.total_devengado,
            "neto_pagar": resultado.neto_pagar
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/liquidaciones")
def listar_liquidaciones():
    """
    Lista todos los PDFs generados

    Returns:
        Lista de archivos en carpeta outputs
    """
    try:
        if not os.path.exists("outputs"):
            return {"archivos": []}

        archivos = [f for f in os.listdir("outputs") if f.endswith(".pdf")]
        return {"archivos": archivos, "total": len(archivos)}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/salud")
def salud():
    """
    Verifica que el servicio esté activo

    Returns:
        Status del servicio
    """
    return {
        "status": "OK",
        "servicio": "Liquidación de Prestaciones",
        "timestamp": datetime.now().isoformat()
    }

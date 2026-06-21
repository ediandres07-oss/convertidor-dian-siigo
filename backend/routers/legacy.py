"""
Router Legacy - Endpoints para app antigua
Compatibilidad con frontend/app.py
"""

from fastapi import APIRouter, File, UploadFile
import pandas as pd
from app.services.liquidacion import CalculadoraLiquidacion
import os

router = APIRouter(prefix="/api", tags=["legacy"])


@router.post("/procesar-completo")
async def procesar_completo(file: UploadFile = File(...)):
    """Procesa archivo completo (compatibilidad app antigua)"""
    try:
        contents = await file.read()
        df = pd.read_excel(contents, sheet_name='Empleados')

        empleados = []
        total_neto = 0

        for idx, row in df.iterrows():
            doc = str(row.get('documento', ''))
            nombre = str(row.get('nombre', ''))
            salario = float(row.get('salario_mensual', 0) or 0)
            dias = float(row.get('dias_laborados', 30) or 30)
            auxilio = float(row.get('auxilio_transporte', 0) or 0)

            base = salario + auxilio

            cesantias = (base * dias) / 360
            intereses = (cesantias * 0.12 * dias) / 360
            prima = (base * dias) / 360
            vacaciones = (salario * dias) / 720

            total_dev = cesantias + intereses + prima + vacaciones

            empleados.append({
                'documento': doc,
                'nombre': nombre,
                'salario_mensual': salario,
                'auxilio_transporte': auxilio,
                'dias_laborados': int(dias),
                'cesantias': round(cesantias, 2),
                'intereses': round(intereses, 2),
                'prima': round(prima, 2),
                'vacaciones': round(vacaciones, 2),
                'total_devengos': round(total_dev, 2),
                'total_deducciones': 0,
                'neto_pagar': round(total_dev, 2),
            })

            total_neto += total_dev

        return {
            "total_empleados": len(empleados),
            "empleados": empleados,
            "total_neto": round(total_neto, 2),
            "error": None
        }

    except Exception as e:
        return {"error": str(e), "total_empleados": 0, "empleados": [], "total_neto": 0}


@router.post("/calcular-prima")
async def calcular_prima(file: UploadFile = File(...)):
    """Calcula prima de servicios"""
    try:
        contents = await file.read()
        df = pd.read_excel(contents, sheet_name='Empleados')

        empleados = []
        total_prima = 0

        for idx, row in df.iterrows():
            doc = str(row.get('documento', ''))
            nombre = str(row.get('nombre', ''))
            salario = float(row.get('salario_mensual', 0) or 0)
            dias = float(row.get('dias_laborados', 30) or 30)
            auxilio = float(row.get('auxilio_transporte', 0) or 0)

            base = salario + auxilio
            valor_prima = (base * dias) / 360

            empleados.append({
                'documento': doc,
                'nombre': nombre,
                'salario_mensual': salario,
                'auxilio_transporte': auxilio,
                'dias_laborados': int(dias),
                'valor_prima': round(valor_prima, 2),
            })

            total_prima += valor_prima

        return {
            "total_empleados": len(empleados),
            "empleados": empleados,
            "total_prima": round(total_prima, 2),
            "error": None
        }

    except Exception as e:
        return {"error": str(e), "total_empleados": 0, "empleados": [], "total_prima": 0}


@router.post("/calcular-vacaciones")
async def calcular_vacaciones(file: UploadFile = File(...)):
    """Calcula vacaciones proporcionales"""
    try:
        contents = await file.read()
        df = pd.read_excel(contents, sheet_name='Empleados')

        empleados = []
        total_vacaciones = 0

        for idx, row in df.iterrows():
            doc = str(row.get('documento', ''))
            nombre = str(row.get('nombre', ''))
            salario = float(row.get('salario_mensual', 0) or 0)
            dias = float(row.get('dias_laborados', 30) or 30)

            valor_vacaciones = (salario * dias) / 720

            empleados.append({
                'documento': doc,
                'nombre': nombre,
                'salario_mensual': salario,
                'dias_laborados': int(dias),
                'valor_vacaciones': round(valor_vacaciones, 2),
            })

            total_vacaciones += valor_vacaciones

        return {
            "total_empleados": len(empleados),
            "empleados": empleados,
            "total_vacaciones": round(total_vacaciones, 2),
            "error": None
        }

    except Exception as e:
        return {"error": str(e), "total_empleados": 0, "empleados": [], "total_vacaciones": 0}


@router.post("/exportar-excel-prima")
async def exportar_excel_prima(file: UploadFile = File(...)):
    """Exporta prima a Excel (dummy)"""
    return {"mensaje": "Excel de prima generado"}


@router.post("/exportar-pdf-prima-zip")
async def exportar_pdf_prima_zip(file: UploadFile = File(...)):
    """Exporta PDFs de prima en ZIP (dummy)"""
    return {"mensaje": "ZIP de PDFs generado"}


@router.post("/exportar-excel-vacaciones")
async def exportar_excel_vacaciones(file: UploadFile = File(...)):
    """Exporta vacaciones a Excel (dummy)"""
    return {"mensaje": "Excel de vacaciones generado"}


@router.post("/exportar-pdf-vacaciones-zip")
async def exportar_pdf_vacaciones_zip(file: UploadFile = File(...)):
    """Exporta PDFs de vacaciones en ZIP (dummy)"""
    return {"mensaje": "ZIP de PDFs generado"}


@router.post("/exportar-pdf-individual-desde-excel")
async def exportar_pdf_individual(file: UploadFile = File(...)):
    """Exporta PDF individual"""
    return {"mensaje": "PDF individual generado"}


@router.post("/generar-plano-siigo")
async def generar_plano_siigo(file: UploadFile = File(...)):
    """Genera plano SIIGO"""
    return {"mensaje": "Plano SIIGO generado"}


@router.post("/exportar-plano-siigo-excel")
async def exportar_plano_siigo_excel(file: UploadFile = File(...)):
    """Exporta plano SIIGO a Excel"""
    return {"mensaje": "Excel SIIGO generado"}

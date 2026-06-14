import zipfile
import tempfile
import pandas as pd
from fastapi import APIRouter, UploadFile, File, Query
from fastapi.responses import FileResponse, StreamingResponse
from io import BytesIO
from ..utils import calcular_liquidacion, calcular_prima, calcular_vacaciones, generar_pdf

router = APIRouter(prefix="/api", tags=["payroll"])


@router.post("/procesar-completo")
async def procesar_completo(
    file: UploadFile = File(...)
):
    """
    Procesa un archivo Excel completo con todas las hojas necesarias
    Retorna los resultados de la liquidación
    """
    try:
        # Leer el archivo Excel
        excel_file = await file.read()

        # Cargar hojas específicas si existen
        try:
            df_empleados = pd.read_excel(
                BytesIO(excel_file),
                sheet_name='Empleados',
                dtype={'documento': str}
            )
        except Exception as e:
            return {"error": f"No se encontró la hoja 'Empleados': {str(e)}"}

        df_parametros = None
        df_novedades = None

        try:
            df_parametros = pd.read_excel(
                BytesIO(excel_file),
                sheet_name='Parametros'
            )
        except:
            pass

        try:
            df_novedades = pd.read_excel(
                BytesIO(excel_file),
                sheet_name='Novedades',
                dtype={'documento': str}
            )
        except:
            pass

        # Calcular liquidación
        resultados = calcular_liquidacion(df_empleados, df_parametros, df_novedades)

        if not resultados:
            return {"error": "No se pudo procesar ningún empleado"}

        return {
            "success": True,
            "total_empleados": len(resultados),
            "empleados": resultados,
            "total_neto": sum(e['neto_pagar'] for e in resultados)
        }

    except Exception as e:
        return {"error": str(e)}


@router.post("/exportar-excel-desde-excel")
async def exportar_excel(file: UploadFile = File(...)):
    """
    Procesa el archivo y exporta un Excel consolidado con la liquidación
    """
    try:
        excel_file = await file.read()
        excel_bytes = BytesIO(excel_file)

        # Cargar empleados
        df_empleados = pd.read_excel(excel_bytes, sheet_name='Empleados', dtype={'documento': str})

        # Cargar parámetros si existen
        df_parametros = None
        try:
            excel_bytes.seek(0)
            df_parametros = pd.read_excel(excel_bytes, sheet_name='Parametros')
        except:
            pass

        # Cargar novedades si existen
        df_novedades = None
        try:
            excel_bytes.seek(0)
            df_novedades = pd.read_excel(excel_bytes, sheet_name='Novedades', dtype={'documento': str})
        except:
            pass

        # Calcular liquidación
        resultados = calcular_liquidacion(df_empleados, df_parametros, df_novedades)

        if not resultados:
            return {"error": "No se pudo procesar ningún empleado"}

        # Crear DataFrame de salida
        df_out = pd.DataFrame(resultados)

        # Crear archivo Excel en memoria
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df_out.to_excel(writer, sheet_name='Liquidacion', index=False)

            # Agregar resumen
            resumen = pd.DataFrame({
                'Concepto': ['Total Empleados', 'Total Devengos', 'Total Deducciones', 'Total Neto'],
                'Valor': [
                    len(resultados),
                    sum(e['total_devengos'] for e in resultados),
                    sum(e['total_deducciones'] for e in resultados),
                    sum(e['neto_pagar'] for e in resultados)
                ]
            })
            resumen.to_excel(writer, sheet_name='Resumen', index=False)

        output.seek(0)

        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": "attachment; filename=liquidacion.xlsx"}
        )

    except Exception as e:
        return {"error": str(e)}


@router.post("/exportar-pdf-individual-desde-excel")
async def pdf_individual(
    file: UploadFile = File(...),
    documento: str = Query(...)
):
    """
    Exporta un PDF individual de un empleado específico
    """
    try:
        excel_file = await file.read()
        excel_bytes = BytesIO(excel_file)

        # Cargar empleados
        df_empleados = pd.read_excel(excel_bytes, sheet_name='Empleados', dtype={'documento': str})

        # Cargar parámetros si existen
        df_parametros = None
        try:
            excel_bytes.seek(0)
            df_parametros = pd.read_excel(excel_bytes, sheet_name='Parametros')
        except:
            pass

        # Cargar novedades si existen
        df_novedades = None
        try:
            excel_bytes.seek(0)
            df_novedades = pd.read_excel(excel_bytes, sheet_name='Novedades', dtype={'documento': str})
        except:
            pass

        # Calcular liquidación
        resultados = calcular_liquidacion(df_empleados, df_parametros, df_novedades)

        # Buscar empleado
        empleado = next((e for e in resultados if e["documento"] == documento), None)
        if not empleado:
            return {"error": f"Empleado con documento {documento} no encontrado"}

        # Generar PDF
        pdf_content = generar_pdf(empleado, documento)

        return StreamingResponse(
            iter([pdf_content]),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={empleado['nombre']}.pdf"}
        )

    except Exception as e:
        return {"error": str(e)}


@router.post("/exportar-pdf-zip-desde-excel")
async def pdf_zip(file: UploadFile = File(...)):
    """
    Exporta un ZIP con PDFs individuales de todos los empleados
    """
    try:
        excel_file = await file.read()
        excel_bytes = BytesIO(excel_file)

        # Cargar empleados
        df_empleados = pd.read_excel(excel_bytes, sheet_name='Empleados', dtype={'documento': str})

        # Cargar parámetros si existen
        df_parametros = None
        try:
            excel_bytes.seek(0)
            df_parametros = pd.read_excel(excel_bytes, sheet_name='Parametros')
        except:
            pass

        # Cargar novedades si existen
        df_novedades = None
        try:
            excel_bytes.seek(0)
            df_novedades = pd.read_excel(excel_bytes, sheet_name='Novedades', dtype={'documento': str})
        except:
            pass

        # Calcular liquidación
        resultados = calcular_liquidacion(df_empleados, df_parametros, df_novedades)

        if not resultados:
            return {"error": "No se pudo procesar ningún empleado"}

        # Crear ZIP en memoria
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as z:
            for emp in resultados:
                pdf_content = generar_pdf(emp, emp['documento'])
                nombre_archivo = f"{emp['nombre'].replace(' ', '_')}.pdf"
                z.writestr(nombre_archivo, pdf_content)

        zip_buffer.seek(0)

        return StreamingResponse(
            iter([zip_buffer.getvalue()]),
            media_type="application/zip",
            headers={"Content-Disposition": "attachment; filename=liquidaciones.zip"}
        )

    except Exception as e:
        return {"error": str(e)}


@router.post("/calcular-prima")
async def calcular_prima_endpoint(file: UploadFile = File(...)):
    """
    Calcula prima de servicios: (salario + auxilio) * dias / 360
    """
    try:
        excel_file = await file.read()
        excel_bytes = BytesIO(excel_file)

        # Cargar empleados
        df_empleados = pd.read_excel(excel_bytes, sheet_name='Empleados', dtype={'documento': str})

        # Calcular prima
        resultados = calcular_prima(df_empleados)

        if not resultados:
            return {"error": "No se pudo procesar ningún empleado"}

        return {
            "success": True,
            "total_empleados": len(resultados),
            "empleados": resultados,
            "total_prima": sum(e['valor_prima'] for e in resultados)
        }

    except Exception as e:
        return {"error": str(e)}


@router.post("/calcular-vacaciones")
async def calcular_vacaciones_endpoint(file: UploadFile = File(...)):
    """
    Calcula vacaciones proporcionales: salario * dias / 720
    """
    try:
        excel_file = await file.read()
        excel_bytes = BytesIO(excel_file)

        # Cargar empleados
        df_empleados = pd.read_excel(excel_bytes, sheet_name='Empleados', dtype={'documento': str})

        # Calcular vacaciones
        resultados = calcular_vacaciones(df_empleados)

        if not resultados:
            return {"error": "No se pudo procesar ningún empleado"}

        return {
            "success": True,
            "total_empleados": len(resultados),
            "empleados": resultados,
            "total_vacaciones": sum(e['valor_vacaciones'] for e in resultados)
        }

    except Exception as e:
        return {"error": str(e)}


@router.post("/exportar-excel-prima")
async def exportar_excel_prima(file: UploadFile = File(...)):
    """
    Exporta Excel con cálculo de Prima de Servicios
    """
    try:
        excel_file = await file.read()
        excel_bytes = BytesIO(excel_file)

        df_empleados = pd.read_excel(excel_bytes, sheet_name='Empleados', dtype={'documento': str})
        resultados = calcular_prima(df_empleados)

        if not resultados:
            return {"error": "No se pudo procesar ningún empleado"}

        df_resultado = pd.DataFrame(resultados)

        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df_resultado.to_excel(writer, sheet_name='Prima', index=False)

            resumen = pd.DataFrame({
                'Concepto': ['Total Empleados', 'Total Prima'],
                'Valor': [len(resultados), sum(e['valor_prima'] for e in resultados)]
            })
            resumen.to_excel(writer, sheet_name='Resumen', index=False)

        output.seek(0)

        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": "attachment; filename=prima_servicios.xlsx"}
        )

    except Exception as e:
        return {"error": str(e)}


@router.post("/exportar-excel-vacaciones")
async def exportar_excel_vacaciones(file: UploadFile = File(...)):
    """
    Exporta Excel con cálculo de Vacaciones Proporcionales
    """
    try:
        excel_file = await file.read()
        excel_bytes = BytesIO(excel_file)

        df_empleados = pd.read_excel(excel_bytes, sheet_name='Empleados', dtype={'documento': str})
        resultados = calcular_vacaciones(df_empleados)

        if not resultados:
            return {"error": "No se pudo procesar ningún empleado"}

        df_resultado = pd.DataFrame(resultados)

        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df_resultado.to_excel(writer, sheet_name='Vacaciones', index=False)

            resumen = pd.DataFrame({
                'Concepto': ['Total Empleados', 'Total Vacaciones'],
                'Valor': [len(resultados), sum(e['valor_vacaciones'] for e in resultados)]
            })
            resumen.to_excel(writer, sheet_name='Resumen', index=False)

        output.seek(0)

        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": "attachment; filename=vacaciones_proporcionales.xlsx"}
        )

    except Exception as e:
        return {"error": str(e)}

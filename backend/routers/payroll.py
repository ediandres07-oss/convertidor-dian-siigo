import zipfile
import tempfile
import pandas as pd
from fastapi import APIRouter, UploadFile, File, Query
from fastapi.responses import FileResponse, StreamingResponse
from io import BytesIO
from ..utils import calcular_liquidacion, calcular_prima, calcular_vacaciones, generar_pdf, generar_pdf_prima, generar_pdf_vacaciones

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


@router.post("/generar-plano-siigo")
async def generar_plano_siigo(file: UploadFile = File(...)):
    """
    Genera archivo plano compatible con SIIGO
    """
    try:
        from ..utils import calcular_liquidacion
        import io as io_module

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

        # Calcular liquidación completa
        resultados = calcular_liquidacion(df_empleados, df_parametros, df_novedades)

        if not resultados:
            return {"error": "No se pudo procesar ningún empleado"}

        # Generar asientos contables
        asientos = []

        cuentas = {
            'salarios': '5105',
            'cesantias': '510530',
            'intereses_cesantias': '510533',
            'prima': '510536',
            'vacaciones': '510539',
            'salud': '237005',
            'pension': '238030',
            'fondo_solidaridad': '238095',
            'retencion_fuente': '236540',
            'bancos': '111005',
        }

        centro_costos = '01'

        for emp in resultados:
            documento = emp['documento']
            nombre = emp['nombre']

            # DEVENGOS (Débito)
            if emp.get('salario_prorr', 0) > 0:
                asientos.append({
                    'tipo': 'NOMINA',
                    'cuenta': cuentas['salarios'],
                    'documento': documento,
                    'nombre': nombre,
                    'valor': round(emp['salario_prorr'], 2),
                    'debito_credito': 'D',
                    'centro_costos': centro_costos
                })

            if emp.get('cesantias', 0) > 0:
                asientos.append({
                    'tipo': 'NOMINA',
                    'cuenta': cuentas['cesantias'],
                    'documento': documento,
                    'nombre': nombre,
                    'valor': round(emp['cesantias'], 2),
                    'debito_credito': 'D',
                    'centro_costos': centro_costos
                })

            if emp.get('intereses_cesantias', 0) > 0:
                asientos.append({
                    'tipo': 'NOMINA',
                    'cuenta': cuentas['intereses_cesantias'],
                    'documento': documento,
                    'nombre': nombre,
                    'valor': round(emp['intereses_cesantias'], 2),
                    'debito_credito': 'D',
                    'centro_costos': centro_costos
                })

            if emp.get('prima', 0) > 0:
                asientos.append({
                    'tipo': 'NOMINA',
                    'cuenta': cuentas['prima'],
                    'documento': documento,
                    'nombre': nombre,
                    'valor': round(emp['prima'], 2),
                    'debito_credito': 'D',
                    'centro_costos': centro_costos
                })

            if emp.get('vacaciones', 0) > 0:
                asientos.append({
                    'tipo': 'NOMINA',
                    'cuenta': cuentas['vacaciones'],
                    'documento': documento,
                    'nombre': nombre,
                    'valor': round(emp['vacaciones'], 2),
                    'debito_credito': 'D',
                    'centro_costos': centro_costos
                })

            # DEDUCCIONES (Crédito)
            if emp.get('salud', 0) > 0:
                asientos.append({
                    'tipo': 'NOMINA',
                    'cuenta': cuentas['salud'],
                    'documento': documento,
                    'nombre': nombre,
                    'valor': round(emp['salud'], 2),
                    'debito_credito': 'C',
                    'centro_costos': centro_costos
                })

            if emp.get('pension', 0) > 0:
                asientos.append({
                    'tipo': 'NOMINA',
                    'cuenta': cuentas['pension'],
                    'documento': documento,
                    'nombre': nombre,
                    'valor': round(emp['pension'], 2),
                    'debito_credito': 'C',
                    'centro_costos': centro_costos
                })

            if emp.get('fondo_solidaridad', 0) > 0:
                asientos.append({
                    'tipo': 'NOMINA',
                    'cuenta': cuentas['fondo_solidaridad'],
                    'documento': documento,
                    'nombre': nombre,
                    'valor': round(emp['fondo_solidaridad'], 2),
                    'debito_credito': 'C',
                    'centro_costos': centro_costos
                })

            if emp.get('retencion', 0) > 0:
                asientos.append({
                    'tipo': 'NOMINA',
                    'cuenta': cuentas['retencion_fuente'],
                    'documento': documento,
                    'nombre': nombre,
                    'valor': round(emp['retencion'], 2),
                    'debito_credito': 'C',
                    'centro_costos': centro_costos
                })

            # NETO A PAGAR
            if emp.get('neto_pagar', 0) > 0:
                asientos.append({
                    'tipo': 'NOMINA',
                    'cuenta': cuentas['bancos'],
                    'documento': documento,
                    'nombre': nombre,
                    'valor': round(emp['neto_pagar'], 2),
                    'debito_credito': 'C',
                    'centro_costos': centro_costos
                })

        # Generar archivo plano
        plano_content = io_module.StringIO()
        for asiento in asientos:
            linea = (
                f"{asiento['tipo']};"
                f"{asiento['cuenta']};"
                f"{asiento['documento']};"
                f"{asiento['nombre']};"
                f"{asiento['valor']:.2f};"
                f"{asiento['debito_credito']};"
                f"{asiento['centro_costos']}\n"
            )
            plano_content.write(linea)

        plano_bytes = plano_content.getvalue().encode('utf-8')

        return StreamingResponse(
            iter([plano_bytes]),
            media_type="text/plain",
            headers={"Content-Disposition": "attachment; filename=plano_siigo.txt"}
        )

    except Exception as e:
        return {"error": str(e)}


@router.post("/exportar-pdf-prima-zip")
async def exportar_pdf_prima_zip(file: UploadFile = File(...)):
    """
    Exporta un ZIP con PDFs individuales de Prima de Servicios
    """
    try:
        excel_file = await file.read()
        excel_bytes = BytesIO(excel_file)

        df_empleados = pd.read_excel(excel_bytes, sheet_name='Empleados', dtype={'documento': str})
        resultados = calcular_prima(df_empleados)

        if not resultados:
            return {"error": "No se pudo procesar ningún empleado"}

        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as z:
            for emp in resultados:
                pdf_content = generar_pdf_prima(emp)
                nombre_archivo = f"Prima_{emp['nombre'].replace(' ', '_')}.pdf"
                z.writestr(nombre_archivo, pdf_content)

        zip_buffer.seek(0)

        return StreamingResponse(
            iter([zip_buffer.getvalue()]),
            media_type="application/zip",
            headers={"Content-Disposition": "attachment; filename=prima_servicios.zip"}
        )

    except Exception as e:
        return {"error": str(e)}


@router.post("/exportar-pdf-vacaciones-zip")
async def exportar_pdf_vacaciones_zip(file: UploadFile = File(...)):
    """
    Exporta un ZIP con PDFs individuales de Vacaciones
    """
    try:
        excel_file = await file.read()
        excel_bytes = BytesIO(excel_file)

        df_empleados = pd.read_excel(excel_bytes, sheet_name='Empleados', dtype={'documento': str})
        resultados = calcular_vacaciones(df_empleados)

        if not resultados:
            return {"error": "No se pudo procesar ningún empleado"}

        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as z:
            for emp in resultados:
                pdf_content = generar_pdf_vacaciones(emp)
                nombre_archivo = f"Vacaciones_{emp['nombre'].replace(' ', '_')}.pdf"
                z.writestr(nombre_archivo, pdf_content)

        zip_buffer.seek(0)

        return StreamingResponse(
            iter([zip_buffer.getvalue()]),
            media_type="application/zip",
            headers={"Content-Disposition": "attachment; filename=vacaciones_proporcionales.zip"}
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

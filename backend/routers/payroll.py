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
    Genera archivo plano SIIGO con mapeo exacto del modelo oficial de 27 columnas
    """
    try:
        # CAMBIO: Importar mapeo SIIGO
        import sys
        import os
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        from mapeo_nomina_a_siigo import convertir_nomina_a_siigo, exportar_a_siigo_txt
        import io as io_module
        from datetime import datetime

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
        from ..utils import calcular_liquidacion
        resultados = calcular_liquidacion(df_empleados, df_parametros, df_novedades)

        if not resultados:
            return {"error": "No se pudo procesar ningún empleado"}

        # CAMBIO: Usar mapeo para convertir a formato SIIGO exacto
        fecha_hoy = datetime.now().strftime("%d/%m/%Y")
        df_siigo = convertir_nomina_a_siigo(resultados, fecha_comprobante=fecha_hoy)

        # Generar archivo plano TXT
        plano_content = io_module.StringIO()
        for idx, row in df_siigo.iterrows():
            # Obtener valores
            tipo = row['Tipo de comprobante']
            cuenta = row['Código cuenta contable']
            documento = row['Identificación tercero']
            descripcion = row['Descripción']
            debito = row['Débito']
            credito = row['Crédito']

            # Determinar valor y naturaleza
            if debito and str(debito).strip():
                valor = debito
                naturaleza = 'D'
            else:
                valor = credito
                naturaleza = 'C'

            # Escribir línea en formato SIIGO
            linea = f"{tipo};{cuenta};{documento};{descripcion};{valor};{naturaleza}\n"
            plano_content.write(linea)

        plano_bytes = plano_content.getvalue().encode('utf-8')

        return StreamingResponse(
            iter([plano_bytes]),
            media_type="text/plain",
            headers={"Content-Disposition": "attachment; filename=plano_siigo.txt"}
        )

    except Exception as e:
        return {"error": str(e)}


@router.post("/convertir-plano-txt-a-excel")
async def convertir_plano_txt_a_excel(file: UploadFile = File(...)):
    """
    Convierte archivo plano TXT de SIIGO a Excel con múltiples hojas de validación
    """
    try:
        # Leer archivo TXT
        contenido = await file.read()
        lineas = contenido.decode('utf-8').strip().split('\n')

        # Procesar líneas
        columnas = ['tipo', 'cuenta', 'documento', 'nombre', 'valor', 'naturaleza']
        datos = []

        for linea in lineas:
            if linea.strip():
                campos = linea.split(';')
                if len(campos) >= 6:
                    datos.append({
                        'tipo': campos[0],
                        'cuenta': campos[1],
                        'documento': campos[2],
                        'nombre': campos[3],
                        'valor': float(campos[4]),
                        'naturaleza': campos[5]
                    })

        if not datos:
            return {"error": "No se encontraron datos válidos en el archivo"}

        df = pd.DataFrame(datos)

        # Validación contable
        debitos = df[df['naturaleza'] == 'D']['valor'].sum()
        creditos = df[df['naturaleza'] == 'C']['valor'].sum()
        diferencia = abs(debitos - creditos)
        balanceado = diferencia < 0.01

        # Descripciones de cuentas
        cuentas_desc = {
            '5105': 'Salarios',
            '510530': 'Cesantías',
            '510533': 'Intereses Cesantías',
            '510536': 'Prima de Servicios',
            '510539': 'Vacaciones',
            '237005': 'Salud',
            '238030': 'Pensión',
            '238095': 'Fondo Solidaridad',
            '236540': 'Retención en la Fuente',
            '111005': 'Bancos'
        }

        df['descripcion'] = df['cuenta'].map(cuentas_desc).fillna('Otros')

        # Resumen por cuenta
        resumen_cuenta = df.groupby(['cuenta', 'descripcion', 'naturaleza'])['valor'].sum().reset_index()
        resumen_cuenta.columns = ['Cuenta', 'Descripción', 'Naturaleza', 'Valor']

        # Resumen por empleado
        resumen_empleado = df.groupby(['documento', 'nombre'])['valor'].sum().reset_index()
        resumen_empleado.columns = ['Documento', 'Nombre', 'Total']

        # Validación
        validacion = pd.DataFrame([{
            'Total Débitos': round(debitos, 2),
            'Total Créditos': round(creditos, 2),
            'Diferencia': round(diferencia, 2),
            'Estado': 'BALANCEADO' if balanceado else 'DESBALANCEADO'
        }])

        # Exportar
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df[['tipo', 'cuenta', 'descripcion', 'documento', 'nombre', 'valor', 'naturaleza']].to_excel(
                writer, sheet_name='Plano', index=False
            )
            validacion.to_excel(writer, sheet_name='Validacion', index=False)
            resumen_cuenta.to_excel(writer, sheet_name='Por Cuenta', index=False)
            resumen_empleado.to_excel(writer, sheet_name='Por Empleado', index=False)

        output.seek(0)

        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": "attachment; filename=plano_siigo_convertido.xlsx"}
        )

    except Exception as e:
        return {"error": str(e)}


@router.post("/exportar-plano-siigo-excel")
async def exportar_plano_siigo_excel(file: UploadFile = File(...)):
    """
    Genera archivo Excel con el plano SIIGO
    """
    try:
        from ..utils import calcular_liquidacion

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
                    'TIPO': 'NOMINA',
                    'CUENTA': cuentas['salarios'],
                    'DOCUMENTO': documento,
                    'NOMBRE': nombre,
                    'VALOR': round(emp['salario_prorr'], 2),
                    'DEBITO_CREDITO': 'D',
                    'CENTRO_COSTOS': centro_costos,
                    'CONCEPTO': 'SALARIO'
                })

            if emp.get('cesantias', 0) > 0:
                asientos.append({
                    'TIPO': 'NOMINA',
                    'CUENTA': cuentas['cesantias'],
                    'DOCUMENTO': documento,
                    'NOMBRE': nombre,
                    'VALOR': round(emp['cesantias'], 2),
                    'DEBITO_CREDITO': 'D',
                    'CENTRO_COSTOS': centro_costos,
                    'CONCEPTO': 'CESANTIAS'
                })

            if emp.get('intereses_cesantias', 0) > 0:
                asientos.append({
                    'TIPO': 'NOMINA',
                    'CUENTA': cuentas['intereses_cesantias'],
                    'DOCUMENTO': documento,
                    'NOMBRE': nombre,
                    'VALOR': round(emp['intereses_cesantias'], 2),
                    'DEBITO_CREDITO': 'D',
                    'CENTRO_COSTOS': centro_costos,
                    'CONCEPTO': 'INTERESES CESANTIAS'
                })

            if emp.get('prima', 0) > 0:
                asientos.append({
                    'TIPO': 'NOMINA',
                    'CUENTA': cuentas['prima'],
                    'DOCUMENTO': documento,
                    'NOMBRE': nombre,
                    'VALOR': round(emp['prima'], 2),
                    'DEBITO_CREDITO': 'D',
                    'CENTRO_COSTOS': centro_costos,
                    'CONCEPTO': 'PRIMA SERVICIOS'
                })

            if emp.get('vacaciones', 0) > 0:
                asientos.append({
                    'TIPO': 'NOMINA',
                    'CUENTA': cuentas['vacaciones'],
                    'DOCUMENTO': documento,
                    'NOMBRE': nombre,
                    'VALOR': round(emp['vacaciones'], 2),
                    'DEBITO_CREDITO': 'D',
                    'CENTRO_COSTOS': centro_costos,
                    'CONCEPTO': 'VACACIONES'
                })

            # DEDUCCIONES (Crédito)
            if emp.get('salud', 0) > 0:
                asientos.append({
                    'TIPO': 'NOMINA',
                    'CUENTA': cuentas['salud'],
                    'DOCUMENTO': documento,
                    'NOMBRE': nombre,
                    'VALOR': round(emp['salud'], 2),
                    'DEBITO_CREDITO': 'C',
                    'CENTRO_COSTOS': centro_costos,
                    'CONCEPTO': 'APORTE SALUD'
                })

            if emp.get('pension', 0) > 0:
                asientos.append({
                    'TIPO': 'NOMINA',
                    'CUENTA': cuentas['pension'],
                    'DOCUMENTO': documento,
                    'NOMBRE': nombre,
                    'VALOR': round(emp['pension'], 2),
                    'DEBITO_CREDITO': 'C',
                    'CENTRO_COSTOS': centro_costos,
                    'CONCEPTO': 'APORTE PENSION'
                })

            if emp.get('fondo_solidaridad', 0) > 0:
                asientos.append({
                    'TIPO': 'NOMINA',
                    'CUENTA': cuentas['fondo_solidaridad'],
                    'DOCUMENTO': documento,
                    'NOMBRE': nombre,
                    'VALOR': round(emp['fondo_solidaridad'], 2),
                    'DEBITO_CREDITO': 'C',
                    'CENTRO_COSTOS': centro_costos,
                    'CONCEPTO': 'FONDO SOLIDARIDAD'
                })

            if emp.get('retencion', 0) > 0:
                asientos.append({
                    'TIPO': 'NOMINA',
                    'CUENTA': cuentas['retencion_fuente'],
                    'DOCUMENTO': documento,
                    'NOMBRE': nombre,
                    'VALOR': round(emp['retencion'], 2),
                    'DEBITO_CREDITO': 'C',
                    'CENTRO_COSTOS': centro_costos,
                    'CONCEPTO': 'RETENCION FUENTE'
                })

            # NETO A PAGAR
            if emp.get('neto_pagar', 0) > 0:
                asientos.append({
                    'TIPO': 'NOMINA',
                    'CUENTA': cuentas['bancos'],
                    'DOCUMENTO': documento,
                    'NOMBRE': nombre,
                    'VALOR': round(emp['neto_pagar'], 2),
                    'DEBITO_CREDITO': 'C',
                    'CENTRO_COSTOS': centro_costos,
                    'CONCEPTO': 'NETO A PAGAR'
                })

        # Crear DataFrame
        df_asientos = pd.DataFrame(asientos)

        # Calcular balance
        debitos = df_asientos[df_asientos['DEBITO_CREDITO'] == 'D']['VALOR'].sum()
        creditos = df_asientos[df_asientos['DEBITO_CREDITO'] == 'C']['VALOR'].sum()

        # Exportar a Excel con múltiples hojas
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            # Hoja 1: Asientos
            df_asientos.to_excel(writer, sheet_name='Plano SIIGO', index=False)

            # Hoja 2: Resumen
            resumen = pd.DataFrame({
                'CONCEPTO': ['Total Débitos', 'Total Créditos', 'Diferencia', 'ESTADO'],
                'VALOR': [debitos, creditos, abs(debitos - creditos), 'BALANCEADO' if abs(debitos - creditos) < 0.01 else 'DESBALANCEADO']
            })
            resumen.to_excel(writer, sheet_name='Resumen', index=False)

            # Hoja 3: Por Cuenta
            por_cuenta = df_asientos.groupby('CUENTA')['VALOR'].sum().reset_index()
            por_cuenta.columns = ['CUENTA', 'TOTAL']
            por_cuenta = por_cuenta.sort_values('TOTAL', ascending=False)
            por_cuenta.to_excel(writer, sheet_name='Por Cuenta', index=False)

            # Hoja 4: Instrucciones
            instrucciones = pd.DataFrame({
                'INSTRUCCIONES PARA CARGAR EN SIIGO': [
                    '1. Abre SIIGO',
                    '2. Ve a: Contabilidad → Comprobantes → Importar',
                    '3. Selecciona la hoja "Plano SIIGO"',
                    '4. Los campos son:',
                    '   - TIPO: Tipo de movimiento (NOMINA)',
                    '   - CUENTA: Número de cuenta contable',
                    '   - DOCUMENTO: Cédula del empleado',
                    '   - NOMBRE: Nombre del empleado',
                    '   - VALOR: Valor del movimiento',
                    '   - DEBITO_CREDITO: D (Débito) o C (Crédito)',
                    '   - CENTRO_COSTOS: Centro de costos',
                    '5. Valida los asientos',
                    '6. Graba el comprobante'
                ]
            })
            instrucciones.to_excel(writer, sheet_name='Instrucciones', index=False, header=False)

        output.seek(0)

        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": "attachment; filename=plano_siigo.xlsx"}
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

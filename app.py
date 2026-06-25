from flask import Flask, request, send_file, render_template, jsonify
import io
import json
import traceback
import zipfile
from datetime import datetime
from converter import process_file, process_liquidacion_iva, _cargar_nomina_balance, convert_nomina, generate_balance_prueba, generate_liquidaciones
from siigo_integration import subir_planos_a_siigo
from dian_integration import descargar_reporte_dian
from liquidacion_pdf_premium import generar_liquidacion_pdf_premium
from retencion import calcular_retencion, generar_reporte_retenciones
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 20 * 1024 * 1024  # 20 MB máximo

@app.route('/')
def index():
    return render_template('app.html')

@app.route('/legacy')
def legacy_index():
    return render_template('index.html')

@app.route('/api/convert', methods=['POST'])
def convert():
    if 'file' not in request.files:
        return {'error': 'No se proporcionó ningún archivo'}, 400
        
    file = request.files['file']
    if file.filename == '':
        return {'error': 'Archivo no seleccionado'}, 400
        
    try:
        consec_compras = int(request.form.get('consec_compras', 371))
        consec_nc = int(request.form.get('consec_nc', 271))
        consec_gastos = int(request.form.get('consec_gastos', 798))
        consec_ventas    = int(request.form.get('consec_ventas', 1))
        consec_nc_ventas = int(request.form.get('consec_nc_ventas', 1))
    except ValueError:
        return {'error': 'Los consecutivos deben ser números válidos'}, 400

    try:
        # Leer el archivo en memoria
        input_stream = io.BytesIO(file.read())
        file_data = input_stream.getvalue()

        # Procesar el archivo
        planos_stream = process_file(
            io.BytesIO(file_data),
            consec_compras=consec_compras,
            consec_nc=consec_nc,
            consec_gastos=consec_gastos,
            consec_ventas=consec_ventas,
            consec_nc_ventas=consec_nc_ventas
        )

        # Generar retenciones desde planos
        planos_stream.seek(0)
        retenciones_stream = generar_reporte_retenciones_excel({
            'compras': [],
            'ventas': [],
            'gastos': []
        })

        # Crear ZIP con planos + retenciones
        original_name = file.filename.rsplit('.', 1)[0]
        zip_buffer = io.BytesIO()

        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
            # Agregar planos
            planos_stream.seek(0)
            zf.writestr(f'PLANOS_{original_name}.xlsx', planos_stream.read())

            # Agregar retenciones
            retenciones_stream.seek(0)
            zf.writestr('RETENCIONES.xlsx', retenciones_stream.read())

        zip_buffer.seek(0)
        download_name = f"CONVERSION_{original_name}.zip"

        return send_file(
            zip_buffer,
            as_attachment=True,
            download_name=download_name,
            mimetype="application/zip"
        )
    except Exception as e:
        traceback.print_exc()
        return {'error': f'Error procesando el archivo: {str(e)}'}, 500

@app.route('/api/liquidar-iva', methods=['POST'])
def liquidar_iva():
    if 'file' not in request.files:
        return {'error': 'No se proporcionó ningún archivo'}, 400

    file = request.files['file']
    if file.filename == '':
        return {'error': 'Archivo no seleccionado'}, 400

    try:
        input_stream = io.BytesIO(file.read())
        output_stream = process_liquidacion_iva(input_stream)

        original_name = file.filename.rsplit('.', 1)[0]
        download_name = f"LIQUIDACION_IVA_{original_name}.xlsx"

        return send_file(
            output_stream,
            as_attachment=True,
            download_name=download_name,
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    except Exception as e:
        traceback.print_exc()
        return {'error': f'Error generando liquidación: {str(e)}'}, 500


@app.route('/api/nomina', methods=['POST'])
def nomina():
    if 'balance' not in request.files:
        return {'error': 'Se requiere el archivo de Balance de prueba por tercero'}, 400

    balance_file = request.files['balance']
    if balance_file.filename == '':
        return {'error': 'Archivo de balance no seleccionado'}, 400

    try:
        consec_nomina = int(request.form.get('consec_nomina', 1))
    except ValueError:
        return {'error': 'El consecutivo debe ser un número válido'}, 400

    try:
        import tempfile, os
        # Guardar balance en archivo temporal (openpyxl necesita path real para read_only)
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp:
            balance_file.save(tmp)
            tmp_path = tmp.name

        from openpyxl import Workbook
        empleados = _cargar_nomina_balance(tmp_path)
        os.unlink(tmp_path)

        wb_dst = Workbook()
        if wb_dst.active:
            wb_dst.remove(wb_dst.active)

        convert_nomina(empleados, wb_dst, consec_nomina)

        output_stream = io.BytesIO()
        wb_dst.save(output_stream)
        output_stream.seek(0)

        return send_file(
            output_stream,
            as_attachment=True,
            download_name='PLANO_NOMINA.xlsx',
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    except Exception as e:
        traceback.print_exc()
        return {'error': f'Error generando nómina: {str(e)}'}, 500


@app.route('/api/balance', methods=['POST'])
def balance():
    if 'file' not in request.files:
        return {'error': 'No se proporcionó ningún archivo'}, 400
    file = request.files['file']
    if file.filename == '':
        return {'error': 'Archivo no seleccionado'}, 400
    try:
        input_stream = io.BytesIO(file.read())
        output_stream = generate_balance_prueba(input_stream)
        original_name = file.filename.rsplit('.', 1)[0]
        download_name = f"BALANCE_TERCERO_{original_name}.xlsx"
        return send_file(
            output_stream,
            as_attachment=True,
            download_name=download_name,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    except Exception as e:
        traceback.print_exc()
        return {'error': f'Error generando balance: {str(e)}'}, 500


@app.route('/api/liquidaciones', methods=['POST'])
def liquidaciones():
    try:
        data = request.get_json()
        if not data or 'empleados' not in data:
            return {'error': 'No se proporcionaron datos de empleados'}, 400

        empleados = data['empleados']
        # Validar que al menos un empleado tenga nombre
        if not any(emp.get('nombre', '').strip() for emp in empleados):
            return {'error': 'Todos los empleados deben tener un nombre'}, 400

        # Generar Excel
        excel_stream = generate_liquidaciones(empleados)

        # Crear ZIP con Excel + PDFs de liquidación
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # Agregar Excel
            excel_stream.seek(0)
            zip_file.writestr('LIQUIDACIONES.xlsx', excel_stream.read())

            # Generar PDF para cada empleado (versión premium)
            for emp in empleados:
                nombre = emp.get('nombre', 'Sin_nombre').replace(' ', '_')
                try:
                    # Estructura de datos para PDF
                    datos_emp = {
                        'nombre': emp.get('nombre', ''),
                        'cedula': emp.get('cedula', ''),
                        'cargo': emp.get('cargo', ''),
                        'departamento': emp.get('departamento', ''),
                        'salario': float(emp.get('salario', 0)),
                        'fecha_inicio': emp.get('fecha_inicio', ''),
                        'fecha_retiro': emp.get('fecha_retiro', ''),
                        'dias_trabajados': emp.get('dias_trabajados', ''),
                        'tipo_contrato': emp.get('tipo_contrato', 'Indefinido'),
                        'metodo_pago': emp.get('metodo_pago', 'Transferencia Bancaria'),
                        'banco': emp.get('banco', ''),
                        'tipo_cuenta': emp.get('tipo_cuenta', ''),
                        'numero_cuenta': emp.get('numero_cuenta', ''),
                    }
                    datos_liq = {
                        'cesantias': float(emp.get('cesantias', 0)),
                        'dias_cesantias': emp.get('dias_cesantias', ''),
                        'vr_diario_cesantias': emp.get('vr_diario_cesantias', ''),
                        'prima': float(emp.get('prima', 0)),
                        'dias_prima': emp.get('dias_prima', ''),
                        'vr_diario_prima': emp.get('vr_diario_prima', ''),
                        'vacaciones': float(emp.get('vacaciones', 0)),
                        'dias_vacaciones': emp.get('dias_vacaciones', ''),
                        'vr_diario_vacaciones': emp.get('vr_diario_vacaciones', ''),
                        'intereses_cesantias': float(emp.get('intereses', 0)),
                        'aporte_pension': -float(emp.get('pension', 0)),
                        'aporte_salud': -float(emp.get('salud', 0)),
                        'aporte_solidaridad': -float(emp.get('solidaridad', 0)),
                        'embargos': -float(emp.get('embargos', 0)),
                        'otros_descuentos': -float(emp.get('otros_descuentos', 0))
                    }

                    # Datos de empresa
                    empresa_data = {
                        'nombre': emp.get('empresa', 'EMPRESA GIMÉNEZ ASOCIADOS'),
                        'nit': emp.get('empresa_nit', ''),
                        'representante': emp.get('representante_empresa', '')
                    }

                    # Logo (si existe)
                    logo_path = emp.get('logo_path', None)

                    pdf_stream = generar_liquidacion_pdf_premium(datos_emp, datos_liq, logo_path, empresa_data)
                    pdf_stream.seek(0)
                    zip_file.writestr(f'Liquidacion_{nombre}.pdf', pdf_stream.read())
                except Exception as e:
                    print(f"⚠️  Error generando PDF para {nombre}: {str(e)}")

        zip_buffer.seek(0)
        return send_file(
            zip_buffer,
            as_attachment=True,
            download_name=f'LIQUIDACIONES_{datetime.now().strftime("%Y%m%d")}.zip',
            mimetype='application/zip'
        )
    except Exception as e:
        traceback.print_exc()
        return {'error': f'Error generando liquidaciones: {str(e)}'}, 500


@app.route('/api/download-dian', methods=['POST'])
def download_dian():
    """Descarga reporte DIAN automáticamente."""
    try:
        usuario = request.json.get('usuario', '')
        password = request.json.get('password', '')

        if not usuario or not password:
            return {'error': 'Credenciales DIAN requeridas'}, 400

        # Intentar descargar
        archivo = descargar_reporte_dian(usuario, password)

        if not archivo:
            return {
                'error': 'No se pudo descargar automáticamente.',
                'instrucciones': [
                    '1. Ve a https://catalogo-vpfe.dian.gov.co/User/PersonLogin',
                    '2. Ingresa tus credenciales',
                    '3. Menú: "Consulta de Documentos" → "Buscar Documento"',
                    '4. Filtra por período (ej: 2025)',
                    '5. Clickea "Descargar Reporte" (Excel)',
                    '6. Sube el archivo aquí en "Selecciona archivo"'
                ]
            }, 400

        return send_file(
            archivo,
            as_attachment=True,
            download_name=f'Reporte_DIAN_{datetime.now().strftime("%Y%m%d")}.xlsx',
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    except Exception as e:
        traceback.print_exc()
        return {'error': f'Error descargando: {str(e)}'}, 500


@app.route('/api/upload-siigo', methods=['POST'])
def upload_siigo():
    """Genera planos desde DIAN y los sube a Siigo Nube automáticamente."""
    if 'file' not in request.files:
        return {'error': 'No se proporcionó archivo DIAN'}, 400

    file = request.files['file']
    if file.filename == '':
        return {'error': 'Archivo no seleccionado'}, 400

    try:
        username = request.form.get('siigo_user', '')
        password = request.form.get('siigo_pass', '')

        if not username or not password:
            return {'error': 'Credenciales de Siigo requeridas'}, 400

        # Parámetros de consecutivos
        consec_compras = int(request.form.get('consec_compras', 371))
        consec_nc = int(request.form.get('consec_nc', 271))
        consec_gastos = int(request.form.get('consec_gastos', 798))
        consec_ventas = int(request.form.get('consec_ventas', 1))
        consec_nc_ventas = int(request.form.get('consec_nc_ventas', 1))

        # Paso 1: Procesar archivo DIAN y generar planos
        file_data = io.BytesIO(file.read())
        planos_stream = process_file(
            file_data,
            consec_compras=consec_compras,
            consec_nc=consec_nc,
            consec_gastos=consec_gastos,
            consec_ventas=consec_ventas,
            consec_nc_ventas=consec_nc_ventas
        )
        planos_stream.seek(0)

        # Paso 2: Subir planos a Siigo
        resultado = subir_planos_a_siigo(planos_stream, username, password)

        if 'error' in resultado:
            return resultado, 400

        return {
            'success': True,
            'mensaje': f'✅ Planos generados y {resultado["exito"]} registros subidos a Siigo',
            'detalles': resultado
        }, 200

    except Exception as e:
        traceback.print_exc()
        return {'error': f'Error: {str(e)}'}, 500


if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 8080))
    app.run(debug=True, port=port, host='127.0.0.1')


def generar_reporte_retenciones_excel(planos_data):
    """Genera Excel con reporte de retenciones"""
    wb = Workbook()
    ws = wb.active
    ws.title = 'Retenciones'
    
    # Encabezados
    headers = ['Tipo', 'Documento', 'Fecha', 'NIT', 'Tercero', 'Base Gravable', 'Tasa %', 'Valor Retención']
    for col, header in enumerate(headers, 1):
        cell = ws.cell(1, col)
        cell.value = header
        cell.font = Font(bold=True, color='FFFFFF')
        cell.fill = PatternFill(start_color='1a3a5c', end_color='1a3a5c', fill_type='solid')
        cell.alignment = Alignment(horizontal='center')
    
    row = 2
    totales = {'base': 0, 'retencion': 0}
    
    # Ventas
    for doc in planos_data.get('ventas', []):
        base = doc.get('total', 0) - doc.get('iva', 0)
        ret = calcular_retencion(base, 'ventas', doc.get('nit', ''))
        ws.cell(row, 1).value = 'Venta'
        ws.cell(row, 2).value = doc.get('folio', '')
        ws.cell(row, 3).value = doc.get('fecha', '')
        ws.cell(row, 4).value = doc.get('nit', '')
        ws.cell(row, 5).value = doc.get('nombre', '')
        ws.cell(row, 6).value = ret['base']
        ws.cell(row, 7).value = ret['tasa']
        ws.cell(row, 8).value = ret['valor']
        totales['base'] += ret['base']
        totales['retencion'] += ret['valor']
        row += 1
    
    # Compras
    for doc in planos_data.get('compras', []):
        base = doc.get('total', 0) - doc.get('iva', 0)
        ret = calcular_retencion(base, 'compras', doc.get('nit', ''))
        ws.cell(row, 1).value = 'Compra'
        ws.cell(row, 2).value = doc.get('folio', '')
        ws.cell(row, 3).value = doc.get('fecha', '')
        ws.cell(row, 4).value = doc.get('nit', '')
        ws.cell(row, 5).value = doc.get('nombre', '')
        ws.cell(row, 6).value = ret['base']
        ws.cell(row, 7).value = ret['tasa']
        ws.cell(row, 8).value = ret['valor']
        totales['base'] += ret['base']
        totales['retencion'] += ret['valor']
        row += 1
    
    # Gastos
    for doc in planos_data.get('gastos', []):
        base = doc.get('total', 0) - doc.get('iva', 0)
        ret = calcular_retencion(base, 'gastos', doc.get('nit', ''))
        ws.cell(row, 1).value = 'Gasto'
        ws.cell(row, 2).value = doc.get('folio', '')
        ws.cell(row, 3).value = doc.get('fecha', '')
        ws.cell(row, 4).value = doc.get('nit', '')
        ws.cell(row, 5).value = doc.get('nombre', '')
        ws.cell(row, 6).value = ret['base']
        ws.cell(row, 7).value = ret['tasa']
        ws.cell(row, 8).value = ret['valor']
        totales['base'] += ret['base']
        totales['retencion'] += ret['valor']
        row += 1
    
    # Totales
    row += 1
    ws.cell(row, 5).value = 'TOTAL'
    ws.cell(row, 5).font = Font(bold=True)
    ws.cell(row, 6).value = totales['base']
    ws.cell(row, 6).font = Font(bold=True)
    ws.cell(row, 8).value = totales['retencion']
    ws.cell(row, 8).font = Font(bold=True)
    
    # Ajustar anchos
    ws.column_dimensions['A'].width = 12
    ws.column_dimensions['B'].width = 15
    ws.column_dimensions['C'].width = 12
    ws.column_dimensions['D'].width = 15
    ws.column_dimensions['E'].width = 30
    ws.column_dimensions['F'].width = 15
    ws.column_dimensions['G'].width = 10
    ws.column_dimensions['H'].width = 15
    
    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    return output


@app.route('/api/retenciones', methods=['POST'])
def calcular_retenciones():
    """Calcula retenciones de un monto"""
    try:
        data = request.json
        base = float(data.get('base', 0))
        tipo = data.get('tipo', 'compras')  # compras, ventas, gastos
        nit = data.get('nit', '')
        
        resultado = calcular_retencion(base, tipo, nit)
        return resultado
    except Exception as e:
        return {'error': str(e)}, 400

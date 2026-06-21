from flask import Flask, request, send_file, render_template, jsonify
import io
import json
import traceback
from converter import process_file, process_liquidacion_iva, _cargar_nomina_balance, convert_nomina, generate_balance_prueba, generate_liquidaciones
from siigo_integration import subir_planos_a_siigo

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 20 * 1024 * 1024  # 20 MB máximo

@app.route('/')
def index():
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
        
        # Procesar el archivo
        output_stream = process_file(
            input_stream,
            consec_compras=consec_compras,
            consec_nc=consec_nc,
            consec_gastos=consec_gastos,
            consec_ventas=consec_ventas,
            consec_nc_ventas=consec_nc_ventas
        )
        
        # Devolver el archivo convertido
        original_name = file.filename.rsplit('.', 1)[0]
        download_name = f"PLANOS_{original_name}.xlsx"
        
        return send_file(
            output_stream,
            as_attachment=True,
            download_name=download_name,
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
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

        output_stream = generate_liquidaciones(empleados)
        return send_file(
            output_stream,
            as_attachment=True,
            download_name='LIQUIDACIONES.xlsx',
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    except Exception as e:
        traceback.print_exc()
        return {'error': f'Error generando liquidaciones: {str(e)}'}, 500


@app.route('/api/upload-siigo', methods=['POST'])
def upload_siigo():
    """Sube los planos generados a Siigo Nube automáticamente."""
    if 'file' not in request.files:
        return {'error': 'No se proporcionó archivo de planos'}, 400

    file = request.files['file']
    if file.filename == '':
        return {'error': 'Archivo no seleccionado'}, 400

    try:
        username = request.form.get('siigo_user', '')
        password = request.form.get('siigo_pass', '')

        if not username or not password:
            return {'error': 'Credenciales de Siigo requeridas'}, 400

        # Leer el archivo de planos
        file_data = io.BytesIO(file.read())

        # Subir a Siigo
        resultado = subir_planos_a_siigo(file_data, username, password)

        if 'error' in resultado:
            return resultado, 400

        return {
            'success': True,
            'mensaje': f'✅ {resultado["exito"]} registros subidos a Siigo',
            'detalles': resultado
        }, 200

    except Exception as e:
        traceback.print_exc()
        return {'error': f'Error subiendo a Siigo: {str(e)}'}, 500


if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 8080))
    app.run(debug=True, port=port, host='127.0.0.1')

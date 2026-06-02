from flask import Flask, request, send_file, render_template
import io
import traceback
from converter import process_file, process_liquidacion_iva

app = Flask(__name__)

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
            consec_gastos=consec_gastos
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


if __name__ == '__main__':
    app.run(debug=True, port=5000)

#!/usr/bin/env python3
"""
APP WEB v3: Formulario 210 DIAN
Genera Excel idéntico al original con datos de Exógena
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import os
import pandas as pd
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime
import cgi
import tempfile
import shutil

FORMULARIO_210_BASE = "/Users/edison/Downloads/VA23-Formulario-210-AG2022-PN-SIMONVELASQUEZ.xlsx"
UPLOAD_DIR = tempfile.gettempdir()

class AppHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Servir HTML"""
        if self.path == '/' or self.path == '/index.html':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(self.get_html().encode('utf-8'))
        elif self.path.startswith('/descargar/'):
            self.descargar_archivo()
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        """Procesar solicitudes"""
        if self.path == '/procesar':
            self.procesar_exogena()
        else:
            self.send_json({"error": "Ruta no encontrada"}, 404)

    def procesar_exogena(self):
        """Procesa el archivo Exógena cargado"""
        try:
            content_type = self.headers.get('Content-Type', '')

            if 'multipart/form-data' not in content_type:
                self.send_json({"error": "Formato incorrecto"}, 400)
                return

            # Parsear multipart form
            form = cgi.FieldStorage(
                fp=self.rfile,
                headers=self.headers,
                environ={
                    'REQUEST_METHOD': 'POST',
                    'CONTENT_TYPE': content_type,
                }
            )

            if 'exogena' not in form:
                self.send_json({"error": "No se cargó archivo Exógena"}, 400)
                return

            # Guardar archivo temporal
            archivo = form['exogena']
            temp_path = os.path.join(UPLOAD_DIR, f"exogena_{datetime.now().strftime('%s')}.xlsx")

            with open(temp_path, 'wb') as f:
                f.write(archivo.file.read())

            # Procesar
            resultado = self.generar_formulario(temp_path)

            # Limpiar
            try:
                os.remove(temp_path)
            except:
                pass

            if 'error' in resultado:
                self.send_json(resultado, 500)
            else:
                self.send_json(resultado, 200)

        except Exception as e:
            self.send_json({"error": str(e)}, 500)

    def generar_formulario(self, exogena_temp):
        """Genera Excel"""
        try:
            # Leer Exógena
            df = pd.read_excel(exogena_temp, sheet_name="Reporte", header=13)
            df.columns = df.columns.str.strip()
            df["Valor"] = pd.to_numeric(df["Valor"], errors="coerce")
            df = df.dropna(subset=["Valor"])

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            excel_path = os.path.join(UPLOAD_DIR, f"Formulario210_{timestamp}.xlsx")

            # Generar Excel
            self.generar_excel(FORMULARIO_210_BASE, excel_path, df)

            return {
                "exitoso": True,
                "timestamp": timestamp,
                "descargar": f"/descargar/{timestamp}"
            }

        except Exception as e:
            return {"error": str(e)}

    def generar_excel(self, archivo_base, archivo_salida, df_exogena):
        """Copia archivo base y modifica valores"""
        # Copiar archivo
        shutil.copy(archivo_base, archivo_salida)

        temp_dir = tempfile.mkdtemp()

        try:
            # Extraer copia
            with zipfile.ZipFile(archivo_salida, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)

            # Modificar Formulario 210 (sheet4.xml)
            sheet4_path = os.path.join(temp_dir, 'xl', 'worksheets', 'sheet4.xml')
            self.llenar_formulario_210(sheet4_path, df_exogena)

            # Reempacar
            with zipfile.ZipFile(archivo_salida, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root_dir, dirs, files in os.walk(temp_dir):
                    for file in files:
                        file_path = os.path.join(root_dir, file)
                        arcname = os.path.relpath(file_path, temp_dir)
                        zipf.write(file_path, arcname)

        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    def llenar_formulario_210(self, sheet_path, df_exogena):
        """Llena Formulario 210 con los valores"""
        tree = ET.parse(sheet_path)
        root = tree.getroot()

        ns = {'ss': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}

        # Mapeos
        mapeos = {
            "R132 Retenciones año gravable a declarar": "AZ30",
            "Tope 2. Patrimonio | R29 Patrimonio bruto": "AZ40",
            "Tope 2. Patrimonio bruto | R29 Patrimonio bruto": "P25",
            "Tope 2. Patrimonio| R29 Patrimonio bruto": "AD25",
            "TOPE 4. Consignaciones e inversiones": "K44",
            "Tope 1: ingresos brutos | R32 Ingresos brutos por rentas de trabajo (art. 103 E.T.)": "K25",
            "Tope 1: ingresos brutos | R58 Ingresos brutos por rentas de capital | R59 Ingresos no constitutivos  por rentas de capital": "AX47",
        }

        # Agrupar datos
        datos = df_exogena.groupby("Uso declaración Sugerida")["Valor"].sum().to_dict()

        # Buscar y modificar celdas existentes
        for categoria, celda_ref in mapeos.items():
            if categoria not in datos:
                continue

            valor = int(datos[categoria])

            # Buscar la celda en el XML
            for row in root.findall('.//ss:row', ns):
                for cell in row.findall('ss:c', ns):
                    if cell.get('r') == celda_ref:
                        # Encontrar o crear elemento 'v'
                        v_elem = cell.find('ss:v', ns)
                        if v_elem is None:
                            v_elem = ET.Element('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}v')
                            cell.append(v_elem)

                        v_elem.text = str(valor)
                        break

        tree.write(sheet_path, encoding='UTF-8', xml_declaration=True)

    def descargar_archivo(self):
        """Descargar archivo"""
        timestamp = self.path.split('/')[-1]
        archivo = os.path.join(UPLOAD_DIR, f"Formulario210_{timestamp}.xlsx")

        if not os.path.exists(archivo):
            self.send_response(404)
            self.end_headers()
            return

        self.send_response(200)
        self.send_header('Content-type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        self.send_header('Content-Disposition', f'attachment; filename="Formulario210_Diligenciado.xlsx"')
        self.end_headers()

        with open(archivo, 'rb') as f:
            self.wfile.write(f.read())

    def send_json(self, datos, codigo=200):
        """Enviar JSON"""
        self.send_response(codigo)
        self.send_header('Content-type', 'application/json; charset=utf-8')
        self.end_headers()
        self.wfile.write(json.dumps(datos).encode('utf-8'))

    def get_html(self):
        """HTML de la app"""
        return """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Formulario 210 DIAN</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        .container {
            background: white;
            border-radius: 12px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            max-width: 700px;
            width: 100%;
            padding: 40px;
        }
        h1 { color: #333; text-align: center; margin-bottom: 10px; font-size: 28px; }
        .subtitle { color: #666; text-align: center; margin-bottom: 40px; font-size: 14px; }
        .upload-area {
            border: 2px dashed #667eea;
            border-radius: 8px;
            padding: 40px;
            text-align: center;
            cursor: pointer;
            background: #f8f9ff;
            margin-bottom: 30px;
            transition: all 0.3s;
        }
        .upload-area:hover { border-color: #764ba2; background: #f0f2ff; }
        .upload-icon { font-size: 48px; margin-bottom: 15px; }
        .upload-text { color: #333; font-weight: 500; margin-bottom: 5px; }
        .upload-subtext { color: #999; font-size: 12px; }
        input[type="file"] { display: none; }
        button {
            width: 100%;
            padding: 12px 20px;
            border: none;
            border-radius: 6px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            transition: all 0.3s;
            margin-bottom: 10px;
        }
        button:hover { transform: translateY(-2px); box-shadow: 0 10px 20px rgba(102,126,234,0.3); }
        button:disabled { opacity: 0.6; cursor: not-allowed; }
        .loading { display: none; text-align: center; padding: 30px; }
        .spinner {
            border: 4px solid #f0f0f0;
            border-top: 4px solid #667eea;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto 15px;
        }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        .status {
            display: none;
            padding: 20px;
            border-radius: 6px;
            margin-bottom: 20px;
            font-size: 14px;
        }
        .status.success { background: #e8f5e9; border-left: 4px solid #4caf50; color: #2e7d32; }
        .status.error { background: #ffebee; border-left: 4px solid #f44336; color: #c62828; }
        .download-btn {
            display: none;
            width: 100%;
            padding: 12px;
            background: #4caf50;
            color: white;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-weight: 600;
            margin-top: 15px;
            text-decoration: none;
            text-align: center;
            transition: all 0.3s;
        }
        .download-btn:hover { background: #45a049; }
        .footer { text-align: center; margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; color: #999; font-size: 12px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 Formulario 210 DIAN</h1>
        <p class="subtitle">Carga tu Exógena y genera automáticamente tu Formulario 210</p>

        <div class="status" id="status"></div>

        <div class="upload-area" id="uploadArea">
            <div class="upload-icon">📁</div>
            <div class="upload-text">Arrastra tu Exógena aquí</div>
            <div class="upload-subtext">o haz clic para seleccionar (.xlsx)</div>
            <input type="file" id="fileInput" accept=".xlsx,.xls">
        </div>

        <div class="loading" id="loading">
            <div class="spinner"></div>
            <p>Procesando tu Exógena...</p>
            <p style="font-size: 12px; color: #666; margin-top: 10px;">Generando Formulario 210</p>
        </div>

        <button id="processBtn" onclick="procesarExogena()" disabled>
            ▶️ Procesar Exógena
        </button>

        <a class="download-btn" id="downloadBtn" target="_blank">
            ⬇️ Descargar Formulario 210
        </a>

        <footer class="footer">
            <p>💡 Asegúrate de tener tu Exógena descargada de la DIAN</p>
            <p>Versión 3.0 • Generador Formulario 210</p>
        </footer>
    </div>

    <script>
        const uploadArea = document.getElementById('uploadArea');
        const fileInput = document.getElementById('fileInput');
        const status = document.getElementById('status');
        const processBtn = document.getElementById('processBtn');
        const loading = document.getElementById('loading');
        const downloadBtn = document.getElementById('downloadBtn');
        let archivoSeleccionado = null;

        uploadArea.addEventListener('click', () => fileInput.click());
        uploadArea.addEventListener('dragover', e => {
            e.preventDefault();
            uploadArea.style.borderColor = '#764ba2';
        });
        uploadArea.addEventListener('dragleave', () => {
            uploadArea.style.borderColor = '#667eea';
        });
        uploadArea.addEventListener('drop', e => {
            e.preventDefault();
            uploadArea.style.borderColor = '#667eea';
            if (e.dataTransfer.files.length > 0) {
                archivoSeleccionado = e.dataTransfer.files[0];
                processBtn.disabled = false;
            }
        });

        fileInput.addEventListener('change', e => {
            if (e.target.files.length > 0) {
                archivoSeleccionado = e.target.files[0];
                processBtn.disabled = false;
            }
        });

        function procesarExogena() {
            if (!archivoSeleccionado) {
                alert('Por favor selecciona un archivo');
                return;
            }

            processBtn.disabled = true;
            loading.style.display = 'block';
            status.style.display = 'none';
            downloadBtn.style.display = 'none';

            const formData = new FormData();
            formData.append('exogena', archivoSeleccionado);

            fetch('/procesar', {
                method: 'POST',
                body: formData
            })
            .then(r => r.json())
            .then(data => {
                loading.style.display = 'none';

                if (data.error) {
                    status.innerHTML = `<strong>❌ Error:</strong> ${data.error}`;
                    status.className = 'status error';
                } else {
                    status.innerHTML = `<strong>✅ ¡Éxito!</strong><br>Formulario 210 generado correctamente`;
                    status.className = 'status success';

                    downloadBtn.href = data.descargar;
                    downloadBtn.download = 'Formulario210_Diligenciado.xlsx';
                    downloadBtn.style.display = 'block';
                }
                status.style.display = 'block';
                processBtn.disabled = false;
            })
            .catch(err => {
                loading.style.display = 'none';
                status.innerHTML = `<strong>❌ Error:</strong> ${err.message}`;
                status.className = 'status error';
                status.style.display = 'block';
                processBtn.disabled = false;
            });
        }
    </script>
</body>
</html>
        """

    def log_message(self, format, *args):
        pass

if __name__ == '__main__':
    print("\n" + "="*80)
    print("🌐 APP WEB v3: Formulario 210 DIAN")
    print("="*80)
    print("\n✓ Iniciando servidor en http://127.0.0.1:9999/")
    print("✓ Presiona Ctrl+C para detener\n")

    servidor = HTTPServer(('127.0.0.1', 9999), AppHandler)
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        print("\n✓ Servidor detenido\n")

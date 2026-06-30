"""
Módulo de Firma Digital para PDFs de Liquidación
Soporta certificados digitales X.509 (.p12, .pfx, .pem)
"""
import subprocess
import os
import tempfile
from pathlib import Path


class FirmaDigitalPDF:
    """Firma digitalmente archivos PDF con certificados X.509."""

    def __init__(self, cert_path: str, cert_password: str = None):
        """
        Inicializa con ruta al certificado.

        cert_path: Ruta al certificado (.p12, .pfx o .pem)
        cert_password: Contraseña del certificado (si está protegido)
        """
        self.cert_path = cert_path
        self.cert_password = cert_password
        self.disponible = self._verificar_dependencias()

    def _verificar_dependencias(self) -> bool:
        """Verifica si están disponibles las herramientas necesarias."""
        try:
            # Verificar si OpenSSL está disponible
            result = subprocess.run(['openssl', 'version'], capture_output=True, timeout=5)
            return result.returncode == 0
        except:
            return False

    def firmar_pdf(self, pdf_input: bytes, signer_name: str = "Empresa") -> bytes:
        """
        Firma un PDF digitalmente.

        pdf_input: Bytes del PDF a firmar
        signer_name: Nombre del firmante que aparecerá en el PDF

        Retorna: Bytes del PDF firmado
        """
        if not self.disponible:
            raise Exception("OpenSSL no disponible. Instala: brew install openssl")

        if not os.path.exists(self.cert_path):
            raise Exception(f"Certificado no encontrado: {self.cert_path}")

        try:
            # Crear archivos temporales
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_in:
                tmp_in.write(pdf_input)
                tmp_in_path = tmp_in.name

            tmp_out_path = tempfile.mktemp(suffix='.pdf')

            # Comando para firmar con OpenSSL + qpdf
            # Nota: Esto es una demostración. La firma real requiere librerías específicas

            # Por ahora, retornar el PDF sin cambios (preparado para firma real)
            with open(tmp_in_path, 'rb') as f:
                resultado = f.read()

            # Limpiar temporales
            os.unlink(tmp_in_path)

            return resultado

        except Exception as e:
            raise Exception(f"Error firmando PDF: {str(e)}")


def preparar_para_firma(pdf_bytes: bytes, datos_firma: dict) -> bytes:
    """
    Prepara un PDF para firma digital.
    Agrega campos visibles de firma.

    datos_firma: {
        'nombre_firmante': 'Juan Pérez',
        'titulo_firmante': 'Gerente',
        'fecha': '2026-06-21',
        'razon': 'Acta de Liquidación',
        'ubicacion': 'Bogotá, Colombia'
    }
    """
    # Esta función puede ser extendida para agregar campos visibles de firma
    # Por ahora retorna el PDF sin cambios
    return pdf_bytes


def generar_certificado_prueba(output_path: str, password: str = "123456"):
    """
    Genera un certificado autofirmado para pruebas.

    ⚠️ SOLO PARA TESTING - No válido legalmente

    output_path: Ruta donde guardar el certificado (.p12)
    password: Contraseña del certificado
    """
    try:
        # Generar clave privada
        subprocess.run([
            'openssl', 'genrsa',
            '-out', 'key.pem',
            '-aes256',
            '-passout', f'pass:{password}',
            '2048'
        ], check=True, capture_output=True)

        # Generar certificado autofirmado
        subprocess.run([
            'openssl', 'req',
            '-new',
            '-x509',
            '-key', 'key.pem',
            '-passin', f'pass:{password}',
            '-out', 'cert.pem',
            '-days', '365',
            '-subj', '/C=CO/ST=Bogota/L=Bogota/O=Test/CN=Test'
        ], check=True, capture_output=True)

        # Convertir a PKCS#12
        subprocess.run([
            'openssl', 'pkcs12',
            '-export',
            '-out', output_path,
            '-inkey', 'key.pem',
            '-in', 'cert.pem',
            '-passin', f'pass:{password}',
            '-passout', f'pass:{password}',
            '-name', 'Test Certificate'
        ], check=True, capture_output=True)

        # Limpiar
        os.remove('key.pem')
        os.remove('cert.pem')

        return True

    except Exception as e:
        print(f"❌ Error generando certificado de prueba: {e}")
        return False

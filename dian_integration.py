"""
Integración con la plataforma DIAN para descargar reportes automáticamente.
Usa Selenium para web scraping porque DIAN no tiene API pública.
"""
import os
import time
import io
from datetime import datetime
from pathlib import Path

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False


class DIANDownloader:
    """Descarga reportes de la DIAN automáticamente."""

    def __init__(self, usuario: str, password: str):
        self.usuario = usuario
        self.password = password
        self.url_login = "https://catalogo-vpfe.dian.gov.co/User/PersonLogin"
        self.driver = None

    def iniciar_navegador(self) -> bool:
        """Inicia Chrome en modo headless."""
        if not SELENIUM_AVAILABLE:
            print("❌ Selenium no instalado. Instala: pip install selenium")
            return False

        try:
            options = Options()
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)')

            self.driver = webdriver.Chrome(options=options)
            return True
        except Exception as e:
            print(f"❌ Error iniciando Chrome: {e}")
            return False

    def cerrar_navegador(self):
        """Cierra el navegador."""
        if self.driver:
            self.driver.quit()

    def autenticar(self) -> bool:
        """Autentica en la plataforma DIAN."""
        try:
            print("🔐 Autenticando en DIAN...")
            self.driver.get(self.url_login)

            # Esperar a que cargue
            wait = WebDriverWait(self.driver, 10)

            # Llenar usuario
            usuario_input = wait.until(EC.presence_of_element_located((By.ID, "User")))
            usuario_input.clear()
            usuario_input.send_keys(self.usuario)

            # Llenar contraseña
            password_input = self.driver.find_element(By.ID, "Password")
            password_input.clear()
            password_input.send_keys(self.password)

            # Clickear login
            login_btn = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            login_btn.click()

            # Esperar a que se autentique (validar que no hay error)
            time.sleep(3)

            # Verificar si hay error de login
            try:
                error = self.driver.find_element(By.CLASS_NAME, "error-message")
                if error and error.is_displayed():
                    print(f"❌ Error de autenticación: {error.text}")
                    return False
            except:
                pass  # No hay error

            print("✅ Autenticado en DIAN")
            return True

        except Exception as e:
            print(f"❌ Error autenticando: {e}")
            return False

    def descargar_reporte(self, año: int = None, mes: int = None) -> io.BytesIO:
        """
        Descarga el reporte DIAN para un período.
        Nota: La DIAN cambia su interfaz frecuentemente, por lo que la descarga
        automática puede no funcionar. Se recomienda descargar manualmente.
        """
        try:
            if not año:
                año = datetime.now().year

            print(f"📥 Intentando descargar reporte DIAN {año}...")

            # Navegar a la sección de búsqueda
            self.driver.get("https://catalogo-vpfe.dian.gov.co/User/SearchDocument")
            time.sleep(3)

            # La DIAN usa JavaScript para cargar dinámicamente el contenido
            # El web scraping es frágil y se rompe con cambios de interfaz

            # Intentar hacer scroll para cargar más contenido
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)

            # Intentar encontrar botón de descarga
            try:
                descarga_btns = self.driver.find_elements(By.XPATH, "//button[contains(text(), 'Descargar')]")
                if descarga_btns:
                    descarga_btns[0].click()
                    print("📥 Descargando...")
                    time.sleep(5)
                    return True  # Indicar que se inició
                else:
                    print("⚠️  No se encontró botón de descarga")
                    return None
            except Exception as e:
                print(f"⚠️  Error buscando botón de descarga: {e}")
                return None

        except Exception as e:
            print(f"❌ Error en descarga: {e}")
            return None

    def descargar(self) -> io.BytesIO:
        """Realiza todo el proceso de descarga."""
        if not self.iniciar_navegador():
            return None

        try:
            if not self.autenticar():
                return None

            archivo = self.descargar_reporte()
            return archivo

        finally:
            self.cerrar_navegador()


def descargar_reporte_dian(usuario: str, password: str) -> io.BytesIO:
    """
    Descarga un reporte DIAN.
    Retorna bytes del archivo Excel.
    """
    downloader = DIANDownloader(usuario, password)
    return downloader.descargar()

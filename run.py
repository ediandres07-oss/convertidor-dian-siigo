#!/usr/bin/env python3
"""
Script para ejecutar el sistema de liquidaciones de nómina
Instala dependencias, inicia el backend y el frontend
"""

import subprocess
import sys
import time
import os
from pathlib import Path

def install_requirements():
    """Instala las dependencias del proyecto"""
    print("\n" + "="*60)
    print("📦 Instalando dependencias...")
    print("="*60)
    result = subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    if result.returncode != 0:
        print("❌ Error instalando dependencias")
        sys.exit(1)
    print("✅ Dependencias instaladas correctamente\n")


def start_backend():
    """Inicia el servidor FastAPI en el puerto 8000"""
    print("\n" + "="*60)
    print("🚀 Iniciando Backend (FastAPI)...")
    print("="*60)
    print("El backend estará disponible en: http://127.0.0.1:8000")
    print("Documentación en: http://127.0.0.1:8000/docs\n")

    # Obtener ruta absoluta del proyecto
    project_root = Path(__file__).parent.absolute()
    os.chdir(project_root)

    # Ejecutar uvicorn
    return subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "backend.main:app", "--reload", "--host", "127.0.0.1", "--port", "8000"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )


def start_frontend():
    """Inicia la aplicación Streamlit en el puerto 8501"""
    print("\n" + "="*60)
    print("🎨 Iniciando Frontend (Streamlit)...")
    print("="*60)
    print("El frontend estará disponible en: http://127.0.0.1:8501\n")

    # Obtener ruta absoluta del proyecto
    project_root = Path(__file__).parent.absolute()
    os.chdir(project_root)

    # Ejecutar streamlit
    return subprocess.Popen(
        [sys.executable, "-m", "streamlit", "run", "frontend/app.py", "--server.port=8501", "--server.address=127.0.0.1"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )


def main():
    """Función principal"""
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*58 + "║")
    print("║" + "  💼  SISTEMA DE LIQUIDACIONES DE NÓMINA  💼".center(58) + "║")
    print("║" + " "*58 + "║")
    print("╚" + "="*58 + "╝")

    # Instalar dependencias
    install_requirements()

    # Iniciar backend
    print("\n⏳ Esperando a que el backend se inicie...")
    backend_process = start_backend()
    time.sleep(3)

    # Iniciar frontend
    frontend_process = start_frontend()

    print("\n" + "="*60)
    print("✅ SISTEMA INICIADO CORRECTAMENTE")
    print("="*60)
    print("\n📱 ACCESO A LAS APLICACIONES:")
    print("   • Backend (API):  http://127.0.0.1:8000")
    print("   • Backend (Docs): http://127.0.0.1:8000/docs")
    print("   • Frontend:       http://127.0.0.1:8501")
    print("\n💡 Presiona Ctrl+C para detener ambas aplicaciones\n")

    try:
        # Mantener los procesos en ejecución
        while True:
            if backend_process.poll() is not None:
                print("❌ El backend se detuvo inesperadamente")
                break
            if frontend_process.poll() is not None:
                print("❌ El frontend se detuvo inesperadamente")
                break
            time.sleep(1)

    except KeyboardInterrupt:
        print("\n\n⏹️  Deteniendo aplicaciones...")
        backend_process.terminate()
        frontend_process.terminate()
        backend_process.wait(timeout=5)
        frontend_process.wait(timeout=5)
        print("✅ Aplicaciones detenidas correctamente")


if __name__ == "__main__":
    main()

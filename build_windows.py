"""
Script para compilar app_siigo.py a ejecutable Windows (.exe)
Uso: python build_windows.py
"""

import subprocess
import sys
import os
from pathlib import Path

def main():
    print("\n" + "=" * 70)
    print("📦 COMPILADOR - CONVERTIDOR SIIGO")
    print("=" * 70)
    print()

    # Verificar PyInstaller
    print("✓ Verificando PyInstaller...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "show", "pyinstaller"],
                      capture_output=True, check=True)
    except subprocess.CalledProcessError:
        print("  ✗ PyInstaller no instalado")
        print("  Instalando...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"])

    # Verificar archivo fuente
    if not Path("app_siigo.py").exists():
        print("✗ Error: app_siigo.py no encontrado")
        sys.exit(1)

    print("✓ Archivo fuente encontrado: app_siigo.py")
    print()

    # Compilar
    print("🔨 Compilando aplicación...")
    print("-" * 70)

    cmd = [
        sys.executable, "-m", "pyinstaller",
        "--onefile",
        "--windowed",
        "--icon=icono.ico" if Path("icono.ico").exists() else "",
        "--name=Convertidor SIIGO",
        "--distpath=dist",
        "--buildpath=build",
        "--specpath=.",
        "app_siigo.py"
    ]

    # Limpiar comando (remover strings vacíos)
    cmd = [c for c in cmd if c]

    try:
        resultado = subprocess.run(cmd, capture_output=False, check=True)
    except subprocess.CalledProcessError as e:
        print(f"\n✗ Error en compilación: {e}")
        sys.exit(1)

    print("-" * 70)
    print()

    # Verificar resultado
    exe_path = Path("dist/Convertidor SIIGO.exe")
    if exe_path.exists():
        tamaño = exe_path.stat().st_size / (1024 * 1024)
        print("✅ COMPILACIÓN EXITOSA")
        print()
        print("📁 Archivo generado:")
        print(f"   {exe_path}")
        print(f"   Tamaño: {tamaño:.1f} MB")
        print()
        print("🚀 Uso:")
        print("   Doble clic en el archivo .exe para ejecutar")
        print()
        print("📦 Distribución:")
        print(f"   Copia el archivo: {exe_path}")
        print("   Distribúyelo a otros usuarios")
        print("   No necesitan Python instalado")
    else:
        print("✗ Error: No se generó el ejecutable")
        sys.exit(1)

    print()
    print("=" * 70)
    print("✅ Proceso completado")
    print("=" * 70)
    print()

if __name__ == "__main__":
    main()

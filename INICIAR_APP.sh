#!/bin/bash

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║  APLICACIÓN WEB: Declaración de Renta DIAN 2025              ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 no está instalado"
    exit 1
fi

echo "✓ Python3 disponible"

# Instalar Flask si no existe
echo "Verificando dependencias..."
pip3 install -q flask openpyxl pandas werkzeug

echo "✓ Dependencias instaladas"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Iniciando servidor web..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🌐 URL: http://127.0.0.1:5000/"
echo "📝 Abre tu navegador y carga tu Exógena"
echo ""
echo "Presiona Ctrl+C para detener el servidor"
echo ""

cd "$(dirname "$0")"
python3 app_declaracion_renta.py

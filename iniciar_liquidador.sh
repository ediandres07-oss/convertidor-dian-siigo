#!/bin/bash

# Script para iniciar el Liquidador de Formulario 210
# Uso: ./iniciar_liquidador.sh

echo "╔════════════════════════════════════════════════════════════╗"
echo "║     Liquidador de Formulario 210 - DIAN Colombia           ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Verificar si estamos en el directorio correcto
if [ ! -f "liquidador_renta.py" ]; then
    echo "❌ Error: Debes ejecutar este script desde el directorio del proyecto"
    exit 1
fi

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 no está instalado"
    exit 1
fi

# Instalar dependencias
echo "📦 Verificando dependencias..."
pip install -q streamlit pandas openpyxl xlrd 2>/dev/null

if [ $? -eq 0 ]; then
    echo "✅ Dependencias listas"
else
    echo "⚠️  Instalando dependencias (puede tardar)..."
    pip install streamlit pandas openpyxl xlrd
fi

echo ""
echo "🚀 Iniciando aplicación web..."
echo ""
echo "📍 Abre tu navegador en: http://localhost:8501"
echo "⌨️  Presiona Ctrl+C para salir"
echo ""

streamlit run app_liquidador_renta.py

#!/bin/bash

echo "=================================================="
echo "  Declaración de Renta 2025 - App Integrada"
echo "=================================================="
echo ""
echo "Iniciando aplicación Streamlit..."
echo ""

if ! command -v streamlit &> /dev/null; then
    echo "⚠️  Streamlit no está instalado."
    echo "Instálalo con: pip install streamlit pandas openpyxl"
    exit 1
fi

streamlit run app_declaracion_renta_2025.py --logger.level=info

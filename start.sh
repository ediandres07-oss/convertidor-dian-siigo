#!/bin/bash

# Script para iniciar el sistema de liquidaciones

cd "$(dirname "$0")"

# Matar procesos anteriores si existen
pkill -f "uvicorn backend.main" 2>/dev/null
pkill -f "streamlit run" 2>/dev/null
sleep 2

echo "🚀 Iniciando Sistema de Liquidaciones..."

# Iniciar backend
echo "📌 Backend en puerto 8000..."
python3 -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000 > /tmp/backend.log 2>&1 &
BACKEND_PID=$!

sleep 3

# Iniciar frontend
echo "📌 Frontend en puerto 8501..."
echo "" | python3 -m streamlit run frontend/app.py --server.port=8501 --server.address=127.0.0.1 > /tmp/frontend.log 2>&1 &
FRONTEND_PID=$!

sleep 5

echo ""
echo "╔════════════════════════════════════════════╗"
echo "║      ✅ SISTEMA INICIADO                   ║"
echo "╠════════════════════════════════════════════╣"
echo "║  🌐 Frontend: http://127.0.0.1:8501        ║"
echo "║  🔧 Backend: http://127.0.0.1:8000         ║"
echo "║  📖 Docs: http://127.0.0.1:8000/docs       ║"
echo "╚════════════════════════════════════════════╝"
echo ""
echo "Presiona Ctrl+C para detener"
echo ""

# Mantener abierto
wait

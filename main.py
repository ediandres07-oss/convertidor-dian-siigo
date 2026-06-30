"""
Aplicación Principal - FastAPI Backend
Servidor de API para Liquidación de Prestaciones
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.encoders import JSONEncoder
from app.routers import payroll, legacy
import os
import json
import math

class SafeJSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, float):
            if math.isnan(obj):
                return 0
            elif math.isinf(obj):
                return 0
        return super().default(obj)

# ============================================
# INICIALIZACIÓN
# ============================================
app = FastAPI(
    title="Sistema de Liquidación de Prestaciones",
    description="API para cálculo y generación de PDF de prestaciones sociales",
    version="2.0",
    docs_url="/docs",
    redoc_url="/redoc",
    json_encoder=SafeJSONEncoder
)

# ============================================
# CORS
# ============================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================
# ROUTERS
# ============================================
app.include_router(payroll.router)
app.include_router(legacy.router)

# ============================================
# ENDPOINTS ADICIONALES
# ============================================

@app.get("/")
def root():
    """Endpoint raíz"""
    return {
        "mensaje": "Sistema de Liquidación de Prestaciones",
        "version": "2.0",
        "docs": "http://localhost:8000/docs",
        "api": "http://localhost:8000/api"
    }


@app.get("/descargar/{filename}")
def descargar_pdf(filename: str):
    """Descarga un PDF generado"""
    ruta = f"outputs/{filename}"

    if not os.path.exists(ruta):
        return {"error": "Archivo no encontrado"}

    return FileResponse(
        ruta,
        media_type="application/pdf",
        filename=filename
    )


# ============================================
# EJECUCIÓN
# ============================================
if __name__ == "__main__":
    import uvicorn

    print("=" * 60)
    print("🚀 INICIANDO SERVIDOR")
    print("=" * 60)
    print("📡 Backend: http://localhost:8000")
    print("📚 Documentación: http://localhost:8000/docs")
    print("=" * 60)

    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        reload=False,
        log_level="info"
    )

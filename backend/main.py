from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import payroll

app = FastAPI(
    title="Sistema de Liquidaciones de Nómina",
    description="API para procesar y exportar liquidaciones de nómina",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(payroll.router)


@app.get("/")
def read_root():
    return {
        "message": "Sistema de Liquidaciones de Nómina",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
def health_check():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

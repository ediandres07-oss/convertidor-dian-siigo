# 🚀 Cómo Ejecutar el Sistema Completo

Sistema integrado de **FastAPI Backend** + **Streamlit Frontend** para liquidación de prestaciones sociales.

---

## 📦 Requisitos

```bash
pip install fastapi uvicorn streamlit reportlab pydantic requests pytz
```

O usa:
```bash
pip install -r requirements.txt
```

---

## ⚙️ Estructura del Proyecto

```
proyecto/
├── main.py                          # 🚀 Backend FastAPI (PUERTO 8000)
├── app/
│   ├── __init__.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── liquidacion.py          # Cálculos
│   │   └── pdf.py                  # Generación PDF
│   └── routers/
│       ├── __init__.py
│       └── payroll.py              # Endpoints API
├── frontend/
│   └── app_web.py                  # 🌐 Frontend Streamlit (PUERTO 8501)
└── outputs/                         # PDFs generados
```

---

## 🎯 OPCIÓN 1: Ejecutar TODO (Lo Más Fácil)

Abre **DOS TERMINALES** (una al lado de la otra):

### Terminal 1: Backend (FastAPI)
```bash
cd "/Users/edison/Desktop/proyecto-subir info a siigo nube"
python3 main.py
```

**Deberías ver:**
```
🚀 INICIANDO SERVIDOR
📡 Backend: http://localhost:8000
📚 Documentación: http://localhost:8000/docs
```

### Terminal 2: Frontend (Streamlit)
```bash
cd "/Users/edison/Desktop/proyecto-subir info a siigo nube"
streamlit run frontend/app_web.py
```

**Se abrirá automáticamente en:**
```
http://localhost:8501
```

---

## 🎯 OPCIÓN 2: Un Comando para Ambos

```bash
cd "/Users/edison/Desktop/proyecto-subir info a siigo nube" && \
python3 main.py &
sleep 2 && \
streamlit run frontend/app_web.py
```

---

## 🎯 OPCIÓN 3: Solo Backend (API REST)

Si solo quieres usar la API sin frontend:

```bash
python3 main.py
```

Luego accede a la documentación interactiva:
```
http://localhost:8000/docs
```

---

## 📱 URLs de Acceso

| Componente | URL | Descripción |
|-----------|-----|-------------|
| **Frontend** | http://localhost:8501 | Interfaz Streamlit |
| **Backend API** | http://localhost:8000 | API REST |
| **API Docs** | http://localhost:8000/docs | Swagger UI |
| **API Redoc** | http://localhost:8000/redoc | Redoc |

---

## 🧪 Probar la API con cURL

### Liquidar prestaciones:
```bash
curl -X POST "http://localhost:8000/api/liquidar-individual" \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Juan García",
    "documento": "1234567890",
    "cargo": "Gerente",
    "salario": 2600000,
    "auxilio": 140000,
    "fecha_ingreso": "2023-01-01",
    "fecha_retiro": "2024-06-30",
    "empresa": "Mi Empresa"
  }'
```

### Calcular días:
```bash
curl -X POST "http://localhost:8000/api/calcular-dias?fecha_ingreso=2023-01-01&fecha_retiro=2024-06-30"
```

### Ver liquidaciones:
```bash
curl "http://localhost:8000/api/liquidaciones"
```

### Verificar salud:
```bash
curl "http://localhost:8000/api/salud"
```

---

## 📊 Flujo de Ejecución

```
USER → FRONTEND (Streamlit) 
        ↓
      [Ingresa datos]
        ↓
      BACKEND (FastAPI)
        ├─ Valida datos
        ├─ Calcula prestaciones
        ├─ Genera PDF
        └─ Retorna resultados
        ↑
USER ← [Ve resultados]
        ↓
      [Descarga PDF]
```

---

## ⚡ Pasos Típicos de Uso

### 1. Iniciar Sistema
**Terminal 1:**
```bash
python3 main.py
```

**Terminal 2:**
```bash
streamlit run frontend/app_web.py
```

### 2. Abrir Navegador
Ir a: http://localhost:8501

### 3. Completar Formulario
- Nombre: Juan García Pérez
- Documento: 1234567890
- Cargo: Gerente
- Salario: 2,600,000
- Auxilio: 140,000
- Fechas: 2023-01-01 a 2024-06-30

### 4. Liquidar
Click en **✅ LIQUIDAR PRESTACIONES**

### 5. Descargar PDF
Click en **⬇️ Descargar PDF**

---

## 🔍 Solución de Problemas

### "Connection refused" en el frontend
**Solución:** Asegúrate que el backend está corriendo en Terminal 1

### "Port 8000 already in use"
**Solución:**
```bash
lsof -i :8000
kill -9 <PID>
```

### "Port 8501 already in use"
**Solución:**
```bash
streamlit run frontend/app_web.py --server.port 8502
```

### Módulo no encontrado
**Solución:**
```bash
pip install fastapi uvicorn streamlit reportlab pydantic requests
```

---

## 📚 Documentación de Endpoints

### POST /api/liquidar-individual
Liquida prestaciones y genera PDF

**Parámetros:**
```json
{
  "nombre": "string",
  "documento": "string",
  "cargo": "string",
  "salario": 0,
  "auxilio": 0,
  "fecha_ingreso": "YYYY-MM-DD",
  "fecha_retiro": "YYYY-MM-DD",
  "empresa": "string (opcional)"
}
```

**Respuesta:**
```json
{
  "dias_laborados": 0,
  "cesantias": 0,
  "intereses_cesantias": 0,
  "prima_servicios": 0,
  "vacaciones": 0,
  "total_devengado": 0,
  "neto_pagar": 0,
  "pdf": "path/to/pdf"
}
```

### POST /api/calcular-prestaciones
Calcula sin generar PDF

**Parámetros:**
```
salario: float
auxilio: float (opcional)
dias: int (opcional, default 30)
```

### POST /api/calcular-dias
Calcula solo días

**Parámetros:**
```
fecha_ingreso: YYYY-MM-DD
fecha_retiro: YYYY-MM-DD
```

### GET /api/liquidaciones
Lista PDFs generados

### GET /api/salud
Verifica estado del servicio

---

## 🎨 Customización

### Cambiar puerto backend
En `main.py`, línea final:
```python
uvicorn.run(
    app,
    host="0.0.0.0",
    port=9000,  # ← Cambiar aquí
    reload=True
)
```

### Cambiar puerto frontend
```bash
streamlit run frontend/app_web.py --server.port 8502
```

### Cambiar URL de API
En `frontend/app_web.py`, línea ~18:
```python
API_URL = "http://localhost:9000/api"  # ← Cambiar aquí
```

---

## 📊 Monitoreo

### Ver logs del backend
Revisa la Terminal 1 donde corre FastAPI

### Ver logs del frontend
Revisa la Terminal 2 donde corre Streamlit

### API Documentation Interactiva
Abre: http://localhost:8000/docs

---

## ✅ Verificación Rápida

```bash
# Verificar que el backend está corriendo
curl http://localhost:8000/api/salud

# Verificar que el frontend está corriendo
curl http://localhost:8501
```

---

## 🎉 ¡Listo!

El sistema está completamente integrado y listo para usar.

- **Backend:** Calcula prestaciones y genera PDFs
- **Frontend:** Interfaz amigable para usuarios
- **API:** Completamente documentada y lista para integrar

¡Disfruta! 🚀

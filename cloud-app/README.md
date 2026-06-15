# CloudApp - Enterprise Cloud Application

Aplicación empresarial completa lista para producción con backend FastAPI, frontend React, y despliegue cloud escalable.

## 🚀 Características

- **Backend FastAPI**: API REST moderna y rápida
- **Frontend React**: Interface moderna y responsive
- **PostgreSQL**: Base de datos robusta
- **Autenticación JWT**: Seguridad de nivel empresarial
- **Almacenamiento Cloud**: Compatible con AWS S3, Azure, GCP
- **Docker & Kubernetes**: Contenedorización y orquestación
- **Reportes**: PDF y Excel
- **Logging**: Logging centralizado y estructurado
- **Testing**: Suite de pruebas completa
- **CI/CD**: Pipeline de integración continua

## 📋 Requisitos Previos

- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- PostgreSQL 15+ (si no usas Docker)
- AWS CLI / Azure CLI / GCP CLI (opcional)

## 🛠️ Instalación Local

### 1. Clonar el Repositorio

```bash
git clone https://github.com/tu-org/cloudapp.git
cd cloudapp
```

### 2. Configurar Variables de Entorno

```bash
cp .env.example .env
# Editar .env con tus valores
```

### 3. Iniciar con Docker Compose

```bash
docker-compose up -d
```

La aplicación estará disponible en:
- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/docs

### 4. Instalación Manual (Desarrollo)

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r ../requirements.txt
uvicorn main:app --reload

# Frontend (en otra terminal)
cd frontend
npm install
npm start
```

## 📁 Estructura del Proyecto

```
cloud-app/
├── backend/          # FastAPI application
├── frontend/         # React application
├── docker/          # Docker configurations
├── k8s/            # Kubernetes manifests
├── scripts/        # Deploy & utility scripts
├── docs/           # Documentation
└── docker-compose.yml
```

## 🔐 Seguridad

- Contraseñas hasheadas con bcrypt
- JWT tokens con expiración
- CORS configurado
- Variables de entorno para secretos
- Validación de entrada
- Rate limiting
- SQL injection prevention

## 📊 Funcionalidades Principales

### Autenticación
- Login/Register
- JWT tokens
- Refresh tokens
- Password reset

### Usuarios
- CRUD completo
- Roles y permisos
- Perfil de usuario
- Cambio de contraseña

### Órdenes
- Crear, leer, actualizar, eliminar
- Estados: pendiente, en proceso, completada, cancelada
- Búsqueda y filtrado
- Asignación a usuarios

### Inventario
- Gestión de productos
- Control de stock
- Alertas de stock bajo
- Historial de cambios

### Reportes
- Exportación a Excel
- Generación de PDF
- Gráficos y estadísticas
- Reportes programados

### Panel de Control
- Métricas en tiempo real
- Gráficos de rendimiento
- Resumen de actividades

## 🚢 Despliegue

### AWS
```bash
./scripts/deploy.sh aws production
```

### Azure
```bash
./scripts/deploy.sh azure production
```

### GCP
```bash
./scripts/deploy.sh gcp production
```

### Kubernetes
```bash
kubectl apply -f k8s/
```

Ver [DEPLOYMENT.md](docs/DEPLOYMENT.md) para instrucciones detalladas.

## 📖 Documentación

- [SETUP.md](docs/SETUP.md) - Guía de instalación detallada
- [API.md](docs/API.md) - Documentación de API
- [DEPLOYMENT.md](docs/DEPLOYMENT.md) - Guía de despliegue
- [ARCHITECTURE.md](docs/ARCHITECTURE.md) - Arquitectura del sistema
- [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) - Solución de problemas

## 🧪 Testing

```bash
# Backend
cd backend
pytest

# Frontend
cd frontend
npm test
```

## 📝 API Documentation

Una vez el servidor está corriendo:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🔄 CI/CD

El proyecto incluye workflows para:
- Pruebas automáticas
- Build de Docker
- Despliegue automático

## 📞 Soporte

Para reportar problemas o sugerencias, abre un issue en el repositorio.

## 📄 Licencia

MIT License

## 👨‍💻 Autor

Cloud App Team

---

**Última actualización**: 2024

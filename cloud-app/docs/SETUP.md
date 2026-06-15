# CloudApp - Setup Guide

Guía completa para instalar y ejecutar CloudApp localmente.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [Database Migrations](#database-migrations)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)

## Prerequisites

### Minimum Requirements

- Python 3.11+
- Node.js 18+
- Docker & Docker Compose 3.9+
- PostgreSQL 15+ (if not using Docker)
- Git

### Optional Requirements

- AWS CLI (for AWS deployment)
- Azure CLI (for Azure deployment)
- GCP CLI (for GCP deployment)
- Kubernetes 1.24+ (for K8s deployment)

## Installation

### 1. Clone Repository

```bash
git clone https://github.com/your-org/cloudapp.git
cd cloudapp
```

### 2. Set Up Environment Variables

```bash
cp .env.example .env
# Edit .env with your configuration
```

### 3. Option A: Docker Compose (Recommended)

```bash
# Start all services
docker-compose up -d

# Wait for services to be ready
docker-compose ps

# Check health
./scripts/health-check.sh
```

Services will be available at:
- Backend API: http://localhost:8000
- Frontend: http://localhost:3000
- Database: localhost:5432
- Adminer (DB UI): http://localhost:8080

### 3. Option B: Manual Installation

#### Backend Setup

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r ../requirements.txt

# Create database
createdb cloudapp_db

# Run migrations
alembic upgrade head

# Start server
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

## Configuration

### Environment Variables

Create `.env` file with the following variables:

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/cloudapp_db

# JWT Security
SECRET_KEY=your-super-secret-key-min-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# AWS S3 (optional)
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=us-east-1
S3_BUCKET_NAME=your-bucket

# Email Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8000

# Logging
LOG_LEVEL=INFO
ENVIRONMENT=development
```

### Database Configuration

#### PostgreSQL with Docker

```bash
docker run -d \
  --name cloudapp-postgres \
  -e POSTGRES_DB=cloudapp_db \
  -e POSTGRES_USER=cloudapp_user \
  -e POSTGRES_PASSWORD=changeme \
  -p 5432:5432 \
  postgres:15-alpine
```

#### PostgreSQL Local Installation

```bash
# macOS
brew install postgresql
createdb cloudapp_db

# Ubuntu/Debian
sudo apt-get install postgresql postgresql-contrib
sudo -u postgres createdb cloudapp_db

# Windows
# Download and install from https://www.postgresql.org/download/windows/
```

## Running the Application

### Using Docker Compose

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Stop services
docker-compose down

# Stop and remove data
docker-compose down -v
```

### Manual Execution

```bash
# Terminal 1: Backend
cd backend
source venv/bin/activate
uvicorn backend.main:app --reload

# Terminal 2: Frontend
cd frontend
npm start
```

### Health Check

```bash
./scripts/health-check.sh
```

## Database Migrations

### Create New Migration

```bash
alembic revision --autogenerate -m "Description of changes"
```

### Run Migrations

```bash
alembic upgrade head
```

### Rollback Migration

```bash
alembic downgrade -1
```

### View Migration History

```bash
alembic history
```

## Testing

### Backend Tests

```bash
cd backend

# Run all tests
pytest

# Run with coverage
pytest --cov=backend

# Run specific test
pytest tests/test_auth.py::test_login
```

### Frontend Tests

```bash
cd frontend

# Run tests
npm test

# Run with coverage
npm test -- --coverage
```

### Integration Tests

```bash
docker-compose up -d
# Tests run against docker containers
pytest tests/integration/
```

## API Documentation

Once the backend is running, access API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

## Development Tips

### 1. Hot Reload

Both backend and frontend support hot reload:

**Backend**: Change Python files → automatically reloads
**Frontend**: Change JavaScript/CSS → automatically reloads

### 2. Database Reset

```bash
# Drop all tables (WARNING: Destructive!)
python -c "from backend.db.database import drop_db; drop_db()"

# Recreate tables
python -c "from backend.db.database import init_db; init_db()"
```

### 3. Create Admin User

```bash
# Via API
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "username": "admin",
    "password": "securepassword"
  }'

# Then manually set is_admin = true in database
```

### 4. Generate Test Data

```bash
python scripts/generate_test_data.py
```

### 5. Monitor Logs

```bash
# Backend
docker-compose logs -f backend

# Frontend
docker-compose logs -f frontend

# All services
docker-compose logs -f
```

## Troubleshooting

### Database Connection Issues

```bash
# Check PostgreSQL is running
pg_isready -h localhost -p 5432

# Test connection
psql -h localhost -U cloudapp_user -d cloudapp_db

# View recent logs
docker-compose logs postgres
```

### Port Already in Use

```bash
# Find process using port
lsof -i :8000  # Backend
lsof -i :3000  # Frontend
lsof -i :5432  # Database

# Kill process
kill -9 <PID>
```

### Permission Denied Errors

```bash
# Fix file permissions
chmod +x scripts/*.sh

# Docker volume permissions (Linux)
sudo chown -R 1000:1000 ./uploads
```

### Memory Issues with Docker

```bash
# Increase Docker memory
# Edit Docker Desktop settings: Preferences → Resources → Memory

# Or limit containers
docker-compose down
docker system prune -a
docker-compose up -d
```

### Dependency Issues

```bash
# Clear cache and reinstall backend
rm -rf backend/venv
python3 -m venv backend/venv
source backend/venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Clear cache and reinstall frontend
rm -rf frontend/node_modules
npm install
```

## Next Steps

- Read [API Documentation](./API.md)
- Read [Deployment Guide](./DEPLOYMENT.md)
- Read [Architecture Guide](./ARCHITECTURE.md)
- Read [Troubleshooting Guide](./TROUBLESHOOTING.md)

## Support

For issues and questions:
1. Check [TROUBLESHOOTING.md](./TROUBLESHOOTING.md)
2. Check existing issues on GitHub
3. Open a new issue with detailed information

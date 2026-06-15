# CloudApp - Troubleshooting Guide

Soluciones a problemas comunes durante el desarrollo y despliegue.

## Table of Contents

- [Installation Issues](#installation-issues)
- [Runtime Issues](#runtime-issues)
- [Database Issues](#database-issues)
- [Docker Issues](#docker-issues)
- [Deployment Issues](#deployment-issues)
- [Performance Issues](#performance-issues)
- [Security Issues](#security-issues)
- [Getting Help](#getting-help)

## Installation Issues

### Python Dependencies Installation Fails

**Problem**: `pip install -r requirements.txt` fails

**Solutions**:
```bash
# 1. Upgrade pip
pip install --upgrade pip

# 2. Use specific Python version
python3.11 -m pip install -r requirements.txt

# 3. Install system dependencies (Linux)
sudo apt-get install python3.11-dev python3-pip

# 4. Clear cache and retry
pip cache purge
pip install -r requirements.txt

# 5. Install one package at a time to find problematic one
pip install fastapi
pip install uvicorn
# ... etc
```

### Node Modules Installation Fails

**Problem**: `npm install` fails

**Solutions**:
```bash
# 1. Clear npm cache
npm cache clean --force

# 2. Delete package-lock.json and reinstall
rm package-lock.json
npm install

# 3. Use npm ci instead of install
npm ci

# 4. Check Node version
node --version  # Should be 18+

# 5. Install with legacy peer deps
npm install --legacy-peer-deps
```

### PostgreSQL Connection Fails

**Problem**: `psycopg2` installation fails

**Solutions**:
```bash
# Linux
sudo apt-get install libpq-dev

# macOS
brew install postgresql

# Windows
# Download from postgresql.org or use Windows Subsystem for Linux
```

## Runtime Issues

### Backend Won't Start

**Problem**: Backend crashes on startup

**Solutions**:
```bash
# 1. Check logs
docker-compose logs backend

# 2. Verify Python syntax
python -m py_compile backend/main.py

# 3. Check imports
python -c "from backend.main import app"

# 4. Check environment variables
echo $DATABASE_URL
echo $SECRET_KEY

# 5. Run with verbose logging
PYTHONVERBOSE=2 uvicorn backend.main:app
```

### Frontend Won't Load

**Problem**: Frontend shows blank page or 404

**Solutions**:
```bash
# 1. Check build
npm run build

# 2. Clear cache
rm -rf node_modules
npm install

# 3. Check environment variables in .env
REACT_APP_API_URL=http://localhost:8000

# 4. Check console for errors
# Open browser DevTools → Console tab

# 5. Verify backend is running
curl http://localhost:8000/health

# 6. Clear browser cache
# Ctrl+Shift+Delete (Windows) or Cmd+Shift+Delete (Mac)
```

### API Endpoints Return 404

**Problem**: GET/POST requests return 404

**Solutions**:
```bash
# 1. Check API is running
curl http://localhost:8000/health

# 2. Check endpoint path
# /api/v1/users, NOT /users

# 3. Check HTTP method
# POST for create, GET for read, etc

# 4. Verify authentication
curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:8000/api/v1/users/me

# 5. Check logs
docker-compose logs backend

# 6. Verify router is included
# Check backend/main.py includes all routers
```

### Authentication Token Expired

**Problem**: 401 Unauthorized errors

**Solutions**:
```bash
# 1. Get new token
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password"}'

# 2. Use refresh token
curl -X POST http://localhost:8000/api/v1/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{"refresh_token":"your_refresh_token"}'

# 3. Check token expiration in .env
ACCESS_TOKEN_EXPIRE_MINUTES=30

# 4. Increase token expiration (development only)
ACCESS_TOKEN_EXPIRE_MINUTES=1440  # 24 hours
```

## Database Issues

### Can't Connect to PostgreSQL

**Problem**: `psycopg2.OperationalError: could not connect to server`

**Solutions**:
```bash
# 1. Check if PostgreSQL is running
pg_isready -h localhost -p 5432

# 2. Check connection string
echo $DATABASE_URL
# Should be: postgresql://user:password@localhost:5432/dbname

# 3. Check credentials
psql -h localhost -U cloudapp_user -d cloudapp_db

# 4. Start PostgreSQL service
# macOS
brew services start postgresql

# Linux
sudo systemctl start postgresql

# 5. Check port is listening
netstat -tlnp | grep 5432

# 6. Check firewall
sudo ufw allow 5432
```

### Database Migrations Fail

**Problem**: `alembic upgrade head` fails

**Solutions**:
```bash
# 1. Check current revision
alembic current

# 2. View migration history
alembic history

# 3. Check for syntax errors
alembic revision --autogenerate -m "test"

# 4. Downgrade to previous version
alembic downgrade -1

# 5. Check migration file syntax
nano alembic/versions/xyz_migration.py

# 6. Manual migration
psql -h localhost -U cloudapp_user -d cloudapp_db < migration.sql
```

### Data Migration Issues

**Problem**: Data lost or corrupted during migration

**Solutions**:
```bash
# 1. Backup before migration
pg_dump -h localhost -U cloudapp_user -d cloudapp_db > backup.sql

# 2. Restore from backup
psql -h localhost -U cloudapp_user -d cloudapp_db < backup.sql

# 3. Check data integrity
SELECT COUNT(*) FROM users;

# 4. Verify constraints
SELECT constraint_name FROM information_schema.table_constraints WHERE table_name='users';
```

### Database Locked

**Problem**: `database is locked` errors

**Solutions**:
```bash
# 1. View active connections
SELECT pid, usename, application_name, state FROM pg_stat_activity;

# 2. Kill long-running query
SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE duration > interval '1 hour';

# 3. Check for deadlocks
SELECT * FROM pg_locks WHERE NOT granted;

# 4. Restart PostgreSQL
sudo systemctl restart postgresql

# 5. Increase timeout in config
# Edit postgresql.conf
statement_timeout = '30s'
```

## Docker Issues

### Docker Compose Won't Start

**Problem**: `docker-compose up` fails

**Solutions**:
```bash
# 1. Check Docker is running
docker ps

# 2. Rebuild images
docker-compose build --no-cache

# 3. Check for syntax errors
docker-compose config

# 4. View detailed logs
docker-compose up --verbose

# 5. Remove volumes and restart
docker-compose down -v
docker-compose up

# 6. Check Docker daemon
docker info
```

### Container Exits Immediately

**Problem**: Container starts and stops quickly

**Solutions**:
```bash
# 1. Check logs
docker-compose logs -f backend

# 2. Run with interactive shell
docker run -it cloudapp-backend /bin/bash

# 3. Check for missing environment variables
docker-compose config | grep -A20 backend

# 4. Verify CMD in Dockerfile
cat docker/Dockerfile.backend

# 5. Test locally first
python -m backend.main
```

### Port Already in Use

**Problem**: `Address already in use` error

**Solutions**:
```bash
# 1. Find process using port
lsof -i :8000
lsof -i :3000
lsof -i :5432

# 2. Kill process
kill -9 <PID>

# 3. Use different port
docker run -p 8001:8000 cloudapp-backend

# 4. Or update docker-compose.yml
# Change ports: "8000:8000" to "8001:8000"

# 5. Use port scanner
netstat -tlnp | grep LISTEN
```

### Volume Mount Issues

**Problem**: Files not syncing between host and container

**Solutions**:
```bash
# 1. Check volume is mounted
docker inspect cloudapp-backend | grep -A10 Mounts

# 2. Fix permissions (Linux)
chmod -R 777 uploads/

# 3. Restart Docker daemon
sudo systemctl restart docker

# 4. Check docker-compose.yml syntax
docker-compose config

# 5. Use absolute paths
# Change: ./uploads to /full/path/to/uploads
```

## Deployment Issues

### Deployment Script Fails

**Problem**: `./scripts/deploy.sh` fails

**Solutions**:
```bash
# 1. Check script permissions
chmod +x scripts/deploy.sh

# 2. Check bash syntax
bash -n scripts/deploy.sh

# 3. Run with debug output
bash -x scripts/deploy.sh

# 4. Check prerequisites
./scripts/deploy.sh | head -20

# 5. Check cloud CLI tools
aws --version
az --version
gcloud --version
```

### AWS Deployment Fails

**Problem**: ECS/ECR deployment fails

**Solutions**:
```bash
# 1. Check AWS credentials
aws sts get-caller-identity

# 2. Check ECR repository exists
aws ecr describe-repositories --repository-names cloudapp-backend

# 3. Login to ECR
aws ecr get-login-password | docker login --username AWS --password-stdin <ACCOUNT>.dkr.ecr.<REGION>.amazonaws.com

# 4. Check ECS cluster
aws ecs list-clusters

# 5. View task logs
aws ecs describe-tasks --cluster cloudapp-cluster --tasks <TASK_ARN>

# 6. Check CloudWatch logs
aws logs tail /ecs/cloudapp --follow
```

### Certificate Issues

**Problem**: SSL certificate errors in production

**Solutions**:
```bash
# 1. Generate self-signed certificate (development)
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes

# 2. Check certificate validity
openssl x509 -in cert.pem -text -noout

# 3. Update nginx config to use certificate
# In docker/nginx.conf:
# listen 443 ssl;
# ssl_certificate /etc/nginx/certs/cert.pem;
# ssl_certificate_key /etc/nginx/certs/key.pem;

# 4. Use Let's Encrypt (production)
# Via certbot or cloud provider
```

## Performance Issues

### Slow API Responses

**Problem**: API endpoints are slow

**Solutions**:
```bash
# 1. Check database query performance
EXPLAIN ANALYZE SELECT * FROM orders WHERE user_id = 1;

# 2. Check slow query log
SELECT * FROM pg_stat_statements ORDER BY mean_time DESC;

# 3. Add indexes
CREATE INDEX idx_orders_user_id ON orders(user_id);

# 4. Check memory usage
docker stats cloudapp-backend

# 5. Profile code
python -m cProfile -s cumulative backend/main.py

# 6. Check response times
curl -w "@curl-format.txt" -o /dev/null -s http://localhost:8000/api/v1/users
```

### High Memory Usage

**Problem**: Container uses excessive memory

**Solutions**:
```bash
# 1. Check memory limit
docker inspect cloudapp-backend | grep Memory

# 2. Increase memory limit
# In docker-compose.yml:
# deploy:
#   resources:
#     limits:
#       memory: 1G

# 3. Check for memory leaks
docker stats --no-stream

# 4. Profile memory usage
pip install memory-profiler
python -m memory_profiler backend/main.py

# 5. Optimize imports
# Remove unused imports from backend/main.py
```

### Database Query Timeout

**Problem**: Queries taking too long

**Solutions**:
```bash
# 1. Check query plan
EXPLAIN ANALYZE SELECT * FROM inventory WHERE category = 'Electronics';

# 2. Add missing indexes
CREATE INDEX idx_inventory_category ON inventory(category);

# 3. Increase query timeout
# In config.py:
# DB_POOL_TIMEOUT = 30

# 4. Optimize query
# Use pagination, select specific columns
SELECT id, name FROM inventory LIMIT 10;

# 5. Enable connection pooling
# Using PgBouncer or SQLAlchemy pool
```

## Security Issues

### Security Vulnerability in Dependencies

**Problem**: `npm audit` or `pip audit` shows vulnerabilities

**Solutions**:
```bash
# 1. Check vulnerabilities
npm audit
pip audit

# 2. Update packages
npm update
pip install --upgrade -r requirements.txt

# 3. Fix specific package
npm install package@latest
pip install --upgrade package

# 4. Accept risk (not recommended)
npm audit fix --force

# 5. Use lock file to reproduce issue
npm ci  # or pip install -r requirements.txt
```

### Secret Exposure

**Problem**: Secrets committed to Git

**Solutions**:
```bash
# 1. Immediately rotate secrets
# Change all compromised API keys, passwords, tokens

# 2. Remove from history
git filter-branch --tree-filter 'rm -f .env' HEAD

# 3. Or use BFG Repo-Cleaner
bfg --delete-files .env

# 4. Add to .gitignore
echo ".env" >> .gitignore
echo ".env.local" >> .gitignore

# 5. Use secret scanning
# Enable branch protection rules on GitHub

# 6. Check for accidental commits
git log --all --oneline | grep -i secret
```

### CORS Errors

**Problem**: `Access to XMLHttpRequest blocked by CORS policy`

**Solutions**:
```bash
# 1. Check backend CORS configuration
# In backend/config.py:
# CORS_ORIGINS = ["http://localhost:3000", ...]

# 2. Add frontend origin
# CORS_ORIGINS.append("http://localhost:3000")

# 3. Update docker-compose.yml
# CORS_ORIGINS=http://localhost:3000,http://localhost:8000

# 4. Check nginx configuration
# Allow CORS headers in docker/nginx.conf

# 5. Verify request headers
# Check "Origin" header is in allowed list
```

## Getting Help

### Debug Information to Collect

When reporting an issue, include:
1. Error message (full traceback)
2. Steps to reproduce
3. Environment info (OS, Python version, Node version)
4. Relevant logs
5. Configuration (with secrets removed)
6. Docker/deployment information

### Useful Debug Commands

```bash
# Check system info
uname -a
python --version
node --version
docker --version

# Database info
psql --version
pg_isready -V

# Network debugging
netstat -tlnp
ss -tlnp

# Docker debugging
docker-compose config
docker ps
docker logs <container>
docker inspect <container>

# Frontend debugging
npm run build
npm run test
npm run lint

# Backend debugging
pytest -v
flake8 backend/
black --check backend/
```

### Reporting Issues

1. **GitHub Issues**: https://github.com/your-org/cloudapp/issues
2. **Documentation**: Check [README.md](../README.md), [SETUP.md](./SETUP.md)
3. **Discussions**: Use GitHub Discussions for questions
4. **Security**: Report security issues privately to security@cloudapp.com

### Community Support

- **Documentation**: Read setup and deployment guides
- **Examples**: Check example scripts and configurations
- **Stack Overflow**: Tag questions with `cloudapp`
- **Discussions**: Engage in GitHub Discussions

## Common Fixes Summary

| Issue | Quick Fix |
|-------|-----------|
| Backend won't start | Check logs: `docker-compose logs backend` |
| Frontend won't load | Clear cache: `rm -rf node_modules && npm install` |
| Database connection fails | Check PostgreSQL: `pg_isready -h localhost` |
| Port in use | Kill process: `lsof -i :8000 \| kill -9` |
| Docker won't start | Rebuild: `docker-compose build --no-cache` |
| API returns 401 | Get new token: `POST /api/v1/auth/login` |
| Slow queries | Add index: `CREATE INDEX idx_name ON table(column)` |
| CORS errors | Add origin to CORS_ORIGINS |
| Secrets leaked | Rotate keys immediately |
| Out of memory | Increase limits or optimize code |

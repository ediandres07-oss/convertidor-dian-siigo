# CloudApp - Architecture Guide

Descripción detallada de la arquitectura de CloudApp.

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Load Balancer / CDN                       │
│                  (CloudFront, Akamai, etc)                   │
└─────────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
    ┌───▼───┐          ┌───▼───┐          ┌───▼──┐
    │Nginx  │          │Nginx  │          │Nginx │
    │(AZ1)  │          │(AZ2)  │          │(AZ3) │
    └───┬───┘          └───┬───┘          └───┬──┘
        │                  │                  │
    ┌───▼────────┐    ┌────▼────────┐   ┌────▼────────┐
    │  Frontend  │    │  Frontend   │   │  Frontend   │
    │  React 3000│    │  React 3000 │   │  React 3000 │
    └───┬────────┘    └────┬────────┘   └────┬────────┘
        │                  │                  │
        └──────────────────┼──────────────────┘
                           │
    ┌──────────────────────┼──────────────────────┐
    │                      │                      │
┌───▼────────┐        ┌───▼────────┐        ┌───▼────────┐
│  Backend   │        │  Backend   │        │  Backend   │
│ FastAPI   │        │ FastAPI    │        │ FastAPI    │
│  8000     │        │   8000     │        │   8000     │
└───┬────────┘        └───┬────────┘        └───┬────────┘
    │                     │                     │
    └─────────────────────┼─────────────────────┘
                          │
                ┌─────────┴──────────┐
                │                    │
            ┌───▼───────┐       ┌────▼────┐
            │ PostgreSQL │       │  Redis  │
            │  (Primary) │       │  Cache  │
            └───┬───────┘       └────┬────┘
                │
            ┌───▼───────┐
            │PostgreSQL │
            │ (Replica) │
            └───────────┘

        ┌─────────────────────────────────┐
        │   Cloud Storage (S3/Azure/GCS)  │
        │     File Uploads                │
        └─────────────────────────────────┘
```

## Components

### Frontend (React)

**Location**: `frontend/`

**Technology**:
- React 18
- Redux Toolkit
- Axios
- React Router
- Material-UI / Tailwind CSS

**Responsibilities**:
- User interface
- Authentication handling
- API communication
- State management
- Form validation
- File uploads

**Key Features**:
- Responsive design
- Progressive Web App (PWA) ready
- Offline support via service workers
- Real-time notifications (optional WebSocket)

### Backend (FastAPI)

**Location**: `backend/`

**Technology**:
- FastAPI
- SQLAlchemy ORM
- Pydantic
- pytest

**Core Modules**:
- **main.py**: Application entry point
- **config.py**: Configuration management
- **models/**: SQLAlchemy ORM models
- **schemas/**: Pydantic validation schemas
- **routers/**: API endpoints
- **services/**: Business logic
- **core/**: Security, logging, storage

**Key Features**:
- RESTful API
- JWT authentication
- CORS support
- Request validation
- Error handling
- Logging

### Database (PostgreSQL)

**Technology**: PostgreSQL 15+

**Tables**:
- `users`: User accounts and profiles
- `orders`: Order management
- `inventory`: Product inventory
- `inventory_movements`: Stock movement history

**Key Features**:
- Transaction support
- Full-text search
- JSON columns for metadata
- Indexes for performance
- Automatic timestamps

### Cache (Redis)

**Purpose**:
- Session caching
- Request rate limiting
- Query result caching
- Real-time data

**Configuration**:
- Single instance for development
- Cluster for production

### Cloud Storage

**Supported Backends**:
- AWS S3
- Azure Blob Storage
- Google Cloud Storage
- Local filesystem (development)

**Usage**:
- File uploads
- Document storage
- Backup storage

## API Architecture

### Request Flow

```
Request
  ↓
Nginx (reverse proxy)
  ↓
FastAPI App
  ↓
Auth Middleware (JWT validation)
  ↓
Router (endpoint matching)
  ↓
Service Layer (business logic)
  ↓
Database Layer (ORM queries)
  ↓
Response
```

### Authentication Flow

```
1. User submits credentials
2. Backend validates against database
3. Backend generates JWT tokens (access + refresh)
4. Client stores tokens in localStorage/sessionStorage
5. Client includes access token in Authorization header
6. Backend validates token on each request
7. Refresh token used to get new access token when expired
```

### Error Handling

```
Request Error
  ↓
Exception caught in middleware
  ↓
Error logged
  ↓
Error response formatted
  ↓
Client receives error with detail and status code
```

## Database Schema

### Users Table

```sql
CREATE TABLE users (
  id INT PRIMARY KEY,
  email VARCHAR UNIQUE,
  username VARCHAR UNIQUE,
  full_name VARCHAR,
  hashed_password VARCHAR,
  is_active BOOLEAN,
  is_admin BOOLEAN,
  role ENUM,
  created_at TIMESTAMP,
  updated_at TIMESTAMP
);
```

### Orders Table

```sql
CREATE TABLE orders (
  id INT PRIMARY KEY,
  order_number VARCHAR UNIQUE,
  user_id INT FOREIGN KEY,
  status ENUM,
  total_amount FLOAT,
  discount FLOAT,
  tax FLOAT,
  final_amount FLOAT,
  items JSON,
  order_date TIMESTAMP,
  created_at TIMESTAMP,
  updated_at TIMESTAMP
);
```

### Inventory Table

```sql
CREATE TABLE inventory (
  id INT PRIMARY KEY,
  sku VARCHAR UNIQUE,
  name VARCHAR,
  category VARCHAR,
  quantity INT,
  cost_price FLOAT,
  selling_price FLOAT,
  warehouse VARCHAR,
  created_at TIMESTAMP,
  updated_at TIMESTAMP
);
```

## Security Architecture

### Authentication & Authorization

- **JWT Tokens**: Stateless authentication
- **Refresh Tokens**: Extended session management
- **Password Hashing**: bcrypt with 12 rounds
- **Role-Based Access Control (RBAC)**:
  - Admin: Full access
  - Manager: Limited operations
  - User: Own data access

### Data Protection

- **Encryption at Rest**: Database + Cloud storage encryption
- **Encryption in Transit**: TLS 1.3
- **Secrets Management**: Environment variables, AWS Secrets Manager
- **Input Validation**: Pydantic schemas
- **SQL Injection Prevention**: SQLAlchemy ORM

### Security Headers

```
Strict-Transport-Security: max-age=31536000; includeSubDomains
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Referrer-Policy: strict-origin-when-cross-origin
Content-Security-Policy: default-src 'self'
```

## Scaling Strategy

### Horizontal Scaling

**Frontend**:
- Multiple instances behind load balancer
- Static files served by CDN
- Stateless application

**Backend**:
- Multiple instances behind load balancer
- Horizontal pod autoscaling (Kubernetes)
- Database connection pooling

**Database**:
- Primary-replica replication
- Read replicas for read-heavy operations
- Database sharding (if needed)

### Vertical Scaling

- Increase container resources
- Increase database instance size
- Increase cache memory

### Caching Strategy

- **Client-side**: Browser cache for static assets
- **CDN**: Edge caching for content
- **Server-side**: Redis for expensive queries
- **Database**: Query caching

## Disaster Recovery

### Backup Strategy

- **Database**: Daily automated backups, 30-day retention
- **Files**: Cloud storage with versioning
- **Code**: Git repository with remote backup

### High Availability

- **Multi-AZ deployment**: Spread across availability zones
- **Load balancing**: Distribute traffic
- **Auto-scaling**: Scale based on demand
- **Database replication**: Primary-replica setup

### Recovery Procedures

1. **RTO (Recovery Time Objective)**: < 1 hour
2. **RPO (Recovery Point Objective)**: < 15 minutes
3. **Failover**: Automatic for database replicas
4. **Manual recovery**: Documented procedures

## Monitoring & Observability

### Metrics

- Request latency
- Error rate
- Database query time
- Cache hit rate
- Memory usage
- CPU usage
- Network I/O

### Logging

- **Structured logging**: JSON format
- **Centralized logging**: CloudWatch, ELK, Datadog
- **Log levels**: DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Log retention**: 30 days

### Tracing

- Request tracing with unique IDs
- Performance profiling
- Distributed tracing (optional)

## CI/CD Pipeline

```
Code Push
  ↓
Run Tests
  ↓
Build Docker Images
  ↓
Push to Registry
  ↓
Deploy to Staging
  ↓
Run Integration Tests
  ↓
Deploy to Production
  ↓
Health Checks
  ↓
Monitoring
```

## Development Workflow

1. **Feature Branch**: Create from `develop`
2. **Local Testing**: Run tests and checks
3. **Pull Request**: Code review
4. **CI Pipeline**: Automated tests
5. **Merge**: To develop branch
6. **Release**: Tag and deploy to production

## Technology Stack Summary

| Layer | Technology |
|-------|-----------|
| **Frontend** | React, Redux, TypeScript |
| **Backend** | FastAPI, Python 3.11 |
| **Database** | PostgreSQL 15 |
| **Cache** | Redis 7 |
| **Storage** | AWS S3 / Azure / GCP |
| **Authentication** | JWT, bcrypt |
| **Web Server** | Nginx |
| **Containerization** | Docker |
| **Orchestration** | Docker Compose, Kubernetes |
| **CI/CD** | GitHub Actions, GitLab CI |
| **Monitoring** | CloudWatch, Datadog, Prometheus |
| **Logging** | ELK, Loki, CloudWatch |

## Best Practices

### Code Quality

- Type hints (Python, TypeScript)
- Linting (pylint, ESLint)
- Code formatting (Black, Prettier)
- Unit tests (pytest, Jest)
- Integration tests
- End-to-end tests

### Performance

- Database indexing
- Query optimization
- Caching strategy
- CDN for static files
- Lazy loading
- Code splitting

### Security

- Regular security audits
- Dependency scanning
- Secret management
- Access control
- Rate limiting
- Input validation

### Maintainability

- Clear code organization
- Comprehensive documentation
- API versioning
- Backward compatibility
- Database migrations
- Changelog

## Future Enhancements

- [ ] GraphQL API alternative
- [ ] Real-time features (WebSocket)
- [ ] Machine learning recommendations
- [ ] Mobile app (React Native)
- [ ] Blockchain integration (optional)
- [ ] Advanced analytics
- [ ] Micro-services architecture
- [ ] Event-driven architecture

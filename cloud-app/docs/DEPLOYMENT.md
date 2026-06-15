# CloudApp - Deployment Guide

Guía para desplegar CloudApp en AWS, Azure, GCP y Kubernetes.

## Table of Contents

- [AWS Deployment](#aws-deployment)
- [Azure Deployment](#azure-deployment)
- [GCP Deployment](#gcp-deployment)
- [Kubernetes Deployment](#kubernetes-deployment)
- [Production Checklist](#production-checklist)
- [Monitoring & Logging](#monitoring--logging)
- [Scaling](#scaling)

## AWS Deployment

### Prerequisites

- AWS Account
- AWS CLI configured
- ECR repository created
- RDS PostgreSQL instance
- ECS Cluster

### Step 1: Prepare AWS Credentials

```bash
aws configure
# Enter your AWS Access Key ID and Secret Access Key
```

### Step 2: Create ECR Repository

```bash
aws ecr create-repository --repository-name cloudapp-backend
aws ecr create-repository --repository-name cloudapp-frontend
```

### Step 3: Build and Push Images

```bash
./scripts/deploy.sh production aws

# Or manually:
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
REGION=us-east-1
REGISTRY="${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com"

# Login
aws ecr get-login-password --region $REGION | docker login --username AWS --password-stdin $REGISTRY

# Build and push backend
docker build -t cloudapp-backend:latest -f docker/Dockerfile.backend .
docker tag cloudapp-backend:latest ${REGISTRY}/cloudapp-backend:latest
docker push ${REGISTRY}/cloudapp-backend:latest

# Build and push frontend
docker build -t cloudapp-frontend:latest -f docker/Dockerfile.frontend ./frontend
docker tag cloudapp-frontend:latest ${REGISTRY}/cloudapp-frontend:latest
docker push ${REGISTRY}/cloudapp-frontend:latest
```

### Step 4: Create RDS Database

```bash
aws rds create-db-instance \
  --db-instance-identifier cloudapp-db \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --master-username admin \
  --master-user-password changeme \
  --allocated-storage 20 \
  --publicly-accessible false
```

### Step 5: Create ECS Task Definition

```json
{
  "family": "cloudapp-backend",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "256",
  "memory": "512",
  "containerDefinitions": [
    {
      "name": "cloudapp-backend",
      "image": "${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com/cloudapp-backend:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "DATABASE_URL",
          "value": "postgresql://user:password@rds-endpoint:5432/cloudapp_db"
        },
        {
          "name": "SECRET_KEY",
          "value": "your-secret-key"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/cloudapp",
          "awslogs-region": "${REGION}",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

### Step 6: Create ECS Service

```bash
aws ecs create-service \
  --cluster cloudapp-cluster \
  --service-name cloudapp-service \
  --task-definition cloudapp-backend \
  --desired-count 2 \
  --launch-type FARGATE \
  --network-configuration awsvpcConfiguration={subnets=[subnet-xxx],securityGroups=[sg-xxx],assignPublicIp=ENABLED} \
  --load-balancers targetGroupArn=arn:aws:elasticloadbalancing:...,containerName=cloudapp-backend,containerPort=8000
```

### Step 7: Configure Auto Scaling

```bash
aws autoscaling create-auto-scaling-group \
  --auto-scaling-group-name cloudapp-asg \
  --launch-configuration cloudapp-lc \
  --min-size 2 \
  --max-size 10 \
  --desired-capacity 2 \
  --availability-zones us-east-1a us-east-1b
```

### Step 8: Set Up CloudWatch Monitoring

```bash
aws cloudwatch put-metric-alarm \
  --alarm-name cloudapp-high-cpu \
  --alarm-description "Alert when CPU is high" \
  --metric-name CPUUtilization \
  --namespace AWS/ECS \
  --statistic Average \
  --period 300 \
  --threshold 80 \
  --comparison-operator GreaterThanThreshold
```

## Azure Deployment

### Prerequisites

- Azure Account
- Azure CLI installed
- Azure Container Registry
- Azure Database for PostgreSQL

### Step 1: Set Up Azure Resources

```bash
# Login
az login

# Create resource group
az group create --name cloudapp-rg --location eastus

# Create container registry
az acr create --resource-group cloudapp-rg --name cloudappacr --sku Basic
```

### Step 2: Build and Push Images

```bash
az acr build \
  --registry cloudappacr \
  --image cloudapp-backend:latest \
  --file docker/Dockerfile.backend \
  .

az acr build \
  --registry cloudappacr \
  --image cloudapp-frontend:latest \
  --file docker/Dockerfile.frontend \
  ./frontend
```

### Step 3: Create PostgreSQL Server

```bash
az postgres server create \
  --resource-group cloudapp-rg \
  --name cloudapp-db \
  --admin-user dbadmin \
  --admin-password changeme \
  --sku-name B_Gen5_2 \
  --storage-size 51200
```

### Step 4: Deploy with App Service

```bash
# Create App Service Plan
az appservice plan create \
  --name cloudapp-plan \
  --resource-group cloudapp-rg \
  --sku B1 \
  --is-linux

# Create Web Apps
az webapp create \
  --resource-group cloudapp-rg \
  --plan cloudapp-plan \
  --name cloudapp-backend \
  --deployment-container-image-name cloudappacr.azurecr.io/cloudapp-backend:latest

# Configure environment variables
az webapp config appsettings set \
  --resource-group cloudapp-rg \
  --name cloudapp-backend \
  --settings \
    DATABASE_URL=postgresql://... \
    SECRET_KEY=your-secret-key
```

### Step 5: Configure Autoscaling

```bash
az monitor autoscale create \
  --resource-group cloudapp-rg \
  --resource cloudapp-plan \
  --resource-type "Microsoft.Web/serverfarms" \
  --name cloudapp-autoscale \
  --min-count 2 \
  --max-count 10 \
  --count 2
```

## GCP Deployment

### Prerequisites

- GCP Account
- gcloud CLI installed
- GCP Project created

### Step 1: Configure gcloud

```bash
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
```

### Step 2: Create Artifact Registry

```bash
gcloud artifacts repositories create cloudapp \
  --repository-format=docker \
  --location=us-central1
```

### Step 3: Build and Push Images

```bash
gcloud builds submit \
  --tag us-central1-docker.pkg.dev/PROJECT_ID/cloudapp/backend:latest \
  --file docker/Dockerfile.backend \
  .

gcloud builds submit \
  --tag us-central1-docker.pkg.dev/PROJECT_ID/cloudapp/frontend:latest \
  --file docker/Dockerfile.frontend \
  ./frontend
```

### Step 4: Create Cloud SQL Instance

```bash
gcloud sql instances create cloudapp-db \
  --database-version=POSTGRES_15 \
  --tier=db-f1-micro \
  --region=us-central1 \
  --availability-type=REGIONAL
```

### Step 5: Deploy to Cloud Run

```bash
# Backend
gcloud run deploy cloudapp-backend \
  --image us-central1-docker.pkg.dev/PROJECT_ID/cloudapp/backend:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars \
    DATABASE_URL=postgresql://...,\
    SECRET_KEY=your-secret-key \
  --memory 512Mi \
  --cpu 1

# Frontend
gcloud run deploy cloudapp-frontend \
  --image us-central1-docker.pkg.dev/PROJECT_ID/cloudapp/frontend:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

## Kubernetes Deployment

### Prerequisites

- Kubernetes cluster (EKS, AKS, GKE)
- kubectl installed and configured
- Helm 3+ (optional)

### Step 1: Create Namespaces and Secrets

```bash
kubectl create namespace cloudapp

# Create database secret
kubectl create secret generic db-credentials \
  --from-literal=username=dbuser \
  --from-literal=password=dbpassword \
  -n cloudapp

# Create app secret
kubectl create secret generic app-secrets \
  --from-literal=secret-key=your-secret-key \
  -n cloudapp
```

### Step 2: Deploy PostgreSQL

```bash
kubectl apply -f k8s/postgres-deployment.yml
```

### Step 3: Deploy Backend

```bash
kubectl apply -f k8s/backend-deployment.yml
```

### Step 4: Deploy Frontend

```bash
kubectl apply -f k8s/frontend-deployment.yml
```

### Step 5: Deploy Service and Ingress

```bash
kubectl apply -f k8s/service.yml
kubectl apply -f k8s/ingress.yml
```

### Step 6: Verify Deployment

```bash
# Check pods
kubectl get pods -n cloudapp

# Check services
kubectl get svc -n cloudapp

# Check ingress
kubectl get ingress -n cloudapp

# View logs
kubectl logs -n cloudapp -l app=cloudapp-backend
```

## Production Checklist

- [ ] Environment variables configured for production
- [ ] SSL/TLS certificates installed
- [ ] Database backups configured
- [ ] Monitoring and alerting set up
- [ ] Log aggregation configured
- [ ] Database migrations ran successfully
- [ ] Static files configured (CDN)
- [ ] Email service configured
- [ ] API documentation accessible
- [ ] Health checks passing
- [ ] Auto-scaling configured
- [ ] Disaster recovery plan in place
- [ ] Security audit completed
- [ ] Load testing completed
- [ ] Documentation updated

## Monitoring & Logging

### CloudWatch (AWS)

```bash
# View logs
aws logs tail /ecs/cloudapp --follow

# Create metric alarm
aws cloudwatch put-metric-alarm \
  --alarm-name cloudapp-error-rate \
  --metric-name ErrorCount \
  --threshold 10
```

### Application Insights (Azure)

```bash
az monitor app-insights create \
  --resource-group cloudapp-rg \
  --application cloudapp-insights
```

### Cloud Logging (GCP)

```bash
gcloud logging read "resource.type=cloud_run_revision" --limit 10
```

### Sentry Integration

Set `SENTRY_DSN` environment variable for error tracking.

## Scaling

### Horizontal Scaling

Configure autoscaling based on metrics:

```yaml
# Example: Scale based on CPU
targetCPUUtilizationPercentage: 70
minReplicas: 2
maxReplicas: 10
```

### Vertical Scaling

Increase resource limits:
- CPU
- Memory
- Storage

### Database Scaling

- Enable read replicas
- Use connection pooling
- Implement caching (Redis)

## Cleanup

To remove resources:

```bash
# AWS
aws ecs delete-service --cluster cloudapp --service cloudapp-service
aws ec2 delete-security-group --group-id sg-xxx

# Azure
az group delete --name cloudapp-rg

# GCP
gcloud run services delete cloudapp-backend
gcloud sql instances delete cloudapp-db

# Kubernetes
kubectl delete namespace cloudapp
```

## Support

For deployment issues:
1. Check cloud provider documentation
2. Review logs with `./scripts/health-check.sh`
3. Check [TROUBLESHOOTING.md](./TROUBLESHOOTING.md)

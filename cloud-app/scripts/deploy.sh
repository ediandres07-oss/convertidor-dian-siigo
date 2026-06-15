#!/bin/bash

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
ENVIRONMENT=${1:-development}
CLOUD_PROVIDER=${2:-aws}
VERSION=$(git describe --tags --always 2>/dev/null || echo "latest")

echo -e "${YELLOW}Deploying CloudApp (${VERSION})${NC}"
echo -e "${YELLOW}Environment: ${ENVIRONMENT}${NC}"
echo -e "${YELLOW}Cloud Provider: ${CLOUD_PROVIDER}${NC}"

# Function to check prerequisites
check_prerequisites() {
    echo -e "${YELLOW}Checking prerequisites...${NC}"

    if ! command -v docker &> /dev/null; then
        echo -e "${RED}Docker is not installed${NC}"
        exit 1
    fi

    if [ "$CLOUD_PROVIDER" = "aws" ]; then
        if ! command -v aws &> /dev/null; then
            echo -e "${RED}AWS CLI is not installed${NC}"
            exit 1
        fi
    elif [ "$CLOUD_PROVIDER" = "azure" ]; then
        if ! command -v az &> /dev/null; then
            echo -e "${RED}Azure CLI is not installed${NC}"
            exit 1
        fi
    elif [ "$CLOUD_PROVIDER" = "gcp" ]; then
        if ! command -v gcloud &> /dev/null; then
            echo -e "${RED}GCP CLI is not installed${NC}"
            exit 1
        fi
    fi

    echo -e "${GREEN}Prerequisites check passed${NC}"
}

# Function to build Docker images
build_images() {
    echo -e "${YELLOW}Building Docker images...${NC}"

    docker-compose build --no-cache

    echo -e "${GREEN}Docker images built successfully${NC}"
}

# Function to deploy to AWS
deploy_aws() {
    echo -e "${YELLOW}Deploying to AWS...${NC}"

    # Push images to ECR
    echo -e "${YELLOW}Pushing images to ECR...${NC}"
    ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
    REGION=${AWS_REGION:-us-east-1}
    REGISTRY="${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com"

    # Login to ECR
    aws ecr get-login-password --region $REGION | docker login --username AWS --password-stdin $REGISTRY

    # Tag and push backend
    docker tag cloudapp-backend:latest ${REGISTRY}/cloudapp-backend:${VERSION}
    docker push ${REGISTRY}/cloudapp-backend:${VERSION}

    # Tag and push frontend
    docker tag cloudapp-frontend:latest ${REGISTRY}/cloudapp-frontend:${VERSION}
    docker push ${REGISTRY}/cloudapp-frontend:${VERSION}

    echo -e "${GREEN}Images pushed to ECR${NC}"

    # Update ECS task definitions
    echo -e "${YELLOW}Updating ECS task definitions...${NC}"
    aws ecs update-service \
        --cluster cloudapp-cluster \
        --service cloudapp-service \
        --force-new-deployment \
        --region $REGION

    echo -e "${GREEN}Deployment to AWS completed${NC}"
}

# Function to deploy to Azure
deploy_azure() {
    echo -e "${YELLOW}Deploying to Azure...${NC}"

    RESOURCE_GROUP=${AZURE_RESOURCE_GROUP:-cloudapp-rg}
    ACR_NAME=${AZURE_ACR_NAME:-cloudappacr}
    REGION=${AZURE_REGION:-eastus}

    # Build and push to ACR
    echo -e "${YELLOW}Building and pushing to Azure Container Registry...${NC}"
    az acr build \
        --registry $ACR_NAME \
        --image cloudapp-backend:${VERSION} \
        --file docker/Dockerfile.backend \
        .

    az acr build \
        --registry $ACR_NAME \
        --image cloudapp-frontend:${VERSION} \
        --file docker/Dockerfile.frontend \
        ./frontend

    echo -e "${GREEN}Images pushed to ACR${NC}"

    # Update Azure Container Instances or App Service
    echo -e "${YELLOW}Updating Azure deployment...${NC}"
    az container create \
        --resource-group $RESOURCE_GROUP \
        --name cloudapp \
        --image ${ACR_NAME}.azurecr.io/cloudapp-backend:${VERSION} \
        --environment-variables \
            DATABASE_URL=$DATABASE_URL \
            SECRET_KEY=$SECRET_KEY \
        --registry-login-server ${ACR_NAME}.azurecr.io \
        --registry-username $AZURE_REGISTRY_USERNAME \
        --registry-password $AZURE_REGISTRY_PASSWORD \
        --ports 8000 80 443

    echo -e "${GREEN}Deployment to Azure completed${NC}"
}

# Function to deploy to GCP
deploy_gcp() {
    echo -e "${YELLOW}Deploying to GCP...${NC}"

    PROJECT_ID=${GCP_PROJECT_ID}
    REGION=${GCP_REGION:-us-central1}

    # Configure gcloud
    gcloud config set project $PROJECT_ID

    # Build and push to Artifact Registry
    echo -e "${YELLOW}Building and pushing to Artifact Registry...${NC}"
    gcloud builds submit \
        --tag ${REGION}-docker.pkg.dev/${PROJECT_ID}/cloudapp/backend:${VERSION} \
        --file docker/Dockerfile.backend \
        .

    gcloud builds submit \
        --tag ${REGION}-docker.pkg.dev/${PROJECT_ID}/cloudapp/frontend:${VERSION} \
        --file docker/Dockerfile.frontend \
        ./frontend

    echo -e "${GREEN}Images pushed to Artifact Registry${NC}"

    # Deploy to Cloud Run
    echo -e "${YELLOW}Deploying to Cloud Run...${NC}"
    gcloud run deploy cloudapp-backend \
        --image ${REGION}-docker.pkg.dev/${PROJECT_ID}/cloudapp/backend:${VERSION} \
        --platform managed \
        --region $REGION \
        --allow-unauthenticated \
        --set-env-vars DATABASE_URL=$DATABASE_URL,SECRET_KEY=$SECRET_KEY

    gcloud run deploy cloudapp-frontend \
        --image ${REGION}-docker.pkg.dev/${PROJECT_ID}/cloudapp/frontend:${VERSION} \
        --platform managed \
        --region $REGION \
        --allow-unauthenticated

    echo -e "${GREEN}Deployment to GCP completed${NC}"
}

# Function to run migrations
run_migrations() {
    echo -e "${YELLOW}Running database migrations...${NC}"

    docker-compose exec backend alembic upgrade head

    echo -e "${GREEN}Migrations completed${NC}"
}

# Function to verify deployment
verify_deployment() {
    echo -e "${YELLOW}Verifying deployment...${NC}"

    # Check backend health
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        echo -e "${GREEN}Backend health check passed${NC}"
    else
        echo -e "${RED}Backend health check failed${NC}"
        exit 1
    fi

    # Check frontend
    if curl -f http://localhost:3000 > /dev/null 2>&1; then
        echo -e "${GREEN}Frontend health check passed${NC}"
    else
        echo -e "${RED}Frontend health check failed${NC}"
        exit 1
    fi
}

# Main execution
main() {
    check_prerequisites
    build_images

    case $ENVIRONMENT in
        development)
            echo -e "${YELLOW}Starting development environment...${NC}"
            docker-compose up -d
            verify_deployment
            echo -e "${GREEN}Development environment started${NC}"
            ;;
        production)
            case $CLOUD_PROVIDER in
                aws)
                    deploy_aws
                    ;;
                azure)
                    deploy_azure
                    ;;
                gcp)
                    deploy_gcp
                    ;;
                *)
                    echo -e "${RED}Unknown cloud provider: $CLOUD_PROVIDER${NC}"
                    exit 1
                    ;;
            esac
            ;;
        *)
            echo -e "${RED}Unknown environment: $ENVIRONMENT${NC}"
            exit 1
            ;;
    esac

    echo -e "${GREEN}Deployment completed successfully${NC}"
}

main "$@"

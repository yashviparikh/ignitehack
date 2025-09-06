#!/bin/bash

# Hackathon Express API - Quick Deploy Script
# Supports multiple deployment targets

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
DEPLOYMENT_TARGET=""
APP_NAME="hackathon-api"
ENVIRONMENT="production"
REGISTRY=""
TAG="latest"

# Function to display usage
usage() {
    echo -e "${BLUE}Hackathon Express API - Quick Deploy Script${NC}"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -t, --target TARGET      Deployment target (docker|k8s|aws|gcp|azure)"
    echo "  -n, --name NAME          Application name (default: hackathon-api)"
    echo "  -e, --env ENVIRONMENT    Environment (development|staging|production)"
    echo "  -r, --registry REGISTRY  Docker registry URL"
    echo "  --tag TAG                Docker image tag (default: latest)"
    echo "  -h, --help               Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 -t docker                    # Deploy with Docker Compose"
    echo "  $0 -t k8s -n my-api            # Deploy to Kubernetes"
    echo "  $0 -t aws -r my-registry.com   # Deploy to AWS ECS"
    echo ""
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -t|--target)
            DEPLOYMENT_TARGET="$2"
            shift 2
            ;;
        -n|--name)
            APP_NAME="$2"
            shift 2
            ;;
        -e|--env)
            ENVIRONMENT="$2"
            shift 2
            ;;
        -r|--registry)
            REGISTRY="$2"
            shift 2
            ;;
        --tag)
            TAG="$2"
            shift 2
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            usage
            exit 1
            ;;
    esac
done

# Validate deployment target
if [[ -z "$DEPLOYMENT_TARGET" ]]; then
    echo -e "${RED}❌ Deployment target is required${NC}"
    usage
    exit 1
fi

# Validate deployment target value
case $DEPLOYMENT_TARGET in
    docker|k8s|aws|gcp|azure)
        ;;
    *)
        echo -e "${RED}❌ Invalid deployment target: $DEPLOYMENT_TARGET${NC}"
        echo -e "${YELLOW}Valid targets: docker, k8s, aws, gcp, azure${NC}"
        exit 1
        ;;
esac

echo -e "${BLUE}🚀 Deploying Hackathon Express API${NC}"
echo -e "${BLUE}=====================================${NC}"
echo -e "Target:      ${GREEN}$DEPLOYMENT_TARGET${NC}"
echo -e "App Name:    ${GREEN}$APP_NAME${NC}"
echo -e "Environment: ${GREEN}$ENVIRONMENT${NC}"
echo -e "Registry:    ${GREEN}${REGISTRY:-"local"}${NC}"
echo -e "Tag:         ${GREEN}$TAG${NC}"
echo ""

# Function to check prerequisites
check_prerequisites() {
    echo -e "${BLUE}🔍 Checking prerequisites...${NC}"
    
    # Check if .env file exists
    if [[ ! -f .env && "$ENVIRONMENT" == "production" ]]; then
        echo -e "${YELLOW}⚠️ .env file not found. Creating from template...${NC}"
        cp .env.example .env
        echo -e "${RED}❌ Please update .env file with production values before deploying${NC}"
        exit 1
    fi
    
    # Check Node.js
    if ! command -v node &> /dev/null; then
        echo -e "${RED}❌ Node.js is required but not installed${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ Prerequisites check passed${NC}"
}

# Function to build Docker image
build_docker_image() {
    echo -e "${BLUE}🏗️ Building Docker image...${NC}"
    
    local image_name="$APP_NAME"
    if [[ -n "$REGISTRY" ]]; then
        image_name="$REGISTRY/$APP_NAME"
    fi
    
    docker build -t "$image_name:$TAG" .
    
    if [[ $? -eq 0 ]]; then
        echo -e "${GREEN}✅ Docker image built successfully: $image_name:$TAG${NC}"
        
        # Push to registry if specified
        if [[ -n "$REGISTRY" ]]; then
            echo -e "${BLUE}📤 Pushing to registry...${NC}"
            docker push "$image_name:$TAG"
            echo -e "${GREEN}✅ Image pushed to registry${NC}"
        fi
    else
        echo -e "${RED}❌ Failed to build Docker image${NC}"
        exit 1
    fi
}

# Function to deploy with Docker Compose
deploy_docker() {
    echo -e "${BLUE}🐳 Deploying with Docker Compose...${NC}"
    
    # Stop existing containers
    docker-compose down
    
    # Build and start services
    docker-compose up -d --build
    
    if [[ $? -eq 0 ]]; then
        echo -e "${GREEN}✅ Deployment successful!${NC}"
        echo -e "${BLUE}📊 Service Status:${NC}"
        docker-compose ps
        echo -e "\n${GREEN}🌐 Application URLs:${NC}"
        echo -e "API:         ${BLUE}http://localhost:3000${NC}"
        echo -e "API Docs:    ${BLUE}http://localhost:3000/api-docs${NC}"
        echo -e "Health:      ${BLUE}http://localhost:3000/health${NC}"
    else
        echo -e "${RED}❌ Deployment failed${NC}"
        exit 1
    fi
}

# Function to deploy to Kubernetes
deploy_k8s() {
    echo -e "${BLUE}☸️ Deploying to Kubernetes...${NC}"
    
    # Check if kubectl is available
    if ! command -v kubectl &> /dev/null; then
        echo -e "${RED}❌ kubectl is required but not installed${NC}"
        exit 1
    fi
    
    # Create namespace if it doesn't exist
    kubectl create namespace hackathon --dry-run=client -o yaml | kubectl apply -f -
    
    # Create Kubernetes manifests
    create_k8s_manifests
    
    # Apply manifests
    kubectl apply -f k8s/ -n hackathon
    
    # Wait for deployment
    kubectl rollout status deployment/$APP_NAME -n hackathon
    
    if [[ $? -eq 0 ]]; then
        echo -e "${GREEN}✅ Kubernetes deployment successful!${NC}"
        echo -e "${BLUE}📊 Pod Status:${NC}"
        kubectl get pods -n hackathon
        
        # Get service URL
        local service_url=$(kubectl get service $APP_NAME -n hackathon -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
        if [[ -n "$service_url" ]]; then
            echo -e "\n${GREEN}🌐 Application URL: ${BLUE}http://$service_url${NC}"
        fi
    else
        echo -e "${RED}❌ Kubernetes deployment failed${NC}"
        exit 1
    fi
}

# Function to create Kubernetes manifests
create_k8s_manifests() {
    mkdir -p k8s
    
    # Deployment manifest
    cat > k8s/deployment.yaml << EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: $APP_NAME
  labels:
    app: $APP_NAME
spec:
  replicas: 3
  selector:
    matchLabels:
      app: $APP_NAME
  template:
    metadata:
      labels:
        app: $APP_NAME
    spec:
      containers:
      - name: api
        image: ${REGISTRY:+$REGISTRY/}$APP_NAME:$TAG
        ports:
        - containerPort: 3000
        env:
        - name: NODE_ENV
          value: "$ENVIRONMENT"
        - name: PORT
          value: "3000"
        livenessProbe:
          httpGet:
            path: /health/live
            port: 3000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health/ready
            port: 3000
          initialDelaySeconds: 5
          periodSeconds: 5
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "512Mi"
            cpu: "500m"
EOF

    # Service manifest
    cat > k8s/service.yaml << EOF
apiVersion: v1
kind: Service
metadata:
  name: $APP_NAME
spec:
  selector:
    app: $APP_NAME
  ports:
  - protocol: TCP
    port: 80
    targetPort: 3000
  type: LoadBalancer
EOF

    echo -e "${GREEN}✅ Kubernetes manifests created${NC}"
}

# Function to deploy to AWS
deploy_aws() {
    echo -e "${BLUE}☁️ Deploying to AWS...${NC}"
    
    # Check if AWS CLI is available
    if ! command -v aws &> /dev/null; then
        echo -e "${RED}❌ AWS CLI is required but not installed${NC}"
        exit 1
    fi
    
    # Build and push Docker image to ECR
    local aws_account=$(aws sts get-caller-identity --query Account --output text)
    local aws_region=$(aws configure get region)
    local ecr_registry="$aws_account.dkr.ecr.$aws_region.amazonaws.com"
    
    # Create ECR repository if it doesn't exist
    aws ecr describe-repositories --repository-names $APP_NAME &> /dev/null || \
        aws ecr create-repository --repository-name $APP_NAME
    
    # Login to ECR
    aws ecr get-login-password --region $aws_region | docker login --username AWS --password-stdin $ecr_registry
    
    # Build and push image
    docker build -t $APP_NAME:$TAG .
    docker tag $APP_NAME:$TAG $ecr_registry/$APP_NAME:$TAG
    docker push $ecr_registry/$APP_NAME:$TAG
    
    echo -e "${GREEN}✅ Image pushed to ECR: $ecr_registry/$APP_NAME:$TAG${NC}"
    echo -e "${YELLOW}💡 Next steps:${NC}"
    echo -e "   1. Create ECS cluster or EKS cluster"
    echo -e "   2. Deploy using the image: $ecr_registry/$APP_NAME:$TAG"
}

# Function to deploy to Google Cloud
deploy_gcp() {
    echo -e "${BLUE}☁️ Deploying to Google Cloud...${NC}"
    
    # Check if gcloud is available
    if ! command -v gcloud &> /dev/null; then
        echo -e "${RED}❌ Google Cloud SDK is required but not installed${NC}"
        exit 1
    fi
    
    local project_id=$(gcloud config get-value project)
    local gcr_registry="gcr.io/$project_id"
    
    # Build and push to Google Container Registry
    docker build -t $APP_NAME:$TAG .
    docker tag $APP_NAME:$TAG $gcr_registry/$APP_NAME:$TAG
    docker push $gcr_registry/$APP_NAME:$TAG
    
    # Deploy to Cloud Run
    gcloud run deploy $APP_NAME \
        --image $gcr_registry/$APP_NAME:$TAG \
        --platform managed \
        --region us-central1 \
        --allow-unauthenticated \
        --port 3000
    
    if [[ $? -eq 0 ]]; then
        local service_url=$(gcloud run services describe $APP_NAME --platform managed --region us-central1 --format 'value(status.url)')
        echo -e "${GREEN}✅ Deployed to Cloud Run: $service_url${NC}"
    fi
}

# Function to deploy to Azure
deploy_azure() {
    echo -e "${BLUE}☁️ Deploying to Azure...${NC}"
    
    # Check if Azure CLI is available
    if ! command -v az &> /dev/null; then
        echo -e "${RED}❌ Azure CLI is required but not installed${NC}"
        exit 1
    fi
    
    local resource_group="hackathon-rg"
    local acr_name="hackathonacr$RANDOM"
    
    # Create resource group
    az group create --name $resource_group --location eastus
    
    # Create Azure Container Registry
    az acr create --resource-group $resource_group --name $acr_name --sku Basic
    
    # Build and push image
    az acr build --registry $acr_name --image $APP_NAME:$TAG .
    
    # Deploy to Container Instances
    az container create \
        --resource-group $resource_group \
        --name $APP_NAME \
        --image $acr_name.azurecr.io/$APP_NAME:$TAG \
        --ports 3000 \
        --environment-variables NODE_ENV=$ENVIRONMENT
    
    echo -e "${GREEN}✅ Deployed to Azure Container Instances${NC}"
}

# Main deployment function
main() {
    check_prerequisites
    
    case $DEPLOYMENT_TARGET in
        docker)
            deploy_docker
            ;;
        k8s)
            build_docker_image
            deploy_k8s
            ;;
        aws)
            deploy_aws
            ;;
        gcp)
            deploy_gcp
            ;;
        azure)
            deploy_azure
            ;;
    esac
    
    echo -e "\n${GREEN}🎉 Deployment completed successfully!${NC}"
    echo -e "${BLUE}📝 Next steps:${NC}"
    echo -e "   1. Test your API endpoints"
    echo -e "   2. Configure monitoring and logging"
    echo -e "   3. Set up CI/CD pipeline"
    echo -e "   4. Scale based on usage"
}

# Run main function
main

#!/bin/bash

# OCI Container Instance Deployment Script
# This script helps deploy the application to Oracle Cloud Infrastructure

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}OCI Container Deployment Script${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Function to print colored output
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if .env file exists
if [ ! -f "$PROJECT_ROOT/.env" ]; then
    print_error ".env file not found!"
    print_info "Creating .env from .env.example..."
    cp "$PROJECT_ROOT/.env.example" "$PROJECT_ROOT/.env"
    print_warn "Please edit .env file with your configuration before continuing"
    exit 1
fi

# Load environment variables
source "$PROJECT_ROOT/.env"

# Check required variables
if [ -z "$GOOGLE_API_KEY" ] || [ "$GOOGLE_API_KEY" = "your_google_api_key_here" ]; then
    print_error "GOOGLE_API_KEY is not set in .env file"
    exit 1
fi

# Get OCI configuration
read -p "Enter OCI Region Key (e.g., iad, phx): " REGION_KEY
read -p "Enter OCI Tenancy Namespace: " TENANCY_NAMESPACE
read -p "Enter Container Registry Repository Name: " REPO_NAME

OCIR_URL="${REGION_KEY}.ocir.io"
IMAGE_PREFIX="${OCIR_URL}/${TENANCY_NAMESPACE}/${REPO_NAME}"

print_info "OCIR URL: $OCIR_URL"
print_info "Image Prefix: $IMAGE_PREFIX"
echo ""

# Step 1: Build images
print_info "Step 1: Building Docker images..."
cd "$PROJECT_ROOT"
docker-compose build

if [ $? -ne 0 ]; then
    print_error "Failed to build images"
    exit 1
fi
print_info "✓ Images built successfully"
echo ""

# Step 2: Tag images for OCIR
print_info "Step 2: Tagging images for OCIR..."
docker tag system-architect-generator-backend:latest "${IMAGE_PREFIX}/backend:latest"
docker tag system-architect-generator-frontend:latest "${IMAGE_PREFIX}/frontend:latest"

if [ $? -ne 0 ]; then
    print_error "Failed to tag images"
    exit 1
fi
print_info "✓ Images tagged successfully"
echo ""

# Step 3: Login to OCIR
print_info "Step 3: Logging in to OCIR..."
print_warn "You will be prompted for your OCI Auth Token"
print_info "Username format: <tenancy-namespace>/<username>"
docker login $OCIR_URL

if [ $? -ne 0 ]; then
    print_error "Failed to login to OCIR"
    exit 1
fi
print_info "✓ Logged in successfully"
echo ""

# Step 4: Push images
print_info "Step 4: Pushing images to OCIR..."
print_info "Pushing backend image..."
docker push "${IMAGE_PREFIX}/backend:latest"

print_info "Pushing frontend image..."
docker push "${IMAGE_PREFIX}/frontend:latest"

if [ $? -ne 0 ]; then
    print_error "Failed to push images"
    exit 1
fi
print_info "✓ Images pushed successfully"
echo ""

# Step 5: Generate deployment info
print_info "Step 5: Generating deployment information..."

cat > "$PROJECT_ROOT/oci-deployment-info.txt" << EOF
OCI Container Instance Deployment Information
==============================================

Images pushed to OCIR:
- Backend:  ${IMAGE_PREFIX}/backend:latest
- Frontend: ${IMAGE_PREFIX}/frontend:latest

Required Environment Variables for Backend Container:
------------------------------------------------------
MONGODB_URL=mongodb://admin:<password>@<mongodb-host>:27017/system_architect_generator?authSource=admin
MONGODB_DB_NAME=system_architect_generator
MONGODB_USERNAME=admin
MONGODB_PASSWORD=<your-password>
GOOGLE_API_KEY=${GOOGLE_API_KEY}
DEFAULT_MODEL=${DEFAULT_MODEL}
PYTHONUNBUFFERED=1

Container Configuration:
------------------------
Backend Container:
  - Image: ${IMAGE_PREFIX}/backend:latest
  - Port: 8000
  - Health Check: /api/health
  - CPU: 2 OCPU recommended
  - Memory: 4GB recommended

Frontend Container:
  - Image: ${IMAGE_PREFIX}/frontend:latest
  - Port: 80
  - Health Check: /health
  - CPU: 1 OCPU recommended
  - Memory: 2GB recommended

MongoDB Container:
  - Image: mongo:7.0
  - Port: 27017
  - CPU: 2 OCPU recommended
  - Memory: 4GB recommended
  - Volume: Required for data persistence

Networking:
-----------
1. Create a VCN with appropriate subnets
2. Configure security lists:
   - Frontend: Allow inbound 80/443
   - Backend: Allow inbound 8000 from frontend
   - MongoDB: Allow inbound 27017 from backend
3. Use private IPs for internal communication

Next Steps:
-----------
1. Create OCI Container Instance for MongoDB
2. Create OCI Container Instance for Backend
3. Create OCI Container Instance for Frontend
4. Configure Load Balancer (optional)
5. Set up monitoring and logging
6. Configure backup for MongoDB

For detailed instructions, see DEPLOYMENT.md
EOF

print_info "✓ Deployment info saved to oci-deployment-info.txt"
echo ""

# Summary
print_info "========================================${NC}"
print_info "${GREEN}Deployment preparation complete!${NC}"
print_info "========================================${NC}"
echo ""
print_info "Next steps:"
print_info "1. Review oci-deployment-info.txt"
print_info "2. Create Container Instances in OCI Console"
print_info "3. Configure networking and security"
print_info "4. Set environment variables in OCI"
print_info "5. Start containers in order: MongoDB -> Backend -> Frontend"
echo ""
print_info "Images available at:"
print_info "  - ${IMAGE_PREFIX}/backend:latest"
print_info "  - ${IMAGE_PREFIX}/frontend:latest"
echo ""

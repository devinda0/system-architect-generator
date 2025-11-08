#!/bin/bash

# Manual Docker Build and Push Script for OCI Registry
# This script builds and pushes both backend and frontend images

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
# OCI Region: iad = Ashburn, phx = Phoenix, fra = Frankfurt, lhr = London
# Change REGION to match your OCI region
REGION="iad"
REGISTRY="${REGION}.ocir.io"
NAMESPACE="ax1cmfkxkbut"
BACKEND_REPO="${NAMESPACE}/ranga-tech/dev/app-1"
FRONTEND_REPO="${NAMESPACE}/ranga-tech/dev/app-2"
BACKEND_IMAGE="${REGISTRY}/${BACKEND_REPO}"
FRONTEND_IMAGE="${REGISTRY}/${FRONTEND_REPO}"

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Docker Build and Push to OCI Registry${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Function to print colored messages
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# Check if Docker is running
print_step "Checking Docker..."
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker Desktop and try again."
    exit 1
fi
print_info "✓ Docker is running"
echo ""

# Load credentials
if [ -f "$PROJECT_ROOT/.env.local" ]; then
    print_info "Loading credentials from .env.local..."
    source "$PROJECT_ROOT/.env.local"
elif [ -f "$PROJECT_ROOT/.env" ]; then
    print_info "Loading credentials from .env..."
    source "$PROJECT_ROOT/.env"
fi

# Check for credentials
if [ -z "$OCI_USERNAME" ] || [ -z "$OCI_AUTH_TOKEN" ]; then
    print_warn "OCI credentials not found in environment or .env file"
    echo ""
    read -p "Enter OCI Username (format: namespace/username): " OCI_USERNAME
    read -sp "Enter OCI Auth Token: " OCI_AUTH_TOKEN
    echo ""
fi

# Login to OCI Registry
print_step "Logging in to OCI Container Registry..."
echo "$OCI_AUTH_TOKEN" | docker login "$REGISTRY" -u "$OCI_USERNAME" --password-stdin

if [ $? -ne 0 ]; then
    print_error "Failed to login to OCI Registry"
    exit 1
fi
print_info "✓ Successfully logged in to $REGISTRY"
echo ""

# Build Backend Image
print_step "Building backend image..."
cd "$PROJECT_ROOT"
docker build -t backend:latest -f backend/Dockerfile backend/

if [ $? -ne 0 ]; then
    print_error "Failed to build backend image"
    exit 1
fi
print_info "✓ Backend image built successfully"
echo ""

# Build Frontend Image
print_step "Building frontend image..."
docker build -t frontend:latest -f frontend/Dockerfile frontend/

if [ $? -ne 0 ]; then
    print_error "Failed to build frontend image"
    exit 1
fi
print_info "✓ Frontend image built successfully"
echo ""

# Tag Backend Image
print_step "Tagging backend image..."
docker tag backend:latest "${BACKEND_IMAGE}:latest"
docker tag backend:latest "${BACKEND_IMAGE}:$(date +%Y%m%d-%H%M%S)"

if [ $? -ne 0 ]; then
    print_error "Failed to tag backend image"
    exit 1
fi
print_info "✓ Backend image tagged"
echo ""

# Tag Frontend Image
print_step "Tagging frontend image..."
docker tag frontend:latest "${FRONTEND_IMAGE}:latest"
docker tag frontend:latest "${FRONTEND_IMAGE}:$(date +%Y%m%d-%H%M%S)"

if [ $? -ne 0 ]; then
    print_error "Failed to tag frontend image"
    exit 1
fi
print_info "✓ Frontend image tagged"
echo ""

# Push Backend Image
print_step "Pushing backend image to OCIR..."
docker push "${BACKEND_IMAGE}:latest"
docker push "${BACKEND_IMAGE}:$(date +%Y%m%d-%H%M%S)"

if [ $? -ne 0 ]; then
    print_error "Failed to push backend image"
    exit 1
fi
print_info "✓ Backend image pushed successfully"
echo ""

# Push Frontend Image
print_step "Pushing frontend image to OCIR..."
docker push "${FRONTEND_IMAGE}:latest"
docker push "${FRONTEND_IMAGE}:$(date +%Y%m%d-%H%M%S)"

if [ $? -ne 0 ]; then
    print_error "Failed to push frontend image"
    exit 1
fi
print_info "✓ Frontend image pushed successfully"
echo ""

# Summary
print_info "========================================${NC}"
echo -e "${GREEN}✅ All images pushed successfully!${NC}"
print_info "========================================${NC}"
echo ""
echo -e "${BLUE}Backend Image:${NC}"
echo "  ${BACKEND_IMAGE}:latest"
echo ""
echo -e "${BLUE}Frontend Image:${NC}"
echo "  ${FRONTEND_IMAGE}:latest"
echo ""
print_info "You can now use these images in your OCI Container Instances"
echo ""

# Cleanup (optional)
read -p "Do you want to remove local images to free up space? [y/N] " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_step "Cleaning up local images..."
    docker rmi backend:latest frontend:latest || true
    print_info "✓ Local images removed"
fi

echo ""
print_info "Done! 🚀"

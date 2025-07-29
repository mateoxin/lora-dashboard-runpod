#!/bin/bash

# LoRA Dashboard - Automated RunPod Deployment Script
# Usage: ./deploy-to-runpod.sh

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_step() {
    echo -e "${BLUE}🔷 $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Banner
echo -e "${BLUE}"
echo "=================================="
echo "🚀 LoRA Dashboard RunPod Deployer"
echo "=================================="
echo -e "${NC}"

# Check if .env file exists
if [ ! -f ".env" ]; then
    print_error ".env file not found!"
    echo "Copy .env.example to .env and fill in your values:"
    echo "cp .env.example .env"
    exit 1
fi

# Source environment variables
source .env

# Validate required variables
if [ -z "$DOCKER_USERNAME" ]; then
    print_error "DOCKER_USERNAME not set in .env file"
    exit 1
fi

if [ -z "$RUNPOD_API_KEY" ]; then
    print_error "RUNPOD_API_KEY not set in .env file"
    exit 1
fi

# Step 1: Build Docker image
print_step "Building Docker image..."
docker build -t $DOCKER_USERNAME/lora-dashboard-backend:latest .
print_success "Docker image built successfully"

# Step 2: Test image locally (optional)
print_step "Testing Docker image locally..."
CONTAINER_ID=$(docker run -d -p 8001:8000 \
    -e REDIS_URL="redis://localhost:6379/0" \
    $DOCKER_USERNAME/lora-dashboard-backend:latest)

sleep 5

if curl -s http://localhost:8001/api/health > /dev/null; then
    print_success "Local Docker test passed"
else
    print_warning "Local Docker test failed (this might be OK if Redis is not running locally)"
fi

# Stop test container
docker stop $CONTAINER_ID > /dev/null
docker rm $CONTAINER_ID > /dev/null

# Step 3: Push to Docker Hub
print_step "Pushing image to Docker Hub..."
if ! docker push $DOCKER_USERNAME/lora-dashboard-backend:latest; then
    print_error "Failed to push to Docker Hub. Make sure you're logged in: docker login"
    exit 1
fi
print_success "Image pushed to Docker Hub"

# Step 4: Check if RunPod CLI is installed
if ! command -v runpod &> /dev/null; then
    print_step "Installing RunPod CLI..."
    pip install runpod
    print_success "RunPod CLI installed"
fi

# Step 5: Configure RunPod CLI
print_step "Configuring RunPod CLI..."
runpod config set api-key $RUNPOD_API_KEY
print_success "RunPod CLI configured"

# Step 6: Create Storage Secrets (if they don't exist)
print_step "Creating storage secrets..."
if [ -n "$S3_ACCESS_KEY" ] && [ -n "$S3_SECRET_KEY" ] && [ -n "$S3_BUCKET" ]; then
    if ! runpod get secrets | grep -q "storage-secrets"; then
        runpod create secret storage-secrets \
            --from-literal=bucket-name="$S3_BUCKET" \
            --from-literal=access-key="$S3_ACCESS_KEY" \
            --from-literal=secret-key="$S3_SECRET_KEY"
        print_success "Storage secrets created"
    else
        print_warning "Storage secrets already exist"
    fi
else
    print_warning "S3 credentials not found in .env - skipping storage secrets"
fi

# Step 7: Deploy Endpoint
print_step "Deploying endpoint to RunPod..."

ENDPOINT_NAME="lora-dashboard-backend"

# Check if endpoint already exists
if runpod get endpoints | grep -q "$ENDPOINT_NAME"; then
    print_warning "Endpoint $ENDPOINT_NAME already exists"
    read -p "Do you want to update it? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_step "Updating existing endpoint..."
        runpod update endpoint $ENDPOINT_NAME \
            --image "$DOCKER_USERNAME/lora-dashboard-backend:latest"
        print_success "Endpoint updated"
    else
        print_warning "Skipping deployment"
        exit 0
    fi
else
    # Create new endpoint
    runpod create endpoint \
        --name "$ENDPOINT_NAME" \
        --image "$DOCKER_USERNAME/lora-dashboard-backend:latest" \
        --gpu-type "A40" \
        --gpu-count 1 \
        --env REDIS_URL="redis://redis:6379/0" \
        --env S3_ENDPOINT_URL="${S3_ENDPOINT_URL:-https://storage.runpod.io}" \
        --env MAX_CONCURRENT_JOBS="${MAX_CONCURRENT_JOBS:-10}" \
        --env GPU_TIMEOUT="${GPU_TIMEOUT:-14400}" \
        --env LOG_LEVEL="${LOG_LEVEL:-INFO}" \
        --secret storage-secrets \
        --min-replicas 0 \
        --max-replicas 5 \
        --timeout 4h
    
    print_success "Endpoint deployed successfully"
fi

# Step 8: Get endpoint URL
print_step "Getting endpoint information..."
ENDPOINT_INFO=$(runpod get endpoints | grep "$ENDPOINT_NAME")
if [ -n "$ENDPOINT_INFO" ]; then
    echo "$ENDPOINT_INFO"
    print_success "Endpoint is ready!"
else
    print_error "Could not find endpoint information"
fi

# Step 9: Set budget limits (optional)
if [ -n "$MONTHLY_BUDGET_LIMIT" ]; then
    print_step "Setting budget limits..."
    runpod billing set-limit --monthly $MONTHLY_BUDGET_LIMIT
    print_success "Budget limit set to \$$MONTHLY_BUDGET_LIMIT/month"
fi

# Step 10: Create budget alert (optional)
if [ -n "$ALERT_EMAIL" ]; then
    print_step "Creating budget alert..."
    runpod billing create-alert \
        --threshold 80 \
        --email "$ALERT_EMAIL" || print_warning "Could not create budget alert"
fi

print_success "Deployment completed!"
echo
echo -e "${GREEN}🎉 Your LoRA Dashboard backend is now running on RunPod!${NC}"
echo
echo "Next steps:"
echo "1. Get your endpoint URL from: runpod get endpoints"
echo "2. Update your frontend environment.ts with the endpoint URL"
echo "3. Set mockMode: false in environment.ts"
echo "4. Test your deployment with: curl YOUR_ENDPOINT_URL/api/health"
echo
echo "Monitoring:"
echo "- View logs: runpod logs $ENDPOINT_NAME --follow"
echo "- Check costs: runpod billing usage --current"
echo "- Monitor endpoint: runpod get endpoints"
echo
print_warning "Remember to monitor your costs and set appropriate limits!" 
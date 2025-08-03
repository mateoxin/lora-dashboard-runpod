#!/bin/bash
# 🚀 Build and Deploy Simple Backend

echo "🐳 Building Simple Backend Docker Image"
echo "======================================"

# Build image
docker build -t mateoxin/simple-runpod-test:v1 .

if [ $? -eq 0 ]; then
    echo "✅ Build successful!"
    
    # Test locally first
    echo "🧪 Testing locally..."
    docker run -d --name simple-test -p 8000:8000 mateoxin/simple-runpod-test:v1
    
    # Wait a bit
    sleep 5
    
    # Stop test container
    docker rm -f simple-test
    
    # Push to Docker Hub
    echo "📤 Pushing to Docker Hub..."
    docker push mateoxin/simple-runpod-test:v1
    
    if [ $? -eq 0 ]; then
        echo "🎉 Deploy successful!"
        echo ""
        echo "📋 RunPod Configuration:"
        echo "  Docker Image: mateoxin/simple-runpod-test:v1"
        echo "  Min Workers: 1"
        echo "  Max Workers: 1" 
        echo "  Container Disk: 5 GB"
        echo "  Memory: 4096 MB"
        echo ""
        echo "🧪 After creating endpoint, update test_simple_backend.py with:"
        echo "  ENDPOINT_ID = 'your-new-endpoint-id'"
    else
        echo "❌ Push failed!"
    fi
else
    echo "❌ Build failed!"
fi 
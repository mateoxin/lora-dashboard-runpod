# Deploy Backend to RunPod - Complete Guide

This guide walks you through deploying the LoRA Dashboard backend to RunPod Serverless with A40 GPUs, cost controls, and S3 storage integration.

## 📋 Prerequisites

- RunPod account with billing set up
- Docker installed locally
- RunPod CLI installed
- Access to container registry (Docker Hub, GitHub Container Registry, etc.)

## 🔧 Step 1: Environment Setup

### Install RunPod CLI
```bash
# Install RunPod CLI
pip install runpod

# Login to RunPod
runpod login
```

### Set up S3 Storage
1. Go to RunPod Console → Storage
2. Create a new bucket (e.g., `lora-dashboard-storage`)
3. Note down:
   - Bucket name
   - Access key
   - Secret key
   - Endpoint URL

## 🐳 Step 2: Build and Push Docker Image

### Build the Docker Image
```bash
cd Serverless/Backend

# Build the image
docker build -t your-registry/lora-dashboard-backend:latest .

# Test locally first
docker run -p 8000:8000 \
  -e REDIS_URL="redis://localhost:6379/0" \
  -e S3_ACCESS_KEY="your-access-key" \
  -e S3_SECRET_KEY="your-secret-key" \
  -e S3_BUCKET="your-bucket" \
  your-registry/lora-dashboard-backend:latest
```

### Push to Registry
```bash
# Docker Hub
docker push your-registry/lora-dashboard-backend:latest

# Or GitHub Container Registry
docker tag your-registry/lora-dashboard-backend:latest ghcr.io/yourusername/lora-dashboard-backend:latest
docker push ghcr.io/yourusername/lora-dashboard-backend:latest
```

## ⚙️ Step 3: Configure RunPod Secrets

Create secrets for sensitive configuration:

```bash
# Create storage secrets
runpod secret create storage-secrets \
  --from-literal=bucket-name="your-bucket-name" \
  --from-literal=access-key="your-access-key" \
  --from-literal=secret-key="your-secret-key"
```

## 🚀 Step 4: Deploy the Endpoint

### Method A: Using RunPod CLI
```bash
# Deploy using the runpod.yaml configuration
runpod deploy --config runpod.yaml
```

### Method B: Using RunPod Console

1. **Go to RunPod Console → Serverless**
2. **Click "New Endpoint"**
3. **Configure Container:**
   - Image: `your-registry/lora-dashboard-backend:latest`
   - Port: `8000`
   - GPU Type: `A40`
   - GPU Count: `1`

4. **Set Environment Variables:**
   ```bash
   REDIS_URL=redis://redis:6379/0
   MAX_CONCURRENT_JOBS=10
   GPU_TIMEOUT=14400
   LOG_LEVEL=INFO
   ```

5. **Configure Secrets:**
   - Link the `storage-secrets` secret
   - Map to environment variables:
     - `S3_BUCKET` → `bucket-name`
     - `S3_ACCESS_KEY` → `access-key`
     - `S3_SECRET_KEY` → `secret-key`

6. **Set Scaling Configuration:**
   - Min Replicas: `0`
   - Max Replicas: `10`
   - Scale to Zero Delay: `300s`
   - Target Concurrency: `1`

7. **Configure Timeout:**
   - Request Timeout: `4h`
   - Idle Timeout: `10m`

## 💰 Step 5: Set Up Cost Controls

### Budget Limits
1. Go to **Account Settings → Billing**
2. Set up budget alerts:
   - 80% threshold → Email notification
   - 95% threshold → Email + webhook notification
3. Enable auto-pause on budget limit

### Cost Monitoring
```bash
# Check current spend
runpod billing current-usage

# Set spending limits
runpod billing set-limit --hourly 20.0 --monthly 500.0
```

### Resource Optimization
```yaml
# In runpod.yaml - optimize for cost
scaling:
  minReplicas: 0           # Scale to zero when idle
  maxReplicas: 10          # Limit concurrent instances
  scaleToZeroDelay: 300    # 5 minutes idle before scale-down
  
timeouts:
  idle: 10m                # Kill idle containers
  request: 4h              # Maximum job duration
```

## 📊 Step 6: Configure Monitoring

### Health Check Setup
```bash
# Test health endpoint
curl -f https://your-endpoint-id.runpod.ai/api/health

# Expected response
{
  "success": true,
  "data": {
    "status": "healthy",
    "services": {
      "process_manager": "healthy",
      "storage": "healthy",
      "gpu_manager": {...}
    }
  }
}
```

### Logging Configuration
```bash
# View logs
runpod logs --endpoint your-endpoint-id --follow

# Configure log retention
runpod endpoint update your-endpoint-id \
  --log-retention-days 7
```

## 🔧 Step 7: Test the Deployment

### Test Training Endpoint
```bash
curl -X POST https://your-endpoint-id.runpod.ai/api/train \
  -H "Content-Type: application/json" \
  -d '{
    "config": "job: extension\nconfig:\n  name: \"test_training\"\n  process:\n    - type: sd_trainer\n      device: cuda:0\n      # ... rest of config"
  }'
```

### Test Generation Endpoint  
```bash
curl -X POST https://your-endpoint-id.runpod.ai/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "config": "job: generate\nconfig:\n  name: \"test_generation\"\n  process:\n    - type: to_folder\n      device: cuda:0\n      # ... rest of config"
  }'
```

### Test Process Monitoring
```bash
# Get all processes
curl https://your-endpoint-id.runpod.ai/api/processes

# Get specific process
curl https://your-endpoint-id.runpod.ai/api/processes/{process-id}
```

## 🚨 Step 8: Production Configuration

### Security Hardening
```yaml
# Update runpod.yaml for production
spec:
  # Remove debug settings
  container:
    env:
      - name: LOG_LEVEL
        value: "WARNING"  # Reduce log verbosity
      - name: DEBUG
        value: "false"
        
  # Add resource limits
  resources:
    limits:
      cpu: "4"
      memory: "8Gi"
    requests:
      cpu: "1" 
      memory: "2Gi"
```

### Backup Configuration
```bash
# Export endpoint configuration
runpod endpoint describe your-endpoint-id > backup-config.yaml

# Export secrets (metadata only)
runpod secret list > backup-secrets.yaml
```

## 📈 Step 9: Scaling Optimization

### Auto-scaling Metrics
```yaml
scaling:
  metrics:
    - type: QueueLength
      target:
        averageValue: 5    # Scale up when queue > 5
    - type: GPUUtilization
      target:
        averageValue: 80   # Scale up when GPU > 80%
```

### Cold Start Optimization
```dockerfile
# In Dockerfile - optimize startup time
RUN pip install --no-cache-dir --pre-compile poetry
RUN poetry install --no-dev --no-interaction --compile

# Pre-warm model loading
RUN python -c "import torch; torch.cuda.is_available()"
```

## 🔍 Step 10: Troubleshooting

### Common Issues

**1. Container startup timeout**
```bash
# Increase startup timeout
runpod endpoint update your-endpoint-id \
  --startup-timeout 300
```

**2. GPU allocation failures**
```bash
# Check GPU availability
runpod gpu list --available

# Request different GPU type
runpod endpoint update your-endpoint-id \
  --gpu-type RTX4090  # Alternative if A40 unavailable
```

**3. Storage connection issues**
```bash
# Test S3 connectivity
curl -X GET https://your-endpoint-id.runpod.ai/api/health
# Check storage status in response
```

**4. Redis connection problems**
```bash
# Deploy Redis service separately
kubectl apply -f - <<EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: redis
spec:
  replicas: 1
  selector:
    matchLabels:
      app: redis
  template:
    metadata:
      labels:
        app: redis
    spec:
      containers:
      - name: redis
        image: redis:7-alpine
        ports:
        - containerPort: 6379
EOF
```

### Monitoring Commands
```bash
# Monitor resource usage
runpod endpoint metrics your-endpoint-id

# Check cost breakdown
runpod billing detailed-usage --endpoint your-endpoint-id

# View recent errors
runpod logs --endpoint your-endpoint-id --level ERROR --tail 100
```

## 📋 Final Checklist

- [ ] Docker image built and pushed
- [ ] Secrets created and configured
- [ ] Endpoint deployed with correct GPU type
- [ ] Environment variables set
- [ ] Cost controls configured
- [ ] Health checks passing
- [ ] Training endpoint tested
- [ ] Generation endpoint tested
- [ ] Storage integration working
- [ ] Monitoring and logging set up
- [ ] Backup configuration saved

## 💡 Cost Optimization Tips

1. **Use spot instances** when possible for training (longer jobs)
2. **Scale to zero** aggressively (5-10 minutes idle)
3. **Optimize container size** - remove unnecessary dependencies
4. **Use shared storage** for models to avoid repeated downloads
5. **Monitor queue length** to optimize concurrent instances
6. **Set strict timeouts** to prevent runaway processes

## 🆘 Support

If you encounter issues:
1. Check RunPod documentation: https://docs.runpod.io
2. Join RunPod Discord: https://discord.gg/runpod
3. Contact RunPod support through the console
4. Review logs: `runpod logs --endpoint your-endpoint-id`

## 🔗 Next Steps

After successful deployment:
1. Update frontend environment to point to your endpoint
2. Configure CI/CD for automatic deployments
3. Set up monitoring dashboards
4. Implement backup and disaster recovery
5. Scale testing with real workloads 
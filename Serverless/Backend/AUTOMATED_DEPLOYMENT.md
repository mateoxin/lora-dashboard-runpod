# 🤖 Automated Deployment - RunPod Script

**Automatyczny skrypt wdrożenia na RunPod (zastępuje manual deployment)**

## 📋 Przygotowanie

### 1. Skopiuj i wypełnij środowisko
```bash
cd Serverless/Backend
cp .env.example .env
# Edytuj .env i wypełnij wszystkie wymagane pola
```

### 2. Utwórz automatyczny skrypt
Stwórz plik `deploy-runpod.sh`:

```bash
#!/bin/bash
# Automated RunPod Deployment for LoRA Dashboard

set -e
source .env

echo "🚀 Starting automated RunPod deployment..."

# Validate environment
if [ -z "$DOCKER_USERNAME" ] || [ -z "$RUNPOD_API_KEY" ]; then
    echo "❌ Missing required environment variables in .env"
    exit 1
fi

# Build and push Docker image
echo "📦 Building Docker image..."
docker build -t $DOCKER_USERNAME/lora-dashboard-backend:latest .
docker push $DOCKER_USERNAME/lora-dashboard-backend:latest

# Install and configure RunPod CLI
pip install runpod
runpod config set api-key $RUNPOD_API_KEY

# Create storage secrets
if [ -n "$S3_ACCESS_KEY" ]; then
    runpod create secret storage-secrets \
        --from-literal=bucket-name="$S3_BUCKET" \
        --from-literal=access-key="$S3_ACCESS_KEY" \
        --from-literal=secret-key="$S3_SECRET_KEY" || echo "Secrets might already exist"
fi

# Deploy endpoint
runpod create endpoint \
    --name "lora-dashboard-backend" \
    --image "$DOCKER_USERNAME/lora-dashboard-backend:latest" \
    --gpu-type "A40" \
    --gpu-count 1 \
    --min-replicas 0 \
    --max-replicas 5 \
    --timeout 4h \
    --env REDIS_URL="redis://redis:6379/0" \
    --env S3_ENDPOINT_URL="$S3_ENDPOINT_URL" \
    --env MAX_CONCURRENT_JOBS="$MAX_CONCURRENT_JOBS" \
    --secret storage-secrets

# Set budget limits
if [ -n "$MONTHLY_BUDGET_LIMIT" ]; then
    runpod billing set-limit --monthly $MONTHLY_BUDGET_LIMIT
fi

echo "✅ Deployment completed!"
echo "Check endpoint: runpod get endpoints"
```

### 3. Uruchom skrypt
```bash
# Uczyń skrypt wykonalnym
chmod +x deploy-runpod.sh

# Uruchom deployment
./deploy-runpod.sh
```

## 🔄 Automatyczna aktualizacja

```bash
#!/bin/bash
# Update existing deployment

source .env
docker build -t $DOCKER_USERNAME/lora-dashboard-backend:latest .
docker push $DOCKER_USERNAME/lora-dashboard-backend:latest
runpod update endpoint lora-dashboard-backend --image "$DOCKER_USERNAME/lora-dashboard-backend:latest"
```

## 💰 Automatyczne zarządzanie kosztami

```bash
#!/bin/bash
# Cost monitoring script

source .env
CURRENT_SPEND=$(runpod billing usage --current --format json | jq .monthly_spend)

if (( $(echo "$CURRENT_SPEND > $MONTHLY_BUDGET_LIMIT * 0.8" | bc -l) )); then
    echo "⚠️ Budget warning: 80% of monthly limit reached"
    # Optionally scale down
    runpod update endpoint lora-dashboard-backend --max-replicas 1
fi
```

## 🔍 Monitoring i logging

```bash
#!/bin/bash
# Monitoring script

ENDPOINT_ID=$(runpod get endpoints | grep lora-dashboard-backend | awk '{print $1}')

echo "📊 Endpoint Status:"
runpod get endpoints | grep lora-dashboard-backend

echo "💰 Current Costs:"
runpod billing usage --current

echo "📝 Recent Logs:"
runpod logs $ENDPOINT_ID --tail 20
```

## 🚀 CI/CD Integration

### GitHub Actions przykład:
```yaml
name: Deploy to RunPod

on:
  push:
    branches: [main]
    paths: ['Serverless/Backend/**']

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Build and push Docker
      run: |
        echo ${{ secrets.DOCKER_PASSWORD }} | docker login -u ${{ secrets.DOCKER_USERNAME }} --password-stdin
        docker build -t ${{ secrets.DOCKER_USERNAME }}/lora-dashboard-backend:latest Serverless/Backend
        docker push ${{ secrets.DOCKER_USERNAME }}/lora-dashboard-backend:latest
    
    - name: Deploy to RunPod
      run: |
        pip install runpod
        runpod config set api-key ${{ secrets.RUNPOD_API_KEY }}
        runpod update endpoint lora-dashboard-backend --image "${{ secrets.DOCKER_USERNAME }}/lora-dashboard-backend:latest"
```

## 🛠️ Utilitki pomocnicze

### Scale Down (oszczędność kosztów)
```bash
runpod update endpoint lora-dashboard-backend --max-replicas 0
```

### Scale Up (przywrócenie)
```bash  
runpod update endpoint lora-dashboard-backend --max-replicas 5
```

### Backup konfiguracji
```bash
runpod get endpoints lora-dashboard-backend --format yaml > backup-config.yaml
```

### Restore z backup
```bash
runpod create endpoint --config backup-config.yaml
```

## 📋 Checklist automatyzacji

- [ ] ✅ `.env` file wypełniony
- [ ] ✅ Docker Hub account skonfigurowany  
- [ ] ✅ RunPod API key gotowy
- [ ] ✅ Budget limity ustawione
- [ ] ✅ Storage bucket utworzony
- [ ] ✅ Deployment script wykonalny
- [ ] ✅ Monitoring skonfigurowany
- [ ] ✅ CI/CD pipeline (opcjonalnie)

## ⚡ One-liner deployment
```bash
curl -s https://raw.githubusercontent.com/your-repo/main/Serverless/Backend/deploy-runpod.sh | bash
```

**💡 Tip:** Zapisz wszystkie skrypty w katalogu `scripts/` dla łatwego zarządzania! 
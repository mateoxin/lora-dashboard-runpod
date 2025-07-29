# 🧪 Local Testing Guide - LoRA Dashboard Backend

Przewodnik testowania lokalnego backend'u przed wdrożeniem na RunPod Serverless.

## 🏗️ **NOWA ARCHITEKTURA - DUAL MODE**

**Po aktualizacji mamy dual architecture:**

```
Frontend
    ↓
FastAPI Server (Development)  ←→  RunPod Serverless (Production)
    ↓                                      ↓
RunPodAdapter  ←―――――――――――――――――→  rp_handler.py
    ↓                                      ↓
Shared Business Logic (services/*)
```

**Korzyści:**
- ✅ **Development**: Szybkie testowanie z FastAPI  
- ✅ **Production**: RunPod Serverless auto-scaling
- ✅ **Unified**: Ta sama logika biznesowa w obu trybach
- ✅ **Frontend**: Bez zmian - kompatybilność API zachowana

## 📋 Przygotowanie

### 1. Instalacja zależności
```bash
cd Serverless/Backend

# Zainstaluj RunPod SDK
poetry add runpod

# Lub pip
pip install runpod

# Zainstaluj wszystkie zależności
poetry install
```

### 2. Struktura plików testowych
```
Serverless/Backend/
├── app/
│   ├── rp_handler.py          # ← RunPod Serverless handler
│   ├── main.py                # ← FastAPI (dla development)
│   └── services/              # ← Twoje usługi
├── test_input.json            # ← Domyślny test input
├── test_inputs/               # ← Różne scenariusze testowe
│   ├── health_check.json
│   ├── train_test.json
│   ├── generate_test.json
│   ├── processes_test.json
│   └── lora_models_test.json
├── test_local.py              # ← Skrypt testowy
└── LOCAL_TESTING_GUIDE.md     # ← Ten przewodnik
```

## 🚀 Metody testowania

### **NOWE! Opcja 0: Test FastAPI + RunPodAdapter (REKOMENDOWANE)**

**Najłatwiejszy sposób - testuj przez FastAPI server:**

```bash
# Uruchom FastAPI server (używa RunPodAdapter wewnętrznie)
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# W drugim terminalu test endpoints:
curl http://localhost:8000/api/health
curl -X POST http://localhost:8000/api/train -H "Content-Type: application/json" -d '{"config": "job: extension..."}'
curl http://localhost:8000/api/processes
curl http://localhost:8000/api/lora
```

### **Opcja 1: Test RunPod Handler bezpośrednio**

```bash
# Test domyślny (health check)
python app/rp_handler.py

# Test z plikiem test_input.json
python app/rp_handler.py

# Test z custom input
python app/rp_handler.py --test_input '{"input": {"type": "health"}}'
```

### **Opcja 2: Test przez RunPodAdapter**

**Testuj adapter layer bezpośrednio:**

```python
# test_adapter.py
import asyncio
from app.adapters.runpod_adapter import RunPodAdapter
from app.core.models import TrainRequest

async def test_adapter():
    adapter = RunPodAdapter()
    
    # Test health
    result = await adapter.health_check()
    print("Health:", result)
    
    # Test training
    request = TrainRequest(config="job: extension\nconfig:\n  name: test")
    result = await adapter.start_training(request)
    print("Training:", result)

# Uruchom test
asyncio.run(test_adapter())
```

### **Opcja 3: Local API Server (Legacy)**

```bash
# Uruchom local server
python app/rp_handler.py --rp_serve_api

# Test przez HTTP
curl -X POST http://localhost:8000/run \
  -H "Content-Type: application/json" \
  -d '{"input": {"type": "health"}}'

# Server z custom port
python app/rp_handler.py --rp_serve_api --rp_api_port 8080
```

### **Opcja 3: Advanced Testing Script**

```bash
# Użyj test_local.py dla comprehensive testing

# Health check (default)
python test_local.py

# Specific test
python test_local.py --test health
python test_local.py --test train
python test_local.py --test generate

# All tests
python test_local.py --all

# Custom input
python test_local.py --input '{"input": {"type": "health"}}'

# Custom file
python test_local.py --file my_test.json

# Verbose mode
python test_local.py --all --verbose
```

## 📊 Test Scenarios

### **1. Health Check**
```json
{
    "input": {
        "type": "health"
    }
}
```

**Expected Output:**
```json
{
    "success": true,
    "data": {
        "status": "healthy",
        "services": {
            "process_manager": "healthy",
            "storage": "healthy", 
            "gpu_manager": {...}
        },
        "worker_id": "local",
        "environment": "serverless"
    },
    "message": "LoRA Dashboard API is healthy"
}
```

### **2. Training Request**
```json
{
    "input": {
        "type": "train",
        "config": "job: extension\nconfig:\n  name: \"test_training\"\n  process:\n    - type: sd_trainer\n      device: cuda:0\n      trigger_word: \"test_trigger\""
    }
}
```

**Expected Output:**
```json
{
    "success": true,
    "data": {"process_id": "training-xyz123"},
    "message": "Training process started successfully"
}
```

### **3. Generation Request**
```json
{
    "input": {
        "type": "generate", 
        "config": "job: generate\nconfig:\n  name: \"test_gen\"\n  process:\n    - type: to_folder\n      device: cuda:0"
    }
}
```

### **4. List Processes**
```json
{
    "input": {
        "type": "processes"
    }
}
```

### **5. List LoRA Models**
```json
{
    "input": {
        "type": "lora"
    }
}
```

## 🔧 Debugging & Troubleshooting

### **Enable Debug Mode**
```bash
# RunPod debugger
python app/rp_handler.py --rp_serve_api --rp_debugger --rp_log_level DEBUG

# Verbose testing
python test_local.py --all --verbose
```

### **Common Issues & Solutions**

**❌ Import Error: Cannot import services**
```bash
# Solution: Check if you're in correct directory
cd Serverless/Backend
python -c "from app.services.gpu_manager import GPUManager; print('✅ Import OK')"
```

**❌ "Process manager not initialized"**
```bash
# Solution: Check Redis connection (for local testing, mock it)
export REDIS_URL="redis://localhost:6379/0"

# Or modify rp_handler.py to use mock services for testing
```

**❌ "Failed to initialize services"**
```bash
# Check if all dependencies are installed
poetry install

# Check if GPU is available (for local testing)
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"
```

### **Mock Services for Testing**

For local testing without full infrastructure:

```python
# In rp_handler.py - add mock mode
import os

MOCK_MODE = os.environ.get("MOCK_MODE", "false").lower() == "true"

if MOCK_MODE:
    # Use mock services instead of real ones
    logger.info("Running in MOCK MODE")
```

## 📈 Performance Testing

### **Load Testing**
```bash
# Multiple concurrent requests
for i in {1..10}; do
  curl -X POST http://localhost:8000/run \
    -H "Content-Type: application/json" \
    -d '{"input": {"type": "health"}}' &
done
wait
```

### **Memory & CPU Monitoring**
```bash
# Monitor resources during testing
python -m memory_profiler test_local.py --all

# Or use htop/top in another terminal
htop
```

## 🚀 Integration with FastAPI

Możesz testować oba podejścia równocześnie:

```bash
# Terminal 1: FastAPI server
cd Serverless/Backend
python -m uvicorn app.main:app --reload --port 8001

# Terminal 2: RunPod handler
python app/rp_handler.py --rp_serve_api --rp_api_port 8000

# Test both
curl http://localhost:8001/api/health  # FastAPI
curl -X POST http://localhost:8000/run -d '{"input": {"type": "health"}}'  # RunPod
```

## 📝 Test Automation

### **CI/CD Testing Script**
```bash
#!/bin/bash
# test.sh - Automated testing script

set -e

echo "🧪 Running LoRA Dashboard Backend Tests..."

# Install dependencies
poetry install

# Run tests
python test_local.py --all

# Check exit code
if [ $? -eq 0 ]; then
    echo "✅ All tests passed!"
else
    echo "❌ Tests failed!"
    exit 1
fi
```

### **GitHub Actions Integration**
```yaml
# .github/workflows/test-backend.yml
name: Test Backend
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - uses: actions/setup-python@v4
      with:
        python-version: '3.12'
    - name: Install dependencies
      run: |
        cd Serverless/Backend
        pip install poetry
        poetry install
    - name: Run tests
      run: |
        cd Serverless/Backend
        python test_local.py --all
```

## 🎯 Next Steps

Po lokalnym testowaniu:

1. **Build Docker Image:**
   ```bash
   docker build -t lora-dashboard-backend .
   ```

2. **Test Docker Locally:**
   ```bash
   docker run -p 8000:8000 -e MOCK_MODE=true lora-dashboard-backend
   ```

3. **Deploy to RunPod:**
   ```bash
   docker push your-username/lora-dashboard-backend
   # Then deploy via RunPod Console or CLI
   ```

## 💡 Tips & Best Practices

1. **Always test locally first** - saves time and money
2. **Use mock mode** for testing without infrastructure dependencies
3. **Test all endpoints** - health, train, generate, processes, lora
4. **Monitor resource usage** - memory, CPU, GPU
5. **Test error scenarios** - invalid inputs, missing configs
6. **Automate testing** - use CI/CD for consistent testing

**�� Happy Testing!** 
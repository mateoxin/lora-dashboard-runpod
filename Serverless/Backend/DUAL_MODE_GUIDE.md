# 🔄 Dual Mode Guide - FastAPI ↔ RunPod Serverless

Przewodnik przełączania między trybami development i production.

## 🏗️ **ARCHITEKTURA DUAL MODE**

Backend LoRA Dashboard wspiera 2 tryby działania z **tym samym API**:

| Tryb | Użycie | Zalety | Kiedy używać |
|------|--------|--------|--------------|
| **🔧 FastAPI** | Development | Szybkie iteracje, debugging | Lokalny development, testing |
| **☁️ RunPod** | Production | Auto-scaling, GPU on-demand | Production, intensive training |

## 🔧 **TRYB 1: FastAPI (Development)**

### Uruchomienie backend'u lokalnie

```bash
# 1. Przejdź do projektu backend
cd Serverless/Backend

# 2. Zainstaluj zależności
pip install -r requirements.txt
# lub
poetry install

# 3. Uruchom FastAPI server
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# ✅ Backend dostępny na: http://localhost:8000
```

### Konfiguracja frontend'u

```typescript
// Serverless/Front/lora-dashboard/src/environments/environment.ts
export const environment = {
  apiBaseUrl: 'http://localhost:8000/api',  // ← FastAPI server
  mockMode: false,                          // ← Użyj prawdziwego backend'u
  // ... reszta konfiguracji
};
```

### Test API

```bash
# Health check
curl http://localhost:8000/api/health

# Training test  
curl -X POST http://localhost:8000/api/train \
  -H "Content-Type: application/json" \
  -d '{"config": "job: extension\nconfig:\n  name: test"}'

# Processes
curl http://localhost:8000/api/processes
```

## ☁️ **TRYB 2: RunPod Serverless (Production)**

### Wdrożenie na RunPod

```bash
# 1. Zbuduj i wypchnij Docker image
docker build -t your-username/lora-dashboard-backend:latest .
docker push your-username/lora-dashboard-backend:latest

# 2. Deploy na RunPod (używając CLI lub Web UI)
runpod create endpoint \
  --name "lora-dashboard" \
  --image "your-username/lora-dashboard-backend:latest" \
  --gpu-type "A40"
```

### Konfiguracja frontend'u

```typescript
// Serverless/Front/lora-dashboard/src/environments/environment.ts
export const environment = {
  // ↓ RunPod endpoint URL (zastąp YOUR_ENDPOINT_ID)
  apiBaseUrl: 'https://YOUR_ENDPOINT_ID-8000.proxy.runpod.net/api',
  mockMode: false,
  // ... reszta konfiguracji
};
```

### Test API

```bash
# Health check (zastąp URL swoim endpoint'em)
curl https://YOUR_ENDPOINT_ID-8000.proxy.runpod.net/api/health

# Training test
curl -X POST https://YOUR_ENDPOINT_ID-8000.proxy.runpod.net/api/train \
  -H "Content-Type: application/json" \
  -d '{"config": "job: extension\nconfig:\n  name: test"}'
```

## 🔄 **PRZEŁĄCZANIE MIĘDZY TRYBAMI**

### Z FastAPI → RunPod

1. **Zatrzymaj lokalny FastAPI server** (Ctrl+C)
2. **Deploy na RunPod** (jeśli jeszcze nie zrobione)
3. **Zmień frontend environment:**
   ```typescript
   apiBaseUrl: 'https://YOUR_ENDPOINT_ID-8000.proxy.runpod.net/api'
   ```
4. **Restart frontend** (`npm start`)

### Z RunPod → FastAPI

1. **Uruchom lokalny FastAPI server:**
   ```bash
   python -m uvicorn app.main:app --reload --port 8000
   ```
2. **Zmień frontend environment:**
   ```typescript
   apiBaseUrl: 'http://localhost:8000/api'
   ```
3. **Restart frontend** (`npm start`)

## 🧪 **TRYB DEVELOPMENT Z MOCK DATA**

```typescript
// Dla rozwoju UI bez backend'u
export const environment = {
  apiBaseUrl: 'http://localhost:8000/api',  // Nieważne gdy mockMode=true
  mockMode: true,                           // ← Użyj mock data
};
```

## ⚙️ **ARCHITEKTURA WEWNĘTRZNA**

### Jak to działa w kodzie:

```
Frontend API Call
        ↓
┌─────────────────┐    ┌─────────────────────┐
│   FastAPI Mode  │    │  RunPod Mode        │
│   (app/main.py) │    │  (rp_handler.py)    │
└─────────────────┘    └─────────────────────┘
        ↓                       ↓
┌─────────────────┐    ┌─────────────────────┐
│  RunPodAdapter  │ ←→ │  async_handler()    │
│  (converts API) │    │  (processes jobs)   │
└─────────────────┘    └─────────────────────┘
        ↓                       ↓
┌─────────────────────────────────────────────┐
│        Shared Business Logic                │
│  • ProcessManager (Redis queue)             │
│  • StorageService (S3/RunPod storage)      │
│  • GPUManager (CUDA management)            │
│  • LoRAService (Model management)          │
└─────────────────────────────────────────────┘
```

### Key Benefits:

- ✅ **Same Business Logic**: Obie tryby używają tych samych serwisów
- ✅ **Same API**: Frontend nie musi się zmieniać
- ✅ **Easy Testing**: Test lokalnie, deploy na RunPod
- ✅ **Cost Effective**: Pay-per-use GPU tylko w production

## 📊 **PORÓWNANIE TRYBÓW**

| Aspekt | FastAPI Mode | RunPod Mode |
|--------|--------------|-------------|
| **Setup Time** | < 1 min | ~10 min |
| **GPU Access** | Local GPU/CPU | Cloud A40 GPU |
| **Scaling** | Manual | Auto-scaling |
| **Cost** | Local resources | Pay-per-use |
| **Development** | ⭐⭐⭐⭐⭐ Fast | ⭐⭐⭐ Slower |
| **Production** | ⭐⭐ Limited | ⭐⭐⭐⭐⭐ Scalable |

## 🎯 **RECOMMENDED WORKFLOW**

1. **Development Phase:**
   - Use **FastAPI mode** for fast iteration
   - Test all features locally
   - Debug and optimize code

2. **Testing Phase:**
   - Use **FastAPI mode** for integration tests
   - Test with real data and workflows
   - Performance baseline

3. **Production Phase:**
   - Deploy to **RunPod mode**
   - Monitor performance and costs
   - Scale as needed

## 🔧 **TROUBLESHOOTING**

### FastAPI Mode Issues

```bash
# Port already in use
netstat -ano | findstr :8000
# Kill process or use different port

# Dependencies missing
pip install -r requirements.txt

# Environment variables
cp .env.example .env
# Edit .env with your settings
```

### RunPod Mode Issues

```bash
# Check endpoint status
runpod get endpoints

# View logs
runpod logs endpoint YOUR_ENDPOINT_ID

# Test connectivity
curl https://YOUR_ENDPOINT_ID-8000.proxy.runpod.net/api/health
```

### Frontend Connection Issues

```typescript
// Enable CORS for local development
apiBaseUrl: 'http://localhost:8000/api',

// Check if backend is running
// Open browser dev tools → Network tab
// Look for failed API calls
```

## 🎉 **READY TO GO!**

Your LoRA Dashboard now supports dual mode architecture:

- ✅ **Fast development** with FastAPI
- ✅ **Production scalability** with RunPod
- ✅ **Unified codebase** for both modes
- ✅ **Easy switching** between environments

**Happy coding!** 🚀 
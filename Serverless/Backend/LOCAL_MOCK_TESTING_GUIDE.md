# 🧪 Local Mock Testing Guide - Frontend ↔ Backend

**Kompletny przewodnik testowania lokalnego bez external dependencies**

## 🎯 **CO TO JEST MOCK TESTING?**

Mock testing pozwala na testowanie całego systemu frontend ↔ backend **lokalnie** bez:
- ❌ Redis
- ❌ S3/Storage  
- ❌ GPU
- ❌ RunPod account
- ❌ External services

**✅ Używa fake services które symulują prawdziwe behavior!**

## 🏗️ **ARCHITEKTURA MOCK MODE**

```
Frontend (Angular)
        ↓ (HTTP calls)
Backend FastAPI (Mock Mode)
        ↓
┌─────────────────────────────────────────┐
│           Mock Services                 │
│  ┌─────────────────────────────────────┐ │
│  │ MockProcessManager                  │ │
│  │ • Fake training/generation processes│ │
│  │ • Simulated progress updates        │ │
│  │ • No Redis dependency              │ │
│  └─────────────────────────────────────┘ │
│  ┌─────────────────────────────────────┐ │
│  │ MockStorageService                  │ │
│  │ • Fake file uploads/downloads       │ │
│  │ • Mock S3 URLs                     │ │
│  │ • No S3 dependency                 │ │
│  └─────────────────────────────────────┘ │
│  ┌─────────────────────────────────────┐ │
│  │ MockLoRAService                     │ │
│  │ • Sample LoRA models                │ │
│  │ • Fake metadata                     │ │
│  └─────────────────────────────────────┘ │
│  ┌─────────────────────────────────────┐ │
│  │ MockGPUManager                      │ │
│  │ • Simulated GPU allocation          │ │
│  │ • No CUDA dependency               │ │
│  └─────────────────────────────────────┘ │
└─────────────────────────────────────────┘
```

## 🚀 **QUICK START - 3 KROKI**

### **1. Setup Backend (Mock Mode)**

```bash
# Przejdź do backend directory
cd "Serverless/Backend"

# Skopiuj mock config
copy mock_config.env .env

# Zainstaluj dependencies (minimal)
pip install fastapi uvicorn pydantic pydantic-settings

# Uruchom backend w mock mode
python -m uvicorn app.main:app --reload --port 8000
```

### **2. Setup Frontend (Real Backend Mode)**

```typescript
// Serverless/Front/lora-dashboard/src/environments/environment.ts
export const environment = {
  apiBaseUrl: 'http://localhost:8000/api',  // ← Backend URL
  mockMode: false,                          // ← Use real backend calls
  // ... reszta config
};
```

### **3. Start Frontend**

```bash
# W drugim terminalu
cd "Serverless/Front/lora-dashboard"
npm start

# Frontend: http://localhost:4200
# Backend:  http://localhost:8000
```

## 🎯 **CO MOŻNA TESTOWAĆ?**

### ✅ **Frontend Features**
- **Navigation**: Wszystkie tabs działają
- **Training Tab**: Start training, config editing  
- **Generation Tab**: LoRA selection, image generation
- **Processes Tab**: Process monitoring, progress bars
- **API Integration**: Wszystkie HTTP calls

### ✅ **Backend Features**  
- **Health Check**: `/api/health`
- **Training**: `/api/train` - simulated training
- **Generation**: `/api/generate` - simulated generation  
- **Processes**: `/api/processes` - fake process list
- **LoRA Models**: `/api/lora` - sample models
- **Process Cancel**: `/api/processes/{id}` DELETE

### ✅ **End-to-End Workflows**
- **Complete Training Flow**: Start → Monitor → Complete
- **Complete Generation Flow**: Select LoRA → Generate → Monitor
- **Process Management**: Start, cancel, monitor multiple processes
- **Real-time Updates**: Progress bars, status changes

## 🧪 **TESTOWANIE KROK PO KROKU**

### **Test 1: Health Check**

```bash
# Backend URL test
curl http://localhost:8000/api/health

# Expected response:
{
  "success": true,
  "data": {
    "status": "healthy",
    "services": {
      "process_manager": "healthy",
      "storage": "healthy", 
      "gpu_manager": {
        "total_gpus": 2,
        "allocated_gpus": 1,
        "available_gpus": 1,
        "gpu_memory": "24GB",
        "gpu_type": "RTX 4090 (Mock)"
      }
    }
  },
  "message": "API is healthy"
}
```

### **Test 2: Training Workflow**

```bash
# Start training
curl -X POST http://localhost:8000/api/train \
  -H "Content-Type: application/json" \
  -d '{
    "config": "job: extension\nconfig:\n  name: \"test_training\"\n  trigger_word: \"test_style\""
  }'

# Expected response:
{
  "success": true,
  "data": {
    "process_id": "training_abc12345"
  },
  "message": "Training process started successfully"
}

# Monitor progress
curl http://localhost:8000/api/processes

# Check specific process
curl http://localhost:8000/api/processes/training_abc12345
```

### **Test 3: LoRA Models**

```bash
# Get available models
curl http://localhost:8000/api/lora

# Expected response:
{
  "models": [
    {
      "id": "lora_001",
      "name": "Anime Style LoRA",
      "path": "/workspace/models/anime_style.safetensors",
      "size": 1048576,
      "metadata": {
        "trigger_word": "anime_style",
        "model_type": "LoRA",
        "steps": 1000,
        "learning_rate": 0.0001,
        "base_model": "flux.1-dev"
      }
    }
  ]
}
```

### **Test 4: Frontend Integration**

1. **Open Frontend**: http://localhost:4200
2. **Check Health**: Dashboard should load without errors  
3. **LoRA Training Tab**:
   - ✅ Config editor works
   - ✅ "Start Training" button works
   - ✅ Process appears in processes tab
4. **Photos Generation Tab**:
   - ✅ LoRA models load in dropdown
   - ✅ Model selection works
   - ✅ "Start Generation" works
5. **Processes Tab**:
   - ✅ Processes list loads
   - ✅ Progress bars update
   - ✅ Cancel button works
   - ✅ LoRA info displays with copy button

## 🔧 **TROUBLESHOOTING**

### **Backend nie startuje**

```bash
# Check Python path
python --version

# Check installed packages
pip list | grep fastapi

# Manual install
pip install fastapi uvicorn pydantic pydantic-settings pyyaml

# Check port
netstat -ano | findstr :8000
```

### **Frontend nie łączy się z backend'em**

```typescript
// Check environment.ts
mockMode: false,                    // ← Must be false!
apiBaseUrl: 'http://localhost:8000/api',  // ← Check URL

// Check browser console
// Look for CORS errors or 404s
```

### **CORS Errors**

Backend ma już skonfigurowane CORS dla localhost:
```python
# app/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows localhost
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### **Mock Services nie działają**

```bash
# Check .env file
cat .env
# Should contain: MOCK_MODE=true

# Check logs
# Backend should show: "🧪 Starting in MOCK MODE"

# Restart backend
# Ctrl+C then restart with uvicorn
```

## ⚡ **PORÓWNANIE TRYBÓW TESTOWANIA**

| Feature | Frontend Mock | Backend Mock | Full Real |
|---------|---------------|--------------|-----------|
| **Setup Time** | < 1 min | ~3 min | ~15 min |
| **External Dependencies** | None | None | Redis, S3, GPU |
| **Frontend Testing** | ✅ UI only | ✅ Full | ✅ Full |
| **Backend Testing** | ❌ None | ✅ API layer | ✅ Complete |
| **API Integration** | ❌ Mocked | ✅ Real HTTP | ✅ Real HTTP |
| **Process Simulation** | ✅ Static | ✅ Dynamic | ✅ Real |
| **Development Speed** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |

## 🎉 **REZULTAT**

Po przejściu tego guide'a będziesz mieć:

- ✅ **Działający backend** z mock services
- ✅ **Działający frontend** łączący się z backend'em  
- ✅ **Pełny workflow** training → generation → monitoring
- ✅ **Debugowane API** - wszystkie endpoint'y przetestowane
- ✅ **Gotowość do production** - wiesz że wszystko działa

## 🚀 **NASTĘPNE KROKI**

Po udanym teście lokalnym:

1. **Deploy na RunPod**: Użyj [RUNPOD_DEPLOYMENT_GUIDE.md](./RUNPOD_DEPLOYMENT_GUIDE.md)
2. **Switch to Production**: Zmień `environment.ts` na RunPod URL
3. **Monitor Costs**: Ustaw budget limits na RunPod
4. **Scale Up**: Dodaj więcej GPU typów i auto-scaling

**Happy Testing!** 🧪✨ 
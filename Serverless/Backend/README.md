# 🚀 LoRA Dashboard Backend

**FastAPI backend dla LoRA Dashboard - Serverless Training & Generation Suite**

Backend obsługuje trenowanie modeli LoRA i generowanie obrazów na GPU RunPod Serverless.

## 📚 Przewodniki wdrożenia

### 🎯 Quick Start (10 minut)
**Najszybszy sposób na uruchomienie:**
- 📖 [QUICK_START.md](./QUICK_START.md) - Wdrożenie w 10 minut

### 📖 Szczegółowy przewodnik 
**Kompletny przewodnik krok po kroku:**
- 📘 [RUNPOD_DEPLOYMENT_GUIDE.md](./RUNPOD_DEPLOYMENT_GUIDE.md) - Kompletne instrukcje

### 🤖 Automatyzacja
**Automatyczne skrypty wdrożenia:**
- 🛠️ [AUTOMATED_DEPLOYMENT.md](./AUTOMATED_DEPLOYMENT.md) - Skrypty i CI/CD

## 🏗️ **NOWA ARCHITEKTURA - DUAL MODE**

**Backend teraz wspiera 2 tryby działania:**

| Mode | Use Case | Benefits |
|------|----------|----------|
| **🔧 FastAPI** | Development, Testing | Fast iteration, debugging |
| **☁️ RunPod Serverless** | Production | Auto-scaling, GPU on-demand |

### **Unified Architecture:**
```
Frontend (Angular)
        ↓ (REST API)
┌─────────────────────────────────────────────┐
│            Backend (Python)                 │
│  ┌─────────────┐    ┌────────────────────┐  │
│  │  FastAPI    │ ←→ │  RunPod Serverless │  │
│  │  Server     │    │  Handler           │  │
│  └─────────────┘    └────────────────────┘  │
│         ↓                     ↓             │
│  ┌─────────────┐    ┌────────────────────┐  │
│  │RunPodAdapter│ ←→ │   rp_handler.py    │  │
│  └─────────────┘    └────────────────────┘  │
│                ↓                            │
│        Shared Business Logic                │
│   ├── ProcessManager (Redis Queue)          │
│   ├── StorageService (S3/RunPod)           │
│   ├── GPUManager (CUDA + A40)              │
│   └── LoRAService (Model Management)        │
└─────────────────────────────────────────────┘
```

### **Key Components:**
- **RunPodAdapter**: Converts REST API → RunPod Serverless format
- **rp_handler.py**: RunPod Serverless entry point
- **app/main.py**: FastAPI development server
- **Shared Services**: Same logic in both modes

### Główne komponenty:
- **FastAPI** - REST API server
- **GPU Manager** - Zarządzanie zasobami GPU
- **Process Manager** - Kolejkowanie i monitorowanie zadań
- **Storage Service** - Integracja z RunPod S3
- **LoRA Service** - Zarządzanie modelami LoRA

## 🔌 API Endpoints

### Podstawowe
- `GET /api/health` - Health check
- `GET /api/processes` - Lista procesów
- `GET /api/lora` - Dostępne modele LoRA

### Operacje
- `POST /api/train` - Uruchom trening LoRA
- `POST /api/generate` - Generuj obrazy
- `DELETE /api/processes/{id}` - Anuluj proces
- `GET /api/download/{id}` - Pobierz wyniki

## 🛠️ Development

### Lokalne uruchomienie
```bash
# Zainstaluj zależności
poetry install

# Uruchom serwer development
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Test
curl http://localhost:8000/api/health
```

### Zmienne środowiskowe
```bash
# Skopiuj przykład
cp .env.example .env

# Główne zmienne:
REDIS_URL=redis://localhost:6379/0
S3_ACCESS_KEY=your-key
S3_SECRET_KEY=your-secret
S3_BUCKET=your-bucket
MAX_CONCURRENT_JOBS=10
```

## 📦 Docker

### Budowanie obrazu
```bash
docker build -t lora-dashboard-backend .
```

### Uruchomienie lokalnie
```bash
docker run -p 8000:8000 \
  -e REDIS_URL="redis://localhost:6379/0" \
  lora-dashboard-backend
```

## 🎯 RunPod Deployment

### 🚀 Szybkie wdrożenie
```bash
# 1. Przygotuj środowisko
cp .env.example .env
# Wypełnij .env swoimi danymi

# 2. Zbuduj i wypchnij obraz
docker build -t your-username/lora-dashboard-backend .
docker push your-username/lora-dashboard-backend

# 3. Deploy na RunPod
pip install runpod
runpod create endpoint \
  --name "lora-dashboard" \
  --image "your-username/lora-dashboard-backend" \
  --gpu-type "A40"
```

### 📖 Szczegółowe instrukcje
Zobacz odpowiedni przewodnik w zależności od Twoich potrzeb:

| Potrzebujesz | Przewodnik | Czas |
|-------------|------------|------|
| Szybkie uruchomienie | [QUICK_START.md](./QUICK_START.md) | 10 min |
| Pełne instrukcje | [RUNPOD_DEPLOYMENT_GUIDE.md](./RUNPOD_DEPLOYMENT_GUIDE.md) | 30 min |
| Automatyzacja | [AUTOMATED_DEPLOYMENT.md](./AUTOMATED_DEPLOYMENT.md) | Różnie |

## 💰 Kontrola kosztów

### Budget monitoring
```bash
# Ustaw limity
runpod billing set-limit --monthly 100.0

# Sprawdź koszty
runpod billing usage --current

# Alert przy 80% budżetu
runpod billing create-alert --threshold 80 --email "your@email.com"
```

### Optymalizacja
- **Scale to Zero**: Automatyczne wyłączanie po 5 min nieaktywności
- **A40 GPU**: Wysokowydajne GPU dla szybkiego trenowania
- **Max Replicas**: Limit jednoczesnych instancji (domyślnie 5)

## 📊 Monitoring

### Sprawdzanie statusu
```bash
# Status endpoints
runpod get endpoints

# Logi w czasie rzeczywistym
runpod logs your-endpoint-id --follow

# Metryki GPU
runpod metrics your-endpoint-id
```

### Health checks
```bash
# Test połączenia
curl https://your-endpoint-url/api/health

# Test treningu
curl -X POST https://your-endpoint-url/api/train \
  -H "Content-Type: application/json" \
  -d '{"config": "..."}'
```

## 🔧 Konfiguracja

### GPU Settings
```python
MAX_CONCURRENT_JOBS=10  # Maksymalnie zadań jednocześnie
GPU_TIMEOUT=14400       # 4 godziny timeout
```

### Storage Settings  
```python
S3_ENDPOINT_URL=https://storage.runpod.io
S3_BUCKET=your-bucket-name
S3_REGION=us-east-1
```

### Process Settings
```python
REDIS_URL=redis://redis:6379/0  # Kolejka zadań
WORKSPACE_PATH=/workspace       # Katalog roboczy
OUTPUT_PATH=/workspace/output   # Wyniki
```

## 🚨 Troubleshooting

### Najczęstsze problemy

**❌ "Container failed to start"**
```bash
# Sprawdź logi
runpod logs your-endpoint-id --tail 50

# Test lokalnie
docker run -p 8000:8000 your-image
```

**❌ "GPU unavailable"**
```bash
# Sprawdź dostępność
runpod gpu list --available

# Zmień typ GPU
runpod update endpoint your-id --gpu-type RTX4090
```

**❌ "Storage connection failed"**
```bash
# Sprawdź secrets
runpod get secrets storage-secrets

# Test endpoint health
curl your-endpoint-url/api/health
```

**❌ "Za wysokie koszty"**
```bash
# Sprawdź użycie
runpod billing usage --detailed

# Zmniejsz repliki
runpod update endpoint your-id --max-replicas 1

# Zatrzymaj endpoint
runpod stop endpoint your-id
```

## 📞 Wsparcie

**Potrzebujesz pomocy?**
- 📖 [RunPod Documentation](https://docs.runpod.io/)
- 💬 [RunPod Discord](https://discord.gg/runpod)
- 🎫 Support ticket w RunPod Console
- 📧 [support@runpod.io](mailto:support@runpod.io)

## 🎉 Co dalej?

Po wdrożeniu backend'u:

1. **Frontend**: Skonfiguruj frontend do połączenia z API
2. **Testing**: Przetestuj pełny workflow treningowy
3. **Monitoring**: Skonfiguruj alerty i monitoring
4. **Backup**: Ustaw automatyczne backupy
5. **CI/CD**: Zautomatyzuj wdrożenia

**🚀 Gratulacje! Twój LoRA Dashboard backend jest gotowy w chmurze!** 
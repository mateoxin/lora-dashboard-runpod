# 🚀 RunPod Serverless Deployment Guide - LoRA Dashboard Backend

Kompletny przewodnik wdrożenia backend'u LoRA Dashboard na RunPod Serverless z GPU A40.

## 🏗️ **NOWA ARCHITEKTURA - DUAL MODE**

**Backend teraz wspiera 2 tryby działania:**

| Mode | Użycie | Zalety |
|------|--------|--------|
| **FastAPI** | Development, lokalny testing | Szybkie iteracje, debugowanie |
| **RunPod Serverless** | Production | Auto-scaling, GPU on-demand, pay-per-use |

**Dual Architecture:**
```
Frontend
    ↓ (REST API calls)
┌─────────────────────────────────────────────────────────┐
│                    Backend                              │
│  ┌─────────────────┐     ┌─────────────────────────────┐ │
│  │  FastAPI Server │ ←→  │   RunPod Serverless        │ │
│  │  (Development)  │     │   (Production)             │ │
│  └─────────────────┘     └─────────────────────────────┘ │
│           ↓                          ↓                   │
│  ┌─────────────────┐     ┌─────────────────────────────┐ │
│  │  RunPodAdapter  │ ←→  │      rp_handler.py         │ │
│  └─────────────────┘     └─────────────────────────────┘ │
│                    ↓                                     │
│              Shared Business Logic                       │
│         (process_manager, storage_service, etc.)        │
└─────────────────────────────────────────────────────────┘
```

**Korzyści:**
- ✅ **Jeden codebase** - ta sama logika w obu trybach
- ✅ **Łatwy development** - szybkie testowanie lokalnie
- ✅ **Production ready** - pełna skalowalnośćRunPod
- ✅ **Frontend compatibility** - bez zmian w API

## 📋 Wymagania

- Konto na RunPod.io
- Docker Desktop zainstalowany lokalnie
- Git 
- Karta kredytowa/PayPal do płatności RunPod

## 🔑 Krok 1: Uzyskanie tokenu RunPod API

### 1.1 Zarejestruj się na RunPod
1. Idź na https://runpod.io
2. Kliknij **"Sign Up"**
3. Stwórz konto z emailem i hasłem
4. Potwierdź email

### 1.2 Dodaj metodę płatności
1. Zaloguj się do RunPod Console: https://www.runpod.io/console
2. Idź do **Account Settings** → **Billing**
3. Kliknij **"Add Payment Method"**
4. Dodaj kartę kredytową lub PayPal
5. **WAŻNE**: Ustaw limit budżetu na $100/miesiąc dla bezpieczeństwa

### 1.3 Wygeneruj API Token
1. W RunPod Console idź do **Settings** → **API Keys**
2. Kliknij **"+ API Key"**
3. Nazwij klucz: `lora-dashboard-backend`
4. Wybierz scope: **"Read/Write"**
5. Kliknij **"Create"**
6. **SKOPIUJ TOKEN** - nie będziesz mógł go ponownie zobaczyć!

```bash
# Zachowaj token w bezpiecznym miejscu
export RUNPOD_API_KEY="your-api-key-here"
```

## 🏗️ Krok 2: Instalacja narzędzi

### 2.1 Zainstaluj RunPod CLI
```bash
# Zainstaluj przez pip
pip install runpod

# Lub jeśli masz problemy z pip
pip3 install runpod

# Sprawdź instalację
runpod --version
```

### 2.2 Zaloguj się do RunPod CLI
```bash
# Ustaw token
runpod config set api-key your-api-key-here

# Sprawdź połączenie
runpod whoami
```

### 2.3 Zainstaluj Docker (jeśli nie masz)
**Windows:**
1. Pobierz Docker Desktop z https://www.docker.com/products/docker-desktop
2. Zainstaluj i uruchom
3. Sprawdź: `docker --version`

**macOS:**
```bash
# Przez Homebrew
brew install --cask docker

# Lub pobierz z strony Docker
```

**Linux:**
```bash
# Ubuntu/Debian
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
```

## 📦 Krok 3: Budowanie obrazu Docker

### 3.1 Przygotuj projekt
```bash
# Przejdź do katalogu backend
cd "Serverless/Backend"

# Sprawdź czy masz wszystkie pliki
ls -la
# Powinniśmy zobaczyć: Dockerfile, pyproject.toml, runpod.yaml, app/
```

### 3.2 Utwórz konto na Docker Hub (jeśli nie masz)
1. Idź na https://hub.docker.com
2. Stwórz darmowe konto
3. Zanotuj swoją nazwę użytkownika

### 3.3 Zbuduj obraz Docker
```bash
# Zastąp "your-username" swoją nazwą użytkownika Docker Hub
export DOCKER_USERNAME="your-username"


# Zbuduj obraz
docker build -t $DOCKER_USERNAME/lora-dashboard-backend:latest .

# Sprawdź czy obraz został zbudowany
docker images | grep lora-dashboard
```

### 3.4 Przetestuj obraz lokalnie
```bash
# Uruchom kontener testowo
docker run -p 8000:8000 \
  -e REDIS_URL="redis://localhost:6379/0" \
  $DOCKER_USERNAME/lora-dashboard-backend:latest &

# Sprawdź czy działa (w nowym terminalu)
curl http://localhost:8000/api/health

# Zatrzymaj kontener
docker stop $(docker ps -q --filter ancestor=$DOCKER_USERNAME/lora-dashboard-backend:latest)
```

### 3.5 Wypchnij obraz do Docker Hub
```bash
# Zaloguj się do Docker Hub
docker login

# Wypchnij obraz
docker push $DOCKER_USERNAME/lora-dashboard-backend:latest
```

## 💾 Krok 4: Konfiguracja Storage

### 4.1 Utwórz RunPod Storage Bucket
1. W RunPod Console idź do **Storage**
2. Kliknij **"+ Create Bucket"**
3. Nazwa: `lora-dashboard-storage`
4. Region: wybierz najbliższy (np. `US-East`)
5. Kliknij **"Create"**

### 4.2 Uzyskaj dane dostępowe S3
1. Kliknij na swój bucket
2. Idź do **"Access Keys"**
3. Kliknij **"Generate Access Key"**
4. **SKOPIUJ I ZAPISZ**:
   - Access Key ID
   - Secret Access Key
   - Endpoint URL (np. `https://storage.runpod.io`)

```bash
# Zapisz dane (NIE commituj do git!)
export S3_ACCESS_KEY="your-access-key"
export S3_SECRET_KEY="your-secret-key"
export S3_BUCKET="lora-dashboard-storage"
export S3_ENDPOINT="https://storage.runpod.io"
```

## 🚀 Krok 5: Deploy na RunPod Serverless

### 5.1 Przygotuj konfigurację
```bash
# W katalogu Serverless/Backend
# Edytuj runpod.yaml - zaktualizuj obraz Docker
sed -i "s/your-registry/$DOCKER_USERNAME/g" runpod.yaml
```

### 5.2 Utwórz secrets
```bash
# Utwórz secret z danymi Storage
runpod create secret storage-secrets \
  --from-literal=bucket-name="$S3_BUCKET" \
  --from-literal=access-key="$S3_ACCESS_KEY" \
  --from-literal=secret-key="$S3_SECRET_KEY"

# Sprawdź czy secret został utworzony
runpod get secrets
```

### 5.3 Deploy endpoint
```bash
# Deploy using CLI
runpod create endpoint \
  --name "lora-dashboard-backend" \
  --image "$DOCKER_USERNAME/lora-dashboard-backend:latest" \
  --gpu-type "A40" \
  --gpu-count 1 \
  --env REDIS_URL="redis://redis:6379/0" \
  --env S3_ENDPOINT_URL="$S3_ENDPOINT" \
  --env MAX_CONCURRENT_JOBS="10" \
  --env GPU_TIMEOUT="14400" \
  --env LOG_LEVEL="INFO" \
  --secret storage-secrets \
  --min-replicas 0 \
  --max-replicas 5 \
  --timeout 4h

# Sprawdź status
runpod get endpoints
```

### 5.4 Alternatywnie: Deploy przez Console UI

**Jeśli CLI nie działa, użyj interfejsu web:**

1. **RunPod Console** → **Serverless** → **+ Create Endpoint**

2. **Basic Configuration:**
   - Name: `lora-dashboard-backend`
   - Container Image: `your-username/lora-dashboard-backend:latest`
   - Container Port: `8000`

3. **GPU Configuration:**
   - GPU Type: `A40`
   - GPU Count: `1`

4. **Environment Variables:**
   ```
   REDIS_URL=redis://redis:6379/0
   S3_ENDPOINT_URL=https://storage.runpod.io
   MAX_CONCURRENT_JOBS=10
   GPU_TIMEOUT=14400
   LOG_LEVEL=INFO
   ```

5. **Secrets:**
   - Select `storage-secrets`
   - Map:
     - `S3_BUCKET` → `bucket-name`
     - `S3_ACCESS_KEY` → `access-key`
     - `S3_SECRET_KEY` → `secret-key`

6. **Scaling:**
   - Min Workers: `0`
   - Max Workers: `5`
   - Idle Timeout: `5 minutes`
   - Max Job Timeout: `4 hours`

7. **Kliknij "Deploy"**

## 🔧 Krok 6: Testowanie wdrożenia (Dual Mode)

### 6.1 Pre-deployment test (FastAPI mode)

**NAJPIERW przetestuj lokalnie przed wdrożeniem na RunPod:**

```bash
# W projekcie backend
cd Serverless/Backend

# Uruchom FastAPI server (używa RunPodAdapter wewnętrznie)
python -m uvicorn app.main:app --reload --port 8000

# W drugim terminalu testuj wszystkie endpoints:
curl http://localhost:8000/api/health
curl -X POST http://localhost:8000/api/train \
  -H "Content-Type: application/json" \
  -d '{"config": "job: extension\nconfig:\n  name: test_local"}'
curl http://localhost:8000/api/processes
curl http://localhost:8000/api/lora
```

**✅ Jeśli wszystko działa lokalnie → Deploy na RunPod!**
**❌ Jeśli błędy → Fix lokalnie, potem deploy.**

### 6.1 Uzyskaj URL endpoint
```bash
# Sprawdź status i URL
runpod get endpoints

# Lub w Console Web sprawdź zakładkę Serverless
```

### 6.2 Test Health Check
```bash
# Zastąp YOUR_ENDPOINT_ID rzeczywistym ID
export ENDPOINT_URL="https://YOUR_ENDPOINT_ID-8000.proxy.runpod.net"

# Test health
curl -f $ENDPOINT_URL/api/health

# Oczekiwana odpowiedź:
# {
#   "success": true,
#   "data": {
#     "status": "healthy",
#     "services": {...}
#   }
# }
```

### 6.3 Test Training Endpoint
```bash
# Test uruchomienia treningu
curl -X POST $ENDPOINT_URL/api/train \
  -H "Content-Type: application/json" \
  -d '{
    "config": "job: extension\nconfig:\n  name: \"test_training\"\n  process:\n    - type: sd_trainer\n      device: cuda:0\n      trigger_word: \"test\""
  }'

# Oczekiwana odpowiedź:
# {
#   "success": true,
#   "data": {"process_id": "training-xyz..."},
#   "message": "Training process started successfully"
# }
```

### 6.4 Test Processes Endpoint
```bash
# Sprawdź procesy
curl $ENDPOINT_URL/api/processes

# Sprawdź konkretny proces
curl $ENDPOINT_URL/api/processes/PROCESS_ID
```

## 💰 Krok 7: Kontrola kosztów

### 7.1 Ustaw alerty budżetu
```bash
# Ustaw limit miesięczny $100
runpod billing set-limit --monthly 100.0

# Ustaw alert na 80%
runpod billing create-alert \
  --threshold 80 \
  --email "your-email@example.com"

# Sprawdź obecne koszty
runpod billing usage --current
```

### 7.2 Optymalizacja kosztów
**W Console Web:**
1. **Endpoint Settings** → **Auto-scaling**
2. Ustaw **"Scale to Zero Delay"** na `5 minutes`
3. Ustaw **"Max Concurrent Requests"** na `1`
4. Włącz **"Automatic Pausing"** przy osiągnięciu budżetu

## 📊 Krok 8: Monitoring i logi

### 8.1 Sprawdzanie logów
```bash
# Zobacz logi w czasie rzeczywistym
runpod logs YOUR_ENDPOINT_ID --follow

# Zobacz ostatnie 100 linii
runpod logs YOUR_ENDPOINT_ID --tail 100

# Tylko błędy
runpod logs YOUR_ENDPOINT_ID --level ERROR
```

### 8.2 Monitorowanie metryki
```bash
# Sprawdź metryki endpoint
runpod metrics YOUR_ENDPOINT_ID

# Sprawdź użycie GPU
runpod gpu usage
```

## 🔄 Krok 9: Aktualizacja frontendu

### 9.1 Zaktualizuj frontend environment
```typescript
// W pliku: Serverless/Front/lora-dashboard/src/environments/environment.ts

export const environment = {
  production: false,
  apiBaseUrl: 'https://YOUR_ENDPOINT_ID-8000.proxy.runpod.net/api', // ← ZMIEŃ TEN URL
  mockMode: false,  // ← USTAW NA FALSE żeby używać prawdziwego API
  encryptionKey: 'LoRA-Dashboard-Secret-Key-2024',
  autoRefreshInterval: 5000,
  maxFileSize: 50 * 1024 * 1024,
};
```

### 9.2 Test frontend z backendem
```bash
# W katalogu frontend
cd "Serverless/Front/lora-dashboard"
npm start

# Sprawdź w przeglądarce:
# 1. Health check w zakładce Network (F12)
# 2. Processes tab - czy ładuje dane
# 3. Spróbuj uruchomić trening
```

## 🚨 Troubleshooting

### Problem: Endpoint nie startuje
```bash
# Sprawdź logi
runpod logs YOUR_ENDPOINT_ID --tail 50

# Sprawdź czy obraz Docker działa lokalnie
docker run -p 8000:8000 your-username/lora-dashboard-backend:latest
```

### Problem: Brak połączenia z Storage
```bash
# Sprawdź secrets
runpod get secrets storage-secrets

# Test endpoint health
curl YOUR_ENDPOINT_URL/api/health
# W odpowiedzi sprawdź czy "storage": "healthy"
```

### Problem: GPU niedostępne
```bash
# Sprawdź dostępność GPU
runpod gpu list --available

# Zmień typ GPU w endpoint
runpod update endpoint YOUR_ENDPOINT_ID --gpu-type RTX4090
```

### Problem: Za wysokie koszty
```bash
# Sprawdź aktualne użycie
runpod billing usage --detailed

# Zatrzymaj endpoint
runpod stop endpoint YOUR_ENDPOINT_ID

# Ustaw niższe limity
runpod update endpoint YOUR_ENDPOINT_ID --max-replicas 1
```

## ✅ Final Checklist

Po wykonaniu wszystkich kroków sprawdź:

- [ ] ✅ Token RunPod API działa
- [ ] ✅ Docker obraz zbudowany i wypchnięty
- [ ] ✅ RunPod Storage bucket utworzony
- [ ] ✅ Secrets skonfigurowane
- [ ] ✅ Endpoint wdrożony na A40 GPU  
- [ ] ✅ Health check przechodzi
- [ ] ✅ Training endpoint testowany
- [ ] ✅ Processes endpoint działa
- [ ] ✅ Alerty budżetu ustawione
- [ ] ✅ Frontend skonfigurowany z prawdziwym API
- [ ] ✅ Logi monitorowane

## 💡 Wskazówki bezpieczeństwa

1. **NIE commituj** API keys, secrets ani credentials do git
2. **Ustaw** limity budżetu przed deployment
3. **Używaj** environment variables dla wszystkich sekretów
4. **Regularnie sprawdzaj** koszty i użycie
5. **Zatrzymuj** endpoint gdy nie używasz

## 📞 Wsparcie

**Jeśli masz problemy:**
1. 📖 RunPod Docs: https://docs.runpod.io/
2. 💬 RunPod Discord: https://discord.gg/runpod  
3. 🎫 Support ticket w RunPod Console
4. 📧 Email support: support@runpod.io

## 🎉 Gratulacje!

Twój backend LoRA Dashboard jest teraz wdrożony na RunPod Serverless z GPU A40! 

Możesz teraz:
- ✨ Trenować modele LoRA w chmurze
- 🎨 Generować obrazy z wytrenowanymi modelami  
- 📊 Monitorować procesy w czasie rzeczywistym
- 💰 Płacić tylko za użyte zasoby GPU

**Następne kroki:**
1. Przetestuj pełny workflow treningowy
2. Skonfiguruj automatyczne backupy
3. Dodaj więcej GPU typów dla różnych zadań
4. Zintegruj z CI/CD dla automatycznych wdrożeń 
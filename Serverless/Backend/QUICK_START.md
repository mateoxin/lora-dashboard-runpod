# 🚀 Quick Start - RunPod Deployment

**Szybkie wdrożenie LoRA Dashboard na RunPod w 10 minut!**

## 🏗️ **DUAL MODE ARCHITECTURE**

**Nowa architektura wspiera 2 tryby:**
- **🔧 FastAPI Mode**: Lokalny development (instant feedback)
- **☁️ RunPod Mode**: Production serverless (auto-scaling GPU)

**Unified API** - Frontend nie musi się zmieniać!

## ⚡ Przed rozpoczęciem

- [x] Konto na RunPod.io z metodą płatności
- [x] Docker zainstalowany lokalnie
- [x] Konto na Docker Hub

## 🔥 1. Przygotuj się (2 min)

```bash
# Sklonuj repo i przejdź do backend
git clone <your-repo>
cd "Serverless/Backend"

# Skopiuj i wypełnij plik środowiska
cp .env.example .env
# Edytuj .env i wpisz swoje dane
```

## 🐳 2. Zbuduj i wypchnij Docker (3 min)

```bash
# Ustaw swoją nazwę Docker Hub
export DOCKER_USERNAME="your-dockerhub-username"

# Zbuduj obraz
docker build -t $DOCKER_USERNAME/lora-dashboard-backend:latest .

# Zaloguj się i wypchnij
docker login
docker push $DOCKER_USERNAME/lora-dashboard-backend:latest
```

## 🔑 3. Uzyskaj API Token RunPod (1 min)

1. **RunPod Console** → **Settings** → **API Keys**
2. **"+ API Key"** → Name: `lora-dashboard` → **Create**
3. **Skopiuj token!**

```bash
# Ustaw token
export RUNPOD_API_KEY="your-api-token"
```

## 🏗️ 4. Deploy na RunPod (2 min)

### Opcja A: CLI (szybsza)
```bash
# Zainstaluj CLI
pip install runpod

# Zaloguj się
runpod config set api-key $RUNPOD_API_KEY

# Deploy endpoint
runpod create endpoint \
  --name "lora-dashboard" \
  --image "$DOCKER_USERNAME/lora-dashboard-backend:latest" \
  --gpu-type "A40" \
  --gpu-count 1 \
  --min-replicas 0 \
  --max-replicas 3 \
  --timeout 4h
```

### Opcja B: Web UI (prostsze)
1. **RunPod Console** → **Serverless** → **"+ Create Endpoint"**
2. **Name**: `lora-dashboard`
3. **Image**: `your-username/lora-dashboard-backend:latest`
4. **GPU**: A40, Count: 1
5. **Port**: 8000
6. **Deploy**

## 💾 5. Konfiguruj Storage (1 min)

1. **RunPod Console** → **Storage** → **"+ Create Bucket"**
2. **Name**: `lora-storage`
3. **Region**: US-East
4. **Create** → **Access Keys** → **Generate**
5. **Skopiuj**: Access Key, Secret Key

## 🧪 6. Test deployment - DUAL MODE (1 min)

### Local Test (FastAPI mode)
```bash
# Test lokalnie PRZED wdrożeniem
cd Serverless/Backend
python -m uvicorn app.main:app --reload --port 8000

# W drugim terminalu:
curl http://localhost:8000/api/health
```

### Production Test (RunPod mode)

```bash
# Sprawdź status endpoint
runpod get endpoints

# Test health (zastąp URL swoim)
curl https://YOUR_ENDPOINT_ID-8000.proxy.runpod.net/api/health
```

## 🎯 7. Skonfiguruj Frontend

```typescript
// Serverless/Front/lora-dashboard/src/environments/environment.ts
export const environment = {
  apiBaseUrl: 'https://YOUR_ENDPOINT_ID-8000.proxy.runpod.net/api',
  mockMode: false,  // ← WAŻNE: wyłącz mock!
  // ... reszta
};
```

## ✅ Gotowe!

Twój backend działa na RunPod! 🎉

**Test pełny workflow:**
1. Frontend: `npm start` 
2. Idź do zakładki "LoRA Training"
3. Kliknij "Start LoRA Training"
4. Sprawdź zakładkę "Processes"

## 💰 Kontrola kosztów

```bash
# Ustaw limity budżetu
runpod billing set-limit --monthly 100.0

# Monitoruj koszty
runpod billing usage --current
```

## 🆘 Problem?

**Najczęstsze problemy:**
- ❌ **"Container failed to start"** → Sprawdź logi: `runpod logs YOUR_ENDPOINT_ID`
- ❌ **"GPU unavailable"** → Zmień typ GPU: `--gpu-type RTX4090`
- ❌ **"Too expensive"** → Ustaw `--max-replicas 1`

**Potrzebujesz pomocy?**
- 📖 [Pełny przewodnik](./RUNPOD_DEPLOYMENT_GUIDE.md)
- 💬 [RunPod Discord](https://discord.gg/runpod)

---

**🎊 Gratulacje! Masz działający LoRA Dashboard w chmurze!** 
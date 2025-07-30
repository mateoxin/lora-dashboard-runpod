# 🚀 **MANUAL RUNPOD DEPLOYMENT - SIMPLE BACKEND**

## ✅ **OBRAZ DOCKER GOTOWY:**
- Image: `mateoxin/simple-runpod-test:v2`
- Status: ✅ Pushed to Docker Hub

## 🎯 **KROK 1: Utwórz Template na RunPod**

1. **Przejdź do RunPod Console:** https://www.runpod.io/console
2. **Serverless** → **Templates** → **New Template**
3. **Wypełnij konfigurację:**

```
Template Name: simple-backend-test
Container Image: mateoxin/simple-runpod-test:v2
Container Registry Credentials: (leave empty for public)

Container Configuration:
- Container Disk: 5 GB
- Expose HTTP Ports: 8000
- Expose TCP Ports: (leave empty)

Environment Variables:
- PYTHONUNBUFFERED = 1

Docker Command: (leave empty - uses CMD from Dockerfile)
```

4. **Save Template**

## 🎯 **KROK 2: Utwórz Endpoint**

1. **Serverless** → **Endpoints** → **New Endpoint**
2. **Wybierz utworzony template:** `simple-backend-test`
3. **Konfiguracja endpointu:**

```
Endpoint Name: simple-backend-3090
GPU Configuration:
- GPU Type: RTX 3090
- GPU Count: 1

Scaling Configuration:
- Min Workers: 0
- Max Workers: 1
- Idle Timeout: 5 seconds
- Scale Type: Queue Delay
- Scale Value: 1

Advanced Settings:
- Request Timeout: 60 seconds
- Container Startup Timeout: 60 seconds
```

4. **Create Endpoint**

## 🎯 **KROK 3: Przetestuj Endpoint**

Po utworzeniu endpointu otrzymasz:
- **Endpoint ID**: (np. `xyz123abc456`)
- **Endpoint URL**: `https://api.runpod.ai/v2/xyz123abc456`

### **Test 1: Health Check**
```bash
curl -X POST https://api.runpod.ai/v2/YOUR_ENDPOINT_ID/runsync \
  -H "Authorization: Bearer YOUR_RUNPOD_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"input": {"type": "health"}}'
```

**Spodziewany wynik:**
```json
{
  "status": "COMPLETED",
  "output": {
    "status": "healthy",
    "timestamp": "2024-01-30T...",
    "message": "Simple backend is working!"
  }
}
```

### **Test 2: Ping Test**
```bash
curl -X POST https://api.runpod.ai/v2/YOUR_ENDPOINT_ID/runsync \
  -H "Authorization: Bearer YOUR_RUNPOD_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"input": {"type": "ping"}}'
```

### **Test 3: Echo Test**
```bash
curl -X POST https://api.runpod.ai/v2/YOUR_ENDPOINT_ID/runsync \
  -H "Authorization: Bearer YOUR_RUNPOD_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"input": {"type": "echo", "message": "Hello RunPod!"}}'
```

## 🎯 **KROK 4: Zaktualizuj Config**

Po utworzeniu endpointu, zaktualizuj pliki konfiguracyjne:

```bash
# W pliku Serverless/Testing/config.env
RUNPOD_ENDPOINT_ID=YOUR_NEW_ENDPOINT_ID

# W pliku Serverless/SimpleTest/config.env  
RUNPOD_ENDPOINT_ID=YOUR_NEW_ENDPOINT_ID
```

## 🧪 **KROK 5: Uruchom Automatyczne Testy**

```bash
cd Serverless/SimpleTest
python test_simple_backend.py
```

## 📊 **MONITORING**

1. **RunPod Console** → **Serverless** → **Endpoints**
2. **Kliknij na endpoint** → **Metrics**
3. **Sprawdź:**
   - Request count
   - Response times
   - Errors
   - Costs

## 💰 **KOSZTY (RTX 3090)**

- **Idle**: $0.00/min (0 workers)
- **Active**: ~$0.50/min podczas pracy
- **Tip**: Ustaw `Max Workers: 1` żeby ograniczyć koszty

## 🔧 **TROUBLESHOOTING**

### **Problem: Container nie startuje**
```bash
# Sprawdź logi w RunPod Console
# Lub przetestuj lokalnie:
docker run -p 8000:8000 mateoxin/simple-runpod-test:v2
```

### **Problem: Timeout na requests**
- Zwiększ `Request Timeout` w konfiguracji endpointu
- Sprawdź czy handler odpowiada szybko

### **Problem: High costs**
- Ustaw `Min Workers: 0` 
- Zmniejsz `Idle Timeout`
- Użyj cheaper GPU (A40 zamiast 3090)

---

## 🎉 **ENDPOINT GOTOWY!**

Po wykonaniu tych kroków będziesz miał:
✅ Działający endpoint z RTX 3090
✅ 1 worker maximum
✅ Gotowy do testowania
✅ Minimalne koszty (auto-scale to 0)

**Next:** Przetestuj wszystkie funkcje i sprawdź monitoring! 
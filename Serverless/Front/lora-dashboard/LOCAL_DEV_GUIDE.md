# 🔧 **Local Development Guide - LoRA Dashboard**

## 🚀 **Quick Start (z RunPod tokenem)**

### **1. 🏃‍♂️ Uruchomienie z tokenem (Recommended)**
```bash
cd "Serverless/Front/lora-dashboard"
npm run dev
# lub
npm run start:local
```

**Co to robi:**
- ✅ Używa `environment.local.ts` z twoim tokenem RunPod
- ✅ Otwiera automatycznie przeglądarkę (`--open`)
- ✅ Łączy się z prawdziwym backend API
- ✅ Port: http://localhost:4200

---

## 🎯 **Wszystkie tryby uruchamiania**

### **A. 🚀 Z tokenem RunPod (Local backend)**
```bash
npm run start:local        # Z tokenem, bez SSL
npm run start:local-token  # Alias, to samo co wyżej
npm run dev                # Najkrótszy alias
```

### **B. 🚀 RunPod Serverless Backend (Production)**
```bash
npm run start:runpod       # Frontend → RunPod backend
npm run dev:runpod         # Alias, to samo co wyżej
```

### **C. 🧪 Mock Mode (Fake data)**
```bash
npm run start:mock         # Tylko mock data, bez API
npm run start              # Standard development (SSL + mock)
```

### **D. 🏭 Production Build**
```bash
npm run build:local        # Build z lokalnym tokenem
npm run build:runpod       # Build dla RunPod integration
npm run build:prod         # Production build (bez tokenów)
```

---

## 🔒 **Security i konfiguracja**

### **Token Configuration**
Twój token jest w: `src/environments/environment.local.ts`
```typescript
runpodToken: 'YOUR_RUNPOD_TOKEN_HERE' // Replace with your actual token
```

### **⚠️ Ważne Security Notes:**
- ✅ `environment.local.ts` jest w `.gitignore` 
- ✅ Token NIE będzie commitowany do git
- ✅ Tylko dla lokalnego development
- ❌ NIE używaj tego w production

---

## 🛠️ **Troubleshooting**

### **Problem: Brak pliku environment.local.ts**
```bash
# Stwórz plik ponownie:
# Serverless/Front/lora-dashboard/src/environments/environment.local.ts
```

### **Problem: Token nie działa**
1. Sprawdź czy token jest aktualny w RunPod Console
2. Sprawdź czy backend jest uruchomiony: `http://localhost:8000/api/health`
3. Sprawdź Network tab w Developer Tools (F12)

### **Problem: CORS errors**
```bash
# Uruchom backend z CORS:
cd "Serverless/Backend"
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

---

## 🔗 **Backend Setup**

### **Dual Mode Backend**
Uruchom backend w trybie FastAPI:
```bash
cd "Serverless/Backend"
python -m uvicorn app.main:app --reload --port 8000
```

Backend URL: `http://localhost:8000/api`

---

## 📁 **File Structure**
```
src/environments/
├── environment.ts          # Default (development)
├── environment.prod.ts     # Production (no tokens)
└── environment.local.ts    # LOCAL ONLY (with your token)
```

---

## 🚀 **RunPod Integration Setup**

### **🔗 Po deployment backend na RunPod:**

1. **Skopiuj Endpoint URL z RunPod Console:**
   ```
   https://abc123def-8000.proxy.runpod.net
   ```

2. **Zaktualizuj `src/environments/environment.runpod.ts`:**
   ```typescript
   apiBaseUrl: 'https://abc123def-8000.proxy.runpod.net/api'
   ```

3. **Uruchom frontend z RunPod backend:**
   ```bash
   npm run dev:runpod
   ```

### **🎯 Co to robi:**
- ✅ Frontend localhost:4200
- ✅ Backend na RunPod Serverless  
- ✅ GPU A40 auto-scaling
- ✅ Prawdziwe AI training workloads
- ✅ Production-ready architecture

### **🔧 Troubleshooting RunPod:**
```bash
# Sprawdź health backend na RunPod
curl https://YOUR_ENDPOINT_ID-8000.proxy.runpod.net/api/health

# Sprawdź logi w RunPod Console
# Network tab w Developer Tools (F12)
```

---

## 🎯 **Next Steps**

1. **✅ Run:** `npm run dev`
2. **🌐 Open:** http://localhost:4200  
3. **🔑 Login:** Użyj hardcoded credentials
4. **📊 Test:** Sprawdź Processes tab
5. **🚀 Deploy:** `npm run build:prod` dla production

---

## 💡 **Pro Tips**

```bash
# Hot reload z tokenem
npm run dev

# Testowanie bez backend (mock data)
npm run start:mock

# Build lokalny (z tokenem dla testów)
npm run build:local

# Quick backend health check
curl http://localhost:8000/api/health
```

**Happy coding!** 🎉 
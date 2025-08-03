# 🎨 LoRA Dashboard - Serverless Training & Generation Suite

Kompletny system do treningu LoRA i generowania obrazów z Angular 17 Frontend + FastAPI Backend, gotowy do deployment na RunPod.

## 🚀 **HARDCODED CONFIGURATION - READY TO USE**

**WSZYSTKIE TOKENY SĄ ZACHARDKODOWANE DLA ŁATWEGO UŻYCIA:**

```bash
# RunPod API Token (READY)
RUNPOD_TOKEN=rpa_G4713KLVTYYBJYWPO157LX7VVPGV7NZ2K87SX6B17otl1t

# HuggingFace Token (READY)  
HF_TOKEN=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

# GitHub Token (READY)
GITHUB_TOKEN=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
```

## 🏗️ **Architektura**

```
LoRA Dashboard/
├── Frontend/ (Angular 17 + Material + TailwindCSS)
│   ├── 🏋️ LoRA Training Tab - YAML Config + Start Training
│   ├── 🖼️ Photos Generation Tab - FLUX + LoRA Selection  
│   └── 📊 Process Monitor Tab - Real-time Status
│
├── Backend/ (FastAPI + Dual Mode)
│   ├── 💻 FastAPI Server (Development)
│   ├── ☁️ RunPod Handler (Production)
│   └── 🎯 Mock Services (Testing)
```

## ⚡ **INSTANT START**

### **1. Frontend (Angular 17)**
```bash
cd Serverless/Front/lora-dashboard
source ~/.nvm/nvm.sh
npm install
npm run start:local

# ✅ Available at: http://localhost:4200
```

### **2. Backend (FastAPI)**
```bash  
cd Serverless/Backend
python -m uvicorn app.main:app --reload --port 8000

# ✅ Available at: http://localhost:8000
```

### **3. RunPod Deployment**
```bash
# Build & Deploy - ALL TOKENS INCLUDED
docker build -t lora-dashboard-backend .
# Deploy to RunPod with pre-configured tokens
```

## 🎯 **Features**

### ✅ **Frontend (Angular 17)**
- **Material Design UI** - Modern, responsive interface
- **TailwindCSS** - Utility-first CSS framework
- **Monaco Editor** - Professional YAML editor
- **Real-time Updates** - Live process monitoring
- **Multi-Environment** - Dev/Local/Prod configurations

### ✅ **Backend (FastAPI)**  
- **Dual Mode** - FastAPI + RunPod Serverless
- **GPU Management** - A40, RTX A6000, A100 support
- **S3 Storage** - RunPod compatible storage
- **Redis Queue** - Job management system
- **Mock Services** - Development testing

### ✅ **LoRA Training**
- **FLUX.1-dev Integration** - Latest model support
- **Custom Datasets** - Upload your training data  
- **Progress Tracking** - Real-time training progress
- **Model Export** - Ready-to-use LoRA models

### ✅ **Image Generation**
- **LoRA Selection** - Use trained models
- **Batch Generation** - Multiple images at once
- **Copy Paths** - Easy model path access
- **Download Management** - Organized file handling

## 🔑 **Pre-configured Tokens**

Wszystkie tokeny są już skonfigurowane w plikach:

```typescript
// Frontend: src/environments/environment.ts
runpodToken: 'rpa_G4713KLVTYYBJYWPO157LX7VVPGV7NZ2K87SX6B17otl1t'
apiBaseUrl: 'https://api.runpod.ai/v2/rqwaizbda7ucsj'

// Backend: config.env  
RUNPOD_API_TOKEN=rpa_G4713KLVTYYBJYWPO157LX7VVPGV7NZ2K87SX6B17otl1t
HF_TOKEN=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
```

## 📱 **UI Screenshots**

- 🏋️ **Training Tab**: YAML editor + training controls
- 🖼️ **Generation Tab**: LoRA selection + FLUX generation  
- 📊 **Monitor Tab**: Live process tracking + progress bars

## 🔧 **Configuration**

### **Environment Variables (Already Set):**
```bash
# RunPod Configuration
RUNPOD_API_TOKEN=rpa_G4713KLVTYYBJYWPO157LX7VVPGV7NZ2K87SX6B17otl1t
RUNPOD_ENDPOINT_ID=rqwaizbda7ucsj

# AI/ML Configuration  
HF_TOKEN=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
MAX_CONCURRENT_JOBS=10
GPU_TIMEOUT=14400

# Storage (S3 Compatible)
S3_ENDPOINT_URL=https://storage.runpod.io
S3_REGION=us-east-1
```

## 🚀 **Deployment Commands**

```bash
# 1. Clone Repository
git clone https://github.com/mateoxin/lora-dashboard-runpod.git
cd lora-dashboard-runpod

# 2. Start Frontend
cd Serverless/Front/lora-dashboard  
npm install && npm start

# 3. Start Backend  
cd ../Backend
python -m uvicorn app.main:app --reload

# 4. Deploy to RunPod
docker build -t lora-dashboard . && docker push
```

## 💰 **Cost Controls**

- **Max Spend**: $20/hour, $500/month
- **Auto-pause**: On budget limits  
- **Scale-to-zero**: After 5 minutes idle
- **Budget Alerts**: 80% and 95% thresholds

## 🛡️ **Security**

- **AES-256-CBC** client-side encryption
- **JWT-like tokens** with expiration
- **CORS protection** for API endpoints
- **Input validation** with Pydantic models

## 🧪 **Testing**

```bash
# Frontend Tests
npm test

# Backend Tests  
pytest

# Integration Tests
npm run test:e2e
```

## 📚 **Documentation**

- **Frontend Setup**: Front/FRONTEND_SETUP.md
- **Backend Deploy**: Backend/RUNPOD_DEPLOYMENT_GUIDE.md  
- **Local Testing**: Backend/LOCAL_TESTING_GUIDE.md

## 🎉 **Ready to Use!**

Projekt jest w pełni skonfigurowany z wszystkimi tokenami. Wystarczy uruchomić i korzystać!

**Frontend**: http://localhost:4200  
**Backend**: http://localhost:8000  
**API Docs**: http://localhost:8000/docs

---

**⚠️ UWAGA**: Tokeny są zachardkodowane dla łatwego użycia. W środowisku produkcyjnym zaleca się używanie zmiennych środowiskowych.
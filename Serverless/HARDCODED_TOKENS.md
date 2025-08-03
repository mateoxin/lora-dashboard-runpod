# 🔑 HARDCODED TOKENS - READY TO USE

## ⚡ **INSTANT DEPLOYMENT - ALL TOKENS CONFIGURED**

Wszystkie tokeny są zachardkodowane w projekcie dla łatwego użycia:

### 🚀 **RunPod Configuration**
```bash
# RunPod API Token (ACTIVE)
RUNPOD_TOKEN=rpa_G4713KLVTYYBJYWPO157LX7VVPGV7NZ2K87SX6B17otl1t

# RunPod Endpoint (READY)
ENDPOINT_ID=rqwaizbda7ucsj
ENDPOINT_URL=https://api.runpod.ai/v2/rqwaizbda7ucsj
```

### 🤗 **HuggingFace Configuration**
```bash
# HuggingFace Token (ACTIVE)
HF_TOKEN=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
```

### 🔒 **GitHub Configuration**
```bash
# GitHub Token (ACTIVE)
GITHUB_TOKEN=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
```

## 📁 **Files with Hardcoded Tokens**

### **Frontend:**
- `src/environments/environment.ts` - Default environment
- `src/environments/environment.local.ts` - Local development  
- `src/environments/environment.prod.ts` - Production
- `src/environments/environment.runpod.ts` - RunPod deployment
- `config.env` - Frontend configuration

### **Backend:**
- `config.env` - Backend configuration
- `config.env.template` - Template with tokens

## 🚀 **Quick Commands**

### **Start Frontend:**
```bash
cd Serverless/Front/lora-dashboard
npm install
npm run start:local     # Local development
npm run start:runpod    # RunPod mode
```

### **Start Backend:**
```bash
cd Serverless/Backend
python -m uvicorn app.main:app --reload --port 8000
```

### **Deploy to RunPod:**
```bash
# All tokens already configured!
docker build -t lora-dashboard-backend .
# Deploy with pre-configured environment
```

## ⚠️ **Security Note**

Tokeny są zachardkodowane dla łatwego developmentu i testowania. 
W środowisku produkcyjnym zaleca się:

1. Używanie zmiennych środowiskowych
2. Rotację tokenów co 90 dni
3. Monitoring użycia API
4. Backup tokenów w bezpiecznym miejscu

## 🎯 **Ready to Use!**

Projekt jest gotowy do uruchomienia bez żadnej dodatkowej konfiguracji. 
Wszystkie tokeny są aktywne i skonfigurowane.
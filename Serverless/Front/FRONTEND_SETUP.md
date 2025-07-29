# 🎨 LoRA Dashboard Frontend - Setup Guide

Angular 17 frontend aplikacji do zarządzania treningiem LoRA i generowaniem obrazów.

## 🏗️ **Architektura Frontend**

```
Angular 17 Frontend
├── 🔐 Authentication (wyłączone w dev)
├── 📝 LoRA Training Tab - Konfiguracja YAML + Start Training  
├── 🖼️ Photos Generation Tab - Generowanie obrazów z LoRA
└── 📊 Process Monitor Tab - Status procesów w czasie rzeczywistym
```

## 🚀 **Quick Start**

### **1. Instalacja Dependencies**

```bash
# Przejdź do frontend directory
cd "Serverless/Front/lora-dashboard"

# Zainstaluj dependencies
npm install

# Start development server
npm start

# Frontend dostępny na: http://localhost:4200
```

### **2. Konfiguracja Backend Connection**

**Plik:** `src/environments/environment.ts`

```typescript
export const environment = {
  production: false,
  
  // 🏗️ DUAL MODE BACKEND CONFIG
  // FastAPI Mode (Development): http://localhost:8000/api
  // RunPod Mode (Production): https://YOUR_ENDPOINT_ID-8000.proxy.runpod.net/api
  apiBaseUrl: 'http://localhost:8000/api',
  
  // Security
  encryptionKey: 'LoRA-Dashboard-Secret-Key-2024',
  
  // UI Settings
  autoRefreshInterval: 5000, // 5 seconds
  maxFileSize: 50 * 1024 * 1024, // 50MB
  
  // 🧪 TESTING MODE
  // true  = Use mock data (for UI development)
  // false = Connect to real backend (FastAPI or RunPod)
  mockMode: false, // ← USTAW NA FALSE dla prawdziwego backend!
};
```

## 🎯 **Główne Features**

### **Tab 1: LoRA Training**
- ✅ **YAML Configuration**: Edycja konfiguracji treningowej
- ✅ **Template System**: Predefiniowane szablony
- ✅ **Start Training**: Przycisk do rozpoczęcia treningu
- ✅ **Validation**: Sprawdzanie składni YAML

### **Tab 2: Photos Generation**  
- ✅ **LoRA Selection**: Wybór wytrenowanych modeli LoRA
- ✅ **Prompt System**: Wielopromptsowe generowanie
- ✅ **FLUX Integration**: Integracja z FLUX.1-dev
- ✅ **Copy LoRA Path**: Kopiowanie ścieżek do schowka

### **Tab 3: Process Monitor**
- ✅ **Real-time Updates**: Auto-refresh co 5 sekund
- ✅ **Progress Tracking**: Paski postępu dla zadań
- ✅ **Process Management**: Start, stop, view details
- ✅ **LoRA Path Display**: Wyświetlanie ścieżek z przyciskiem kopiowania

## 🔧 **Configuration Options**

### **Backend Modes:**
```typescript
// 1. Mock Mode (UI Development)
mockMode: true,   // Używa fake data z mock-api.service.ts

// 2. FastAPI Mode (Local Backend) 
mockMode: false,
apiBaseUrl: 'http://localhost:8000/api'

// 3. RunPod Mode (Production)
mockMode: false,
apiBaseUrl: 'https://YOUR_ENDPOINT_ID-8000.proxy.runpod.net/api'
```

### **Authentication:**
```typescript
// Authentication jest WYŁĄCZONE w development
// W app-routing.module.ts:
{ path: '', redirectTo: '/dashboard', pathMatch: 'full' }  // ← Bez logowania

// W dashboard.component.ts:
// ngOnInit() {
//   // Authentication checks są zakomentowane
// }
```

## 🎨 **UI/UX Features**

- ✅ **Material Design**: Angular Material components
- ✅ **TailwindCSS**: Modern styling system
- ✅ **Responsive Design**: Mobile-friendly
- ✅ **Dark/Light Theme**: Auto theme switching
- ✅ **Copy to Clipboard**: Easy path copying
- ✅ **Real-time Updates**: Live process monitoring

## 🧪 **Development & Testing**

### **Local Development:**
```bash
# Start backend first (w mock mode)
cd "Serverless/Backend"
copy mock_config.env .env
python -m uvicorn app.main:app --reload --port 8000

# Start frontend (w drugim terminalu)
cd "Serverless/Front/lora-dashboard"  
npm start

# Test frontend-backend connection:
# 1. Otwórz http://localhost:4200
# 2. Sprawdź czy Process Monitor tab pokazuje procesy
# 3. Przetestuj Start Training w LoRA Training tab
```

### **Production Deployment:**
```typescript
// environment.prod.ts
export const environment = {
  production: true,
  apiBaseUrl: 'https://YOUR_RUNPOD_ENDPOINT.proxy.runpod.net/api',
  mockMode: false,
  // ... reszta config
};
```

## 📋 **Build & Deploy**

```bash
# Development build
ng build

# Production build
ng build --configuration production

# Serve built files (example with simple HTTP server)
npx http-server dist/lora-dashboard -p 4200 --cors
```

## 🚨 **Common Issues**

### **1. "Failed to start generation"**
- ✅ Check `mockMode: false` in environment.ts
- ✅ Verify backend is running on http://localhost:8000  
- ✅ Test backend health: `GET http://localhost:8000/api/health`

### **2. "CORS errors"**
- ✅ Backend ma CORS enabled dla http://localhost:4200
- ✅ Check CORS configuration w backend/main.py

### **3. "Process Monitor empty"**
- ✅ Backend mock services muszą być włączone (`MOCK_MODE=true`)
- ✅ Frontend `mockMode: false` + `apiBaseUrl` pointing to backend

### **4. "Authentication redirect loop"**
- ✅ Authentication jest wyłączone w development
- ✅ Default route: `''` → `'/dashboard'`

## 📚 **Struktura Kodu**

```
src/app/
├── auth/                     # Authentication (wyłączone)
├── core/                     # Services & Models
│   ├── api.service.ts        # HTTP client for backend
│   ├── mock-api.service.ts   # Mock data service  
│   └── models/               # TypeScript interfaces
├── dashboard/                # Main application
│   ├── config-tab/           # LoRA Training tab
│   ├── lora-tab/             # Photos Generation tab  
│   └── processes-tab/        # Process Monitor tab
└── environments/             # Configuration files
```

## 💡 **Tips & Best Practices**

1. **Always test locally first** z mock backend
2. **Use mockMode: false** for integration testing  
3. **Check browser console** for API errors
4. **Test all tabs** before production deployment
5. **Verify LoRA paths** are copyable and correct 
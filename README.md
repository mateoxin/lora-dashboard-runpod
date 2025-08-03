# 🎨 LoRA Dashboard - Serverless Training & Generation Suite

[![Angular](https://img.shields.io/badge/Angular-17-red.svg)](https://angular.io/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Latest-green.svg)](https://fastapi.tiangolo.com/)
[![RunPod](https://img.shields.io/badge/RunPod-Ready-blue.svg)](https://runpod.io/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.4-blue.svg)](https://www.typescriptlang.org/)

**Kompletny system do treningu LoRA i generowania obrazów z FLUX.1-dev**

🚀 **HARDCODED TOKENS - READY TO USE!** 🚀

## ⚡ **Instant Start**

```bash
# 1. Clone Repository
git clone https://github.com/mateoxin/lora-dashboard-runpod.git
cd lora-dashboard-runpod

# 2. Start Frontend (Angular 17)
cd Serverless/Front/lora-dashboard
npm install && npm run start:local

# 3. Start Backend (FastAPI)  
cd ../Backend
python -m uvicorn app.main:app --reload

# ✅ Frontend: http://localhost:4200
# ✅ Backend:  http://localhost:8000
```

## 🏗️ **Architecture**

```mermaid
graph TB
    subgraph "Frontend (Angular 17)"
        A[🏋️ LoRA Training Tab<br/>YAML Config + Start Training]
        B[🖼️ Photos Generation Tab<br/>LoRA Selection + FLUX Generation]
        C[📊 Process Monitor Tab<br/>Real-time Status + Progress]
    end
    
    subgraph "Backend (Dual Mode)"
        D[💻 FastAPI Server<br/>Development/Testing]
        E[☁️ RunPod Handler<br/>Production/Auto-scaling]
    end
    
    subgraph "Infrastructure"
        F[🚀 RunPod A40 GPUs<br/>Auto-scaling]
        G[💾 S3 Compatible Storage<br/>Models + Images]
        H[⚡ Redis Queue<br/>Job Management]
    end
    
    A --> D
    B --> D
    C --> D
    D --> E
    E --> F
    E --> G
    E --> H
```

## 🔑 **Pre-configured Tokens (HARDCODED)**

**Wszystkie tokeny są już skonfigurowane!**

```bash
🚀 RUNPOD_TOKEN=rpa_G4713KLVTYYBJYWPO157LX7VVPGV7NZ2K87SX6B17otl1t
🤗 HF_TOKEN=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  
🔒 GITHUB_TOKEN=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
```

## ✨ **Features**

### 🎨 **Frontend (Angular 17 + Material Design)**
- **Modern UI** - Material Design + TailwindCSS
- **Monaco Editor** - Professional YAML configuration
- **Real-time Monitoring** - Live process updates
- **Multi-Environment** - Dev/Local/Production configs
- **Responsive Design** - Works on desktop and mobile

### ⚙️ **Backend (FastAPI + RunPod)**
- **Dual Mode** - Local FastAPI + RunPod Serverless
- **GPU Support** - A40, RTX A6000, A100 compatible
- **Queue Management** - Redis-based job processing
- **S3 Storage** - RunPod compatible file storage
- **Mock Services** - Local development testing

### 🏋️ **LoRA Training**
- **FLUX.1-dev Integration** - Latest AI model
- **Custom Datasets** - Upload your training images
- **Progress Tracking** - Real-time training status
- **Model Export** - Download trained LoRA models

### 🖼️ **Image Generation**
- **LoRA Selection** - Use your trained models
- **Batch Processing** - Generate multiple images
- **FLUX Integration** - High-quality image generation
- **Download Management** - Organized file handling

## 📱 **UI Screenshots**

| Training Tab | Generation Tab | Monitor Tab |
|-------------|----------------|-------------|
| ![Training](docs/screenshots/training.png) | ![Generation](docs/screenshots/generation.png) | ![Monitor](docs/screenshots/monitor.png) |

## 🚀 **Deployment Options**

### **💻 Local Development**
```bash
# Backend (Mock mode)
cd Serverless/Backend
python -m uvicorn app.main:app --reload

# Frontend  
cd Serverless/Front/lora-dashboard
npm start
```

### **☁️ RunPod Production**
```bash
# Build Docker image
docker build -t lora-dashboard-backend .

# Deploy to RunPod (tokens pre-configured)
# See: Serverless/Backend/RUNPOD_DEPLOYMENT_GUIDE.md
```

### **🌐 Frontend Hosting**
- **Netlify**: Auto-deploy from GitHub
- **Vercel**: Zero-config deployment
- **GitHub Pages**: Static hosting

## 📁 **Project Structure**

```
lora-dashboard-runpod/
├── 📱 Serverless/
│   ├── 🎨 Front/                    # Angular 17 Frontend
│   │   └── lora-dashboard/
│   │       ├── src/app/
│   │       │   ├── dashboard/       # Main dashboard
│   │       │   ├── auth/           # Authentication
│   │       │   └── core/           # Services & models
│   │       └── src/environments/   # Configurations
│   │
│   ├── ⚙️ Backend/                  # FastAPI Backend
│   │   ├── app/
│   │   │   ├── core/              # Configuration
│   │   │   ├── services/          # Business logic
│   │   │   └── main.py            # FastAPI app
│   │   └── config.env             # Hardcoded tokens
│   │
│   └── 📚 Documentation/
│       ├── HARDCODED_TOKENS.md    # Token reference
│       └── README.md              # Setup guide
│
├── 📖 README.md                    # This file
└── 📄 package.json                # Root configuration
```

## 🔧 **Configuration Files**

### **Pre-configured with tokens:**
- `Serverless/Backend/config.env` - Backend configuration
- `Serverless/Front/lora-dashboard/config.env` - Frontend configuration
- `src/environments/*.ts` - Angular environments

### **Ready-to-use commands:**
```bash
# Frontend environments
npm run start:local    # Local development
npm run start:runpod   # RunPod production
npm run start:mock     # Mock data mode

# Backend modes
python -m uvicorn app.main:app --reload  # Development
docker run lora-dashboard-backend        # Production
```

## 💰 **Cost Management**

Built-in cost controls for RunPod deployment:

- **Max Spend**: $20/hour, $500/month
- **Auto-pause**: On budget limits
- **Scale-to-zero**: After 5 minutes idle
- **Budget Alerts**: 80% and 95% notifications

## 🛡️ **Security Features**

- **AES-256-CBC** encryption for sensitive data
- **JWT-like tokens** with expiration
- **CORS protection** for API endpoints
- **Input validation** with Pydantic models
- **Rate limiting** on API endpoints

## 🧪 **Testing**

```bash
# Frontend Tests
cd Serverless/Front/lora-dashboard
npm test              # Unit tests
npm run test:e2e      # End-to-end tests

# Backend Tests
cd Serverless/Backend  
pytest                # Unit tests
pytest --cov         # Coverage report
```

## 📚 **Documentation**

- **[Frontend Setup](Serverless/Front/FRONTEND_SETUP.md)** - Angular configuration
- **[Backend Deploy](Serverless/Backend/RUNPOD_DEPLOYMENT_GUIDE.md)** - RunPod deployment
- **[Local Testing](Serverless/Backend/LOCAL_TESTING_GUIDE.md)** - Development guide
- **[Hardcoded Tokens](Serverless/HARDCODED_TOKENS.md)** - Token reference

## 🤝 **Contributing**

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting  
5. Submit a pull request

## 📄 **License**

MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 **Acknowledgments**

- **FLUX.1-dev** - Amazing image generation model
- **RunPod** - Excellent GPU infrastructure
- **Angular Team** - Fantastic framework
- **FastAPI** - Modern Python web framework

## 🎯 **Ready to Use!**

**Projekt jest w pełni skonfigurowany z zachardkodowanymi tokenami.**
**Wystarczy sklonować, uruchomić i korzystać!**

---

**⚠️ Security Note**: Tokeny są zachardkodowane dla łatwego developmentu. W środowisku produkcyjnym zaleca się używanie zmiennych środowiskowych.

**🚀 Made with ❤️ for the AI/ML community**
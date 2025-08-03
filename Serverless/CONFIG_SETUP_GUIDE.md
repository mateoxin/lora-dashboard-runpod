# 🔐 **TOKEN CONFIGURATION SETUP GUIDE**

## 📋 **Overview**

This guide explains the new secure token management system for the LoRA Dashboard project. All tokens and sensitive configuration are now stored in separate files that are excluded from Git commits.

## 🏗️ **Architecture**

```
Project/
├── Serverless/
│   ├── Backend/
│   │   ├── config.env.template     # ← Copy to config.env
│   │   └── app/utils/config_loader.py
│   ├── Testing/
│   │   ├── config.env.template     # ← Copy to config.env  
│   │   └── config_loader_shared.py
│   ├── SimpleTest/
│   │   └── config.env.template     # ← Copy to config.env
│   └── Front/lora-dashboard/
│       ├── config.env.template     # ← Copy to config.env
│       └── src/assets/config.json.template  # ← Copy to config.json
└── .gitignore                      # ← Updated to ignore config files
```

## ⚙️ **Setup Instructions**

### 1. **Backend Configuration**

```bash
cd Serverless/Backend
cp config.env.template config.env
# Edit config.env with your actual tokens
```

**Required tokens in `config.env`:**
```bash
RUNPOD_API_TOKEN=your_actual_runpod_token_here
RUNPOD_ENDPOINT_ID=your_endpoint_id_here
S3_ACCESS_KEY=your_s3_access_key
S3_SECRET_KEY=your_s3_secret_key
S3_BUCKET=your_s3_bucket_name
```

### 2. **Testing Configuration**

```bash
cd Serverless/Testing
cp config.env.template config.env
# Edit config.env with your test configuration
```

**Required tokens in `config.env`:**
```bash
RUNPOD_TOKEN=your_actual_runpod_token_here
RUNPOD_ENDPOINT_ID=your_endpoint_id_here
```

### 3. **SimpleTest Configuration**

```bash
cd Serverless/SimpleTest
cp config.env.template config.env
# Edit config.env with your simple test configuration
```

### 4. **Frontend Configuration**

```bash
cd Serverless/Front/lora-dashboard
cp config.env.template config.env
cp src/assets/config.json.template src/assets/config.json
# Edit both files with your frontend configuration
```

## 🔧 **Configuration Files**

### **Backend: config.env**
```bash
# RunPod Configuration
RUNPOD_API_TOKEN=rpa_your_actual_token_here
RUNPOD_ENDPOINT_ID=your-endpoint-id

# S3 Storage
S3_ACCESS_KEY=your_access_key
S3_SECRET_KEY=your_secret_key
S3_BUCKET=your_bucket_name

# Application Settings
DEBUG=false
MOCK_MODE=false
MAX_CONCURRENT_JOBS=10
```

### **Testing: config.env**
```bash
# RunPod Configuration  
RUNPOD_TOKEN=rpa_your_actual_token_here
RUNPOD_ENDPOINT_ID=your-endpoint-id

# Test Settings
TEST_TIMEOUT=300
MAX_RETRIES=3
POLLING_INTERVAL=5
```

### **Frontend: config.json**
```json
{
  "runpodToken": "rpa_your_actual_token_here",
  "runpodEndpointUrl": "https://your-endpoint-id.runpod.net/api",
  "apiBaseUrl": "http://localhost:8000/api",
  "encryptionKey": "LoRA-Dashboard-Secret-Key-2024",
  "autoRefreshInterval": 5000,
  "maxFileSize": 52428800,
  "mockMode": false
}
```

## 🔍 **How It Works**

### **Backend**
- `config_loader.py` utility loads tokens from `config.env` file
- Fallback to environment variables if config file not found
- Validates tokens and rejects placeholders
- Used by `config.py` for application settings

### **Testing Tools**
- `config_loader_shared.py` handles configuration for all test scripts
- All testing scripts now import and use this loader
- Consistent error handling and validation

### **Frontend**
- `EnvironmentConfigService` loads configuration at runtime
- Can read from `assets/config.json` or environment
- Validates configuration and shows helpful error messages

## 🛡️ **Security Features**

### **Git Protection**
- All actual config files are in `.gitignore`
- Only template files are committed to Git
- Prevents accidental token commits

### **Validation**
- Config loaders validate tokens and reject placeholders
- Clear error messages guide users to proper setup
- Graceful fallbacks to environment variables

### **Flexibility**  
- Supports both file-based and environment variable configuration
- Easy to deploy in different environments (dev/staging/prod)
- Runtime configuration for frontend without rebuilds

## 🚀 **Quick Start**

1. **Copy all template files:**
   ```bash
   find . -name "*.template" -exec sh -c 'cp "$1" "${1%.template}"' _ {} \;
   ```

2. **Set your RunPod token in all config files:**
   ```bash
   # Replace YOUR_TOKEN with your actual token
   find . -name "config.env" -exec sed -i 's/your_.*_token_here/YOUR_TOKEN/g' {} \;
   ```

3. **Verify configuration:**
   ```bash
   # Backend
   cd Serverless/Backend && python -c "from app.utils.config_loader import get_runpod_token; print('✅ Backend config OK')"
   
   # Testing  
   cd Serverless/Testing && python -c "from config_loader_shared import get_runpod_token; print('✅ Testing config OK')"
   ```

## 🔧 **Troubleshooting**

### **"RUNPOD_TOKEN not found" Error**
- Ensure you copied `config.env.template` to `config.env`
- Check that the token is set and not a placeholder
- Verify file permissions and encoding (UTF-8)

### **"Could not import config_loader" Error**
- Ensure `config_loader_shared.py` is in the same directory
- Check Python path and imports
- Verify file is not corrupted

### **Frontend Configuration Issues**
- Check that `config.json` exists in `src/assets/`
- Verify JSON syntax is valid
- Check browser console for loading errors

## 📝 **Migration from Old System**

The new system replaces:
- ❌ Hardcoded tokens in Python files
- ❌ Tokens in environment.ts files  
- ❌ Placeholder strings like `YOUR_RUNPOD_TOKEN_HERE`

With:
- ✅ External configuration files
- ✅ Runtime configuration loading
- ✅ Git-ignored credential files
- ✅ Proper validation and error handling

## 🎯 **Best Practices**

1. **Never commit actual tokens** - Always use template files in Git
2. **Use environment variables in production** - Override config files with env vars
3. **Validate configuration early** - Check tokens at application startup
4. **Document required tokens** - Keep template files up to date
5. **Use different tokens per environment** - Dev/staging/prod separation

---

**🎉 Your tokens are now secure and properly managed!** 
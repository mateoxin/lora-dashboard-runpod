# 🚀 FastBackend - Ultra-Quick RunPod Deployment

Deploy LoRA training backend w **~30 sekund** zamiast 20 minut!

## ✨ Zalety

- ⚡ **Instant Deploy**: Bez Docker build (0 sekund)
- 🔄 **Live Updates**: Push do GitHub = automatyczny update  
- 💾 **Minimal Size**: ~50MB zamiast 6GB Docker image
- 🚀 **RunPod Cache**: Wykorzystuje PyTorch cache RunPod (3x szybciej)
- 🛠️ **Runtime Setup**: Heavy dependencies instalowane w runtime
- 🐙 **GitHub Integration**: Automatyczne pobieranie latest kodu

## 📊 Performance Comparison

| Method | Build Time | Deploy Time | Update Time | Image Size |
|--------|------------|-------------|-------------|------------|
| Old Docker | 15-20 min | 5-10 min | 15-20 min | ~6GB |
| **FastBackend** | **0 min** | **30 sek** | **30 sek** | **~50MB** |

## 🚀 Quick Start

### 1. Clone & Setup

```bash
# Clone this repo
git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git
cd YOUR_REPO/Serverless/FastBackend

# Copy config template
cp config.env.template config.env

# Edit config with your details
nano config.env
```

### 2. Update GitHub URLs

```bash
# Update startup script URLs
export GITHUB_USERNAME="your_username"
export GITHUB_REPO="your_repo"

sed -i "s/YOUR_USERNAME/$GITHUB_USERNAME/g" startup.sh
sed -i "s/YOUR_REPO/$GITHUB_REPO/g" startup.sh
```

### 3. Deploy to RunPod

```bash
# Set your RunPod API key
export RUNPOD_API_KEY="your_api_key"

# Deploy!
python deploy_fast.py
```

### 4. Test Deployment

```bash
# Test endpoint
curl -X POST "https://api.runpod.ai/v2/ENDPOINT_ID/run" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"input": {"type": "health"}}'
```

### 5. Update Code (Instant!)

```bash
# Make changes to handler_fast.py
# Commit and push
git add .
git commit -m "Update handler"
git push

# RunPod automatically uses latest version on next request!
```

## 🛠️ How It Works

1. **Minimal Startup**: Only basic dependencies (runpod, pyyaml, Pillow)
2. **GitHub Download**: Latest handler code pulled from GitHub  
3. **Lazy Loading**: Heavy dependencies (PyTorch, transformers) installed on-demand
4. **RunPod Cache**: PyTorch downloads use RunPod's cache (much faster)
5. **Runtime Setup**: Environment configured when first heavy operation requested

## 📝 API Usage

### Health Check (Instant)
```python
import requests

response = requests.post("https://api.runpod.ai/v2/ENDPOINT_ID/run", 
    headers={"Authorization": "Bearer YOUR_API_KEY"},
    json={"input": {"type": "health"}})

print(response.json())
# {"status": "healthy", "environment_ready": false, ...}
```

### Setup Environment (One-time)
```python
response = requests.post("https://api.runpod.ai/v2/ENDPOINT_ID/run",
    headers={"Authorization": "Bearer YOUR_API_KEY"}, 
    json={"input": {"type": "setup_environment"}})

# This triggers PyTorch + ML libraries installation
```

### Heavy Operations (Auto-setup)
```python
# Upload training data (triggers auto-setup if needed)
response = requests.post("https://api.runpod.ai/v2/ENDPOINT_ID/run",
    headers={"Authorization": "Bearer YOUR_API_KEY"},
    json={
        "input": {
            "type": "upload_training_data",
            "training_name": "my_training",
            "files": [...]
        }
    })

# Train LoRA model
response = requests.post("https://api.runpod.ai/v2/ENDPOINT_ID/run",
    headers={"Authorization": "Bearer YOUR_API_KEY"},
    json={
        "input": {
            "type": "train_with_yaml", 
            "yaml_config": "..."
        }
    })
```

## 🔧 Configuration Files

- `handler_fast.py` - Main handler with lazy loading
- `startup.sh` - RunPod startup script (downloads from GitHub)
- `deploy_fast.py` - Automated deployment script
- `requirements_minimal.txt` - Minimal dependencies
- `config.env.template` - Environment configuration template

## 🎯 Available Operations

### Instant Operations (No Setup Required)
- `health` - Health check
- `ping` - Simple ping/pong
- `echo` - Echo input back
- `setup_environment` - Manual environment setup

### Heavy Operations (Auto-setup Triggered)
- `upload_training_data` - Upload training images/captions
- `train_with_yaml` - Train LoRA model with YAML config
- `list_models` - List trained models
- `processes` - List running processes

## 🚀 Deployment Options

### Option 1: Serverless Endpoint (Recommended)
```bash
python deploy_fast.py
# Choose option 1
```

### Option 2: Simple Pod
```bash
python deploy_fast.py  
# Choose option 2
```

### Option 3: Manual RunPod Dashboard
1. Create new Pod/Endpoint
2. Use image: `runpod/pytorch:2.1.0-py3.10-cuda11.8.0-devel-ubuntu22.04`
3. Set Docker start command: `bash -c 'curl -s https://raw.githubusercontent.com/YOUR_USERNAME/YOUR_REPO/main/Serverless/FastBackend/startup.sh | bash'`
4. Add environment variables from `config.env.template`

## 🔄 Updates & Maintenance

### Instant Updates
```bash
# Edit handler_fast.py
# Push to GitHub
git push

# Next RunPod request uses updated code!
```

### Update Dependencies
```bash
# Edit requirements_minimal.txt
# Push to GitHub
git push

# Restart RunPod pod/endpoint to get new dependencies
```

### Monitor Logs
```bash
# In RunPod dashboard, check pod logs for:
# - Setup progress
# - Error messages
# - Performance metrics
```

## 🐛 Troubleshooting

### Setup Failed
```python
# Manually trigger setup
response = requests.post("https://api.runpod.ai/v2/ENDPOINT_ID/run",
    json={"input": {"type": "setup_environment"}})
```

### GitHub Download Failed
- Check GitHub URLs in `startup.sh`
- Verify repo is public or add GitHub token
- Check internet connectivity in RunPod

### PyTorch Install Failed
- RunPod cache might be corrupted
- Restart pod to get fresh environment
- Check CUDA compatibility

### Memory Issues
- Reduce batch size in training config
- Use gradient checkpointing
- Monitor GPU memory usage

## 📈 Performance Tips

1. **First Request**: Will be slower (setup time) but subsequent requests instant
2. **Keep Warm**: Use health checks to prevent cold starts
3. **Batch Operations**: Group multiple operations in single request
4. **Monitor Usage**: Check RunPod dashboard for resource usage

## 🔒 Security Notes

- HuggingFace token included for demo (replace with your own)
- RunPod API key never stored in code
- All operations isolated per worker
- No persistent data without volumes

## 📞 Support

- Check RunPod logs for errors
- Test locally with `python handler_fast.py`
- Verify GitHub URLs are accessible
- Monitor environment setup progress

---

**🎉 Enjoy lightning-fast LoRA training deployments!**
#!/bin/bash
# 🚀 Ultra-fast RunPod startup script
# Deploy time: ~30 seconds instead of 20 minutes!

echo "🚀 Starting FastBackend from GitHub..."
echo "================================================"

# Set environment variables
export PYTHONUNBUFFERED=1
export PYTHONDONTWRITEBYTECODE=1
export HF_TOKEN="${HF_TOKEN:-your_huggingface_token_here}"
export WORKSPACE_PATH="/workspace"

# Create workspace
mkdir -p /workspace /workspace/models /workspace/training_data /workspace/cache

# Install minimal requirements (fast)
echo "📦 Installing minimal requirements..."
pip install --no-cache-dir runpod pyyaml Pillow python-dotenv

# Install HuggingFace CLI (upgraded version)
pip install --upgrade "huggingface_hub[cli]"

# Download handler from GitHub (update on every start!)
echo "📥 Downloading latest handler from GitHub..."
REPO_URL="https://raw.githubusercontent.com/YOUR_USERNAME/YOUR_REPO/main"
curl -o /workspace/handler_fast.py "${REPO_URL}/Serverless/FastBackend/handler_fast.py" || {
    echo "⚠️ Failed to download from GitHub, using local fallback"
    # Fallback - basic handler
    cat > /workspace/handler_fast.py << 'EOF'
import runpod
from datetime import datetime

def handler(job):
    return {
        "status": "healthy",
        "message": "FastBackend running (fallback mode)",
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    runpod.serverless.start({"handler": handler})
EOF
}

# Optional: Download additional modules
curl -o /workspace/full_handler.py "${REPO_URL}/Serverless/FastBackend/full_handler.py" 2>/dev/null || echo "⚠️ Full handler not found (optional)"

# Start handler
echo "🎯 Starting FastBackend handler..."
cd /workspace
python handler_fast.py
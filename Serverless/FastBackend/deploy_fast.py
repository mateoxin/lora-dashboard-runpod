#!/usr/bin/env python3
"""
🚀 Ultra-Fast RunPod Deployment Script
Deploy w ~30 sekund zamiast 20 minut!
"""

import requests
import json
import os
import time
from datetime import datetime

# RunPod API configuration
RUNPOD_API_KEY = os.environ.get("RUNPOD_API_KEY", "YOUR_API_KEY_HERE")
RUNPOD_API_URL = "https://api.runpod.ai/v2"

# GitHub configuration - UPDATE THESE URLs!
GITHUB_USERNAME = os.environ.get("GITHUB_USERNAME", "YOUR_USERNAME")
GITHUB_REPO = os.environ.get("GITHUB_REPO", "YOUR_REPO")
GITHUB_RAW_URL = f"https://raw.githubusercontent.com/{GITHUB_USERNAME}/{GITHUB_REPO}/main"
STARTUP_SCRIPT_URL = f"{GITHUB_RAW_URL}/Serverless/FastBackend/startup.sh"

def create_fast_endpoint():
    """Create RunPod endpoint with GitHub-based fast deployment"""
    
    endpoint_config = {
        "name": f"lora-fast-{int(datetime.now().timestamp())}",
        "template_id": None,  # Will use custom config
        "image_name": "runpod/pytorch:2.1.0-py3.10-cuda11.8.0-devel-ubuntu22.04",
        "docker_start_cmd": f"bash -c 'curl -s {STARTUP_SCRIPT_URL} | bash'",
        "container_disk_in_gb": 50,
        "volume_in_gb": 100,
        "gpu_type_id": "NVIDIA GeForce RTX 4090",
        "env": {
            "HF_TOKEN": "your_huggingface_token_here",
            "PYTHONUNBUFFERED": "1",
            "GITHUB_USERNAME": GITHUB_USERNAME,
            "GITHUB_REPO": GITHUB_REPO
        },
        "workers_min": 0,
        "workers_max": 3,
        "idle_timeout": 5,
        "locations": "EU-SE-1,US-CA-1",  # Closest regions
        "network_volume_id": None
    }
    
    headers = {
        "Authorization": f"Bearer {RUNPOD_API_KEY}",
        "Content-Type": "application/json"
    }
    
    print("🚀 Creating fast RunPod endpoint...")
    print(f"📦 Using startup script: {STARTUP_SCRIPT_URL}")
    print(f"🐙 GitHub repo: {GITHUB_USERNAME}/{GITHUB_REPO}")
    
    response = requests.post(
        f"{RUNPOD_API_URL}/endpoints",
        headers=headers,
        json=endpoint_config
    )
    
    if response.status_code == 200:
        result = response.json()
        endpoint_id = result.get("id")
        
        print(f"✅ Endpoint created successfully!")
        print(f"🆔 Endpoint ID: {endpoint_id}")
        print(f"🌐 API URL: https://api.runpod.ai/v2/{endpoint_id}/run")
        print(f"⚡ Deploy time: ~30 seconds")
        print(f"🔄 Updates: Just push to GitHub!")
        
        return endpoint_id
    else:
        print(f"❌ Failed to create endpoint: {response.status_code}")
        print(f"Error: {response.text}")
        return None

def create_fast_pod():
    """Alternative: Create simple pod instead of serverless endpoint"""
    
    pod_config = {
        "name": f"lora-fast-pod-{int(datetime.now().timestamp())}",
        "image_name": "runpod/pytorch:2.1.0-py3.10-cuda11.8.0-devel-ubuntu22.04",
        "gpu_type_id": "NVIDIA GeForce RTX 4090",
        "container_disk_in_gb": 50,
        "volume_in_gb": 100,
        "docker_start_cmd": f"bash -c 'curl -s {STARTUP_SCRIPT_URL} | bash'",
        "env": {
            "HF_TOKEN": "your_huggingface_token_here",
            "PYTHONUNBUFFERED": "1"
        },
        "ports": "8000/http"
    }
    
    headers = {
        "Authorization": f"Bearer {RUNPOD_API_KEY}",
        "Content-Type": "application/json"
    }
    
    print("🚀 Creating fast RunPod pod...")
    
    response = requests.post(
        f"{RUNPOD_API_URL}/pods",
        headers=headers,
        json=pod_config
    )
    
    if response.status_code == 200:
        result = response.json()
        pod_id = result.get("id")
        
        print(f"✅ Pod created successfully!")
        print(f"🆔 Pod ID: {pod_id}")
        print(f"⚡ Deploy time: ~30 seconds")
        
        return pod_id
    else:
        print(f"❌ Failed to create pod: {response.status_code}")
        print(f"Error: {response.text}")
        return None

def test_endpoint(endpoint_id):
    """Test the deployed endpoint"""
    
    test_payload = {
        "input": {
            "type": "health"
        }
    }
    
    headers = {
        "Authorization": f"Bearer {RUNPOD_API_KEY}",
        "Content-Type": "application/json"
    }
    
    print(f"🧪 Testing endpoint {endpoint_id}...")
    
    response = requests.post(
        f"{RUNPOD_API_URL}/{endpoint_id}/run",
        headers=headers,
        json=test_payload
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Test successful!")
        print(f"Response: {json.dumps(result, indent=2)}")
        return True
    else:
        print(f"❌ Test failed: {response.status_code}")
        print(f"Error: {response.text}")
        return False

def update_github_urls():
    """Helper to update GitHub URLs in scripts"""
    print("\n📝 Setup Instructions:")
    print("1. Set environment variables:")
    print(f"   export RUNPOD_API_KEY='your_api_key'")
    print(f"   export GITHUB_USERNAME='{GITHUB_USERNAME}'")
    print(f"   export GITHUB_REPO='{GITHUB_REPO}'")
    print("\n2. Update startup.sh URLs:")
    print(f"   sed -i 's/YOUR_USERNAME/{GITHUB_USERNAME}/g' startup.sh")
    print(f"   sed -i 's/YOUR_REPO/{GITHUB_REPO}/g' startup.sh")
    print("\n3. Push to GitHub and deploy!")

def deploy_with_mcp():
    """Deploy using MCP RunPod tools if available"""
    try:
        # This would use the MCP RunPod tools if available
        print("🔧 Trying MCP RunPod deployment...")
        
        # Placeholder for MCP deployment
        config = {
            "name": f"lora-fast-mcp-{int(datetime.now().timestamp())}",
            "imageName": "runpod/pytorch:2.1.0-py3.10-cuda11.8.0-devel-ubuntu22.04",
            "ports": ["8000/http"],
            "env": {
                "HF_TOKEN": "your_huggingface_token_here"
            },
            "gpuCount": 1,
            "containerDiskInGb": 50,
            "volumeInGb": 100
        }
        
        print("📋 MCP Config ready - use mcp_runpod-mcp-ts_create-pod with this config")
        return config
        
    except Exception as e:
        print(f"⚠️ MCP deployment not available: {e}")
        return None

if __name__ == "__main__":
    print("🚀 FastBackend Deployment")
    print("=" * 40)
    
    # Check configuration
    if RUNPOD_API_KEY == "YOUR_API_KEY_HERE":
        print("❌ Please set RUNPOD_API_KEY environment variable")
        update_github_urls()
        exit(1)
    
    if GITHUB_USERNAME == "YOUR_USERNAME":
        print("❌ Please set GITHUB_USERNAME and GITHUB_REPO")
        update_github_urls()
        exit(1)
    
    # Choose deployment method
    print("Choose deployment method:")
    print("1. Serverless Endpoint (recommended)")
    print("2. Simple Pod") 
    print("3. MCP Tools")
    
    choice = input("Enter choice (1-3): ").strip()
    
    if choice == "1":
        # Create endpoint
        endpoint_id = create_fast_endpoint()
        
        if endpoint_id:
            # Wait for startup
            print("⏳ Waiting for endpoint to start...")
            time.sleep(30)
            
            # Test endpoint
            test_endpoint(endpoint_id)
    
    elif choice == "2":
        # Create pod
        pod_id = create_fast_pod()
        if pod_id:
            print(f"🎯 Pod {pod_id} created. Check RunPod dashboard for status.")
    
    elif choice == "3":
        # MCP deployment
        config = deploy_with_mcp()
        if config:
            print(f"🔧 Use MCP tools with config: {json.dumps(config, indent=2)}")
    
    else:
        print("❌ Invalid choice")
    
    update_github_urls()
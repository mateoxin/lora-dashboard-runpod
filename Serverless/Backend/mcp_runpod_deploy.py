#!/usr/bin/env python3
"""
🚀 MCP RunPod Deployment Script
Automatyczny deployment backend na RunPod Serverless
"""

import os
import json
import time
import runpod
from typing import Optional, Dict, Any

# Configuration
DOCKER_IMAGE = "mateoxin/lora-dashboard-backend:latest"
ENDPOINT_NAME = "lora-dashboard-backend"
RUNPOD_API_KEY = "YOUR_RUNPOD_API_TOKEN_HERE"  # Replace with your token

def setup_runpod_client(api_key: str) -> None:
    """Initialize RunPod client with API key."""
    runpod.api_key = api_key
    print("✅ RunPod client initialized")

def check_available_gpus() -> None:
    """Check and display available GPUs."""
    try:
        print("🔍 Checking available GPUs...")
        gpus = runpod.get_gpus()
        
        print("📋 Available GPUs:")
        rtx_gpus = []
        for gpu in gpus:
            gpu_name = str(gpu)
            if '5090' in gpu_name or '4090' in gpu_name:
                print(f"  🎮 {gpu_name}")
                rtx_gpus.append(gpu_name)
            elif 'RTX' in gpu_name:
                print(f"  🎮 {gpu_name}")
                rtx_gpus.append(gpu_name)
        
        if not rtx_gpus:
            print("  ⚠️ No RTX GPUs found in available list")
        
        return rtx_gpus
        
    except Exception as e:
        print(f"⚠️ Could not check GPUs: {e}")
        return []

def create_serverless_endpoint() -> Optional[str]:
    """Create RunPod Serverless endpoint."""
    
    print("🚀 Creating RunPod Serverless endpoint...")
    print(f"📦 Docker Image: {DOCKER_IMAGE}")
    print(f"🏷️ Name: {ENDPOINT_NAME}")
    
    # RTX 5090 identifiers from RunPod docs (exact from documentation table)
    gpu_ids_to_try = [
        "NVIDIA GeForce RTX 5090",  # Exact from GPU types documentation
        "RTX 5090",                 # Display name from docs
        "5090"                      # Simple ID from pricing table
    ]
    
    # Create unique template name with timestamp
    import time
    timestamp = str(int(time.time()))
    template_name = f"{ENDPOINT_NAME}-template-{timestamp}"
    
    for gpu_id in gpu_ids_to_try:
        try:
            print(f"🚀 Trying RTX 5090 with GPU ID: {gpu_id}")
            
            # Step 1: Create template with Docker image
            print("📋 Creating template...")
            template = runpod.create_template(
                name=template_name,
                image_name=DOCKER_IMAGE,
                is_serverless=True
            )
            
            if not template or not template.get("id"):
                print("❌ Failed to create template")
                continue
                
            template_id = template["id"]
            print(f"✅ Template created: {template_id}")
            
            # Step 2: Create endpoint using template
            print("🔗 Creating endpoint...")
            endpoint = runpod.create_endpoint(
                name=ENDPOINT_NAME,
                template_id=template_id,
                gpu_ids=gpu_id,        # Try current GPU ID
                workers_min=1,         # Always keep 1 worker ready
                workers_max=5          # Scale up to 5 workers
            )
            
            if endpoint and endpoint.get("id"):
                endpoint_id = endpoint["id"]
                endpoint_url = f"https://api.runpod.ai/v2/{endpoint_id}"
                
                print("🎉 RTX 5090 Endpoint created successfully!")
                print(f"🚀 GPU Used: {gpu_id} (32GB GDDR7)")
                print(f"🆔 Endpoint ID: {endpoint_id}")
                print(f"🌐 Endpoint URL: {endpoint_url}")
                print(f"🔗 API Base URL: {endpoint_url}")
                
                return endpoint_url
            else:
                print(f"❌ Failed to create endpoint with GPU ID: {gpu_id}")
                continue
                
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Error with GPU ID '{gpu_id}': {error_msg}")
            
            # Check if it's availability issue
            if "not available" in error_msg.lower() or "quota" in error_msg.lower():
                print("   💡 RTX 5090 może być niedostępny w tym regionie/momencie")
            continue
    
    # If all GPU IDs failed, show manual instructions for RTX 5090
    print("\n❌ Automatyczny deployment RTX 5090 nie udał się!")
    print("🖱️  MANUAL DEPLOYMENT - krok po kroku:")
    print("=" * 50)
    print("1. Idź na: https://www.runpod.io/console/serverless")
    print("2. Kliknij 'New Endpoint'") 
    print("3. Wybierz 'Custom Image'")
    print(f"4. Container Image: {DOCKER_IMAGE}")
    print("5. GPU Selection:")
    print("   - Wybierz 'RTX 5090' z listy")
    print("   - Jeśli nie ma RTX 5090, sprawdź inne regiony")
    print("6. Configuration:")
    print("   - Min Workers: 1")
    print("   - Max Workers: 5") 
    print("   - GPU Count: 1")
    print("7. Environment Variables:")
    print("   REDIS_URL=redis://redis:6379/0")
    print("   LOG_LEVEL=INFO")
    print("   MAX_CONCURRENT_JOBS=5")
    print("   GPU_TIMEOUT=14400")
    print("8. Kliknij 'Deploy'")
    print("\n💡 Tip: RTX 5090 może być dostępny w różnych regionach o różnych porach")
    
    return None

def wait_for_endpoint_ready(endpoint_url: str, timeout: int = 600) -> bool:
    """Wait for endpoint to be ready."""
    import requests
    
    # RunPod serverless endpoints use /health for health checks
    health_url = f"{endpoint_url}/health"
    print(f"⏳ Waiting for endpoint to be ready: {health_url}")
    
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = requests.get(health_url, timeout=10)
            if response.status_code == 200:
                print("✅ Endpoint is ready and healthy!")
                return True
        except requests.exceptions.RequestException:
            pass
        
        print("⏳ Endpoint not ready yet, waiting 15 seconds...")
        time.sleep(15)
    
    print("⚠️ Timeout waiting for endpoint to be ready")
    return False

def update_frontend_config(endpoint_url: str) -> None:
    """Update frontend configuration with new endpoint URL."""
    
    config_file = "../Front/lora-dashboard/src/environments/environment.runpod.ts"
    # For RunPod serverless, we need to add /api to the base URL
    api_base_url = f"{endpoint_url}/api" if not endpoint_url.endswith('/api') else endpoint_url
    
    try:
        with open(config_file, 'r') as f:
            content = f.read()
        
        # Replace placeholder with actual URL
        updated_content = content.replace(
            'https://YOUR_ENDPOINT_ID-8000.proxy.runpod.net/api',
            api_base_url
        )
        
        with open(config_file, 'w') as f:
            f.write(updated_content)
        
        print(f"✅ Frontend config updated: {config_file}")
        print(f"🔗 API Base URL: {api_base_url}")
        
    except Exception as e:
        print(f"⚠️ Could not update frontend config: {e}")
        print(f"📝 Manually update: {config_file}")
        print(f"🔄 Replace placeholder with: {api_base_url}")

def main():
    """Main deployment function."""
    print("🚀 LoRA Dashboard - RunPod Deployment")
    print("=" * 50)
    
    # Check if API key is set
    if RUNPOD_API_KEY == "YOUR_RUNPOD_API_TOKEN_HERE":
        print("❌ Please set your RunPod API key in the script")
        print("🔑 Get your key from: https://www.runpod.io/console/settings")
        return False
    
    # Initialize RunPod client
    setup_runpod_client(RUNPOD_API_KEY)
    
    # Check available GPUs first
    available_gpus = check_available_gpus()
    
    # Create endpoint
    endpoint_url = create_serverless_endpoint()
    if not endpoint_url:
        return False
    
    # Wait for endpoint to be ready
    if wait_for_endpoint_ready(endpoint_url):
        # Update frontend configuration
        update_frontend_config(endpoint_url)
        
        print("\n🎉 Deployment Complete!")
        print("=" * 50)
        print(f"🌐 Backend URL: {endpoint_url}")
        print(f"🔗 API URL: {endpoint_url}/api")
        print(f"💻 Frontend: npm run dev:runpod")
        print("\n🧪 Test deployment:")
        print(f"curl {endpoint_url}/api/health")
        
        return True
    
    return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 
#!/usr/bin/env python3
"""
🚀 FastBackend Deployment using MCP RunPod Tools
Ultra-fast deployment with MCP integration
"""

import json
import os
from datetime import datetime

def get_mcp_pod_config():
    """Get configuration for MCP RunPod pod creation"""
    
    # GitHub configuration
    github_username = os.environ.get("GITHUB_USERNAME", "YOUR_USERNAME")
    github_repo = os.environ.get("GITHUB_REPO", "YOUR_REPO")
    startup_url = f"https://raw.githubusercontent.com/{github_username}/{github_repo}/main/Serverless/FastBackend/startup.sh"
    
    config = {
        "name": f"lora-fast-mcp-{int(datetime.now().timestamp())}",
        "imageName": "runpod/pytorch:2.1.0-py3.10-cuda11.8.0-devel-ubuntu22.04",
        "ports": ["8000/http"],
        "env": {
            "HF_TOKEN": "your_huggingface_token_here",
            "PYTHONUNBUFFERED": "1",
            "PYTHONDONTWRITEBYTECODE": "1",
            "WORKSPACE_PATH": "/workspace",
            "GITHUB_USERNAME": github_username,
            "GITHUB_REPO": github_repo,
            "STARTUP_URL": startup_url
        },
        "gpuCount": 1,
        "containerDiskInGb": 50,
        "volumeInGb": 100,
        "cloudType": "SECURE"
    }
    
    return config

def get_mcp_endpoint_config():
    """Get configuration for MCP RunPod serverless endpoint"""
    
    github_username = os.environ.get("GITHUB_USERNAME", "YOUR_USERNAME")
    github_repo = os.environ.get("GITHUB_REPO", "YOUR_REPO")
    
    config = {
        "name": f"lora-fast-endpoint-{int(datetime.now().timestamp())}",
        "templateId": None,  # Will use custom template
        "computeType": "GPU",
        "gpuCount": 1,
        "workersMin": 0,
        "workersMax": 3
    }
    
    return config

def get_mcp_template_config():
    """Get configuration for MCP RunPod template"""
    
    github_username = os.environ.get("GITHUB_USERNAME", "YOUR_USERNAME")
    github_repo = os.environ.get("GITHUB_REPO", "YOUR_REPO")
    startup_url = f"https://raw.githubusercontent.com/{github_username}/{github_repo}/main/Serverless/FastBackend/startup.sh"
    
    config = {
        "name": f"fastbackend-template-{int(datetime.now().timestamp())}",
        "imageName": "runpod/pytorch:2.1.0-py3.10-cuda11.8.0-devel-ubuntu22.04",
        "dockerStartCmd": [
            "bash", "-c", f"curl -s {startup_url} | bash"
        ],
        "env": {
            "HF_TOKEN": "your_huggingface_token_here",
            "PYTHONUNBUFFERED": "1",
            "WORKSPACE_PATH": "/workspace"
        },
        "ports": ["8000/http"],
        "containerDiskInGb": 50,
        "volumeInGb": 100,
        "isServerless": True,
        "readme": """# FastBackend Template

Ultra-fast LoRA training backend with GitHub integration.

## Features
- ⚡ Instant startup (~30 seconds)
- 🔄 Auto-updates from GitHub
- 🐳 No Docker build required
- 🚀 Runtime dependency installation

## Usage
1. Create pod/endpoint from this template
2. Test with health check: `{"input": {"type": "health"}}`
3. Use heavy operations: `{"input": {"type": "train_with_yaml", ...}}`

Updates automatically from GitHub repository.
"""
    }
    
    return config

def print_mcp_instructions():
    """Print instructions for using MCP tools"""
    
    print("🔧 MCP RunPod Deployment Instructions")
    print("=" * 50)
    
    print("\n1. 📋 Create Template (Optional)")
    template_config = get_mcp_template_config()
    print("Use mcp_runpod-mcp-ts_create-template with this config:")
    print(json.dumps(template_config, indent=2))
    
    print("\n2. 🚀 Create Pod (Recommended)")
    pod_config = get_mcp_pod_config()
    print("Use mcp_runpod-mcp-ts_create-pod with this config:")
    print(json.dumps(pod_config, indent=2))
    
    print("\n3. ⚡ Create Serverless Endpoint")
    endpoint_config = get_mcp_endpoint_config()
    print("First create template, then use mcp_runpod-mcp-ts_create-endpoint:")
    print(json.dumps(endpoint_config, indent=2))
    
    print("\n4. 🧪 Test Deployment")
    test_payload = {
        "input": {
            "type": "health"
        }
    }
    print("Test with this payload:")
    print(json.dumps(test_payload, indent=2))
    
    print("\n5. 📊 Monitor Deployment")
    print("Use these MCP commands:")
    print("- mcp_runpod-mcp-ts_list-pods")
    print("- mcp_runpod-mcp-ts_get-pod with podId")
    print("- mcp_runpod-mcp-ts_list-endpoints")

def save_mcp_configs():
    """Save MCP configurations to files"""
    
    configs = {
        "pod_config.json": get_mcp_pod_config(),
        "endpoint_config.json": get_mcp_endpoint_config(), 
        "template_config.json": get_mcp_template_config()
    }
    
    for filename, config in configs.items():
        with open(filename, 'w') as f:
            json.dump(config, f, indent=2)
        print(f"💾 Saved: {filename}")
    
    # Create test payload
    test_payload = {"input": {"type": "health"}}
    with open("test_payload.json", 'w') as f:
        json.dump(test_payload, f, indent=2)
    print(f"💾 Saved: test_payload.json")

def check_environment():
    """Check if environment is properly configured"""
    
    print("🔍 Checking environment...")
    
    required_vars = ["GITHUB_USERNAME", "GITHUB_REPO"]
    missing_vars = []
    
    for var in required_vars:
        value = os.environ.get(var, f"YOUR_{var.split('_')[1]}")
        if value.startswith("YOUR_"):
            missing_vars.append(var)
            print(f"❌ {var}: Not set")
        else:
            print(f"✅ {var}: {value}")
    
    if missing_vars:
        print(f"\n⚠️ Please set environment variables:")
        for var in missing_vars:
            print(f"export {var}='your_value'")
        return False
    
    return True

if __name__ == "__main__":
    print("🚀 FastBackend MCP Deployment Helper")
    print("=" * 60)
    
    # Check environment
    if not check_environment():
        print("\n❌ Environment not configured properly")
        exit(1)
    
    # Save configuration files
    print("\n💾 Saving MCP configuration files...")
    save_mcp_configs()
    
    # Print instructions
    print_mcp_instructions()
    
    print("\n" + "=" * 60)
    print("🎯 Quick MCP Deployment Steps:")
    print("1. Set GITHUB_USERNAME and GITHUB_REPO env vars")
    print("2. Use mcp_runpod-mcp-ts_create-pod with pod_config.json")
    print("3. Wait ~30 seconds for startup")
    print("4. Test with test_payload.json")
    print("5. Deploy instantly on GitHub push!")
    print("\n🎉 Happy deploying!")
#!/usr/bin/env python3
"""
🧠 MATT LORA TRAINING TEST
Test LoRA training with real Matt photos and check process status.
"""

import requests
import time
import yaml
from datetime import datetime
from pathlib import Path

# Configuration  
ENDPOINT_ID = "8s9y5exor2uidx"  # MODEL-DOWNLOAD endpoint
RUNPOD_TOKEN = "rpa_G4713KLVTYYBJYWPO157LX7VVPGV7NZ2K87SX6B17otl1t"
BASE_URL = f"https://api.runpod.ai/v2/{ENDPOINT_ID}"

headers = {
    'Authorization': f'Bearer {RUNPOD_TOKEN}',
    'Content-Type': 'application/json'
}

def start_matt_training():
    """Start LoRA training with Matt dataset."""
    print("🧠 Starting Matt LoRA Training...")
    
    # Load YAML config
    yaml_path = Path("training_conservative.yaml")
    with open(yaml_path, 'r') as f:
        yaml_config = yaml.safe_load(f)
    
    # Update dataset path to Matt's uploaded folder
    if "config" in yaml_config and "process" in yaml_config["config"]:
        for process_config in yaml_config["config"]["process"]:
            if "datasets" in process_config:
                for dataset in process_config["datasets"]:
                    dataset["folder_path"] = "/workspace/training_data"  # Will use matt_lora_dataset folder
    
    # Configure for Matt training
    yaml_config["config"]["name"] = "matt_lora_training"
    
    # Prepare training request
    training_data = {
        "input": {
            "type": "train_with_yaml", 
            "yaml_config": yaml_config,
            "dataset_path": "/workspace/training_data"
        }
    }
    
    print(f"📝 Config: {yaml_config['config']['name']}")
    print(f"📁 Dataset: {yaml_config['config']['process'][0]['datasets'][0]['folder_path']}")
    print(f"🎯 Steps: {yaml_config['config']['process'][0]['train']['steps']}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/runsync",
            headers=headers,
            json=training_data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            output = result.get('output', {})
            
            if output.get('status') == 'success':
                process_id = output.get('process_id')
                print(f"✅ Training started!")
                print(f"   📋 Process ID: {process_id}")
                print(f"   📝 Config: {output.get('config_path', 'unknown')}")
                return process_id
            else:
                print(f"❌ Training failed: {output.get('error', 'unknown')}")
                return None
        else:
            print(f"❌ HTTP Error: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Training error: {e}")
        return None

def check_process_status(process_id: str):
    """Check specific process status."""
    try:
        response = requests.post(
            f"{BASE_URL}/runsync",
            headers=headers,
            json={"input": {"type": "process_status", "process_id": process_id}}
        )
        
        if response.status_code == 200:
            result = response.json()
            output = result.get('output', {})
            
            if output.get('status') == 'success':
                process = output.get('process', {})
                status = process.get('status', 'unknown')
                updated_at = process.get('updated_at', 'unknown')
                error = process.get('error', None)
                
                print(f"   📋 Process {process_id}: {status}")
                print(f"   ⏰ Updated: {updated_at}")
                
                if error:
                    print(f"   ❌ Error: {error[:100]}{'...' if len(error) > 100 else ''}")
                
                return status
            else:
                print(f"   ❌ Status check failed: {output.get('error', 'unknown')}")
                return "error"
        else:
            print(f"   ❌ HTTP Error: {response.status_code}")
            return "error"
            
    except Exception as e:
        print(f"   ❌ Status check error: {e}")
        return "error"

def monitor_training(process_id: str, timeout: int = 600):
    """Monitor training progress."""
    print(f"\n👀 Monitoring training process {process_id}...")
    print(f"⏰ Timeout: {timeout} seconds")
    
    start_time = time.time()
    last_status = None
    
    while time.time() - start_time < timeout:
        status = check_process_status(process_id)
        
        if status != last_status:
            print(f"📊 Status change: {last_status} → {status}")
            last_status = status
        
        if status == "completed":
            print(f"🎉 Training completed successfully!")
            return True
        elif status == "failed":
            print(f"❌ Training failed!")
            return False
        elif status == "error":
            print(f"⚠️ Cannot check status")
            time.sleep(10)
        else:
            print(f"⏳ {status}... (elapsed: {int(time.time() - start_time)}s)")
            time.sleep(30)  # Check every 30 seconds
    
    print(f"⏰ Monitoring timeout after {timeout} seconds")
    return False

def list_models():
    """List available trained models."""
    print("\n📋 Checking for trained models...")
    
    response = requests.post(
        f"{BASE_URL}/runsync",
        headers=headers,
        json={"input": {"type": "list_models"}}
    )
    
    if response.status_code == 200:
        result = response.json()
        models = result.get("output", {}).get("models", [])
        count = result.get("output", {}).get("total_count", 0)
        
        print(f"   ✅ Found {count} trained models:")
        for model in models:
            print(f"      📦 {model.get('filename', 'unknown')} ({model.get('size_mb', 0)}MB)")
            print(f"         📅 {model.get('modified_date', 'unknown')}")
        
        return models
    else:
        print(f"   ❌ Failed to list models: {response.status_code}")
        return []

def main():
    """Run Matt LoRA training test."""
    print("🧠 MATT LORA TRAINING TEST")
    print(f"🎯 Endpoint: {ENDPOINT_ID}")
    print(f"⏰ Time: {datetime.now()}")
    print("=" * 60)
    
    # Step 1: Start training
    process_id = start_matt_training()
    
    if not process_id:
        print("❌ Failed to start training")
        return
    
    # Step 2: Monitor training
    success = monitor_training(process_id, timeout=1200)  # 20 minutes
    
    # Step 3: Check final status
    print(f"\n📊 Final status check...")
    final_status = check_process_status(process_id)
    
    # Step 4: List models
    models = list_models()
    
    # Summary
    print(f"\n{'='*60}")
    print(f"📊 TRAINING SUMMARY")
    print(f"{'='*60}")
    print(f"📋 Process ID: {process_id}")
    print(f"🎯 Final Status: {final_status}")
    print(f"⏱️ Monitoring Success: {'Yes' if success else 'No'}")
    print(f"📦 Models Available: {len(models)}")
    
    if success and models:
        print(f"\n🎉 MATT LORA TRAINING SUCCESSFUL!")
        print(f"💡 Matt's LoRA model is ready for download!")
    elif final_status == "completed":
        print(f"\n✅ Training completed but models not found yet")
        print(f"💡 Check again in a few minutes")
    else:
        print(f"\n❌ Training was not successful")
        print(f"💡 Check logs for details")

if __name__ == "__main__":
    main()
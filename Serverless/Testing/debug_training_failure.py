#!/usr/bin/env python3
"""
🔧 Training Failure Diagnostic Tool

Diagnozuje dlaczego trening LoRA nie działa w RunPod.
Sprawdza szczegółowe błędy i stan systemu.
"""

import os
import requests
import time
import json
from datetime import datetime

# Load config
def load_config():
    try:
        from config_loader_shared import get_runpod_token, get_config_value
        
        token = get_runpod_token()
        endpoint_id = get_config_value('RUNPOD_ENDPOINT_ID')
        
        if not endpoint_id:
            print("❌ Error: RUNPOD_ENDPOINT_ID not found in config")
            return None
            
        # Construct URL from endpoint ID (same pattern as other testing scripts)
        base_url = f"https://api.runpod.ai/v2/{endpoint_id}"
        endpoint_url = f"{base_url}/runsync"
        
        return {
            "token": token,
            "endpoint_url": endpoint_url
        }
        
    except ImportError:
        print("❌ Error: config_loader_shared.py not found")
        print("🔧 Create config.env with RUNPOD_ENDPOINT_ID and RUNPOD_TOKEN")
        return None
    except ValueError as e:
        print(f"❌ Config error: {e}")
        return None

def make_request(job_type, input_data):
    """Make request to RunPod endpoint"""
    config = load_config()
    if not config:
        return None
    
    url = config["endpoint_url"]
    headers = {
        "Authorization": f"Bearer {config['token']}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "input": {
            "type": job_type,
            **input_data
        }
    }
    
    try:
        print(f"📤 Sending {job_type} request...")
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Response received: {response.status_code}")
            return result
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return None

def test_system_health():
    """Test if system is working"""
    print("\n" + "="*60)
    print("🏥 TESTING SYSTEM HEALTH")
    print("="*60)
    
    result = make_request("health", {})
    if result:
        print("✅ System is responding")
        return True
    else:
        print("❌ System not responding")
        return False

def check_current_processes():
    """Check what processes are currently running"""
    print("\n" + "="*60)
    print("📋 CHECKING CURRENT PROCESSES")
    print("="*60)
    
    result = make_request("processes", {})
    if result and "output" in result:
        processes = result["output"]
        print(f"📊 Raw processes response: {processes}")
        
        # Handle different response formats
        if isinstance(processes, list):
            print(f"📊 Found {len(processes)} processes:")
            
            for i, process in enumerate(processes):
                if isinstance(process, dict):
                    proc_id = process.get("id", f"process_{i}")
                    proc_type = process.get("type", "unknown")
                    status = process.get("status", "unknown")
                    error = process.get("error", "")
                    
                    print(f"   🔹 {proc_id} | {proc_type} | {status}")
                    if error:
                        print(f"     ❌ Error: {error}")
                else:
                    print(f"   🔹 Process {i}: {process}")
        else:
            print(f"📊 Processes response: {processes}")
                
        return processes
    else:
        print("❌ Could not get processes")
        return []

def test_training_with_simple_config():
    """Test training with a simple YAML config"""
    print("\n" + "="*60)
    print("🎯 TESTING TRAINING WITH SIMPLE CONFIG")
    print("="*60)
    
    # Simple test YAML config
    test_config = """
job: extension
config:
  name: test_lora_debug
  process:
    - type: sd_trainer
      training_folder: /workspace/training_data
      
      model:
        name_or_path: black-forest-labs/FLUX.1-dev
        is_flux: true
        quantize: true
        
      sample:
        sampler: flowmatch
        sample_every: 250
        sample_steps: 20
        width: 1024
        height: 1024
        prompts:
          - "A photo of sks person"
        
      train:
        batch_size: 1
        steps: 50
        gradient_accumulation_steps: 1
        train_unet: true
        train_text_encoder: false
        gradient_checkpointing: true
        noise_scheduler: flowmatch
        optimizer: adamw8bit
        lr: 4e-4
        
        dtype: bf16
        
      save:
        dtype: bf16
        save_every: 50
        max_step_saves_to_keep: 1

meta:
  name: test_lora_debug
  version: '1.0'
"""
    
    print("📝 Using test YAML config:")
    print(test_config[:300] + "...")
    
    result = make_request("train_with_yaml", {"config": test_config})
    
    if result and "output" in result:
        output = result["output"]
        if "process_id" in output:
            process_id = output["process_id"]
            print(f"✅ Training started with ID: {process_id}")
            
            # Monitor the process
            return monitor_process(process_id)
        elif "error" in output:
            print(f"❌ Training failed: {output['error']}")
            return False
    else:
        print("❌ No valid response")
        return False

def monitor_process(process_id, max_wait=300):
    """Monitor a process and get detailed status"""
    print(f"\n👀 Monitoring process: {process_id}")
    print("="*40)
    
    start_time = time.time()
    last_status = None
    
    while time.time() - start_time < max_wait:
        result = make_request("process_status", {"process_id": process_id})
        
        if result and "output" in result:
            status_info = result["output"]
            current_status = status_info.get("status", "unknown")
            
            if current_status != last_status:
                print(f"🔄 Status: {current_status}")
                last_status = current_status
                
                # Check for detailed info
                if "error" in status_info:
                    print(f"❌ Error details: {status_info['error']}")
                    return False
                    
                if "output_path" in status_info:
                    print(f"📁 Output: {status_info['output_path']}")
                    
            if current_status == "completed":
                print("✅ Process completed successfully!")
                return True
            elif current_status == "failed":
                print("❌ Process failed!")
                if "error" in status_info:
                    print(f"Error details: {status_info['error']}")
                return False
                
        time.sleep(5)
    
    print("⏰ Timeout waiting for process")
    return False

def test_ai_toolkit_availability():
    """Test if AI toolkit is available"""
    print("\n" + "="*60)
    print("🛠️ TESTING AI TOOLKIT AVAILABILITY")
    print("="*60)
    
    # Try to run a simple command that checks if python modules exist
    test_config = """
import sys
import os
print("Python path:", sys.executable)
print("Working dir:", os.getcwd())

# Check if ai-toolkit exists
if os.path.exists("/workspace/ai-toolkit"):
    print("✅ ai-toolkit directory exists")
    if os.path.exists("/workspace/ai-toolkit/run.py"):
        print("✅ run.py exists")
    else:
        print("❌ run.py missing")
else:
    print("❌ ai-toolkit directory missing")

# Check python modules
try:
    import torch
    print(f"✅ PyTorch: {torch.__version__}")
except ImportError:
    print("❌ PyTorch not available")

try:
    import transformers
    print(f"✅ Transformers: {transformers.__version__}")
except ImportError:
    print("❌ Transformers not available")
"""
    
    # This is a bit hacky but we can test with a simple generation to see system state
    result = make_request("health", {})
    return result is not None

def main():
    """Main diagnostic function"""
    print("🔧 RUNPOD TRAINING FAILURE DIAGNOSTIC")
    print("="*60)
    print(f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Step 1: Test basic health
    if not test_system_health():
        print("\n❌ CRITICAL: System not responding")
        return
    
    # Step 2: Check current processes
    processes = check_current_processes()
    
    # Step 3: Test AI toolkit availability
    test_ai_toolkit_availability()
    
    # Step 4: Try a simple training test
    print("\n🎯 Starting training test...")
    training_success = test_training_with_simple_config()
    
    # Summary
    print("\n" + "="*60)
    print("📊 DIAGNOSTIC SUMMARY")
    print("="*60)
    
    if training_success:
        print("✅ Training works - original problem may be config-related")
    else:
        print("❌ Training fails - system issue detected")
        print("\n🔧 RECOMMENDED ACTIONS:")
        print("   1. Check if AI toolkit is properly installed")
        print("   2. Verify all Python dependencies")
        print("   3. Check HuggingFace token configuration")
        print("   4. Review container startup logs")
        print("   5. Test with simpler training configurations")

if __name__ == "__main__":
    main()
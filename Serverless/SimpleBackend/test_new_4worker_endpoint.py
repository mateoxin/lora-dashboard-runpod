#!/usr/bin/env python3
"""
🚀 TEST NEW 4-WORKER ENDPOINT
Test the new endpoint with 4 workers for parallel LoRA training.
"""

import requests
import time
import base64
import json
import yaml
from datetime import datetime

# Configuration
NEW_ENDPOINT_ID = "rqwaizbda7ucsj"  # 4-worker endpoint
RUNPOD_TOKEN = "rpa_G4713KLVTYYBJYWPO157LX7VVPGV7NZ2K87SX6B17otl1t"
BASE_URL = f"https://api.runpod.ai/v2/{NEW_ENDPOINT_ID}"

headers = {
    'Authorization': f'Bearer {RUNPOD_TOKEN}',
    'Content-Type': 'application/json'
}

def test_health():
    """Test basic health endpoint."""
    print("🔍 Testing Health Check...")
    
    try:
        response = requests.post(
            f"{BASE_URL}/runsync",
            headers=headers,
            json={"input": {"type": "health"}},
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            output = result.get('output', {})
            print(f"   ✅ Health Status: {output.get('status', 'unknown')}")
            print(f"   🕐 Timestamp: {output.get('timestamp', 'unknown')}")
            return True
        else:
            print(f"   ❌ HTTP Error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        return False

def test_upload_sample_data():
    """Upload some sample images for testing."""
    print("\n📤 Testing Sample Data Upload...")
    
    try:
        # Create 3 sample images (dummy data)
        sample_files = []
        for i in range(3):
            # Create minimal valid image data (1x1 PNG)
            png_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\nIDATx\x9cc```\x00\x00\x00\x04\x00\x01]\xcc\xdb\x8d\x00\x00\x00\x00IEND\xaeB`\x82'
            caption_data = f"Test image {i+1}, a sample training image for LoRA".encode('utf-8')
            
            # Convert to base64
            image_b64 = base64.b64encode(png_data).decode('utf-8')
            caption_b64 = base64.b64encode(caption_data).decode('utf-8')
            
            sample_files.extend([
                {
                    "filename": f"test_{i+1}.png",
                    "content": image_b64
                },
                {
                    "filename": f"test_{i+1}.txt", 
                    "content": caption_b64
                }
            ])
        
        payload = {
            "input": {
                "type": "upload_training_data",
                "training_name": "4worker_test",
                "trigger_word": "test_subject",
                "cleanup_existing": True,
                "files": sample_files
            }
        }
        
        response = requests.post(
            f"{BASE_URL}/runsync",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            output = result.get('output', {})
            print(f"   ✅ Upload Status: {output.get('status', 'unknown')}")
            if output.get('training_folder'):
                print(f"   📁 Training Folder: {output['training_folder']}")
            return True
        else:
            print(f"   ❌ HTTP Error: {response.status_code}")
            print(f"   📝 Response: {response.text[:200]}...")
            return False
            
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        return False

def test_yaml_training():
    """Test LoRA training with YAML config."""
    print("\n🎯 Testing YAML LoRA Training...")
    
    try:
        # Load training config
        yaml_config = {
            "job": "extension",
            "config": {
                "name": "4worker_test_lora",
                "process": [
                    {
                        "type": "sd_trainer",
                        "training_folder": "/workspace/training_data",
                        "device": "cuda:0",
                        "trigger_word": "test_subject",
                        "network": {
                            "type": "lora",
                            "linear": 16,
                            "linear_alpha": 16
                        },
                        "save": {
                            "dtype": "float16",
                            "save_every": 50,
                            "max_step_saves_to_keep": 1
                        },
                        "datasets": [
                            {
                                "folder_path": "/workspace/training_data",
                                "caption_ext": "txt",
                                "caption_dropout_rate": 0.1,
                                "shuffle_tokens": False,
                                "cache_latents_to_disk": True,
                                "resolution": [896, 896]
                            }
                        ],
                        "train": {
                            "batch_size": 1,
                            "steps": 10,  # Quick test
                            "gradient_accumulation_steps": 4,
                            "train_unet": True,
                            "train_text_encoder": False,
                            "gradient_checkpointing": True,
                            "noise_scheduler": "flowmatch",
                            "optimizer": "adamw",
                            "lr": 4e-4,
                            "ema_config": {
                                "use_ema": False
                            },
                            "dtype": "bf16"
                        },
                        "model": {
                            "name_or_path": "black-forest-labs/FLUX.1-dev",
                            "is_flux": True,
                            "quantize": False
                        },
                        "sample": {
                            "sampler": "flowmatch",
                            "sample_every": 50,
                            "width": 896,
                            "height": 896,
                            "prompts": [
                                "test_subject, a portrait photo",
                                "test_subject, standing in a field"
                            ],
                            "neg": "",
                            "seed": 42,
                            "walk_seed": False,
                            "guidance_scale": 2,
                            "sample_steps": 20
                        }
                    }
                ]
            }
        }
        
        payload = {
            "input": {
                "type": "train_with_yaml",
                "yaml_config": yaml_config
            }
        }
        
        response = requests.post(
            f"{BASE_URL}/runsync",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            output = result.get('output', {})
            
            if output.get('status') == 'success':
                process_id = output.get('process_id')
                print(f"   ✅ Training Started!")
                print(f"   📋 Process ID: {process_id}")
                return process_id
            else:
                print(f"   ❌ Training Failed: {output.get('error', 'unknown')}")
                return None
        else:
            print(f"   ❌ HTTP Error: {response.status_code}")
            print(f"   📝 Response: {response.text[:200]}...")
            return None
            
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        return None

def test_process_status(process_id):
    """Check status of training process."""
    print(f"\n📊 Checking Process {process_id[:8]}...")
    
    try:
        payload = {
            "input": {
                "type": "process_status",
                "process_id": process_id
            }
        }
        
        response = requests.post(
            f"{BASE_URL}/runsync",
            headers=headers,
            json=payload,
            timeout=15
        )
        
        if response.status_code == 200:
            result = response.json()
            output = result.get('output', {})
            
            if output.get('status') == 'success':
                process = output.get('process', {})
                status = process.get('status', 'unknown')
                created_at = process.get('created_at', 'unknown')
                
                print(f"   📊 Status: {status}")
                print(f"   📅 Created: {created_at}")
                
                if process.get('error'):
                    print(f"   ❌ Error: {process.get('error', '')[:100]}...")
                
                return status
            else:
                print(f"   ❌ Failed: {output.get('error', 'unknown')}")
                return 'error'
        else:
            print(f"   ❌ HTTP Error: {response.status_code}")
            return 'http_error'
            
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        return 'exception'

def test_all_processes():
    """List all processes."""
    print(f"\n📋 Checking All Processes...")
    
    try:
        payload = {
            "input": {
                "type": "processes"
            }
        }
        
        response = requests.post(
            f"{BASE_URL}/runsync",
            headers=headers,
            json=payload,
            timeout=15
        )
        
        if response.status_code == 200:
            result = response.json()
            output = result.get('output', {})
            
            if output.get('status') == 'success':
                processes = output.get('processes', [])
                total_count = output.get('total_count', len(processes))
                
                print(f"   📊 Found {total_count} processes:")
                
                for process in processes:
                    process_id = process.get('id', 'unknown')[:8]
                    status = process.get('status', 'unknown')
                    process_type = process.get('type', 'unknown')
                    
                    print(f"      📋 {process_id} ({process_type}): {status}")
                
                return processes
            else:
                print(f"   ❌ Failed: {output.get('error', 'unknown')}")
                return []
        else:
            print(f"   ❌ HTTP Error: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        return []

def main():
    """Run comprehensive test of 4-worker endpoint."""
    print("🚀 4-WORKER ENDPOINT TEST")
    print(f"🎯 Endpoint: {NEW_ENDPOINT_ID}")
    print(f"⏰ Time: {datetime.now()}")
    print("=" * 60)
    
    # Test 1: Health Check
    if not test_health():
        print("\n❌ Health check failed - endpoint not ready")
        return
    
    # Test 2: Upload Sample Data
    if not test_upload_sample_data():
        print("\n❌ Upload failed - cannot proceed with training")
        return
    
    # Test 3: Start Training
    process_id = test_yaml_training()
    if not process_id:
        print("\n❌ Training start failed")
        return
    
    # Test 4: Monitor Training
    print(f"\n👀 Monitoring process {process_id[:8]} for 2 minutes...")
    
    for i in range(12):  # 2 minutes / 10 seconds = 12 checks
        status = test_process_status(process_id)
        
        if status == 'completed':
            print(f"\n🎉 Training completed successfully!")
            break
        elif status == 'failed':
            print(f"\n❌ Training failed!")
            break
        elif status in ['running', 'pending']:
            print(f"   ⏳ Still {status}... ({i+1}/12)")
            time.sleep(10)
        else:
            print(f"   ❓ Unknown status: {status}")
            time.sleep(10)
    
    # Test 5: List All Processes  
    test_all_processes()
    
    print(f"\n{'='*60}")
    print(f"🏁 4-WORKER ENDPOINT TEST COMPLETED")
    print(f"⏰ Time: {datetime.now()}")
    print(f"🎯 Endpoint ID: {NEW_ENDPOINT_ID}")
    print(f"📋 Last Process ID: {process_id[:8] if process_id else 'None'}")

if __name__ == "__main__":
    main()
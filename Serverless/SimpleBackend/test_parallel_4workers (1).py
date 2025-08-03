#!/usr/bin/env python3
"""
🔄 TEST PARALLEL 4-WORKERS
Test multiple parallel LoRA training jobs on 4 workers.
"""

import requests
import time
import base64
import threading
import json
from datetime import datetime

# Configuration
ENDPOINT_ID = "rqwaizbda7ucsj"  # 4-worker endpoint
RUNPOD_TOKEN = "rpa_G4713KLVTYYBJYWPO157LX7VVPGV7NZ2K87SX6B17otl1t"
BASE_URL = f"https://api.runpod.ai/v2/{ENDPOINT_ID}"

headers = {
    'Authorization': f'Bearer {RUNPOD_TOKEN}',
    'Content-Type': 'application/json'
}

def upload_sample_data(training_name):
    """Upload sample data for a specific training job."""
    print(f"📤 Uploading data for {training_name}...")
    
    try:
        # Create 2 sample images (minimal PNG)
        sample_files = []
        png_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\nIDATx\x9cc```\x00\x00\x00\x04\x00\x01]\xcc\xdb\x8d\x00\x00\x00\x00IEND\xaeB`\x82'
        
        for i in range(2):
            caption_data = f"{training_name} sample {i+1}, test training image".encode('utf-8')
            
            image_b64 = base64.b64encode(png_data).decode('utf-8')
            caption_b64 = base64.b64encode(caption_data).decode('utf-8')
            
            sample_files.extend([
                {"filename": f"{training_name}_{i+1}.png", "content": image_b64},
                {"filename": f"{training_name}_{i+1}.txt", "content": caption_b64}
            ])
        
        payload = {
            "input": {
                "type": "upload_training_data",
                "training_name": training_name,
                "trigger_word": training_name,
                "cleanup_existing": True,
                "files": sample_files
            }
        }
        
        response = requests.post(f"{BASE_URL}/runsync", headers=headers, json=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            output = result.get('output', {})
            print(f"   ✅ {training_name}: Upload OK")
            return True
        else:
            print(f"   ❌ {training_name}: Upload failed ({response.status_code})")
            return False
            
    except Exception as e:
        print(f"   ❌ {training_name}: Upload error - {e}")
        return False

def start_training(training_name):
    """Start LoRA training for a specific job."""
    print(f"🎯 Starting training for {training_name}...")
    
    try:
        # Simple working config with Matt dataset path
        yaml_config = {
            "job": "extension",
            "config": {
                "name": f"{training_name}_lora",
                "process": [
                    {
                        "type": "sd_trainer",
                        "training_folder": "/workspace/training_data",
                        "device": "cuda:0",
                        "trigger_word": training_name,
                        "network": {
                            "type": "lora",
                            "linear": 8,   # Smaller network
                            "linear_alpha": 8
                        },
                        "save": {
                            "dtype": "float16",
                            "save_every": 5,   # Save often
                            "max_step_saves_to_keep": 1
                        },
                        "datasets": [
                            {
                                "folder_path": "/workspace/training_data",
                                "caption_ext": "txt",
                                "caption_dropout_rate": 0.0,
                                "shuffle_tokens": False,
                                "cache_latents_to_disk": True,
                                "resolution": [512, 512]  # Smaller resolution
                            }
                        ],
                        "train": {
                            "batch_size": 1,
                            "steps": 5,  # Very quick test
                            "gradient_accumulation_steps": 1,
                            "train_unet": True,
                            "train_text_encoder": False,
                            "gradient_checkpointing": True,
                            "noise_scheduler": "flowmatch",
                            "optimizer": "adamw",
                            "lr": 1e-4,
                            "ema_config": {"use_ema": False},
                            "dtype": "bf16"
                        },
                        "model": {
                            "name_or_path": "black-forest-labs/FLUX.1-dev",
                            "is_flux": True,
                            "quantize": False
                        },
                        "sample": {
                            "sampler": "flowmatch",
                            "sample_every": 5,
                            "width": 512,
                            "height": 512,
                            "prompts": [f"{training_name}, portrait photo"],
                            "guidance_scale": 2,
                            "sample_steps": 4  # Quick sampling
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
        
        # Training is long-running - use /run (async) instead of /runsync (1min max)
        response = requests.post(f"{BASE_URL}/run", headers=headers, json=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            # /run returns job id, not direct output
            job_id = result.get('id')
            if job_id:
                print(f"   ✅ {training_name}: Training job queued (Job ID: {job_id[:8]})")
                return job_id
            else:
                print(f"   ❌ {training_name}: No job ID returned")
                return None
        else:
            print(f"   ❌ {training_name}: HTTP {response.status_code}")
            return None
            
    except Exception as e:
        print(f"   ❌ {training_name}: Training error - {e}")
        return None

def monitor_process(job_id, training_name):
    """Monitor a specific training job."""
    print(f"👀 Monitoring {training_name} ({job_id[:8]})...")
    
    for i in range(30):  # 5 minutes max
        try:
            # Check job status using /status endpoint
            response = requests.get(f"{BASE_URL}/status/{job_id}", headers=headers, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                status = result.get('status', 'unknown')
                
                if status == 'COMPLETED':
                    output = result.get('output', {})
                    print(f"   🎉 {training_name}: COMPLETED!")
                    return 'completed'
                elif status == 'FAILED':
                    error = result.get('error', '')[:50]
                    print(f"   ❌ {training_name}: FAILED - {error}...")
                    return 'failed'
                elif status in ['IN_QUEUE', 'IN_PROGRESS']:
                    print(f"   ⏳ {training_name}: {status.lower()}... ({i+1}/30)")
                else:
                    print(f"   ❓ {training_name}: {status}")
            else:
                print(f"   ❌ {training_name}: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ {training_name}: Monitor error - {e}")
        
        time.sleep(10)
    
    print(f"   ⏰ {training_name}: Timeout after 5 minutes")
    return 'timeout'

def run_parallel_job(job_id):
    """Run a complete parallel job: upload + train + monitor."""
    training_name = f"job{job_id}"
    
    print(f"\n🚀 STARTING JOB {job_id} ({training_name})")
    print(f"⏰ Start time: {datetime.now()}")
    
    # Step 1: Upload data
    if not upload_sample_data(training_name):
        print(f"❌ Job {job_id}: Upload failed")
        return {'job_id': job_id, 'status': 'upload_failed'}
    
    # Step 2: Start training
    runpod_job_id = start_training(training_name)
    if not runpod_job_id:
        print(f"❌ Job {job_id}: Training start failed")
        return {'job_id': job_id, 'status': 'training_start_failed'}
    
    # Step 3: Monitor (short monitoring)
    final_status = monitor_process(runpod_job_id, training_name)
    
    result = {
        'job_id': job_id,
        'training_name': training_name,
        'runpod_job_id': runpod_job_id,
        'final_status': final_status,
        'end_time': datetime.now()
    }
    
    print(f"🏁 Job {job_id} finished: {final_status}")
    return result

def main():
    """Test parallel training on 4 workers."""
    print("🔄 PARALLEL 4-WORKER TRAINING TEST")
    print(f"🎯 Endpoint: {ENDPOINT_ID}")
    print(f"⏰ Start time: {datetime.now()}")
    print("=" * 60)
    
    # Test 1: Quick health check
    print("🔍 Health check...")
    try:
        response = requests.post(f"{BASE_URL}/runsync", headers=headers, json={"input": {"type": "health"}}, timeout=10)
        if response.status_code == 200:
            print("   ✅ Endpoint healthy")
        else:
            print("   ❌ Endpoint not healthy")
            return
    except Exception as e:
        print(f"   ❌ Health check failed: {e}")
        return
    
    # Test 2: Start 3 parallel jobs (should scale to 3 workers)
    print(f"\n🚀 Starting 3 parallel training jobs...")
    
    threads = []
    results = []
    
    def job_wrapper(job_id):
        result = run_parallel_job(job_id)
        results.append(result)
    
    # Start jobs in parallel
    for job_id in range(1, 4):  # Jobs 1, 2, 3
        thread = threading.Thread(target=job_wrapper, args=(job_id,))
        threads.append(thread)
        thread.start()
        time.sleep(5)  # Stagger starts by 5 seconds
    
    # Wait for all jobs to complete
    print(f"\n⏳ Waiting for all jobs to complete...")
    for thread in threads:
        thread.join()
    
    # Test 3: Check final status
    print(f"\n📊 FINAL RESULTS:")
    print("=" * 60)
    
    for result in results:
        job_id = result['job_id']
        status = result['final_status']
        print(f"   📋 Job {job_id}: {status}")
    
    # Check workers status
    print(f"\n🔍 Checking workers...")
    try:
        response = requests.post(f"{BASE_URL}/runsync", headers=headers, json={"input": {"type": "processes"}}, timeout=15)
        if response.status_code == 200:
            result = response.json()
            output = result.get('output', {})
            if output.get('status') == 'success':
                processes = output.get('processes', [])
                print(f"   📊 Active processes: {len(processes)}")
                for p in processes:
                    print(f"      📋 {p.get('id', '')[:8]} ({p.get('type', '')}): {p.get('status', '')}")
            else:
                print(f"   ❌ Failed to get processes")
        else:
            print(f"   ❌ HTTP {response.status_code}")
    except Exception as e:
        print(f"   ❌ Workers check failed: {e}")
    
    print(f"\n{'='*60}")
    print(f"🏁 PARALLEL TEST COMPLETED")
    print(f"⏰ End time: {datetime.now()}")
    print(f"📊 Jobs completed: {len([r for r in results if r.get('final_status') == 'completed'])}/3")
    print(f"❌ Jobs failed: {len([r for r in results if r.get('final_status') == 'failed'])}/3")

if __name__ == "__main__":
    main()
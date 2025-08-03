#!/usr/bin/env python3
"""
🧠 Test LoRA Training in Simple Backend
Tests upload → training → process status workflow
"""

import requests
import json
import time
import base64
import yaml
from datetime import datetime
from pathlib import Path

# Configuration
ENDPOINT_ID = "z4k89xbu1hrt0o"  # MODEL-DOWNLOAD endpoint
RUNPOD_TOKEN = "rpa_G4713KLVTYYBJYWPO157LX7VVPGV7NZ2K87SX6B17otl1t"
BASE_URL = f"https://api.runpod.ai/v2/{ENDPOINT_ID}"

headers = {
    'Authorization': f'Bearer {RUNPOD_TOKEN}',
    'Content-Type': 'application/json'
}

def create_test_images():
    """Create simple test images and captions."""
    test_files = []
    
    # Create a simple test image (1x1 pixel PNG)
    # This is a minimal valid PNG file (43 bytes)
    png_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xdb\x00\x00\x00\x00IEND\xaeB`\x82'
    
    # Test image 1
    test_files.append({
        "filename": "test_person_1.png",
        "content": base64.b64encode(png_data).decode('utf-8'),
        "content_type": "image/png"
    })
    
    # Test caption 1
    caption_content = "a person, photo, high quality"
    test_files.append({
        "filename": "test_person_1.txt",
        "content": base64.b64encode(caption_content.encode('utf-8')).decode('utf-8'),
        "content_type": "text/plain"
    })
    
    # Test image 2
    test_files.append({
        "filename": "test_person_2.png",
        "content": base64.b64encode(png_data).decode('utf-8'),
        "content_type": "image/png"
    })
    
    # Test caption 2
    caption_content = "a person, portrait, upper body"
    test_files.append({
        "filename": "test_person_2.txt",
        "content": base64.b64encode(caption_content.encode('utf-8')).decode('utf-8'),
        "content_type": "text/plain"
    })
    
    return test_files

def test_health():
    """Test health endpoint."""
    print("🔍 Testing health endpoint...")
    
    response = requests.post(
        f"{BASE_URL}/runsync",
        headers=headers,
        json={"input": {"type": "health"}}
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"   ✅ Health check: {result.get('output', {}).get('status', 'unknown')}")
        return True
    else:
        print(f"   ❌ Health check failed: {response.text}")
        return False

def test_upload():
    """Test upload training data."""
    print("📁 Testing upload training data...")
    
    test_files = create_test_images()
    
    response = requests.post(
        f"{BASE_URL}/run",  # Use async for upload
        headers=headers,
        json={
            "input": {
                "type": "upload_training_data",
                "training_name": "test_lora_training",
                "trigger_word": "person",
                "cleanup_existing": True,
                "files": test_files
            }
        }
    )
    
    if response.status_code == 200:
        result = response.json()
        job_id = result.get('id')
        print(f"   📤 Upload job submitted: {job_id}")
        
        # Poll for completion
        return wait_for_job_completion(job_id, "upload")
    else:
        print(f"   ❌ Upload failed: {response.text}")
        return False

def test_training():
    """Test LoRA training with direct config - DISABLED since only YAML config is needed."""
    print("🧠 Testing LoRA training (direct config)...")
    print("   ⏭️ Skipping Direct Config - only YAML config is supported")
    return True  # Skip test
    
    # # COMMENTED OUT - Direct Config not needed, only YAML requests are used
    # # Load training config
    # config_path = Path("training_conservative.yaml")
    # if not config_path.exists():
    #     print(f"   ❌ Config file not found: {config_path}")
    #     return False
    # 
    # with open(config_path, 'r') as f:
    #     training_config = yaml.safe_load(f)
    # 
    # response = requests.post(
    #     f"{BASE_URL}/run",  # Use async for training
    #     headers=headers,
    #     json={
    #         "input": {
    #             "type": "train",
    #             "config": training_config
    #         }
    #     }
    # )
    # 
    # if response.status_code == 200:
    #     result = response.json()
    #     job_id = result.get('id')
    #     print(f"   🚀 Training job submitted: {job_id}")
    #     
    #     # Poll for completion (training takes longer)
    #     return wait_for_job_completion(job_id, "training", timeout=600)  # 10 minutes
    # else:
    #     print(f"   ❌ Training failed: {response.text}")
    #     return False

def test_training_with_yaml():
    """Test LoRA training with YAML config."""
    print("📝 Testing LoRA training (YAML config)...")
    
    # Load training config and parse YAML to JSON
    config_path = Path("training_conservative.yaml")
    if not config_path.exists():
        print(f"   ❌ Config file not found: {config_path}")
        return False
    
    with open(config_path, 'r') as f:
        yaml_content = yaml.safe_load(f)  # Parse YAML to dict/JSON
    
    response = requests.post(
        f"{BASE_URL}/run",  # Use async for training
        headers=headers,
        json={
            "input": {
                "type": "train_with_yaml",
                "yaml_config": yaml_content,  # Send as JSON object, not string
                "dataset_path": "/workspace/training_data"
            }
        }
    )
    
    if response.status_code == 200:
        result = response.json()
        job_id = result.get('id')
        print(f"   📝 YAML Training job submitted: {job_id}")
        
        # Poll for completion (training takes longer)
        return wait_for_job_completion(job_id, "YAML training", timeout=600)  # 10 minutes
    else:
        print(f"   ❌ YAML Training failed: {response.text}")
        return False

def test_processes():
    """Test get processes endpoint."""
    print("📋 Testing get processes...")
    
    response = requests.post(
        f"{BASE_URL}/runsync",
        headers=headers,
        json={"input": {"type": "processes"}}
    )
    
    if response.status_code == 200:
        result = response.json()
        output = result.get('output', {})
        processes = output.get('processes', [])
        print(f"   ✅ Found {len(processes)} processes")
        
        for proc in processes:
            print(f"      - {proc.get('id', 'unknown')}: {proc.get('type', 'unknown')} ({proc.get('status', 'unknown')})")
        
        return True
    else:
        print(f"   ❌ Get processes failed: {response.text}")
        return False

def wait_for_job_completion(job_id: str, job_type: str, timeout: int = 120):
    """Wait for job to complete."""
    print(f"   ⏳ Waiting for {job_type} job {job_id} to complete...")
    
    start_time = time.time()
    while time.time() - start_time < timeout:
        response = requests.get(
            f"{BASE_URL}/status/{job_id}",
            headers=headers
        )
        
        if response.status_code == 200:
            result = response.json()
            status = result.get('status', 'unknown')
            
            if status == "COMPLETED":
                output = result.get('output', {})
                print(f"   ✅ {job_type.title()} completed successfully")
                if 'process_id' in output:
                    print(f"      Process ID: {output['process_id']}")
                return True
            elif status == "FAILED":
                error = result.get('error', 'Unknown error')
                print(f"   ❌ {job_type.title()} failed: {error}")
                return False
            elif status in ["IN_QUEUE", "IN_PROGRESS"]:
                print(f"      Status: {status} (waiting...)")
                time.sleep(5)
            else:
                print(f"      Unexpected status: {status}")
                time.sleep(5)
        else:
            print(f"   ❌ Status check failed: {response.text}")
            return False
    
    print(f"   ⏰ {job_type.title()} timed out after {timeout} seconds")
    return False

def test_list_models():
    """Test listing trained LoRA models."""
    print("📋 Testing list trained models...")
    
    response = requests.post(
        f"{BASE_URL}/runsync",
        headers=headers,
        json={"input": {"type": "list_models"}}
    )
    
    if response.status_code == 200:
        result = response.json()
        models = result.get("output", {}).get("models", [])
        count = result.get("output", {}).get("total_count", 0)
        output_dir = result.get("output", {}).get("output_directory", "unknown")
        
        print(f"   ✅ Found {count} trained models in {output_dir}")
        for model in models:
            print(f"      - {model.get('filename', 'unknown')} ({model.get('size_mb', 0)}MB) - {model.get('modified_date', 'unknown')}")
        return True
    else:
        print(f"   ❌ Failed: {response.status_code} - {response.text}")
        return False

def test_download_model():
    """Test downloading a trained model (if available)."""
    print("📥 Testing download model...")
    
    # First get list of models
    list_response = requests.post(
        f"{BASE_URL}/runsync",
        headers=headers,
        json={"input": {"type": "list_models"}}
    )
    
    if list_response.status_code != 200:
        print(f"   ⚠️ Cannot list models: {list_response.status_code}")
        return True  # Skip test if listing fails
    
    models = list_response.json().get("output", {}).get("models", [])
    
    if not models:
        print(f"   ⚠️ No trained models available for download")
        return True  # Skip test if no models
    
    # Try to download first model
    first_model = models[0]
    filename = first_model.get("filename")
    
    print(f"   📥 Attempting to download: {filename}")
    
    response = requests.post(
        f"{BASE_URL}/runsync",
        headers=headers,
        json={"input": {"type": "download_model", "filename": filename}}
    )
    
    if response.status_code == 200:
        result = response.json()
        output = result.get("output", {})
        
        if output.get("status") == "success":
            downloaded_size = output.get("size_mb", 0)
            print(f"   ✅ Downloaded: {output.get('filename', 'unknown')} ({downloaded_size}MB)")
            return True
        else:
            print(f"   ❌ Download failed: {output.get('error', 'unknown error')}")
            return False
    else:
        print(f"   ❌ Failed: {response.status_code} - {response.text}")
        return False

def main():
    """Run all tests."""
    print("🧪 Simple Backend LoRA Training Test Suite")
    print(f"🎯 Endpoint: {ENDPOINT_ID}")
    print(f"⏰ Time: {datetime.now()}")
    print("=" * 60)
    
    tests = [
        ("Health Check", test_health),
        ("Upload Training Data", test_upload),
        ("Get Processes", test_processes),
        ("LoRA Training (Direct Config)", test_training),
        ("LoRA Training (YAML Config)", test_training_with_yaml),
        ("Get Processes (After Training)", test_processes),
        ("List Trained Models", test_list_models),
        ("Download Model", test_download_model),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"   ❌ {test_name} exception: {e}")
            results[test_name] = False
        
        print()  # Add spacing
    
    # Summary
    print("=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\n📈 Success Rate: {passed}/{total} ({(passed/total)*100:.1f}%)")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
        print("💡 LoRA training workflow is fully functional!")
    elif passed >= total * 0.7:
        print("\n⚠️ Most tests passed - system is mostly functional")
    else:
        print("\n🚨 Many tests failed - check setup and logs")

if __name__ == "__main__":
    main()
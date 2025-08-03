#!/usr/bin/env python3
"""
🔍 CHECK PROCESS 18bec0bb
Check status of the Matt training process and any available models.
"""

import requests
from datetime import datetime

# Configuration
ENDPOINT_ID = "8s9y5exor2uidx"
RUNPOD_TOKEN = "rpa_G4713KLVTYYBJYWPO157LX7VVPGV7NZ2K87SX6B17otl1t"
BASE_URL = f"https://api.runpod.ai/v2/{ENDPOINT_ID}"

headers = {
    'Authorization': f'Bearer {RUNPOD_TOKEN}',
    'Content-Type': 'application/json'
}

def check_specific_process():
    """Check process 18bec0bb status."""
    print("🔍 Checking process 18bec0bb...")
    
    try:
        response = requests.post(
            f"{BASE_URL}/runsync",
            headers=headers,
            json={"input": {"type": "process_status", "process_id": "18bec0bb"}},
            timeout=20
        )
        
        if response.status_code == 200:
            result = response.json()
            output = result.get('output', {})
            
            if output.get('status') == 'success':
                process = output.get('process', {})
                status = process.get('status', 'unknown')
                created_at = process.get('created_at', 'unknown')
                updated_at = process.get('updated_at', 'unknown')
                error = process.get('error', None)
                output_path = process.get('output_path', None)
                
                print(f"   📋 Process ID: 18bec0bb")
                print(f"   📊 Status: {status}")
                print(f"   📅 Created: {created_at}")
                print(f"   🔄 Updated: {updated_at}")
                
                if output_path:
                    print(f"   📁 Output: {output_path}")
                
                if error:
                    print(f"   ❌ Error: {error[:300]}...")
                    
                return status
            else:
                error_msg = output.get('error', 'unknown')
                print(f"   ❌ Failed to get process: {error_msg}")
                return "not_found"
        else:
            print(f"   ❌ HTTP Error: {response.status_code}")
            print(f"      Response: {response.text[:200]}...")
            return "http_error"
            
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        return "exception"

def check_all_processes():
    """Check all processes."""
    print("\n📋 Checking all processes...")
    
    try:
        response = requests.post(
            f"{BASE_URL}/runsync",
            headers=headers,
            json={"input": {"type": "processes"}},
            timeout=20
        )
        
        if response.status_code == 200:
            result = response.json()
            output = result.get('output', {})
            
            if output.get('status') == 'success':
                processes = output.get('processes', [])
                total_count = output.get('total_count', len(processes))
                
                print(f"   📊 Found {total_count} total processes:")
                
                for process in processes:
                    process_id = process.get('id', 'unknown')
                    status = process.get('status', 'unknown')
                    process_type = process.get('type', 'unknown')
                    created_at = process.get('created_at', 'unknown')
                    
                    print(f"      📋 {process_id} ({process_type}): {status}")
                    print(f"         📅 Created: {created_at}")
                    
                    if status == "failed" and process.get('error'):
                        error = process.get('error', '')[:100]
                        print(f"         ❌ Error: {error}...")
                
                return processes
            else:
                error_msg = output.get('error', 'unknown')
                print(f"   ❌ Failed to get processes: {error_msg}")
                return []
        else:
            print(f"   ❌ HTTP Error: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        return []

def check_models():
    """Check for available models."""
    print("\n📦 Checking for trained models...")
    
    try:
        response = requests.post(
            f"{BASE_URL}/runsync",
            headers=headers,
            json={"input": {"type": "list_models"}},
            timeout=20
        )
        
        if response.status_code == 200:
            result = response.json()
            output = result.get('output', {})
            models = output.get('models', [])
            total_count = output.get('total_count', len(models))
            
            print(f"   📊 Found {total_count} trained models:")
            
            if models:
                for model in models:
                    filename = model.get('filename', 'unknown')
                    size_mb = model.get('size_mb', 0)
                    modified_date = model.get('modified_date', 'unknown')
                    
                    print(f"      📦 {filename}")
                    print(f"         📏 Size: {size_mb} MB")
                    print(f"         📅 Modified: {modified_date}")
            else:
                print(f"      💭 No models found yet")
                
            return models
        else:
            print(f"   ❌ HTTP Error: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        return []

def main():
    """Check process 18bec0bb status and models."""
    print("🔍 PROCESS 18bec0bb STATUS CHECK")
    print(f"⏰ Time: {datetime.now()}")
    print(f"🎯 Endpoint: {ENDPOINT_ID}")
    print("=" * 60)
    
    # Check specific process
    process_status = check_specific_process()
    
    # Check all processes
    all_processes = check_all_processes()
    
    # Check models
    models = check_models()
    
    # Summary
    print(f"\n{'='*60}")
    print(f"📊 STATUS SUMMARY")
    print(f"{'='*60}")
    print(f"📋 Process 18bec0bb Status: {process_status}")
    print(f"📊 Total Processes: {len(all_processes)}")
    print(f"📦 Available Models: {len(models)}")
    
    # Analysis
    if process_status == "completed" and models:
        print(f"\n🎉 SUCCESS!")
        print(f"   ✅ Matt LoRA training completed!")
        print(f"   📦 {len(models)} model(s) ready for download!")
        
    elif process_status == "completed" and not models:
        print(f"\n⚠️ TRAINING COMPLETED BUT NO MODELS")
        print(f"   ✅ Process finished successfully")
        print(f"   ❓ Models not found - check output directory")
        
    elif process_status == "failed":
        print(f"\n❌ TRAINING FAILED")
        print(f"   🚨 Process failed - check error details above")
        print(f"   💡 May need to restart with different config")
        
    elif process_status == "running":
        print(f"\n⏳ TRAINING STILL RUNNING")
        print(f"   🔄 Process still active")
        print(f"   ⏰ Check again in 10-15 minutes")
        
    elif process_status == "not_found":
        print(f"\n❓ PROCESS NOT FOUND")
        print(f"   🤔 Process 18bec0bb not in memory")
        print(f"   💡 May have been cleaned up or restarted")
        
    else:
        print(f"\n🚨 UNKNOWN STATUS")
        print(f"   ❓ Status: {process_status}")
        print(f"   💡 Check endpoint and worker health")

if __name__ == "__main__":
    main()
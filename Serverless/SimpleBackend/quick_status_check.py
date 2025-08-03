#!/usr/bin/env python3
"""
🔍 QUICK STATUS CHECK
Check current status of training process b632986d and available models.
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

def check_process_status():
    """Check status of process b632986d."""
    print("🔍 Checking process b632986d status...")
    
    try:
        response = requests.post(
            f"{BASE_URL}/runsync",
            headers=headers,
            json={"input": {"type": "process_status", "process_id": "b632986d"}},
            timeout=30
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
                
                print(f"   📋 Process ID: b632986d")
                print(f"   📊 Status: {status}")
                print(f"   📅 Created: {created_at}")
                print(f"   🔄 Updated: {updated_at}")
                
                if output_path:
                    print(f"   📁 Output: {output_path}")
                
                if error:
                    print(f"   ❌ Error: {error}")
                    
                return status
            else:
                error_msg = output.get('error', 'unknown')
                print(f"   ❌ Failed to get process status: {error_msg}")
                return "error"
        else:
            print(f"   ❌ HTTP Error: {response.status_code}")
            print(f"      Response: {response.text}")
            return "error"
            
    except Exception as e:
        print(f"   ❌ Exception checking status: {e}")
        return "error"

def check_models():
    """Check for available trained models."""
    print("\n📦 Checking for trained models...")
    
    try:
        response = requests.post(
            f"{BASE_URL}/runsync",
            headers=headers,
            json={"input": {"type": "list_models"}},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            output = result.get('output', {})
            models = output.get('models', [])
            total_count = output.get('total_count', 0)
            
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
            print(f"      Response: {response.text}")
            return []
            
    except Exception as e:
        print(f"   ❌ Exception checking models: {e}")
        return []

def check_all_processes():
    """Check all running processes."""
    print("\n📋 Checking all processes...")
    
    try:
        response = requests.post(
            f"{BASE_URL}/runsync",
            headers=headers,
            json={"input": {"type": "processes"}},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            output = result.get('output', {})
            
            if output.get('status') == 'success':
                processes = output.get('processes', [])
                total_count = output.get('total_count', 0)
                
                print(f"   📊 Found {total_count} total processes:")
                
                for process in processes:
                    process_id = process.get('id', 'unknown')
                    status = process.get('status', 'unknown')
                    process_type = process.get('type', 'unknown')
                    created_at = process.get('created_at', 'unknown')
                    
                    print(f"      📋 {process_id} ({process_type}): {status}")
                    print(f"         📅 Created: {created_at}")
                
                return processes
            else:
                error_msg = output.get('error', 'unknown')
                print(f"   ❌ Failed to get processes: {error_msg}")
                return []
        else:
            print(f"   ❌ HTTP Error: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"   ❌ Exception checking processes: {e}")
        return []

def main():
    """Run status check."""
    print("🔍 QUICK STATUS CHECK")
    print(f"⏰ Time: {datetime.now()}")
    print(f"🎯 Endpoint: {ENDPOINT_ID}")
    print("=" * 60)
    
    # Check specific process
    status = check_process_status()
    
    # Check for models
    models = check_models()
    
    # Check all processes
    processes = check_all_processes()
    
    # Summary
    print(f"\n{'='*60}")
    print(f"📊 STATUS SUMMARY")
    print(f"{'='*60}")
    print(f"📋 Process b632986d Status: {status}")
    print(f"📦 Available Models: {len(models)}")
    print(f"🔄 Total Processes: {len(processes)}")
    
    # Interpretation
    if status == "completed" and models:
        print(f"\n🎉 SUCCESS!")
        print(f"   ✅ Training completed successfully")
        print(f"   📦 {len(models)} model(s) ready for download")
        print(f"   💡 Matt's LoRA is ready!")
        
    elif status == "completed" and not models:
        print(f"\n⚠️ PARTIAL SUCCESS")
        print(f"   ✅ Training marked as completed")
        print(f"   ❓ No models found - might need a few minutes to appear")
        print(f"   💡 Check again in 2-3 minutes")
        
    elif status == "running":
        print(f"\n⏳ TRAINING IN PROGRESS")
        print(f"   🔄 Process still running - this is normal")
        print(f"   ⏰ LoRA training can take 30-60+ minutes")
        print(f"   💡 Check again in 10-15 minutes")
        
    elif status == "failed":
        print(f"\n❌ TRAINING FAILED")
        print(f"   🚨 Process failed - check error details above")
        print(f"   💡 May need to restart training with fixes")
        
    else:
        print(f"\n❓ UNKNOWN STATUS")
        print(f"   🤔 Status: {status}")
        print(f"   💡 Check logs for more details")

if __name__ == "__main__":
    main()
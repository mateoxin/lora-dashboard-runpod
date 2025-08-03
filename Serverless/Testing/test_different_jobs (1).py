#!/usr/bin/env python3
"""
🧪 Test różnych typów jobów na endpoint: 4z7x4al6ars9ou
Sprawdzić który typ job się wykonuje
"""

import requests
import time

ENDPOINT_ID = "4z7x4al6ars9ou"
# Import config loader
try:
    from config_loader_shared import get_runpod_token
    TOKEN = get_runpod_token()
except ImportError:
    print("❌ Could not import config_loader_shared.py")
    print("Please ensure config_loader_shared.py is in the same directory.")
    import sys
    sys.exit(1)
except ValueError as e:
    print(f"❌ Configuration error: {e}")
    print("📋 Please copy config.env.template to config.env and set your RunPod token.")
    import sys
    sys.exit(1)
BASE_URL = f"https://api.runpod.ai/v2/{ENDPOINT_ID}"

def submit_and_check_job(job_type, input_data=None):
    """Submit job and check status"""
    print(f"\n🧪 Testing job type: {job_type}")
    
    payload = {
        "input": {
            "type": job_type
        }
    }
    
    if input_data:
        payload["input"].update(input_data)
    
    try:
        # Submit job
        response = requests.post(f"{BASE_URL}/run", 
                               json=payload,
                               headers={
                                   "Authorization": f"Bearer {TOKEN}",
                                   "Content-Type": "application/json"
               }, timeout=10)
        
        if response.status_code != 200:
            print(f"   ❌ Submit failed: {response.status_code}")
            return False
        
        result = response.json()
        job_id = result.get("id")
        initial_status = result.get("status")
        
        print(f"   📦 Job ID: {job_id}")
        print(f"   📋 Initial: {initial_status}")
        
        if not job_id:
            print("   ❌ No job ID")
            return False
        
        # Check status after different intervals
        for wait_time in [3, 8, 15]:
            print(f"   ⏱️ Checking after {wait_time}s...")
            time.sleep(wait_time - (3 if wait_time > 3 else 0))  # Progressive wait
            
            status_response = requests.get(f"{BASE_URL}/status/{job_id}", 
                                         headers={"Authorization": f"Bearer {TOKEN}"},
                                         timeout=10)
            
            if status_response.status_code == 200:
                status_data = status_response.json()
                status = status_data.get("status", "UNKNOWN")
                print(f"   📋 Status: {status}")
                
                if status == "COMPLETED":
                    output = status_data.get("output")
                    print(f"   ✅ SUCCESS! Output: {output}")
                    return True
                elif status == "FAILED":
                    error = status_data.get("error", "Unknown error")
                    print(f"   ❌ FAILED: {error}")
                    return False
                elif status == "IN_PROGRESS":
                    print(f"   ⚡ Processing...")
                    # Continue checking
                elif status == "IN_QUEUE":
                    print(f"   ⏳ Still queued...")
                    # Continue checking
                else:
                    print(f"   🤔 Unknown status: {status}")
            else:
                print(f"   ❌ Status check failed: {status_response.status_code}")
                break
        
        print(f"   ❌ Timeout - job didn't complete in 15s")
        return False
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_all_job_types():
    print("🧪 Test Różnych Typów Jobów")
    print(f"🎯 Endpoint: {ENDPOINT_ID}")
    print("=" * 50)
    
    # Job types from backend handler
    job_types_to_test = [
        ("health", None),
        ("processes", None),
        ("lora", None),
        ("unknown_type", None),  # This should fail fast
    ]
    
    results = {}
    
    for job_type, input_data in job_types_to_test:
        results[job_type] = submit_and_check_job(job_type, input_data)
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 RESULTS SUMMARY")
    print("=" * 50)
    
    working_jobs = []
    failing_jobs = []
    
    for job_type, success in results.items():
        status = "✅ WORKS" if success else "❌ FAILS"
        print(f"   {job_type}: {status}")
        
        if success:
            working_jobs.append(job_type)
        else:
            failing_jobs.append(job_type)
    
    print(f"\n📈 Working jobs: {len(working_jobs)}")
    print(f"📉 Failing jobs: {len(failing_jobs)}")
    
    if working_jobs:
        print("✅ Some job types work - backend is partially functional")
        print("🔧 Problem may be with specific job handlers")
    else:
        print("❌ No jobs work - major backend issue")
        print("🔧 Check worker logs for container startup errors")
    
    return results

if __name__ == "__main__":
    test_all_job_types() 

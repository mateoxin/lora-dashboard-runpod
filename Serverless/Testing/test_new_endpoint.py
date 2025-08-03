#!/usr/bin/env python3
"""
🧪 Test nowego endpoint: 4z7x4al6ars9ou
"""

import requests
import json
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

def test_new_endpoint():
    print("🧪 Test Nowego Endpoint")
    print(f"🎯 ID: {ENDPOINT_ID}")
    print("=" * 40)

    # Test 1: Health check
    print("1️⃣ Health check...")
    try:
        response = requests.get(f"{BASE_URL}/health", 
                              headers={"Authorization": f"Bearer {TOKEN}"}, 
                              timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            workers = data.get("workers", {})
            jobs = data.get("jobs", {})
            print(f"   👷 Workers ready: {workers.get('ready', 0)}")
            print(f"   👷 Workers idle: {workers.get('idle', 0)}")
            print(f"   📋 Jobs in queue: {jobs.get('inQueue', 0)}")
            print(f"   📋 Jobs in progress: {jobs.get('inProgress', 0)}")
            
            if workers.get('ready', 0) > 0:
                print("   ✅ Workers are READY!")
            else:
                print("   ❌ No ready workers")
                return False
        else:
            print(f"   ❌ Health failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Health error: {e}")
        return False

    # Test 2: Submit test job
    print("\n2️⃣ Submitting test job...")
    try:
        payload = {
            "input": {
                "type": "health"
            }
        }
        
        response = requests.post(f"{BASE_URL}/run", 
                               json=payload,
                               headers={
                                   "Authorization": f"Bearer {TOKEN}",
                                   "Content-Type": "application/json"
                               }, 
                               timeout=10)
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            job_id = result.get("id")
            status = result.get("status")
            print(f"   📦 Job ID: {job_id}")
            print(f"   📋 Status: {status}")
            
            if job_id:
                print("   ✅ Job submitted successfully!")
                
                # Wait and check status
                print("\n3️⃣ Checking job status after 5s...")
                time.sleep(5)
                
                status_response = requests.get(f"{BASE_URL}/status/{job_id}", 
                                             headers={"Authorization": f"Bearer {TOKEN}"},
                                             timeout=10)
                
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    final_status = status_data.get("status", "UNKNOWN")
                    print(f"   📋 Final status: {final_status}")
                    
                    if final_status == "COMPLETED":
                        print("   🎉 SUCCESS! Job completed!")
                        print("   ✅ Backend is FULLY WORKING!")
                        return True
                    elif final_status == "IN_PROGRESS":
                        print("   ⚡ Job is processing - Worker is working!")
                        return True
                    elif final_status == "IN_QUEUE":
                        print("   ❌ Still stuck in queue")
                        return False
                    else:
                        print(f"   🤔 Unexpected status: {final_status}")
                        return False
                else:
                    print(f"   ❌ Status check failed: {status_response.status_code}")
                    return False
            else:
                print("   ❌ No job ID returned")
                return False
        else:
            print(f"   ❌ Job submission failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Job submission error: {e}")
        return False

if __name__ == "__main__":
    success = test_new_endpoint()
    
    print("\n" + "=" * 40)
    if success:
        print("🎉 ENDPOINT DZIAŁA PERFEKCYJNIE!")
        print("✅ Workers processing jobs correctly")
        print("🚀 Ready for full backend testing")
        print("\nNext: python async_backend_tester.py")
    else:
        print("🚨 ENDPOINT STILL HAS ISSUES")
        print("❌ Check RunPod Console for problems") 
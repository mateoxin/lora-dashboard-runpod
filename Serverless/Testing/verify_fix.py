#!/usr/bin/env python3
"""
✅ VERIFICATION TEST - Run after endpoint fix
Quick test to verify worker dispatch is working
"""

import requests
import time
import json

# UPDATE THIS WITH NEW ENDPOINT ID IF NEEDED
ENDPOINT_ID = "4z7x4al6ars9ou"  # ✅ UPDATED - New working endpoint
RUNPOD_TOKEN = "YOUR_RUNPOD_TOKEN_HERE"  # Replace with your actual token
BASE_URL = f"https://api.runpod.ai/v2/{ENDPOINT_ID}"

def verify_fix():
    print("✅ VERIFICATION TEST - Endpoint Fix")
    print(f"🎯 Testing: {ENDPOINT_ID}")
    print("=" * 50)
    
    # Step 1: Check health endpoint
    print("1️⃣ Checking endpoint health...")
    try:
        response = requests.get(f"{BASE_URL}/health", 
                              headers={"Authorization": f"Bearer {RUNPOD_TOKEN}"}, 
                              timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            jobs = data.get('jobs', {})
            workers = data.get('workers', {})
            
            print(f"   📊 Jobs in queue: {jobs.get('inQueue', 0)}")
            print(f"   📊 Jobs in progress: {jobs.get('inProgress', 0)}")
            print(f"   👷 Workers ready: {workers.get('ready', 0)}")
            print(f"   👷 Workers idle: {workers.get('idle', 0)}")
            
            if jobs.get('inQueue', 0) > 5:
                print("   ⚠️ WARNING: Still many jobs in queue")
            else:
                print("   ✅ Queue looks normal")
                
        else:
            print(f"   ❌ Health check failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Health check error: {e}")
        return False
    
    # Step 2: Submit test job
    print("\n2️⃣ Submitting test job...")
    try:
        payload = {
            "input": {
                "type": "health"
            }
        }
        
        start_time = time.time()
        response = requests.post(f"{BASE_URL}/run", 
                               json=payload,
                               headers={
                                   "Authorization": f"Bearer {RUNPOD_TOKEN}",
                                   "Content-Type": "application/json"
                               }, 
                               timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            job_id = result.get('id')
            print(f"   ✅ Job submitted: {job_id}")
        else:
            print(f"   ❌ Job submission failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Job submission error: {e}")
        return False
    
    # Step 3: Check job status after short wait
    print("\n3️⃣ Checking job execution...")
    time.sleep(5)  # Wait 5 seconds
    
    try:
        response = requests.get(f"{BASE_URL}/status/{job_id}", 
                              headers={"Authorization": f"Bearer {RUNPOD_TOKEN}"},
                              timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            status = result.get('status', 'UNKNOWN')
            print(f"   📋 Job status: {status}")
            
            if status == 'COMPLETED':
                print("   🎉 SUCCESS! Job completed immediately")
                print("   ✅ Worker dispatch is WORKING")
                return True
            elif status == 'IN_PROGRESS':
                print("   ⚡ Job is processing - Worker dispatch WORKING")
                return True
            elif status == 'IN_QUEUE':
                print("   ❌ STILL BROKEN - Job stuck in queue")
                return False
            else:
                print(f"   🤔 Unexpected status: {status}")
                return False
                
        else:
            print(f"   ❌ Status check failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Status check error: {e}")
        return False

def main():
    success = verify_fix()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 ENDPOINT FIXED SUCCESSFULLY!")
        print("✅ Workers are processing jobs normally")
        print("🚀 Ready to run full backend tests")
        print("\nNext step: python async_backend_tester.py")
    else:
        print("🚨 ENDPOINT STILL BROKEN")
        print("❌ Worker dispatch not working")
        print("🔧 Try:")
        print("   1. Restart workers again")
        print("   2. Create completely new endpoint")
        print("   3. Check worker logs for errors")

if __name__ == "__main__":
    main() 

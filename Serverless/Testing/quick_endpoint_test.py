#!/usr/bin/env python3
"""
🚀 QUICK ENDPOINT TEST - Minimal diagnosis
Find out why /runsync operations timeout

Strategy:
1. Test basic connectivity
2. Try to warm up workers with /run
3. Test simple /runsync operations
4. Diagnose worker state
"""

import requests
import json
import time
from datetime import datetime

# Configuration
ENDPOINT_ID = "4z7x4al6ars9ou"  # ✅ UPDATED - New working endpoint
RUNPOD_TOKEN = "YOUR_RUNPOD_TOKEN_HERE"  # Replace with your actual token
BASE_URL = f"https://api.runpod.ai/v2/{ENDPOINT_ID}"

def test_basic_connectivity():
    """Test if endpoint exists"""
    print("🔍 Testing basic connectivity...")
    try:
        response = requests.get(f"{BASE_URL}/health", 
                              headers={"Authorization": f"Bearer {RUNPOD_TOKEN}"}, 
                              timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code in [200, 404]:
            print("   ✅ Endpoint reachable")
            return True
        else:
            print(f"   ❌ Unexpected status: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Connection failed: {e}")
        return False

def test_async_warmup():
    """Try to warm up workers with /run"""
    print("🔥 Attempting worker warm-up with /run...")
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
                               timeout=30)
        duration = time.time() - start_time
        
        print(f"   Duration: {duration:.1f}s")
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   Response: {result}")
            print("   ✅ Async health check successful")
            return True
        else:
            print(f"   ❌ Failed with status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Warmup failed: {e}")
        return False

def test_sync_after_warmup():
    """Test /runsync after warmup"""
    print("⚡ Testing /runsync after warmup...")
    try:
        payload = {
            "input": {
                "type": "health"
            }
        }
        
        start_time = time.time()
        response = requests.post(f"{BASE_URL}/runsync", 
                               json=payload,
                               headers={
                                   "Authorization": f"Bearer {RUNPOD_TOKEN}",
                                   "Content-Type": "application/json"
                               }, 
                               timeout=60)
        duration = time.time() - start_time
        
        print(f"   Duration: {duration:.1f}s")
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   Response: {result}")
            print("   ✅ Sync health check successful")
            return True
        else:
            print(f"   ❌ Failed with status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Sync test failed: {e}")
        return False

def test_processes_async():
    """Test processes via /run (async)"""
    print("📋 Testing processes via /run...")
    try:
        payload = {
            "input": {
                "type": "processes"
            }
        }
        
        start_time = time.time()
        response = requests.post(f"{BASE_URL}/run", 
                               json=payload,
                               headers={
                                   "Authorization": f"Bearer {RUNPOD_TOKEN}",
                                   "Content-Type": "application/json"
                               }, 
                               timeout=30)
        duration = time.time() - start_time
        
        print(f"   Duration: {duration:.1f}s")
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   Job ID: {result.get('id', 'N/A')}")
            print(f"   Status: {result.get('status', 'N/A')}")
            print("   ✅ Async processes request successful")
            return True
        else:
            print(f"   ❌ Failed with status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Async processes failed: {e}")
        return False

def main():
    print("🧪 Quick Endpoint Diagnosis")
    print(f"🎯 Endpoint: {ENDPOINT_ID}")
    print(f"⏰ Time: {datetime.now()}")
    print("=" * 50)
    
    results = {}
    
    # Test 1: Basic connectivity
    results["connectivity"] = test_basic_connectivity()
    
    if not results["connectivity"]:
        print("\n💥 CRITICAL: Cannot reach endpoint")
        return
    
    # Test 2: Async warmup
    print()
    results["warmup"] = test_async_warmup()
    
    # Wait a bit after warmup
    if results["warmup"]:
        print("\n⏱️ Waiting 10s for worker to be ready...")
        time.sleep(10)
    
    # Test 3: Sync after warmup
    print()
    results["sync_after_warmup"] = test_sync_after_warmup()
    
    # Test 4: Async processes
    print()
    results["processes_async"] = test_processes_async()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 QUICK DIAGNOSIS SUMMARY")
    print("=" * 50)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name}: {status}")
    
    # Recommendations
    print("\n💡 RECOMMENDATIONS:")
    if results.get("connectivity") and results.get("warmup"):
        if results.get("sync_after_warmup"):
            print("   ✅ Endpoint working normally")
        else:
            print("   ⚠️ Workers need warmup - use /run then /runsync")
    else:
        print("   🚨 Endpoint has serious issues - check RunPod Console")
    
    print("\n🔍 NEXT STEPS:")
    print("   1. Check RunPod Console for worker status")
    print("   2. Ensure Min Workers > 0")
    print("   3. Try manual endpoint restart if needed")

if __name__ == "__main__":
    main() 

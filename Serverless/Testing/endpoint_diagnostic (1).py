#!/usr/bin/env python3
"""
🔍 RunPod Endpoint Diagnostic Tool

Comprehensive endpoint testing and diagnostics:
- Connection verification
- Authorization testing
- Endpoint availability
- Response time measurement
- Health checks
"""

import json
import sys
import time
from datetime import datetime
import requests
from typing import Dict, Any, Optional

# Import config loader
try:
    from config_loader_shared import get_runpod_token, get_config_value
except ImportError:
    print("❌ Could not import config_loader_shared.py")
    print("Please ensure config_loader_shared.py is in the same directory.")
    sys.exit(1)

# Configuration - Load from config.env
try:
    RUNPOD_TOKEN = get_runpod_token()
except ValueError as e:
    print(f"❌ Configuration error: {e}")
    print("📋 Please copy config.env.template to config.env and set your RunPod token.")
    sys.exit(1)

ENDPOINT_ID = get_config_value('RUNPOD_ENDPOINT_ID', 'your-endpoint-id-here')
BASE_URL = f"https://api.runpod.ai/v2/{ENDPOINT_ID}"

def submit_test_job():
    """Submit a simple test job"""
    print("🧪 Submitting simple test job...")
    try:
        payload = {
            "input": {
                "type": "health"
            }
        }
        
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
            return job_id
        else:
            print(f"   ❌ Failed: HTTP {response.status_code}")
            print(f"   Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        return None

def check_job_detailed(job_id):
    """Get detailed job information"""
    print(f"\n🔍 Checking job details: {job_id}")
    try:
        response = requests.get(f"{BASE_URL}/status/{job_id}", 
                              headers={"Authorization": f"Bearer {RUNPOD_TOKEN}"},
                              timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            print(f"   Status: {result.get('status', 'N/A')}")
            print(f"   ID: {result.get('id', 'N/A')}")
            
            # Check for error information
            if 'error' in result:
                print(f"   ❌ Error: {result['error']}")
            
            # Check for worker info
            if 'executionTime' in result:
                print(f"   Execution Time: {result['executionTime']}ms")
            
            if 'output' in result:
                print(f"   Output: {result['output']}")
                
            return result
        else:
            print(f"   ❌ Status check failed: HTTP {response.status_code}")
            print(f"   Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        return None

def get_endpoint_info():
    """Try to get endpoint information"""
    print("\n📊 Trying to get endpoint information...")
    
    # Try different endpoints that might give info
    endpoints_to_try = [
        f"https://api.runpod.ai/v2/{ENDPOINT_ID}",
        f"https://api.runpod.ai/v2/{ENDPOINT_ID}/health",
        f"https://api.runpod.ai/v2/{ENDPOINT_ID}/workers"
    ]
    
    for endpoint in endpoints_to_try:
        try:
            response = requests.get(endpoint, 
                                  headers={"Authorization": f"Bearer {RUNPOD_TOKEN}"},
                                  timeout=10)
            print(f"   {endpoint}: HTTP {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"      Data: {json.dumps(data, indent=2)[:200]}...")
                except:
                    print(f"      Text: {response.text[:200]}...")
                    
        except Exception as e:
            print(f"   {endpoint}: Exception - {e}")

def diagnose_problem():
    """Run comprehensive diagnosis"""
    print("🔧 RunPod Endpoint Diagnostic Tool")
    print(f"🎯 Endpoint: {ENDPOINT_ID}")
    print(f"⏰ Time: {datetime.now()}")
    print("=" * 60)
    
    # Step 1: Submit test job
    job_id = submit_test_job()
    
    if not job_id:
        print("\n💥 CRITICAL: Cannot submit jobs")
        print("🔍 Check:")
        print("   1. Endpoint ID is correct")
        print("   2. API token is valid")
        print("   3. Endpoint exists and is not deleted")
        return
    
    # Step 2: Check job immediately
    time.sleep(2)
    job_info = check_job_detailed(job_id)
    
    # Step 3: Wait and check again
    print("\n⏱️ Waiting 10 seconds then checking again...")
    time.sleep(10)
    job_info_2 = check_job_detailed(job_id)
    
    # Step 4: Try to get endpoint info
    get_endpoint_info()
    
    # Step 5: Analysis
    print("\n" + "=" * 60)
    print("🧠 DIAGNOSTIC ANALYSIS")
    print("=" * 60)
    
    if job_info and job_info_2:
        status_1 = job_info.get('status', 'UNKNOWN')
        status_2 = job_info_2.get('status', 'UNKNOWN')
        
        if status_1 == 'IN_QUEUE' and status_2 == 'IN_QUEUE':
            print("❌ PROBLEM: Jobs stuck in IN_QUEUE")
            print("\n🔧 LIKELY CAUSES:")
            print("   1. No active workers (Min Workers = 0)")
            print("   2. Workers are in EXITED state")
            print("   3. Docker container fails to start")
            print("   4. Resource allocation issues")
            
            print("\n✅ SOLUTIONS:")
            print("   1. Go to RunPod Console → Endpoints → noo81tr4l2422v")
            print("   2. Check 'Workers' tab")
            print("   3. Set 'Min Workers' to 1 or higher")
            print("   4. Check worker logs for errors")
            print("   5. Restart workers if they're in EXITED state")
            print("   6. Verify Docker image is correct:")
            print("      mateoxin/lora-dashboard-backend:v7-runpod-compliant")
            
        elif status_2 in ['COMPLETED', 'FAILED']:
            print("✅ Workers are functional")
            print("⚠️ Previous timeouts may have been temporary")
            
        else:
            print(f"🤔 Unusual behavior: {status_1} → {status_2}")
    
    print("\n📞 IMMEDIATE ACTION REQUIRED:")
    print("   🚨 Check RunPod Console workers status")
    print("   🔄 Restart workers or increase Min Workers")
    print("   📋 Check worker logs for container startup errors")

if __name__ == "__main__":
    diagnose_problem() 
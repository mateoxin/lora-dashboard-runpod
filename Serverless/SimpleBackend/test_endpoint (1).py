#!/usr/bin/env python3
"""
🧪 Quick Test for RTX 3090 Simple Backend Endpoint
Tests the newly deployed endpoint: ig5y0d2g4l5n2k
"""

import requests
import json
import time
from datetime import datetime

# Configuration - Load from config file or use fallback
try:
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'Testing'))
    from config_loader_shared import get_runpod_token, get_config_value
    
    RUNPOD_TOKEN = get_runpod_token()
    ENDPOINT_ID = get_config_value('RUNPOD_ENDPOINT_ID', 'ig5y0d2g4l5n2k')
    print(f"🔑 Loaded config from file - Endpoint: {ENDPOINT_ID}")
except (ImportError, ValueError) as e:
    print(f"⚠️  Could not load config from file: {e}")
    print("💡 Please set RUNPOD_TOKEN in this file for testing")
    ENDPOINT_ID = "ig5y0d2g4l5n2k"
    RUNPOD_TOKEN = "YOUR_RUNPOD_TOKEN_HERE"  # Replace with your actual token
    
    if RUNPOD_TOKEN == "YOUR_RUNPOD_TOKEN_HERE":
        print("❌ Please update RUNPOD_TOKEN in this file or config.env")
        exit(1)

BASE_URL = f"https://api.runpod.ai/v2/{ENDPOINT_ID}"
SYNC_URL = f"{BASE_URL}/runsync"
ASYNC_URL = f"{BASE_URL}/run"

def test_endpoint():
    """Test the RTX 3090 simple backend endpoint."""
    print("🚀 Testing RTX 3090 Simple Backend Endpoint")
    print("=" * 50)
    print(f"📍 Endpoint ID: {ENDPOINT_ID}")
    print(f"🔗 URL: {BASE_URL}")
    print()
    
    headers = {
        "Authorization": f"Bearer {RUNPOD_TOKEN}",
        "Content-Type": "application/json"
    }
    
    tests = [
        {
            "name": "Health Check",
            "payload": {"input": {"type": "health"}},
            "description": "Basic connectivity test"
        },
        {
            "name": "Ping Test", 
            "payload": {"input": {"type": "ping"}},
            "description": "Latency test"
        },
        {
            "name": "Echo Test",
            "payload": {"input": {"type": "echo", "message": "Hello RTX 3090!"}},
            "description": "Data passthrough test"
        },
        {
            "name": "Slow Job Test",
            "payload": {"input": {"type": "slow"}},
            "description": "2-second delay simulation"
        }
    ]
    
    results = []
    
    for i, test in enumerate(tests, 1):
        print(f"🧪 Test {i}: {test['name']}")
        print(f"   {test['description']}")
        
        try:
            start_time = time.time()
            response = requests.post(SYNC_URL, headers=headers, json=test['payload'], timeout=30)
            duration = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                status = result.get('status', 'UNKNOWN')
                output = result.get('output', {})
                
                print(f"   ✅ Status: {status}")
                print(f"   ⏱️  Duration: {duration:.2f}s")
                
                if status == "COMPLETED":
                    print(f"   📄 Output: {json.dumps(output, indent=2)[:200]}...")
                    results.append({"test": test['name'], "status": "PASS", "duration": duration})
                else:
                    print(f"   ⚠️  Unexpected status: {status}")
                    results.append({"test": test['name'], "status": "PARTIAL", "duration": duration})
                    
            else:
                print(f"   ❌ HTTP Error: {response.status_code}")
                print(f"   📄 Response: {response.text[:200]}")
                results.append({"test": test['name'], "status": "FAIL", "duration": duration})
                
        except Exception as e:
            duration = time.time() - start_time
            print(f"   ❌ Error: {str(e)}")
            results.append({"test": test['name'], "status": "ERROR", "duration": duration})
        
        print()
    
    # Summary
    print("📊 TEST SUMMARY")
    print("=" * 30)
    
    passed = sum(1 for r in results if r['status'] == 'PASS')
    total = len(results)
    
    for result in results:
        status_emoji = {"PASS": "✅", "PARTIAL": "⚠️", "FAIL": "❌", "ERROR": "💥"}
        emoji = status_emoji.get(result['status'], "❓")
        print(f"{emoji} {result['test']}: {result['status']} ({result['duration']:.2f}s)")
    
    print()
    print(f"🎯 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! RTX 3090 endpoint is working perfectly!")
    elif passed > 0:
        print("⚠️  Some tests passed. Check partial results above.")
    else:
        print("❌ All tests failed. Check endpoint configuration.")
    
    return results

if __name__ == "__main__":
    test_endpoint() 
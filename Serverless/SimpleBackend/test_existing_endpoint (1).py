#!/usr/bin/env python3
"""
🧪 QUICK TEST OF EXISTING RUNPOD ENDPOINT
Test if the endpoint already has our fixes or needs updating
"""

import requests
import json
import time

# Endpoint z 1 workerem
ENDPOINT_URL = "https://api.runpod.ai/v2/8s9y5exor2uidx/run"
# Endpoint z 4 workerami  
ENDPOINT_URL_4W = "https://api.runpod.ai/v2/rqwaizbda7ucsj/run"

def test_available_types(endpoint_url):
    """Test what job types are available."""
    print(f"🧪 Testing available types on {endpoint_url}")
    
    payload = {
        "input": {
            "type": "unknown_test"
        }
    }
    
    try:
        response = requests.post(endpoint_url, json=payload, timeout=30)
        if response.status_code == 200:
            result = response.json()
            output = result.get("output", {})
            available_types = output.get("available_types", [])
            
            print(f"✅ Available types: {available_types}")
            
            # Check if our new type is there
            if "load_matt_dataset" in available_types:
                print("🎉 NEW TYPE FOUND! Endpoint has our fixes!")
                return True, available_types
            else:
                print("❌ Old endpoint - needs updating")
                return False, available_types
        else:
            print(f"❌ Request failed: {response.status_code}")
            return False, []
    except Exception as e:
        print(f"💥 Exception: {e}")
        return False, []

def test_health_check(endpoint_url):
    """Quick health check."""
    print(f"🏥 Testing health on {endpoint_url}")
    
    payload = {
        "input": {
            "type": "health"
        }
    }
    
    try:
        response = requests.post(endpoint_url, json=payload, timeout=30)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Health check passed")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"💥 Health check exception: {e}")
        return False

def main():
    print("🧪 TESTING EXISTING RUNPOD ENDPOINTS")
    print("=" * 50)
    
    # Test both endpoints
    endpoints = [
        ("1-Worker Endpoint", ENDPOINT_URL),
        ("4-Worker Endpoint", ENDPOINT_URL_4W)
    ]
    
    for name, url in endpoints:
        print(f"\n📡 Testing {name}")
        print(f"🌐 URL: {url}")
        
        # Health check first
        health_ok = test_health_check(url)
        
        if health_ok:
            # Check available types
            has_fixes, types = test_available_types(url)
            
            if has_fixes:
                print(f"✅ {name} has our fixes - ready to test!")
                return url
            else:
                print(f"❌ {name} needs updating")
        else:
            print(f"💀 {name} is not responding")
    
    print("\n❌ No endpoints have our fixes - need to create new template/endpoint")
    return None

if __name__ == "__main__":
    ready_endpoint = main()
    if ready_endpoint:
        print(f"\n🎯 READY TO TEST: {ready_endpoint}")
    else:
        print(f"\n🔧 NEED TO CREATE NEW ENDPOINT")
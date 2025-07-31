#!/usr/bin/env python3
"""
🧪 Quick test script for deployed FastBackend endpoint
Test your RunPod deployment quickly
"""

import requests
import json
import time
import os
from datetime import datetime

def test_endpoint(endpoint_url, api_key):
    """Test FastBackend endpoint with various operations"""
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    print(f"🧪 Testing endpoint: {endpoint_url}")
    print("=" * 60)
    
    # Test 1: Health check (should be instant)
    print("\n1. 🩺 Health Check (instant)")
    test_payload = {"input": {"type": "health"}}
    
    start_time = time.time()
    try:
        response = requests.post(endpoint_url, headers=headers, json=test_payload, timeout=30)
        end_time = time.time()
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Health check passed ({end_time - start_time:.2f}s)")
            print(f"   Status: {result.get('status', 'unknown')}")
            print(f"   Environment ready: {result.get('environment_ready', 'unknown')}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except requests.RequestException as e:
        print(f"❌ Health check error: {e}")
        return False
    
    # Test 2: Ping test
    print("\n2. 🏓 Ping Test")
    test_payload = {"input": {"type": "ping"}}
    
    try:
        response = requests.post(endpoint_url, headers=headers, json=test_payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Ping successful")
            print(f"   Response: {result.get('status', 'unknown')}")
        else:
            print(f"❌ Ping failed: {response.status_code}")
            
    except requests.RequestException as e:
        print(f"❌ Ping error: {e}")
    
    # Test 3: Echo test
    print("\n3. 📢 Echo Test")
    test_payload = {
        "input": {
            "type": "echo",
            "message": "Hello from FastBackend!",
            "timestamp": datetime.now().isoformat()
        }
    }
    
    try:
        response = requests.post(endpoint_url, headers=headers, json=test_payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Echo successful")
            echo_data = result.get('echo', {})
            print(f"   Message: {echo_data.get('message', 'none')}")
        else:
            print(f"❌ Echo failed: {response.status_code}")
            
    except requests.RequestException as e:
        print(f"❌ Echo error: {e}")
    
    # Test 4: Environment setup (will trigger heavy dependency installation)
    print("\n4. 🔧 Environment Setup Test (may take 1-2 minutes)")
    test_payload = {"input": {"type": "setup_environment"}}
    
    start_time = time.time()
    try:
        response = requests.post(endpoint_url, headers=headers, json=test_payload, timeout=300)  # 5 min timeout
        end_time = time.time()
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Environment setup completed ({end_time - start_time:.2f}s)")
            print(f"   Status: {result.get('status', 'unknown')}")
            print(f"   Environment ready: {result.get('environment_ready', 'unknown')}")
        else:
            print(f"❌ Environment setup failed: {response.status_code}")
            print(f"   Error: {response.text}")
            
    except requests.RequestException as e:
        print(f"❌ Environment setup error: {e}")
    
    # Test 5: List models (heavy operation)
    print("\n5. 📋 List Models Test (heavy operation)")
    test_payload = {"input": {"type": "list_models"}}
    
    try:
        response = requests.post(endpoint_url, headers=headers, json=test_payload, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ List models successful")
            models = result.get('models', [])
            print(f"   Found {len(models)} trained models")
        else:
            print(f"❌ List models failed: {response.status_code}")
            
    except requests.RequestException as e:
        print(f"❌ List models error: {e}")
    
    print("\n🎉 Testing complete!")
    return True

def load_test_endpoint(endpoint_url, api_key, num_requests=5):
    """Perform load testing on endpoint"""
    
    print(f"\n🚀 Load Testing ({num_requests} requests)")
    print("=" * 40)
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    test_payload = {"input": {"type": "health"}}
    
    response_times = []
    successful_requests = 0
    
    for i in range(num_requests):
        print(f"Request {i+1}/{num_requests}...", end=" ")
        
        start_time = time.time()
        try:
            response = requests.post(endpoint_url, headers=headers, json=test_payload, timeout=30)
            end_time = time.time()
            response_time = end_time - start_time
            
            if response.status_code == 200:
                print(f"✅ ({response_time:.2f}s)")
                response_times.append(response_time)
                successful_requests += 1
            else:
                print(f"❌ (HTTP {response.status_code})")
                
        except requests.RequestException as e:
            print(f"❌ (Error: {e})")
    
    if response_times:
        avg_time = sum(response_times) / len(response_times)
        min_time = min(response_times)
        max_time = max(response_times)
        
        print(f"\n📊 Load Test Results:")
        print(f"   Successful: {successful_requests}/{num_requests}")
        print(f"   Average time: {avg_time:.2f}s")
        print(f"   Min time: {min_time:.2f}s")
        print(f"   Max time: {max_time:.2f}s")
        print(f"   Success rate: {(successful_requests/num_requests)*100:.1f}%")
    else:
        print("❌ No successful requests")

def get_endpoint_config():
    """Get endpoint configuration from user or environment"""
    
    # Try to get from environment first
    endpoint_id = os.environ.get("RUNPOD_ENDPOINT_ID")
    api_key = os.environ.get("RUNPOD_API_KEY")
    
    if not endpoint_id:
        endpoint_id = input("🆔 Enter RunPod Endpoint ID: ").strip()
    
    if not api_key:
        api_key = input("🔑 Enter RunPod API Key: ").strip()
    
    if not endpoint_id or not api_key:
        print("❌ Missing endpoint ID or API key")
        return None, None
    
    # Construct endpoint URL
    endpoint_url = f"https://api.runpod.ai/v2/{endpoint_id}/run"
    
    return endpoint_url, api_key

def main():
    """Main testing function"""
    
    print("🧪 FastBackend Quick Test Suite")
    print("=" * 60)
    
    # Get configuration
    endpoint_url, api_key = get_endpoint_config()
    
    if not endpoint_url or not api_key:
        print("❌ Configuration error")
        return
    
    print(f"🎯 Testing endpoint: {endpoint_url}")
    
    # Run basic tests
    success = test_endpoint(endpoint_url, api_key)
    
    if success:
        # Ask for load testing
        load_test = input("\n🚀 Run load test? (y/n): ").strip().lower()
        if load_test in ['y', 'yes']:
            load_test_endpoint(endpoint_url, api_key)
    
    print("\n" + "=" * 60)
    print("🏁 Testing complete!")
    
    if success:
        print("✅ Your FastBackend is working correctly!")
        print("🎉 Ready for production use!")
    else:
        print("❌ Some issues detected. Check logs and configuration.")

if __name__ == "__main__":
    main()
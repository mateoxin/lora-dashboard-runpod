#!/usr/bin/env python3
"""
⚡ QUICK ENDPOINT TESTER - Fast test when endpoint is ready
Just checks basic functionality and loads Matt's dataset
"""

import requests
import json
import time

# Updated endpoint URL (when image is deployed)
ENDPOINT_URL = "https://api.runpod.ai/v2/4affl2prg8gabs/run"
API_KEY = "A45WS4QMWCM23AMDBDF60RIANG0B0HS33J5FZ86L"

def quick_test():
    """Quick test of endpoint functionality."""
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    
    print("⚡ QUICK ENDPOINT TEST")
    print("=" * 40)
    
    # Test 1: Health check
    print("\n1️⃣ Testing health endpoint...")
    payload = {"input": {"type": "health"}}
    
    try:
        response = requests.post(ENDPOINT_URL, json=payload, headers=headers, timeout=60)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            output = result.get("output", {})
            worker_id = output.get('worker_id', 'unknown')
            available_types = output.get('available_types', [])
            
            print(f"   ✅ Health OK! Worker: {worker_id}")
            print(f"   Available types: {len(available_types)}")
            
            if 'load_matt_dataset' in available_types:
                print("   ✅ load_matt_dataset available!")
            else:
                print("   ❌ load_matt_dataset NOT found")
                
        else:
            print(f"   ❌ Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Connection error: {e}")
        return False
    
    # Test 2: Load Matt's dataset
    print("\n2️⃣ Testing Matt's dataset loading...")
    payload = {"input": {"type": "load_matt_dataset"}}
    
    try:
        response = requests.post(ENDPOINT_URL, json=payload, headers=headers, timeout=180)
        if response.status_code == 200:
            result = response.json()
            output = result.get("output", {})
            
            if output.get("status") == "success":
                total_images = output.get("total_images", 0)
                training_folder = output.get("training_folder", "")
                
                print(f"   ✅ Dataset loaded successfully!")
                print(f"   Images: {total_images}")
                print(f"   Folder: {training_folder}")
                
                return True
            else:
                print(f"   ❌ Dataset loading failed: {output.get('error', 'Unknown error')}")
                return False
        else:
            print(f"   ❌ Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error loading dataset: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting quick endpoint test...")
    
    success = quick_test()
    
    if success:
        print("\n🎉 ENDPOINT IS WORKING!")
        print("Ready for full training tests.")
    else:
        print("\n❌ ENDPOINT HAS ISSUES")
        print("Check deployment or try again.")
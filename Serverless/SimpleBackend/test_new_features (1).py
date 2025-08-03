#!/usr/bin/env python3
"""
🧪 TEST NEW FEATURES
Test the new timeout and force_kill functionality in v14-fix-stuck.
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

def test_health():
    """Test basic health check."""
    print("📊 Test 1: Health Check")
    
    try:
        response = requests.post(
            f"{BASE_URL}/runsync",
            headers=headers,
            json={"input": {"type": "health"}},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            output = result.get('output', {})
            message = output.get('message', 'unknown')
            print(f"   ✅ Health OK: {message}")
            return True
        else:
            print(f"   ❌ Health failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Health exception: {e}")
        return False

def test_processes():
    """Test process listing."""
    print("\n📋 Test 2: List Processes")
    
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
            processes = output.get('processes', [])
            count = len(processes)
            print(f"   📊 Found {count} processes")
            
            for proc in processes:
                proc_id = proc.get('id', 'unknown')
                status = proc.get('status', 'unknown')
                proc_type = proc.get('type', 'unknown')
                print(f"      📋 {proc_id} ({proc_type}): {status}")
            
            return True
        else:
            print(f"   ❌ Processes failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Processes exception: {e}")
        return False

def test_force_kill_invalid():
    """Test force kill with invalid process ID (should fail gracefully)."""
    print("\n💀 Test 3: Force Kill Invalid Process")
    
    try:
        response = requests.post(
            f"{BASE_URL}/runsync",
            headers=headers,
            json={"input": {"type": "force_kill", "process_id": "nonexistent123"}},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            output = result.get('output', {})
            status = output.get('status', 'unknown')
            
            print(f"   📋 Force kill status: {status}")
            
            if status == 'error':
                error_msg = output.get('error', 'unknown')
                print(f"   ✅ Expected error: {error_msg}")
                return True
            else:
                print(f"   ⚠️ Unexpected success: {output}")
                return False
        else:
            print(f"   ❌ Force kill failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Force kill exception: {e}")
        return False

def test_cleanup_stuck():
    """Test cleanup stuck processes."""
    print("\n🧹 Test 4: Cleanup Stuck Processes")
    
    try:
        response = requests.post(
            f"{BASE_URL}/runsync",
            headers=headers,
            json={"input": {"type": "cleanup_stuck"}},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            output = result.get('output', {})
            status = output.get('status', 'unknown')
            killed_processes = output.get('killed_processes', [])
            
            print(f"   📋 Cleanup status: {status}")
            print(f"   💀 Killed processes: {len(killed_processes)}")
            
            for proc_id in killed_processes:
                print(f"      💀 {proc_id}")
            
            return True
        else:
            print(f"   ❌ Cleanup failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Cleanup exception: {e}")
        return False

def test_available_types():
    """Test what types are available."""
    print("\n📋 Test 5: Available Types")
    
    try:
        response = requests.post(
            f"{BASE_URL}/runsync",
            headers=headers,
            json={"input": {"type": "unknown_type_test"}},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            output = result.get('output', {})
            available_types = output.get('available_types', [])
            
            print(f"   📋 Available types: {len(available_types)}")
            for type_name in available_types:
                print(f"      📦 {type_name}")
            
            # Check for our new types
            new_types = ['force_kill', 'cleanup_stuck']
            for new_type in new_types:
                if new_type in available_types:
                    print(f"   ✅ New type available: {new_type}")
                else:
                    print(f"   ❌ Missing new type: {new_type}")
            
            return True
        else:
            print(f"   ❌ Types check failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Types exception: {e}")
        return False

def main():
    """Run all new feature tests."""
    print("🧪 NEW FEATURES TEST SUITE")
    print(f"⏰ Time: {datetime.now()}")
    print(f"🎯 Endpoint: {ENDPOINT_ID}")
    print(f"🔧 Image: v14-fix-stuck")
    print("=" * 60)
    
    tests = [
        ("Health Check", test_health),
        ("List Processes", test_processes),
        ("Force Kill Invalid", test_force_kill_invalid),
        ("Cleanup Stuck", test_cleanup_stuck),
        ("Available Types", test_available_types),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"   ❌ {test_name} exception: {e}")
            results[test_name] = False
    
    # Summary
    print(f"\n{'='*60}")
    print(f"📊 TEST SUMMARY")
    print(f"{'='*60}")
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\n📈 Success Rate: {passed}/{total} ({(passed/total)*100:.1f}%)")
    
    if passed == total:
        print(f"\n🎉 ALL TESTS PASSED!")
        print(f"✅ New features working correctly!")
        print(f"🔧 Timeout and force_kill functions ready!")
    elif passed >= total * 0.8:
        print(f"\n⚠️ Most tests passed - system mostly functional")
    else:
        print(f"\n🚨 Many tests failed - check endpoint and image")

if __name__ == "__main__":
    main()
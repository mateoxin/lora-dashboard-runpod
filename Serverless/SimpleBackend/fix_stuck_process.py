#!/usr/bin/env python3
"""
💀 FIX STUCK PROCESS
Kill the stuck training process b632986d and test new error handling.
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

def kill_stuck_process():
    """Kill the stuck process b632986d."""
    print("💀 Killing stuck process b632986d...")
    
    try:
        response = requests.post(
            f"{BASE_URL}/runsync",
            headers=headers,
            json={
                "input": {
                    "type": "force_kill",
                    "process_id": "b632986d",
                    "reason": "Stuck process - height/width validation error"
                }
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            output = result.get('output', {})
            
            if output.get('status') == 'success':
                print(f"   ✅ Process killed successfully!")
                print(f"      Process ID: {output.get('process_id')}")
                print(f"      Reason: {output.get('reason')}")
                return True
            else:
                print(f"   ❌ Failed to kill process: {output.get('error', 'unknown')}")
                return False
        else:
            print(f"   ❌ HTTP Error: {response.status_code}")
            print(f"      Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        return False

def cleanup_all_stuck():
    """Clean up all stuck processes."""
    print("\n🧹 Cleaning up all stuck processes...")
    
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
            
            if output.get('status') == 'success':
                killed_count = len(output.get('killed_processes', []))
                killed_list = output.get('killed_processes', [])
                
                print(f"   ✅ Cleanup completed!")
                print(f"      Processes killed: {killed_count}")
                for process_id in killed_list:
                    print(f"         💀 {process_id}")
                return True
            else:
                print(f"   ❌ Cleanup failed: {output.get('error', 'unknown')}")
                return False
        else:
            print(f"   ❌ HTTP Error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        return False

def check_status_after_fix():
    """Check status after killing stuck processes."""
    print("\n📊 Checking status after fix...")
    
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
            
            if output.get('status') == 'success':
                processes = output.get('processes', [])
                print(f"   📋 Found {len(processes)} processes:")
                
                for process in processes:
                    process_id = process.get('id', 'unknown')
                    status = process.get('status', 'unknown')
                    process_type = process.get('type', 'unknown')
                    
                    print(f"      📋 {process_id} ({process_type}): {status}")
                
                return processes
            else:
                print(f"   ❌ Failed to get processes: {output.get('error', 'unknown')}")
                return []
        else:
            print(f"   ❌ HTTP Error: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        return []

def main():
    """Fix stuck process and verify."""
    print("💀 FIX STUCK PROCESS")
    print(f"⏰ Time: {datetime.now()}")
    print(f"🎯 Endpoint: {ENDPOINT_ID}")
    print("=" * 60)
    
    # Step 1: Kill specific stuck process
    success1 = kill_stuck_process()
    
    # Step 2: Clean up any other stuck processes
    success2 = cleanup_all_stuck()
    
    # Step 3: Check final status
    processes = check_status_after_fix()
    
    # Summary
    print(f"\n{'='*60}")
    print(f"📊 FIX SUMMARY")
    print(f"{'='*60}")
    print(f"💀 Process b632986d killed: {'Yes' if success1 else 'No'}")
    print(f"🧹 Cleanup completed: {'Yes' if success2 else 'No'}")
    print(f"📋 Active processes: {len(processes)}")
    
    running_count = len([p for p in processes if p.get('status') == 'running'])
    
    if running_count == 0:
        print(f"\n🎉 SUCCESS!")
        print(f"   ✅ No more stuck processes")
        print(f"   🔧 Error handling improvements deployed")
        print(f"   💡 Ready for new training attempts")
    else:
        print(f"\n⚠️ STILL ISSUES:")
        print(f"   🔄 {running_count} processes still running")
        print(f"   💡 May need manual intervention")

if __name__ == "__main__":
    main()
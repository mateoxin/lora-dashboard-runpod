#!/usr/bin/env python3
"""
🐳 TEST DOCKER IMAGE LOKALNIE
Sprawdź czy Docker image działa przed deployment na RunPod
"""

import subprocess
import time
import requests

def test_docker_locally():
    print("🐳 Testing Docker Image Locally")
    print("=" * 40)
    
    image = "mateoxin/lora-dashboard-backend:v7-runpod-compliant"
    container_name = "lora-test"
    
    # Step 1: Pull image
    print("1️⃣ Pulling Docker image...")
    try:
        result = subprocess.run(
            ["docker", "pull", image], 
            capture_output=True, 
            text=True, 
            timeout=300
        )
        
        if result.returncode == 0:
            print("   ✅ Image pulled successfully")
        else:
            print(f"   ❌ Pull failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"   ❌ Pull error: {e}")
        return False
    
    # Step 2: Stop any existing container
    print("2️⃣ Cleaning up old containers...")
    subprocess.run(["docker", "rm", "-f", container_name], capture_output=True)
    
    # Step 3: Run container
    print("3️⃣ Starting container...")
    try:
        result = subprocess.run([
            "docker", "run", "-d", 
            "--name", container_name,
            "-p", "8000:8000",
            "-e", "RUNPOD_SERVERLESS=true",
            image
        ], capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            container_id = result.stdout.strip()
            print(f"   ✅ Container started: {container_id[:12]}")
        else:
            print(f"   ❌ Start failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"   ❌ Start error: {e}")
        return False
    
    # Step 4: Wait for startup
    print("4️⃣ Waiting for container startup...")
    time.sleep(10)
    
    # Step 5: Check container status
    print("5️⃣ Checking container status...")
    try:
        result = subprocess.run(
            ["docker", "ps", "--filter", f"name={container_name}", "--format", "table {{.Status}}"],
            capture_output=True, text=True
        )
        
        if "Up" in result.stdout:
            print("   ✅ Container is running")
        else:
            print("   ❌ Container stopped")
            
            # Get logs
            logs_result = subprocess.run(
                ["docker", "logs", container_name],
                capture_output=True, text=True
            )
            print(f"   📋 Logs: {logs_result.stdout}")
            print(f"   📋 Errors: {logs_result.stderr}")
            return False
            
    except Exception as e:
        print(f"   ❌ Status check error: {e}")
        return False
    
    # Step 6: Test HTTP endpoint
    print("6️⃣ Testing HTTP endpoint...")
    try:
        response = requests.get("http://localhost:8000/health", timeout=10)
        if response.status_code == 200:
            print("   ✅ HTTP endpoint working")
        else:
            print(f"   ❌ HTTP failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ HTTP error: {e}")
        return False
    
    # Step 7: Cleanup
    print("7️⃣ Cleaning up...")
    subprocess.run(["docker", "rm", "-f", container_name], capture_output=True)
    
    print("\n🎉 DOCKER IMAGE WORKS LOCALLY!")
    print("✅ Problem is with RunPod configuration, not the image")
    return True

if __name__ == "__main__":
    success = test_docker_locally()
    
    if success:
        print("\n💡 RECOMMENDATION:")
        print("   Docker image is fine - create new RunPod endpoint")
        print("   with increased resources (15GB disk, 12GB RAM)")
    else:
        print("\n🚨 DOCKER IMAGE HAS ISSUES")
        print("   Need to fix the container before RunPod deployment") 
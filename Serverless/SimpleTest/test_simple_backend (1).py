#!/usr/bin/env python3
"""
🧪 TESTY DLA SIMPLE BACKEND
Prostą testy dla minimalnego RunPod backendu
"""

import requests
import time
import json
from datetime import datetime

class SimpleBackendTester:
    def __init__(self, endpoint_id, runpod_token):
        self.endpoint_id = endpoint_id
        self.runpod_token = runpod_token
        self.base_url = f"https://api.runpod.ai/v2/{endpoint_id}"
        
        self.headers = {
            "Authorization": f"Bearer {runpod_token}",
            "Content-Type": "application/json"
        }
        
        self.results = []
    
    def log_result(self, test_name, success, message, data=None):
        """Log test result"""
        result = {
            "test": test_name,
            "success": success,
            "message": message,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
        self.results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"   {test_name}: {status} - {message}")
        
        return success
    
    def submit_job(self, job_type, extra_data=None):
        """Submit job to RunPod"""
        payload = {
            "input": {
                "type": job_type
            }
        }
        
        if extra_data:
            payload["input"].update(extra_data)
        
        try:
            response = requests.post(f"{self.base_url}/run", 
                                   json=payload, 
                                   headers=self.headers, 
                                   timeout=10)
            
            if response.status_code == 200:
                return response.json()
            else:
                return None
                
        except Exception as e:
            print(f"   ❌ Submit error: {e}")
            return None
    
    def wait_for_job(self, job_id, max_wait=30):
        """Wait for job completion"""
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            try:
                response = requests.get(f"{self.base_url}/status/{job_id}", 
                                      headers=self.headers, 
                                      timeout=10)
                
                if response.status_code == 200:
                    status_data = response.json()
                    status = status_data.get("status")
                    
                    if status == "COMPLETED":
                        return status_data.get("output")
                    elif status == "FAILED":
                        return {"error": status_data.get("error", "Job failed")}
                    elif status in ["IN_QUEUE", "IN_PROGRESS"]:
                        time.sleep(2)
                        continue
                    else:
                        return {"error": f"Unknown status: {status}"}
                else:
                    return {"error": f"Status check failed: {response.status_code}"}
                    
            except Exception as e:
                return {"error": f"Status check error: {e}"}
        
        return {"error": "Timeout waiting for job"}
    
    def test_endpoint_health(self):
        """Test if endpoint is accessible"""
        print("🔍 Testing endpoint health...")
        
        try:
            response = requests.get(f"{self.base_url}/health", 
                                  headers=self.headers, 
                                  timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                workers = data.get("workers", {})
                ready_workers = workers.get("ready", 0)
                
                if ready_workers > 0:
                    return self.log_result("endpoint_health", True, 
                                         f"Endpoint healthy, {ready_workers} workers ready", data)
                else:
                    return self.log_result("endpoint_health", False, 
                                         "No ready workers", data)
            else:
                return self.log_result("endpoint_health", False, 
                                     f"Health check failed: {response.status_code}")
                
        except Exception as e:
            return self.log_result("endpoint_health", False, f"Health check error: {e}")
    
    def test_health_job(self):
        """Test health job type"""
        print("🩺 Testing health job...")
        
        job_data = self.submit_job("health")
        if not job_data:
            return self.log_result("health_job", False, "Failed to submit health job")
        
        job_id = job_data.get("id")
        if not job_id:
            return self.log_result("health_job", False, "No job ID returned")
        
        output = self.wait_for_job(job_id)
        
        if "error" in output:
            return self.log_result("health_job", False, f"Job failed: {output['error']}")
        
        if output.get("status") == "healthy":
            return self.log_result("health_job", True, "Health job completed successfully", output)
        else:
            return self.log_result("health_job", False, f"Unexpected health response: {output}")
    
    def test_ping_job(self):
        """Test ping job type"""
        print("🏓 Testing ping job...")
        
        job_data = self.submit_job("ping")
        if not job_data:
            return self.log_result("ping_job", False, "Failed to submit ping job")
        
        job_id = job_data.get("id")
        output = self.wait_for_job(job_id)
        
        if "error" in output:
            return self.log_result("ping_job", False, f"Job failed: {output['error']}")
        
        if output.get("status") == "pong":
            return self.log_result("ping_job", True, "Ping job completed successfully", output)
        else:
            return self.log_result("ping_job", False, f"Unexpected ping response: {output}")
    
    def test_echo_job(self):
        """Test echo job type"""
        print("🔄 Testing echo job...")
        
        test_data = {
            "message": "Hello Simple Backend!",
            "number": 42,
            "array": [1, 2, 3],
            "nested": {"key": "value"}
        }
        
        job_data = self.submit_job("echo", test_data)
        if not job_data:
            return self.log_result("echo_job", False, "Failed to submit echo job")
        
        job_id = job_data.get("id")
        output = self.wait_for_job(job_id)
        
        if "error" in output:
            return self.log_result("echo_job", False, f"Job failed: {output['error']}")
        
        echo_data = output.get("echo", {})
        
        # Check if echo contains our test data
        if (echo_data.get("message") == test_data["message"] and 
            echo_data.get("number") == test_data["number"]):
            return self.log_result("echo_job", True, "Echo job completed successfully", output)
        else:
            return self.log_result("echo_job", False, f"Echo data mismatch: {echo_data}")
    
    def test_slow_job(self):
        """Test slow job type"""
        print("🐌 Testing slow job...")
        
        start_time = time.time()
        job_data = self.submit_job("slow")
        if not job_data:
            return self.log_result("slow_job", False, "Failed to submit slow job")
        
        job_id = job_data.get("id")
        output = self.wait_for_job(job_id, max_wait=15)  # Give extra time
        
        duration = time.time() - start_time
        
        if "error" in output:
            return self.log_result("slow_job", False, f"Job failed: {output['error']}")
        
        if output.get("status") == "completed" and duration >= 2:
            return self.log_result("slow_job", True, 
                                 f"Slow job completed in {duration:.1f}s", output)
        else:
            return self.log_result("slow_job", False, 
                                 f"Slow job issue - duration: {duration:.1f}s, output: {output}")
    
    def test_unknown_job(self):
        """Test unknown job type"""
        print("❓ Testing unknown job type...")
        
        job_data = self.submit_job("nonexistent_type")
        if not job_data:
            return self.log_result("unknown_job", False, "Failed to submit unknown job")
        
        job_id = job_data.get("id")
        output = self.wait_for_job(job_id)
        
        if "error" in output:
            return self.log_result("unknown_job", False, f"Job failed: {output['error']}")
        
        if (output.get("status") == "unknown_type" and 
            "available_types" in output):
            return self.log_result("unknown_job", True, 
                                 "Unknown job handled correctly", output)
        else:
            return self.log_result("unknown_job", False, 
                                 f"Unexpected unknown job response: {output}")
    
    def run_all_tests(self):
        """Run comprehensive test suite"""
        print("🧪 Simple Backend Test Suite")
        print(f"🎯 Endpoint: {self.endpoint_id}")
        print(f"⏰ Start: {datetime.now()}")
        print("=" * 50)
        
        # Run tests
        tests = [
            self.test_endpoint_health,
            self.test_health_job,
            self.test_ping_job,
            self.test_echo_job,
            self.test_slow_job,
            self.test_unknown_job
        ]
        
        passed = 0
        for test in tests:
            if test():
                passed += 1
        
        # Summary
        total = len(tests)
        failed = total - passed
        success_rate = (passed / total) * 100
        
        print("\n" + "=" * 50)
        print("📊 TEST SUMMARY")
        print("=" * 50)
        print(f"✅ Passed: {passed}/{total}")
        print(f"❌ Failed: {failed}/{total}")
        print(f"📈 Success Rate: {success_rate:.1f}%")
        
        if passed == total:
            print("\n🎉 ALL TESTS PASSED!")
            print("✅ Simple backend is fully functional")
        elif passed >= total * 0.5:
            print("\n⚠️ Most tests passed - minor issues")
        else:
            print("\n🚨 Many tests failed - major problems")
        
        return self.results

def main():
    # Configuration - Load from config file
    try:
        from config_loader_shared import get_runpod_token, get_config_value
        RUNPOD_TOKEN = get_runpod_token()
        ENDPOINT_ID = get_config_value('RUNPOD_ENDPOINT_ID', 'ig5y0d2g4l5n2k')
    except ImportError:
        print("❌ Could not import config_loader_shared.py")
        ENDPOINT_ID = "ig5y0d2g4l5n2k"  # Fallback to our new endpoint
        RUNPOD_TOKEN = "YOUR_RUNPOD_TOKEN_HERE"  # Replace with your actual token
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        return
    
    if ENDPOINT_ID in ["UPDATE_ME", "your_endpoint_id_here"]:
        print("❌ Please update ENDPOINT_ID in config.env file")
        print(f"💡 Current endpoint ID should be: ig5y0d2g4l5n2k")
        return
    
    print(f"🎯 Testing endpoint: {ENDPOINT_ID}")
    
    tester = SimpleBackendTester(ENDPOINT_ID, RUNPOD_TOKEN)
    results = tester.run_all_tests()
    
    # Save results
    with open("simple_test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n💾 Results saved to: simple_test_results.json")

if __name__ == "__main__":
    main() 
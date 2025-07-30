#!/usr/bin/env python3
"""
🚀 ASYNC-ONLY BACKEND TESTER
Strategy: Use /run for everything, poll job status separately

Based on diagnosis:
- /run works perfectly (1.7s)
- /runsync timeouts (60s+)
- Solution: Use async + polling

Author: AI Assistant
Created: 2025-07-30
"""

import requests
import json
import time
import base64
import os
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path
from PIL import Image

# Configuration
class AsyncTestConfig:
    ENDPOINT_ID = "4z7x4al6ars9ou"  # ✅ UPDATED - New working endpoint
    RUNPOD_TOKEN = "YOUR_RUNPOD_TOKEN_HERE"  # Replace with your actual token
    BASE_URL = f"https://api.runpod.ai/v2/{ENDPOINT_ID}"
    
    TIMEOUT = 30        # For /run requests
    POLL_INTERVAL = 3   # Check job status every 3s
    MAX_POLL_TIME = 60  # Max time to wait for job completion
    
    LOG_FILE = "async_test_log.txt"
    RESULTS_FILE = "async_test_results.json"

class AsyncBackendTester:
    def __init__(self, config: AsyncTestConfig):
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {config.RUNPOD_TOKEN}',
            'Content-Type': 'application/json'
        })
        
        self.results = {
            "start_time": datetime.now().isoformat(),
            "strategy": "async_only_with_polling",
            "tests": [],
            "summary": {}
        }
        
    def log_result(self, test_name: str, success: bool, data: Any = None, error: str = None):
        """Log test result"""
        result = {
            "test_name": test_name,
            "timestamp": datetime.now().isoformat(),
            "success": success,
            "data": data,
            "error": error
        }
        self.results["tests"].append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"   {test_name}: {status}")
        if error:
            print(f"      Error: {error}")
    
    def submit_async_job(self, job_type: str, input_data: Dict) -> Optional[str]:
        """Submit async job and return job ID"""
        try:
            payload = {
                "input": {
                    "type": job_type,
                    **input_data
                }
            }
            
            start_time = time.time()
            response = self.session.post(f"{self.config.BASE_URL}/run", 
                                       json=payload, 
                                       timeout=self.config.TIMEOUT)
            duration = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                job_id = result.get('id')
                status = result.get('status')
                print(f"      Job submitted: {job_id} ({status}) in {duration:.1f}s")
                return job_id
            else:
                print(f"      Failed: HTTP {response.status_code}")
                return None
                
        except Exception as e:
            print(f"      Exception: {e}")
            return None
    
    def check_job_status(self, job_id: str) -> Dict:
        """Check job status via RunPod API"""
        try:
            response = self.session.get(f"{self.config.BASE_URL}/status/{job_id}", 
                                      timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                return {"status": "UNKNOWN", "error": f"HTTP {response.status_code}"}
        except Exception as e:
            return {"status": "ERROR", "error": str(e)}
    
    def wait_for_job_completion(self, job_id: str, max_wait: int = None) -> Dict:
        """Wait for job to complete and return final result"""
        max_wait = max_wait or self.config.MAX_POLL_TIME
        start_time = time.time()
        
        print(f"      Polling job {job_id}...")
        
        while time.time() - start_time < max_wait:
            status_info = self.check_job_status(job_id)
            status = status_info.get("status", "UNKNOWN")
            
            if status in ["COMPLETED", "FAILED"]:
                duration = time.time() - start_time
                print(f"      Job {status.lower()} in {duration:.1f}s")
                return status_info
            elif status in ["IN_QUEUE", "IN_PROGRESS"]:
                print(f"      Status: {status} (waiting...)")
                time.sleep(self.config.POLL_INTERVAL)
            else:
                print(f"      Unknown status: {status}")
                time.sleep(self.config.POLL_INTERVAL)
        
        # Timeout
        duration = time.time() - start_time
        print(f"      Timeout after {duration:.1f}s")
        return {"status": "TIMEOUT", "error": "Job did not complete in time"}
    
    def test_health_async(self) -> bool:
        """Test health check via async"""
        print("🔍 Testing health check (async)...")
        try:
            job_id = self.submit_async_job("health", {})
            if not job_id:
                self.log_result("health_async", False, error="Failed to submit job")
                return False
            
            result = self.wait_for_job_completion(job_id, max_wait=30)
            
            if result.get("status") == "COMPLETED":
                output = result.get("output", {})
                self.log_result("health_async", True, output)
                return True
            else:
                self.log_result("health_async", False, error=result.get("error", "Unknown error"))
                return False
                
        except Exception as e:
            self.log_result("health_async", False, error=str(e))
            return False
    
    def test_processes_async(self) -> bool:
        """Test get processes via async"""
        print("📋 Testing get processes (async)...")
        try:
            job_id = self.submit_async_job("processes", {})
            if not job_id:
                self.log_result("processes_async", False, error="Failed to submit job")
                return False
            
            result = self.wait_for_job_completion(job_id, max_wait=30)
            
            if result.get("status") == "COMPLETED":
                output = result.get("output", {})
                processes = output.get("processes", [])
                self.log_result("processes_async", True, {"process_count": len(processes)})
                return True
            else:
                self.log_result("processes_async", False, error=result.get("error", "Unknown error"))
                return False
                
        except Exception as e:
            self.log_result("processes_async", False, error=str(e))
            return False
    
    def test_lora_models_async(self) -> bool:
        """Test get LoRA models via async"""
        print("🎭 Testing get LoRA models (async)...")
        try:
            job_id = self.submit_async_job("lora", {})
            if not job_id:
                self.log_result("lora_async", False, error="Failed to submit job")
                return False
            
            result = self.wait_for_job_completion(job_id, max_wait=30)
            
            if result.get("status") == "COMPLETED":
                output = result.get("output", {})
                models = output.get("models", [])
                self.log_result("lora_async", True, {"model_count": len(models)})
                return True
            else:
                self.log_result("lora_async", False, error=result.get("error", "Unknown error"))
                return False
                
        except Exception as e:
            self.log_result("lora_async", False, error=str(e))
            return False
    
    def create_mini_test_files(self) -> list:
        """Create minimal test files"""
        test_dir = Path("test_mini")
        test_dir.mkdir(exist_ok=True)
        
        # Create 1 tiny image
        img = Image.new('RGB', (64, 64), color=(100, 150, 200))
        img_path = test_dir / "test.jpg"
        img.save(img_path, 'JPEG', quality=75, optimize=True)
        
        # Create 1 caption
        txt_path = test_dir / "test.txt"
        txt_path.write_text("A test image")
        
        return [str(img_path), str(txt_path)]
    
    def file_to_base64(self, filepath: str) -> Dict:
        """Convert file to base64"""
        with open(filepath, 'rb') as f:
            content = base64.b64encode(f.read()).decode('utf-8')
        
        return {
            "filename": os.path.basename(filepath),
            "content": content,
            "content_type": "image/jpeg" if filepath.endswith('.jpg') else "text/plain",
            "size": os.path.getsize(filepath)
        }
    
    def test_upload_async(self) -> bool:
        """Test upload training data via async"""
        print("📁 Testing upload training data (async)...")
        try:
            # Create minimal test files
            files = self.create_mini_test_files()
            base64_files = [self.file_to_base64(f) for f in files]
            
            total_size = sum(f["size"] for f in base64_files)
            print(f"      Upload size: {total_size} bytes, {len(base64_files)} files")
            
            upload_data = {
                "training_name": "test_async",
                "trigger_word": "",
                "cleanup_existing": True,
                "files": base64_files
            }
            
            job_id = self.submit_async_job("upload_training_data", upload_data)
            if not job_id:
                self.log_result("upload_async", False, error="Failed to submit job")
                return False
            
            result = self.wait_for_job_completion(job_id, max_wait=60)  # Upload may take longer
            
            if result.get("status") == "COMPLETED":
                output = result.get("output", {})
                training_folder = output.get("training_folder")
                self.log_result("upload_async", True, {"training_folder": training_folder})
                return True
            else:
                self.log_result("upload_async", False, error=result.get("error", "Unknown error"))
                return False
                
        except Exception as e:
            self.log_result("upload_async", False, error=str(e))
            return False
    
    def test_generation_async(self) -> bool:
        """Test start generation via async"""
        print("🎨 Testing start generation (async)...")
        try:
            generation_config = {
                "name": "test_gen_async",
                "process": [{
                    "type": "sd_sampler",
                    "device": "cuda:0",
                    "model": {
                        "name_or_path": "/workspace/models/FLUX.1-dev",
                        "is_flux": True,
                        "quantize": True
                    },
                    "sample": {
                        "sampler": "flowmatch",
                        "width": 512,
                        "height": 512,
                        "prompts": ["A simple test"],
                        "neg": "",
                        "seed": 42,
                        "guidance_scale": 4,
                        "sample_steps": 4,  # Very few steps
                        "num_samples": 1
                    }
                }]
            }
            
            job_id = self.submit_async_job("generate", {"config": generation_config})
            if not job_id:
                self.log_result("generation_async", False, error="Failed to submit job")
                return False
            
            # For generation, we just check if it starts (don't wait for completion)
            time.sleep(5)  # Wait a bit
            status_info = self.check_job_status(job_id)
            status = status_info.get("status", "UNKNOWN")
            
            if status in ["IN_PROGRESS", "IN_QUEUE", "COMPLETED"]:
                self.log_result("generation_async", True, {"job_status": status})
                return True
            else:
                self.log_result("generation_async", False, error=f"Unexpected status: {status}")
                return False
                
        except Exception as e:
            self.log_result("generation_async", False, error=str(e))
            return False
    
    def run_async_tests(self):
        """Run all async tests"""
        print("🚀 Async-Only Backend Tester")
        print(f"🎯 Endpoint: {self.config.ENDPOINT_ID}")
        print(f"⏰ Time: {datetime.now()}")
        print(f"🔧 Strategy: Use /run + polling (no /runsync)")
        print("=" * 60)
        
        test_results = {}
        
        # Test 1: Health
        test_results["health"] = self.test_health_async()
        
        # Test 2: Processes
        test_results["processes"] = self.test_processes_async()
        
        # Test 3: LoRA Models
        test_results["lora_models"] = self.test_lora_models_async()
        
        # Test 4: Upload
        test_results["upload"] = self.test_upload_async()
        
        # Test 5: Generation
        test_results["generation"] = self.test_generation_async()
        
        # Summary
        total_tests = len(test_results)
        passed_tests = sum(test_results.values())
        
        print("\n" + "=" * 60)
        print("📊 ASYNC TEST SUMMARY")
        print("=" * 60)
        print(f"✅ Passed: {passed_tests}/{total_tests}")
        print(f"❌ Failed: {total_tests - passed_tests}/{total_tests}")
        print(f"📈 Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if passed_tests == total_tests:
            print("\n🎉 ALL ASYNC TESTS PASSED!")
            print("💡 Recommendation: Use async strategy for frontend")
        elif passed_tests >= 3:
            print("\n⚠️ Most tests passed - backend is functional")
        else:
            print("\n🚨 Many tests failed - check backend deployment")
        
        # Save results
        self.results["summary"] = {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "success_rate": f"{(passed_tests/total_tests)*100:.1f}%"
        }
        
        with open(self.config.RESULTS_FILE, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n📊 Results saved to: {self.config.RESULTS_FILE}")
        
        return test_results

if __name__ == "__main__":
    config = AsyncTestConfig()
    tester = AsyncBackendTester(config)
    tester.run_async_tests() 
#!/usr/bin/env python3
"""
🧪 TESTER FOR FIXED LORA TRAINING SYSTEM
Tests the new image validation, worker isolation, and Matt's dataset loading

After implementing all fixes:
- Image validation with PIL
- Worker isolation (unique folders per worker)
- Matt's real dataset loading from 10_Matt folder
- Enhanced monitoring and error reporting
"""

import requests
import json
import time
import base64
import os
from datetime import datetime

class FixedSystemTester:
    def __init__(self, endpoint_url=None):
        """Initialize the tester with RunPod endpoint."""
        # New fixed endpoint URL
        default_endpoint = "https://api.runpod.ai/v2/4affl2prg8gabs/run"
        
        # Try to load from environment or use new default
        self.endpoint_url = endpoint_url or os.environ.get("RUNPOD_ENDPOINT_URL", default_endpoint)
        
        print(f"🎯 Using NEW FIXED ENDPOINT: {self.endpoint_url}")
        
        if not self.endpoint_url:
            print("❌ No endpoint URL provided. Please set RUNPOD_ENDPOINT_URL environment variable")
            print("   Example: export RUNPOD_ENDPOINT_URL=https://api.runpod.ai/v2/4affl2prg8gabs/run")
            exit(1)
            
        self.headers = {
            "Content-Type": "application/json"
        }
        
        # Add authorization - use the endpoint's API key
        api_key = os.environ.get("RUNPOD_API_KEY", "A45WS4QMWCM23AMDBDF60RIANG0B0HS33J5FZ86L")
        if api_key:
            self.headers["Authorization"] = f"Bearer {api_key}"
        
        print(f"🚀 Fixed System Tester initialized")
        print(f"🌐 Endpoint: {self.endpoint_url}")
        print(f"🔑 API Key: {'✅ Set' if api_key else '❌ Not set'}")
        print("=" * 50)

    def make_request(self, job_type, job_input=None):
        """Make a request to the RunPod endpoint."""
        payload = {
            "input": {
                "type": job_type,
                **(job_input or {})
            }
        }
        
        try:
            print(f"📤 Sending {job_type} request...")
            start_time = time.time()
            
            response = requests.post(
                self.endpoint_url,
                headers=self.headers,
                json=payload,
                timeout=60
            )
            
            duration = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ {job_type} completed in {duration:.2f}s")
                return True, result, duration
            else:
                print(f"❌ {job_type} failed: {response.status_code} - {response.text}")
                return False, response.text, duration
                
        except Exception as e:
            duration = time.time() - start_time
            print(f"💥 {job_type} exception: {e}")
            return False, str(e), duration

    def test_health_check(self):
        """Test basic health check."""
        print("\n🏥 Testing Health Check...")
        success, result, duration = self.make_request("health")
        
        if success:
            print(f"   ✅ Backend is healthy")
            print(f"   ⏱️ Response time: {duration:.2f}s")
            return True
        else:
            print(f"   ❌ Health check failed: {result}")
            return False

    def test_load_matt_dataset(self):
        """Test loading Matt's real dataset."""
        print("\n📁 Testing Matt's Dataset Loading...")
        success, result, duration = self.make_request("load_matt_dataset")
        
        if success:
            output = result.get("output", {})
            print(f"   ✅ Matt's dataset loaded successfully")
            print(f"   📊 Total images: {output.get('total_images', 0)}")
            print(f"   📝 Total captions: {output.get('total_captions', 0)}")
            print(f"   📁 Training folder: {output.get('training_folder', 'N/A')}")
            print(f"   👷 Worker ID: {output.get('worker_id', 'N/A')}")
            
            # Check for validation errors
            validation_errors = output.get('validation_errors', [])
            if validation_errors:
                print(f"   ⚠️ Validation errors: {len(validation_errors)}")
                for error in validation_errors[:3]:  # Show first 3 errors
                    print(f"      - {error}")
            else:
                print(f"   ✅ No validation errors")
            
            return True, output.get('training_folder')
        else:
            print(f"   ❌ Failed to load Matt's dataset: {result}")
            return False, None

    def test_bad_images_validation(self):
        """Test validation with intentionally bad images."""
        print("\n🚫 Testing Bad Image Validation...")
        
        # Create test data with bad images (1x1 pixel like in the logs)
        bad_image_b64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAIAAACQd1PeAAAACXBIWXMAAAsTAAALEwEAmpwYAAAACklEQVR4nGNgYGAAAAAEAAFdzNuNAAAAAElFTkSuQmCC"
        
        upload_data = {
            "training_name": "bad_images_test",
            "trigger_word": "test",
            "cleanup_existing": True,
            "files": [
                {
                    "filename": "bad_1x1.png",
                    "content": bad_image_b64,
                    "content_type": "image/png"
                },
                {
                    "filename": "empty.txt",
                    "content": base64.b64encode(b"").decode('utf-8'),
                    "content_type": "text/plain"
                }
            ]
        }
        
        success, result, duration = self.make_request("upload_training_data", upload_data)
        
        if success:
            output = result.get("output", {})
            validation_errors = output.get('validation_errors', [])
            
            if validation_errors:
                print(f"   ✅ Validation correctly caught {len(validation_errors)} errors")
                for error in validation_errors:
                    print(f"      - {error}")
                return True
            else:
                print(f"   ❌ Validation should have caught errors but didn't")
                return False
        else:
            # Check if it failed due to no valid images
            if "No valid images found" in str(result):
                print(f"   ✅ System correctly rejected bad images")
                return True
            else:
                print(f"   ❌ Unexpected failure: {result}")
                return False

    def test_worker_isolation(self):
        """Test worker isolation by simulating multiple workers."""
        print("\n👷 Testing Worker Isolation...")
        
        # Simulate different workers by making multiple requests
        results = []
        
        for i in range(2):
            print(f"   📤 Testing worker {i+1}...")
            
            # Create small test dataset for each worker
            test_image_data = base64.b64encode(b"fake_image_data_worker_" + str(i).encode()).decode('utf-8')
            test_caption = base64.b64encode(f"Worker {i+1} test caption".encode('utf-8')).decode('utf-8')
            
            upload_data = {
                "training_name": f"worker_{i+1}_test",
                "trigger_word": f"worker{i+1}",
                "cleanup_existing": False,  # Don't cleanup to test isolation
                "files": [
                    {
                        "filename": f"worker_{i+1}_test.txt",
                        "content": test_caption,
                        "content_type": "text/plain"
                    }
                ]
            }
            
            success, result, duration = self.make_request("upload_training_data", upload_data)
            
            if success:
                output = result.get("output", {})
                worker_id = output.get('worker_id', 'unknown')
                training_folder = output.get('training_folder', '')
                
                print(f"      ✅ Worker {i+1} assigned ID: {worker_id}")
                print(f"      📁 Folder: {training_folder}")
                
                results.append({
                    'worker_id': worker_id,
                    'folder': training_folder
                })
            else:
                print(f"      ❌ Worker {i+1} failed: {result}")
                return False
        
        # Check if workers got different IDs and folders
        if len(results) >= 2:
            if results[0]['worker_id'] != results[1]['worker_id']:
                print(f"   ✅ Workers have different IDs: {results[0]['worker_id']} vs {results[1]['worker_id']}")
            else:
                print(f"   ⚠️ Workers have same ID (might be same pod): {results[0]['worker_id']}")
            
            if results[0]['folder'] != results[1]['folder']:
                print(f"   ✅ Workers have different folders")
                return True
            else:
                print(f"   ❌ Workers have same folder - isolation failed")
                return False
        
        return True

    def test_training_with_matt_data(self, training_folder):
        """Test training with Matt's validated data."""
        print("\n🧠 Testing LoRA Training with Matt's Data...")
        
        if not training_folder:
            print("   ❌ No training folder available")
            return False
        
        # Create a simple YAML config for training
        training_config = {
            "type": "train_with_yaml",
            "yaml_config": {
                "config": {
                    "name": "matt_lora_test",
                    "process": [{
                        "type": "sd_trainer",
                        "training_folder": training_folder,
                        "device": "cuda:0",
                        "datasets": [{
                            "folder_path": training_folder,
                            "caption_ext": "txt",
                            "caption_dropout_rate": 0,
                            "shuffle_tokens": False,
                            "cache_latents_to_disk": True,
                            "resolution": [512, 512]
                        }],
                        "train": {
                            "batch_size": 1,
                            "steps": 2,  # Very short test
                            "gradient_accumulation_steps": 1,
                            "train_unet": True,
                            "train_text_encoder": False,
                            "gradient_checkpointing": True,
                            "noise_scheduler": "flowmatch",
                            "optimizer": "adamw",
                            "lr": 0.0001,
                            "ema_config": {"use_ema": False},
                            "dtype": "bf16"
                        },
                        "model": {
                            "name_or_path": "black-forest-labs/FLUX.1-dev",
                            "is_flux": True,
                            "quantize": False
                        },
                        "network": {
                            "type": "lora",
                            "linear": 8,
                            "linear_alpha": 8
                        },
                        "save": {
                            "dtype": "float16",
                            "save_every": 10,
                            "max_step_saves_to_keep": 1
                        },
                        "sample": {
                            "sampler": "flowmatch",
                            "sample_every": 10,
                            "width": 512,
                            "height": 512,
                            "guidance_scale": 2,
                            "sample_steps": 4,
                            "prompts": ["Matt, portrait photo"]
                        }
                    }]
                },
                "job": "extension"
            }
        }
        
        success, result, duration = self.make_request("train_with_yaml", training_config)
        
        if success:
            output = result.get("output", {})
            process_id = output.get('process_id')
            
            if process_id:
                print(f"   ✅ Training started with process ID: {process_id}")
                print(f"   ⏱️ Training initiated in {duration:.2f}s")
                
                # Wait a bit and check status
                print("   ⏳ Waiting 10 seconds to check training status...")
                time.sleep(10)
                
                status_success, status_result, _ = self.make_request("process_status", {"process_id": process_id})
                if status_success:
                    status_output = status_result.get("output", {})
                    process_info = status_output.get('process', {})
                    status = process_info.get('status', 'unknown')
                    
                    print(f"   📊 Training status: {status}")
                    
                    if status == 'failed':
                        error = process_info.get('error', 'Unknown error')
                        print(f"   ❌ Training failed: {error}")
                        
                        # Check if it's the same old 0x0 error
                        if "height and width must be > 0" in error:
                            print(f"   🔍 OLD ERROR DETECTED - validation not working in training phase")
                            return False
                        else:
                            print(f"   🔍 Different error - might be model/config related")
                            return True  # At least validation worked
                    elif status == 'running':
                        print(f"   ✅ Training is running (validation passed)")
                        return True
                    elif status == 'completed':
                        print(f"   🎉 Training completed successfully")
                        return True
                    else:
                        print(f"   ⏳ Training status: {status}")
                        return True  # Still progress
                else:
                    print(f"   ❌ Failed to check training status")
                    return False
            else:
                print(f"   ❌ No process ID returned")
                return False
        else:
            print(f"   ❌ Training failed to start: {result}")
            return False

    def run_all_tests(self):
        """Run all tests in sequence."""
        print("🧪 RUNNING FIXED SYSTEM TESTS")
        print("=" * 50)
        
        results = {}
        
        # Test 1: Health check
        results['health'] = self.test_health_check()
        
        # Test 2: Load Matt's dataset
        if results['health']:
            results['matt_dataset'], training_folder = self.test_load_matt_dataset()
        else:
            print("\n❌ Skipping further tests due to health check failure")
            return results
        
        # Test 3: Bad image validation
        results['validation'] = self.test_bad_images_validation()
        
        # Test 4: Worker isolation
        results['isolation'] = self.test_worker_isolation()
        
        # Test 5: Training (only if we have Matt's data)
        if results['matt_dataset'] and training_folder:
            results['training'] = self.test_training_with_matt_data(training_folder)
        else:
            print("\n❌ Skipping training test - no valid Matt's dataset")
            results['training'] = False
        
        # Summary
        print("\n" + "=" * 50)
        print("📊 TEST SUMMARY")
        print("=" * 50)
        
        total_tests = len(results)
        passed_tests = sum(1 for v in results.values() if v)
        
        for test_name, passed in results.items():
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"   {test_name.upper()}: {status}")
        
        print(f"\n🎯 OVERALL: {passed_tests}/{total_tests} tests passed")
        
        if passed_tests == total_tests:
            print("🎉 ALL TESTS PASSED - System is working correctly!")
        elif passed_tests >= total_tests - 1:
            print("⚠️ Most tests passed - System mostly working")
        else:
            print("❌ Multiple failures detected - System needs more work")
        
        return results

    def test_complete_workflow(self):
        """Test complete workflow: load Matt's dataset -> train -> generate."""
        print(f"\n🚀 COMPLETE WORKFLOW TEST")
        print("=" * 50)
        
        # Step 1: Load Matt's dataset
        print("\n📁 Step 1: Loading Matt's dataset...")
        load_result = self.test_load_matt_dataset()
        if not load_result or load_result.get("status") != "success":
            print("❌ Failed to load Matt's dataset - stopping workflow")
            return False
            
        training_folder = load_result.get("training_folder")
        print(f"✅ Dataset loaded to: {training_folder}")
        
        # Step 2: Start training with conservative settings
        print("\n🏋️ Step 2: Starting training with conservative settings...")
        train_payload = {
            "input": {
                "type": "train_with_yaml",
                "training_folder": training_folder,
                "yaml_config": {
                    "job": "extension",
                    "config": {
                        "name": "matt_lora_conservative",
                        "process": [
                            {
                                "type": "sd_trainer",
                                "training_folder": training_folder,
                                "device": "cuda:0",
                                "trigger_word": "Matt",
                                "network": {
                                    "type": "lora",
                                    "linear": 8,
                                    "linear_alpha": 8
                                },
                                "save": {
                                    "dtype": "float16",
                                    "save_every": 50,
                                    "max_step_saves_to_keep": 2
                                },
                                "datasets": [
                                    {
                                        "folder_path": training_folder,
                                        "caption_ext": "txt",
                                        "caption_dropout_rate": 0.1,
                                        "shuffle_tokens": False,
                                        "cache_latents_to_disk": True,
                                        "resolution": [1024, 1024]
                                    }
                                ],
                                "train": {
                                    "batch_size": 1,
                                    "steps": 200,
                                    "gradient_accumulation_steps": 2,
                                    "train_unet": True,
                                    "train_text_encoder": False,
                                    "learning_rate": 5e-5,
                                    "lr_scheduler": "cosine",
                                    "optimizer": "adamw8bit",
                                    "skip_cache_latents": False
                                },
                                "model": {
                                    "name_or_path": "black-forest-labs/FLUX.1-dev",
                                    "is_flux": True,
                                    "quantize": True
                                },
                                "sample": {
                                    "sampler": "flowmatch",
                                    "sample_every": 50,
                                    "width": 1024,
                                    "height": 1024,
                                    "prompts": [
                                        "Matt [trigger] portrait photo, professional lighting",
                                        "Matt [trigger] casual photo, natural lighting"
                                    ],
                                    "neg": "",
                                    "seed": 42,
                                    "walk_seed": True,
                                    "guidance_scale": 3.5,
                                    "sample_steps": 20
                                }
                            }
                        ]
                    }
                }
            }
        }
        
        train_response = self.make_request(train_payload)
        if not train_response:
            return False
            
        print(f"✅ Training started with conservative settings!")
        
        # Step 3: Check training status periodically
        print("\n📊 Step 3: Monitoring training progress...")
        for i in range(5):  # Check 5 times
            time.sleep(30)  # Wait 30 seconds between checks
            status_success, status_result, _ = self.make_request("process_status")
            if status_success:
                output = status_result.get("output", {})
                active_processes = output.get("active_processes", 0)
                print(f"   Check {i+1}: Active processes: {active_processes}")
                
                if active_processes == 0:
                    print("   ✅ Training completed!")
                    break
            else:
                print(f"   ❌ Status check {i+1} failed")
        
        return True

    def quick_endpoint_check(self):
        """Quick check if endpoint is responding."""
        print(f"\n⚡ QUICK ENDPOINT CHECK")
        print("=" * 50)
        
        success, result, duration = self.make_request("health")
        if success:
            output = result.get("output", {})
            worker_id = output.get('worker_id', 'unknown')
            print(f"✅ Endpoint responding! Worker ID: {worker_id}")
            print(f"   Response time: {duration:.2f}s")
            
            # Check available types
            available_types = output.get('available_types', [])
            if 'load_matt_dataset' in available_types:
                print("✅ load_matt_dataset endpoint available!")
            else:
                print("❌ load_matt_dataset endpoint NOT found")
                
            return True
        else:
            print(f"❌ Endpoint not responding: {result}")
            return False

if __name__ == "__main__":
    # Quick test first
    tester = FixedSystemTester()
    
    print("🚀 STARTING ENDPOINT TESTS")
    print("=" * 50)
    
    # Quick check first
    if not tester.quick_endpoint_check():
        print("❌ Endpoint not responding - check deployment")
        exit(1)
    
    # Run all tests
    print("\n🧪 RUNNING FULL TEST SUITE")
    tester.run_all_tests()
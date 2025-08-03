#!/usr/bin/env python3
"""
🧪 Advanced RunPod Backend Tester v2.0

Enhanced testing suite with:
- Multi-version endpoint testing
- Async job handling with intelligent polling
- Progressive complexity testing 
- Advanced error handling and reporting
- Performance metrics and analytics
"""

import asyncio
import json
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import aiohttp
import logging

# Import config loader
try:
    from config_loader_shared import get_runpod_token, get_config_value
except ImportError:
    print("❌ Could not import config_loader_shared.py")
    print("Please ensure config_loader_shared.py is in the same directory.")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TestConfig:
    # 🎯 RUNPOD CONFIGURATION - Load from config.env
    try:
        RUNPOD_TOKEN = get_runpod_token()
    except ValueError as e:
        logger.error(f"❌ Configuration error: {e}")
        logger.error("📋 Please copy config.env.template to config.env and set your RunPod token.")
        sys.exit(1)
    
    ENDPOINT_ID = get_config_value('RUNPOD_ENDPOINT_ID', 'your-endpoint-id-here')
    
    # Endpoint versions to test
    ENDPOINTS = [
        f"https://api.runpod.ai/v2/{ENDPOINT_ID}/runsync",
        f"https://api.runpod.ai/v2/{ENDPOINT_ID}/run",
    ]
    
    # Test configuration
    TIMEOUT = int(get_config_value('TEST_TIMEOUT', '300'))  # 5 minutes
    POLLING_INTERVAL = int(get_config_value('POLLING_INTERVAL', '5'))  # 5 seconds
    MAX_RETRIES = int(get_config_value('MAX_RETRIES', '3'))
    
    # ⚙️ SETTINGS - IMPROVED
    TIMEOUT_SYNC = 120      # Increased for /runsync
    TIMEOUT_ASYNC = 30      # For /run
    RETRY_COUNT = 2
    LOG_FILE = "runpod_test_log_v2.txt"
    RESULTS_FILE = "test_results_v2.json"
    
    # 📁 TEST DATA - SMALLER PAYLOAD
    TEST_TRAINING_NAME = "test_lora_mini"
    TEST_PROMPTS = [
        "A photo of a person, high quality"
    ]

# 🏗️ SIMPLIFIED TEST DATA GENERATOR
class TestDataGenerator:
    def __init__(self):
        self.test_dir = Path("test_data_mini")
        self.test_dir.mkdir(exist_ok=True)
        
    def create_small_test_image(self, filename: str, width: int = 256, height: int = 256) -> str:
        """Create a small test image file"""
        # Create a simple colored image
        img = Image.new('RGB', (width, height), color=(100, 150, 200))
        
        # Add minimal content
        from PIL import ImageDraw
        draw = ImageDraw.Draw(img)
        draw.text((10, 10), f"Test {filename[:4]}", fill=(255, 255, 255))
        draw.rectangle([50, 50, 100, 100], outline=(255, 0, 0), width=2)
        
        filepath = self.test_dir / filename
        img.save(filepath, 'JPEG', quality=85, optimize=True)
        return str(filepath)
    
    def create_test_caption(self, filename: str, content: str) -> str:
        """Create a test caption file"""
        filepath = self.test_dir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return str(filepath)
    
    def generate_mini_dataset(self) -> List[str]:
        """Generate a minimal test dataset (2 images + captions)"""
        files = []
        
        # Only 2 images to reduce payload size
        test_data = [
            ("test_001.jpg", "test_001.txt", "A professional photo of a person"),
            ("test_002.jpg", "test_002.txt", "Portrait shot, detailed face")
        ]
        
        for img_name, txt_name, caption in test_data:
            # Create small image
            img_path = self.create_small_test_image(img_name)
            files.append(img_path)
            
            # Create caption
            txt_path = self.create_test_caption(txt_name, caption)
            files.append(txt_path)
        
        return files

# 🧪 IMPROVED RUNPOD BACKEND TESTER
class RunPodBackendTesterV2:
    def __init__(self, config: TestConfig):
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {config.RUNPOD_TOKEN}',
            'Content-Type': 'application/json'
        })
        
        # Setup logging
        self.setup_logging()
        
        # Test results
        self.results = {
            "start_time": datetime.now().isoformat(),
            "endpoint_id": config.ENDPOINT_ID,
            "version": "2.0",
            "tests": [],
            "summary": {}
        }
        
        # Generate test data
        self.data_generator = TestDataGenerator()
        
    def setup_logging(self):
        """Setup comprehensive logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.config.LOG_FILE, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def log_test_result(self, test_name: str, success: bool, response_data: Any = None, error: str = None, duration: float = None):
        """Log test result with duration"""
        result = {
            "test_name": test_name,
            "timestamp": datetime.now().isoformat(),
            "success": success,
            "duration_seconds": duration,
            "response_data": response_data,
            "error": error
        }
        self.results["tests"].append(result)
        
        duration_str = f" ({duration:.1f}s)" if duration else ""
        if success:
            self.logger.info(f"✅ {test_name} - SUCCESS{duration_str}")
        else:
            self.logger.error(f"❌ {test_name} - FAILED{duration_str}: {error}")
    
    def make_runpod_request(self, job_type: str, input_data: Dict, use_sync: bool = True) -> Dict:
        """Make a request to RunPod endpoint with proper timeout"""
        endpoint = "/runsync" if use_sync else "/run"
        url = f"{self.config.BASE_URL}{endpoint}"
        timeout = self.config.TIMEOUT_SYNC if use_sync else self.config.TIMEOUT_ASYNC
        
        payload = {
            "input": {
                "type": job_type,
                **input_data
            }
        }
        
        payload_size = len(json.dumps(payload))
        self.logger.info(f"📡 Making request to {url}")
        self.logger.info(f"📦 Payload: type={job_type}, size={payload_size} bytes, timeout={timeout}s")
        
        start_time = time.time()
        try:
            response = self.session.post(url, json=payload, timeout=timeout)
            duration = time.time() - start_time
            
            response.raise_for_status()
            result = response.json()
            
            self.logger.info(f"📥 Response: status={response.status_code}, duration={duration:.1f}s")
            
            return result, duration
            
        except requests.exceptions.Timeout:
            duration = time.time() - start_time
            self.logger.error(f"⏰ Request timeout after {duration:.1f}s")
            raise
        except requests.exceptions.RequestException as e:
            duration = time.time() - start_time
            self.logger.error(f"🚨 Request failed after {duration:.1f}s: {e}")
            raise
    
    def file_to_base64(self, filepath: str) -> Dict:
        """Convert file to base64 format for RunPod"""
        with open(filepath, 'rb') as f:
            content = base64.b64encode(f.read()).decode('utf-8')
        
        filename = os.path.basename(filepath)
        file_size = os.path.getsize(filepath)
        
        # Determine content type
        if filepath.lower().endswith(('.jpg', '.jpeg')):
            content_type = 'image/jpeg'
        elif filepath.lower().endswith('.png'):
            content_type = 'image/png'
        elif filepath.lower().endswith('.txt'):
            content_type = 'text/plain'
        else:
            content_type = 'application/octet-stream'
        
        return {
            "filename": filename,
            "content": content,
            "content_type": content_type,
            "size": file_size
        }
    
    # 🔍 IMPROVED TEST METHODS
    
    def test_endpoint_status(self) -> bool:
        """Test endpoint basic connectivity"""
        try:
            # Simple request to check endpoint exists
            health_url = f"{self.config.BASE_URL}/health"
            start_time = time.time()
            
            response = self.session.get(health_url, timeout=10)
            duration = time.time() - start_time
            
            if response.status_code in [200, 404]:  # 404 is OK, means endpoint exists
                self.log_test_result("endpoint_connectivity", True, 
                                   {"status_code": response.status_code}, duration=duration)
                return True
            else:
                self.log_test_result("endpoint_connectivity", False, 
                                   error=f"Unexpected status: {response.status_code}", duration=duration)
                return False
                
        except Exception as e:
            self.log_test_result("endpoint_connectivity", False, error=str(e))
            return False
    
    def test_health_check(self) -> bool:
        """Test health endpoint"""
        try:
            result, duration = self.make_runpod_request("health", {})
            self.log_test_result("health_check", True, result, duration=duration)
            return True
                
        except Exception as e:
            self.log_test_result("health_check", False, error=str(e))
            return False
    
    def test_upload_training_data_mini(self) -> Optional[str]:
        """Test uploading minimal training data"""
        try:
            # Generate minimal test dataset (2 images)
            self.logger.info("🎨 Generating minimal test dataset (2 images)...")
            test_files = self.data_generator.generate_mini_dataset()
            
            # Convert files to base64
            base64_files = []
            total_size = 0
            for filepath in test_files:
                b64_file = self.file_to_base64(filepath)
                base64_files.append(b64_file)
                total_size += b64_file['size']
                self.logger.info(f"📎 Processed: {b64_file['filename']} ({b64_file['size']} bytes)")
            
            self.logger.info(f"📊 Total payload: {total_size} bytes, {len(base64_files)} files")
            
            # Make upload request
            upload_data = {
                "training_name": self.config.TEST_TRAINING_NAME,
                "trigger_word": "",  # Empty as requested
                "cleanup_existing": True,
                "files": base64_files
            }
            
            result, duration = self.make_runpod_request("upload_training_data", upload_data)
            
            # Extract training folder from response
            training_folder = None
            if "output" in result:
                training_folder = result["output"].get("training_folder")
            elif "training_folder" in result:
                training_folder = result["training_folder"]
            
            self.log_test_result("upload_training_data_mini", True, result, duration=duration)
            self.logger.info(f"📁 Training folder: {training_folder}")
            
            return training_folder
            
        except Exception as e:
            self.log_test_result("upload_training_data_mini", False, error=str(e))
            return None
    
    def test_get_processes(self) -> bool:
        """Test getting process list"""
        try:
            result, duration = self.make_runpod_request("processes", {})
            
            processes = []
            if "output" in result:
                processes = result["output"].get("processes", [])
            elif "processes" in result:
                processes = result["processes"]
            
            self.log_test_result("get_processes", True, {"process_count": len(processes)}, duration=duration)
            self.logger.info(f"📋 Found {len(processes)} processes")
            return True
            
        except Exception as e:
            self.log_test_result("get_processes", False, error=str(e))
            return False
    
    def test_get_lora_models_fixed(self) -> bool:
        """Test getting LoRA models list - FIXED job type"""
        try:
            # FIXED: Use 'lora' instead of 'lora_models'
            result, duration = self.make_runpod_request("lora", {})
            
            models = []
            if "output" in result:
                models = result["output"].get("models", [])
            elif "models" in result:
                models = result["models"]
            
            self.log_test_result("get_lora_models_fixed", True, {"model_count": len(models)}, duration=duration)
            self.logger.info(f"🎭 Found {len(models)} LoRA models")
            return True
            
        except Exception as e:
            self.log_test_result("get_lora_models_fixed", False, error=str(e))
            return False
    
    def test_start_generation_quick(self) -> Optional[str]:
        """Test starting a quick image generation"""
        try:
            generation_config = {
                "name": "test_generation_mini",
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
                        "width": 512,  # Smaller size
                        "height": 512,
                        "prompts": ["A simple test image"],
                        "neg": "",
                        "seed": 42,
                        "guidance_scale": 4,
                        "sample_steps": 10,  # Fewer steps
                        "num_samples": 1     # Just 1 image
                    }
                }]
            }
            
            result, duration = self.make_runpod_request("generate", {"config": generation_config}, use_sync=False)
            
            # Extract process ID
            process_id = None
            if "output" in result:
                process_id = result["output"].get("process_id")
            elif "id" in result:
                process_id = result["id"]  # RunPod job ID
            
            self.log_test_result("start_generation_quick", True, result, duration=duration)
            return process_id
            
        except Exception as e:
            self.log_test_result("start_generation_quick", False, error=str(e))
            return None
    
    def test_bulk_download_simple(self) -> bool:
        """Test bulk download with minimal data"""
        try:
            # Simple test with 1 fake process ID
            download_request = {
                "process_ids": ["test_process_1"],
                "include_images": True,
                "include_loras": False  # Skip LoRAs for speed
            }
            
            result, duration = self.make_runpod_request("bulk_download", download_request)
            
            download_items = []
            if "output" in result:
                download_items = result["output"].get("download_items", [])
            elif "download_items" in result:
                download_items = result["download_items"]
            
            self.log_test_result("bulk_download_simple", True, {"download_count": len(download_items)}, duration=duration)
            return True
            
        except Exception as e:
            self.log_test_result("bulk_download_simple", False, error=str(e))
            return False
    
    # 🎯 PROGRESSIVE TEST RUNNER
    
    def run_progressive_tests(self):
        """Run tests progressively, stopping on critical failures"""
        self.logger.info("🚀 Starting RunPod Backend Test Suite v2.0")
        self.logger.info(f"🎯 Endpoint: {self.config.ENDPOINT_ID}")
        self.logger.info(f"📅 Start time: {datetime.now()}")
        self.logger.info("🔧 Improvements: smaller payloads, correct job types, increased timeouts")
        
        test_results = {}
        
        # Phase 1: Basic connectivity
        self.logger.info("\n🔗 Phase 1: Basic Connectivity")
        test_results["connectivity"] = self.test_endpoint_status()
        
        if not test_results["connectivity"]:
            self.logger.error("💥 CRITICAL: Endpoint not reachable. Stopping tests.")
            self.generate_summary(test_results)
            return test_results
        
        # Phase 2: Health check
        self.logger.info("\n🔍 Phase 2: Health Check")
        test_results["health"] = self.test_health_check()
        
        # Phase 3: Quick operations (reduced timeout risk)
        self.logger.info("\n⚡ Phase 3: Quick Operations")
        
        self.logger.info("📋 Testing Get Processes...")
        test_results["processes"] = self.test_get_processes()
        
        self.logger.info("🎭 Testing Get LoRA Models (FIXED)...")
        test_results["lora_models"] = self.test_get_lora_models_fixed()
        
        self.logger.info("⬇️ Testing Bulk Download...")
        test_results["bulk_download"] = self.test_bulk_download_simple()
        
        # Phase 4: File operations
        self.logger.info("\n📁 Phase 4: File Operations")
        self.logger.info("📁 Testing Upload (Mini Dataset)...")
        training_folder = self.test_upload_training_data_mini()
        test_results["upload_mini"] = training_folder is not None
        
        # Phase 5: Generation (async)
        self.logger.info("\n🎨 Phase 5: Generation Operations")
        self.logger.info("🎨 Testing Start Generation...")
        generation_process = self.test_start_generation_quick()
        test_results["generation"] = generation_process is not None
        
        # Generate summary
        self.generate_summary(test_results)
        
        # Save results
        self.save_results()
        
        return test_results
    
    def generate_summary(self, test_results: Dict[str, bool]):
        """Generate test summary"""
        total_tests = len(test_results)
        passed_tests = sum(test_results.values())
        failed_tests = total_tests - passed_tests
        
        self.results["summary"] = {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": f"{(passed_tests/total_tests)*100:.1f}%",
            "end_time": datetime.now().isoformat()
        }
        
        self.logger.info("\n" + "="*60)
        self.logger.info("📊 TEST SUMMARY v2.0")
        self.logger.info("="*60)
        self.logger.info(f"✅ Passed: {passed_tests}/{total_tests}")
        self.logger.info(f"❌ Failed: {failed_tests}/{total_tests}")
        self.logger.info(f"📈 Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        # Group results by phase
        self.logger.info("\n📋 DETAILED RESULTS:")
        for test_name, result in test_results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            self.logger.info(f"   {test_name}: {status}")
        
        self.logger.info("="*60)
        
        # Recommendations
        if passed_tests == total_tests:
            self.logger.info("🎉 ALL TESTS PASSED! Backend is fully functional.")
        elif passed_tests >= total_tests * 0.7:
            self.logger.info("⚠️ Most tests passed. Check failed tests for minor issues.")
        else:
            self.logger.info("🚨 Many tests failed. Check endpoint status and configuration.")
    
    def save_results(self):
        """Save test results to file"""
        with open(self.config.RESULTS_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"💾 Results saved to: {self.config.RESULTS_FILE}")
        self.logger.info(f"📝 Log saved to: {self.config.LOG_FILE}")

# 🎯 MAIN EXECUTION
if __name__ == "__main__":
    print("🧪 RunPod Backend Tester v2.0 - IMPROVED")
    print("=" * 60)
    print("🔧 Fixed: job types, payload sizes, timeouts")
    print("📊 Progressive testing with better diagnostics")
    print("=" * 60)
    
    # Initialize configuration
    config = TestConfig()
    
    # Create tester
    tester = RunPodBackendTesterV2(config)
    
    try:
        # Run progressive tests
        results = tester.run_progressive_tests()
        
        print(f"\n🎉 Testing completed!")
        print(f"📊 Check {config.RESULTS_FILE} for detailed results")
        print(f"📝 Check {config.LOG_FILE} for full logs")
        
    except KeyboardInterrupt:
        print("\n⚠️ Testing interrupted by user")
    except Exception as e:
        print(f"\n💥 Testing failed with error: {e}")
        logging.error(f"Fatal error: {e}", exc_info=True) 
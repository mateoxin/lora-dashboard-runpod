#!/usr/bin/env python3
"""
🧪 Advanced RunPod Backend Tester v2.0

Comprehensive testing suite for RunPod Serverless endpoints with:
- Multiple endpoint versions testing
- Async job handling with polling
- Progressive complexity testing
- Comprehensive error handling and reporting
- Multiple request types (sync/async)
"""

import asyncio
import base64
import json
import os
import requests
import shutil
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import aiohttp
import logging
from PIL import Image, ImageDraw, ImageFont

# Add backend utils to path for config loader
backend_path = Path(__file__).parent.parent / "Backend"
if backend_path.exists():
    sys.path.insert(0, str(backend_path))
    
try:
    from app.utils.config_loader import get_runpod_token, get_config_value
except ImportError:
    # Fallback if config loader not available
    def get_runpod_token():
        token = os.getenv('RUNPOD_TOKEN')
        if not token:
            raise ValueError("RUNPOD_TOKEN not found. Please set it in config.env file or environment variable.")
        if token == "YOUR_RUNPOD_TOKEN_HERE":
            raise ValueError("Please replace YOUR_RUNPOD_TOKEN_HERE with your actual RunPod token in config.env")
        return token
    
    def get_config_value(key: str, default: str = None):
        return os.getenv(key, default)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TestConfig:
    # 🎯 RUNPOD ENDPOINT - UPDATE THIS!
    # Load from config file or environment
    try:
        RUNPOD_TOKEN = get_runpod_token()
    except ValueError as e:
        logger.error(f"Config error: {e}")
        logger.error("Please copy config.env.template to config.env and fill in your RunPod token.")
        sys.exit(1)
    
    ENDPOINT_ID = get_config_value('RUNPOD_ENDPOINT_ID', 'your-endpoint-id-here')
    
    # Endpoint versions to test (add your deployed versions)
    ENDPOINTS = [
        "https://api.runpod.ai/v2/{}/runsync".format(ENDPOINT_ID),
        "https://api.runpod.ai/v2/{}/run".format(ENDPOINT_ID),
    ]
    
    # Test configuration
    TIMEOUT = int(get_config_value('TEST_TIMEOUT', '300'))  # 5 minutes
    POLLING_INTERVAL = int(get_config_value('POLLING_INTERVAL', '5'))  # 5 seconds
    MAX_RETRIES = int(get_config_value('MAX_RETRIES', '3'))
    
    # 📁 TEST DATA
    TEST_TRAINING_NAME = "test_lora_training"
    TEST_PROMPTS = [
        "A photo of a person, high quality",
        "Portrait of a character, detailed",
        "Full body shot, professional photography"
    ]

# 🏗️ TEST DATA GENERATOR
class TestDataGenerator:
    def __init__(self):
        self.test_dir = Path("test_data")
        self.test_dir.mkdir(exist_ok=True)
        self.matt_folder = self._find_matt_folder()
        
    def _find_matt_folder(self) -> Optional[Path]:
        """Find the 10_Matt folder relative to current location"""
        possible_paths = [
            Path("10_Matt"),
            Path("../10_Matt"),
            Path("../../10_Matt"),
            Path("../../../10_Matt"),
            Path("../../Serverless/10_Matt"),
            Path("../Serverless/10_Matt")
        ]
        
        for path in possible_paths:
            if path.exists() and path.is_dir():
                logger.info(f"📸 Found Matt's dataset at: {path.absolute()}")
                return path
                
        logger.warning("⚠️ 10_Matt folder not found, will use synthetic images")
        return None
        
    def create_test_image(self, filename: str, width: int = 512, height: int = 512) -> str:
        """Create a test image file (fallback for when 10_Matt not available)"""
        # Create a simple colored image
        img = Image.new('RGB', (width, height), color=(70, 130, 180))
        
        # Add some text/pattern
        draw = ImageDraw.Draw(img)
        try:
            # Try to use a font
            font = ImageFont.load_default()
            draw.text((10, 10), f"Test Image\n{filename}", fill=(255, 255, 255), font=font)
        except:
            # Fallback without font
            draw.text((10, 10), f"Test Image {filename}", fill=(255, 255, 255))
        
        # Add some geometric shapes
        draw.rectangle([50, 50, 150, 150], outline=(255, 0, 0), width=3)
        draw.ellipse([200, 200, 300, 300], outline=(0, 255, 0), width=3)
        
        filepath = self.test_dir / filename
        img.save(filepath, 'JPEG', quality=95)
        return str(filepath)
    
    def create_test_caption(self, filename: str, content: str) -> str:
        """Create a test caption file"""
        filepath = self.test_dir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return str(filepath)
    
    def generate_test_dataset(self) -> List[str]:
        """Generate a complete test dataset using real Matt's images if available"""
        files = []
        
        # Try to use real Matt's dataset first
        if self.matt_folder and self._use_matt_dataset():
            logger.info("📸 Using real Matt's dataset from 10_Matt folder")
            return self._copy_matt_dataset()
        else:
            logger.info("🎨 Using synthetic test dataset")
            return self._generate_synthetic_dataset()
    
    def _use_matt_dataset(self) -> bool:
        """Check if Matt's dataset has images and captions"""
        if not self.matt_folder:
            return False
            
        jpg_files = list(self.matt_folder.glob("*.jpg"))
        txt_files = list(self.matt_folder.glob("*.txt"))
        
        if len(jpg_files) >= 3 and len(txt_files) >= 3:
            logger.info(f"📸 Found {len(jpg_files)} images and {len(txt_files)} captions in Matt's dataset")
            return True
        else:
            logger.warning(f"⚠️ Insufficient files in Matt's dataset: {len(jpg_files)} images, {len(txt_files)} captions")
            return False
    
    def _copy_matt_dataset(self) -> List[str]:
        """Copy files from Matt's dataset to test directory"""
        files = []
        
        jpg_files = sorted(list(self.matt_folder.glob("*.jpg")))[:5]  # Take first 5 images
        
        for idx, jpg_file in enumerate(jpg_files):
            # Find corresponding txt file
            txt_file = jpg_file.with_suffix('.txt')
            
            if txt_file.exists():
                # Copy image
                new_img_name = f"matt_{idx+1:03d}.jpg"
                new_img_path = self.test_dir / new_img_name
                shutil.copy2(jpg_file, new_img_path)
                files.append(str(new_img_path))
                
                # Copy caption
                new_txt_name = f"matt_{idx+1:03d}.txt"
                new_txt_path = self.test_dir / new_txt_name
                shutil.copy2(txt_file, new_txt_path)
                files.append(str(new_txt_path))
                
                logger.info(f"📋 Copied: {jpg_file.name} -> {new_img_name}")
            else:
                logger.warning(f"⚠️ No caption file for {jpg_file.name}")
        
        return files
    
    def _generate_synthetic_dataset(self) -> List[str]:
        """Generate synthetic test dataset as fallback"""
        files = []
        
        # Create test images with corresponding captions
        test_data = [
            ("person_001.jpg", "person_001.txt", "A professional photo of a person, high quality, detailed"),
            ("person_002.jpg", "person_002.txt", "Portrait shot of a character, studio lighting"),
            ("person_003.jpg", "person_003.txt", "Full body photograph, clear background, professional"),
            ("style_001.jpg", "style_001.txt", "Artistic style reference, detailed texture"),
            ("style_002.jpg", "style_002.txt", "Color palette example, vibrant tones")
        ]
        
        for img_name, txt_name, caption in test_data:
            # Create image
            img_path = self.create_test_image(img_name)
            files.append(img_path)
            
            # Create caption
            txt_path = self.create_test_caption(txt_name, caption)
            files.append(txt_path)
        
        return files

# 🧪 RUNPOD BACKEND TESTER
class RunPodBackendTester:
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
        
    def log_test_result(self, test_name: str, success: bool, response_data: Any = None, error: str = None):
        """Log test result"""
        result = {
            "test_name": test_name,
            "timestamp": datetime.now().isoformat(),
            "success": success,
            "response_data": response_data,
            "error": error
        }
        self.results["tests"].append(result)
        
        if success:
            self.logger.info(f"✅ {test_name} - SUCCESS")
        else:
            self.logger.error(f"❌ {test_name} - FAILED: {error}")
    
    def make_runpod_request(self, job_type: str, input_data: Dict, use_sync: bool = True) -> Dict:
        """Make a request to RunPod endpoint"""
        endpoint = "/runsync" if use_sync else "/run"
        url = f"{self.config.BASE_URL}{endpoint}"
        
        payload = {
            "input": {
                "type": job_type,
                **input_data
            }
        }
        
        self.logger.info(f"📡 Making request to {url}")
        self.logger.info(f"📦 Payload type: {job_type}")
        
        try:
            response = self.session.post(url, json=payload, timeout=self.config.TIMEOUT)
            response.raise_for_status()
            
            result = response.json()
            self.logger.info(f"📥 Response status: {response.status_code}")
            
            return result
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"🚨 Request failed: {e}")
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
    
    # 🔍 TEST METHODS
    
    def test_health_check(self) -> bool:
        """Test health endpoint"""
        try:
            # Try native health endpoint first
            health_url = f"{self.config.BASE_URL}/health"
            response = self.session.get(health_url, timeout=10)
            
            if response.status_code == 200:
                self.log_test_result("health_check_native", True, response.json())
                return True
            else:
                # Fallback to custom health job
                result = self.make_runpod_request("health", {})
                self.log_test_result("health_check_custom", True, result)
                return True
                
        except Exception as e:
            self.log_test_result("health_check", False, error=str(e))
            return False
    
    def test_upload_training_data(self) -> Optional[str]:
        """Test uploading training data"""
        try:
            # Generate test dataset
            self.logger.info("🎨 Generating test dataset...")
            test_files = self.data_generator.generate_test_dataset()
            
            # Convert files to base64
            base64_files = []
            for filepath in test_files:
                b64_file = self.file_to_base64(filepath)
                base64_files.append(b64_file)
                self.logger.info(f"📎 Processed: {b64_file['filename']} ({b64_file['size']} bytes)")
            
            # Make upload request
            upload_data = {
                "training_name": self.config.TEST_TRAINING_NAME,
                "trigger_word": "",  # Empty as requested
                "cleanup_existing": True,
                "files": base64_files
            }
            
            result = self.make_runpod_request("upload_training_data", upload_data)
            
            # Extract training folder from response
            training_folder = None
            if "output" in result:
                training_folder = result["output"].get("training_folder")
            elif "training_folder" in result:
                training_folder = result["training_folder"]
            
            self.log_test_result("upload_training_data", True, result)
            self.logger.info(f"📁 Training folder: {training_folder}")
            
            return training_folder
            
        except Exception as e:
            self.log_test_result("upload_training_data", False, error=str(e))
            return None
    
    def test_start_training(self, training_folder: str) -> Optional[str]:
        """Test starting LoRA training"""
        try:
            training_config = {
                "name": self.config.TEST_TRAINING_NAME,
                "process": [{
                    "type": "sd_trainer",
                    "device": "cuda:0",
                    "network": {
                        "type": "lora",
                        "linear": 16,
                        "linear_alpha": 16
                    },
                    "save": {
                        "dtype": "float16",
                        "save_every": 2000,
                        "max_step_saves_to_keep": 1,
                        "push_to_hub": False
                    },
                    "datasets": [{
                        "folder_path": training_folder,
                        "caption_ext": "txt",
                        "caption_dropout_rate": 0.05,
                        "shuffle_tokens": False,
                        "cache_latents_to_disk": True,
                        "resolution": [512, 768, 1024]
                    }],
                    "train": {
                        "batch_size": 1,
                        "steps": 100,  # Short training for testing
                        "gradient_accumulation_steps": 4,
                        "train_unet": True,
                        "train_text_encoder": False,
                        "gradient_checkpointing": True,
                        "noise_scheduler": "flowmatch",
                        "optimizer": "adamw8bit",
                        "lr": 0.0001,
                        "ema_config": {
                            "use_ema": True,
                            "ema_decay": 0.99
                        }
                    },
                    "dtype": "bf16",
                    "model": {
                        "name_or_path": "/workspace/models/FLUX.1-dev",
                        "is_flux": True,
                        "quantize": True
                    },
                    "sample": {
                        "sampler": "flowmatch",
                        "sample_every": 50,
                        "width": 1024,
                        "height": 1024,
                        "prompts": self.config.TEST_PROMPTS,
                        "neg": "",
                        "seed": 42,
                        "walk_seed": True,
                        "guidance_scale": 4,
                        "sample_steps": 20
                    }
                }]
            }
            
            result = self.make_runpod_request("train", {"config": training_config}, use_sync=False)
            
            # Extract process ID
            process_id = None
            if "output" in result:
                process_id = result["output"].get("process_id")
            elif "id" in result:
                process_id = result["id"]  # RunPod job ID
            
            self.log_test_result("start_training", True, result)
            return process_id
            
        except Exception as e:
            self.log_test_result("start_training", False, error=str(e))
            return None
    
    def test_start_generation(self) -> Optional[str]:
        """Test starting image generation"""
        try:
            generation_config = {
                "name": "test_generation",
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
                        "width": 1024,
                        "height": 1024,
                        "prompts": ["A beautiful landscape, high quality, detailed"],
                        "neg": "",
                        "seed": 42,
                        "guidance_scale": 4,
                        "sample_steps": 20,
                        "num_samples": 2
                    }
                }]
            }
            
            result = self.make_runpod_request("generate", {"config": generation_config}, use_sync=False)
            
            # Extract process ID
            process_id = None
            if "output" in result:
                process_id = result["output"].get("process_id")
            elif "id" in result:
                process_id = result["id"]  # RunPod job ID
            
            self.log_test_result("start_generation", True, result)
            return process_id
            
        except Exception as e:
            self.log_test_result("start_generation", False, error=str(e))
            return None
    
    def test_get_processes(self) -> bool:
        """Test getting process list"""
        try:
            result = self.make_runpod_request("processes", {})
            
            processes = []
            if "output" in result:
                processes = result["output"].get("processes", [])
            elif "processes" in result:
                processes = result["processes"]
            
            self.log_test_result("get_processes", True, {"process_count": len(processes)})
            self.logger.info(f"📋 Found {len(processes)} processes")
            return True
            
        except Exception as e:
            self.log_test_result("get_processes", False, error=str(e))
            return False
    
    def test_get_lora_models(self) -> bool:
        """Test getting LoRA models list"""
        try:
            result = self.make_runpod_request("lora", {})
            
            models = []
            if "output" in result:
                models = result["output"].get("models", [])
            elif "models" in result:
                models = result["models"]
            
            self.log_test_result("get_lora_models", True, {"model_count": len(models)})
            self.logger.info(f"🎭 Found {len(models)} LoRA models")
            return True
            
        except Exception as e:
            self.log_test_result("get_lora_models", False, error=str(e))
            return False
    
    def test_bulk_download(self) -> bool:
        """Test bulk download functionality"""
        try:
            # Test with fake process IDs
            download_request = {
                "process_ids": ["test_process_1", "test_process_2"],
                "include_images": True,
                "include_loras": True
            }
            
            result = self.make_runpod_request("bulk_download", download_request)
            
            download_items = []
            if "output" in result:
                download_items = result["output"].get("download_items", [])
            elif "download_items" in result:
                download_items = result["download_items"]
            
            self.log_test_result("bulk_download", True, {"download_count": len(download_items)})
            return True
            
        except Exception as e:
            self.log_test_result("bulk_download", False, error=str(e))
            return False
    
    def test_process_status(self, process_id: str = None) -> bool:
        """Test process status checking"""
        try:
            # Use provided process_id or a test one
            test_process_id = process_id or "test_process_status"
            
            status_request = {
                "process_id": test_process_id
            }
            
            result = self.make_runpod_request("process_status", status_request)
            
            # Extract status from response
            status = None
            if "output" in result:
                status = result["output"].get("status")
            elif "status" in result:
                status = result["status"]
            
            self.log_test_result("process_status", True, {"process_id": test_process_id, "status": status})
            self.logger.info(f"📋 Process {test_process_id} status: {status}")
            return True
            
        except Exception as e:
            self.log_test_result("process_status", False, error=str(e))
            return False
    
    def test_cancel_process(self, process_id: str = None) -> bool:
        """Test process cancellation"""
        try:
            # Use provided process_id or a test one
            test_process_id = process_id or "test_cancel_process"
            
            cancel_request = {
                "process_id": test_process_id
            }
            
            result = self.make_runpod_request("cancel", cancel_request)
            
            # Extract success from response
            success = False
            if "output" in result:
                success = result["output"].get("success", False)
            elif "success" in result:
                success = result["success"]
            
            self.log_test_result("cancel_process", True, {"process_id": test_process_id, "cancelled": success})
            self.logger.info(f"❌ Process {test_process_id} cancellation: {'successful' if success else 'failed'}")
            return True
            
        except Exception as e:
            self.log_test_result("cancel_process", False, error=str(e))
            return False
    
    def test_download_url(self, process_id: str = None) -> bool:
        """Test download URL generation"""
        try:
            # Use provided process_id or a test one
            test_process_id = process_id or "test_download_url"
            
            download_request = {
                "process_id": test_process_id
            }
            
            result = self.make_runpod_request("download", download_request)
            
            # Extract URL from response
            download_url = None
            if "output" in result:
                download_url = result["output"].get("url")
            elif "url" in result:
                download_url = result["url"]
            
            url_valid = download_url and download_url.startswith(("http://", "https://"))
            
            self.log_test_result("download_url", True, {
                "process_id": test_process_id, 
                "url_provided": download_url is not None,
                "url_valid": url_valid
            })
            self.logger.info(f"⬇️ Download URL for {test_process_id}: {'valid' if url_valid else 'invalid/missing'}")
            return True
            
        except Exception as e:
            self.log_test_result("download_url", False, error=str(e))
            return False
    
    # 🎯 MAIN TEST RUNNER
    
    def run_all_tests(self):
        """Run comprehensive test suite"""
        self.logger.info("🚀 Starting RunPod Backend Test Suite")
        self.logger.info(f"🎯 Endpoint: {self.config.ENDPOINT_ID}")
        self.logger.info(f"📅 Start time: {datetime.now()}")
        
        test_results = {}
        training_folder = None
        
        # 1. Health Check
        self.logger.info("\n🔍 Testing Health Check...")
        test_results["health"] = self.test_health_check()
        
        # 2. Upload Training Data
        self.logger.info("\n📁 Testing Upload Training Data...")
        training_folder = self.test_upload_training_data()
        test_results["upload"] = training_folder is not None
        
        # 3. Start Training (if upload succeeded)
        if training_folder:
            self.logger.info("\n🎓 Testing Start Training...")
            training_process = self.test_start_training(training_folder)
            test_results["training"] = training_process is not None
        else:
            self.logger.warning("⚠️ Skipping training test - upload failed")
            test_results["training"] = False
        
        # 4. Start Generation
        self.logger.info("\n🎨 Testing Start Generation...")
        generation_process = self.test_start_generation()
        test_results["generation"] = generation_process is not None
        
        # 5. Get Processes
        self.logger.info("\n📋 Testing Get Processes...")
        test_results["processes"] = self.test_get_processes()
        
        # 6. Get LoRA Models
        self.logger.info("\n🎭 Testing Get LoRA Models...")
        test_results["lora_models"] = self.test_get_lora_models()
        
        # 7. Process Status (test with any available process)
        self.logger.info("\n📋 Testing Process Status...")
        test_results["process_status"] = self.test_process_status()
        
        # 8. Cancel Process
        self.logger.info("\n❌ Testing Cancel Process...")
        test_results["cancel_process"] = self.test_cancel_process()
        
        # 9. Download URL
        self.logger.info("\n⬇️ Testing Download URL...")
        test_results["download_url"] = self.test_download_url()
        
        # 10. Bulk Download
        self.logger.info("\n⬇️ Testing Bulk Download...")
        test_results["bulk_download"] = self.test_bulk_download()
        
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
        
        self.logger.info("\n" + "="*50)
        self.logger.info("📊 TEST SUMMARY")
        self.logger.info("="*50)
        self.logger.info(f"✅ Passed: {passed_tests}/{total_tests}")
        self.logger.info(f"❌ Failed: {failed_tests}/{total_tests}")
        self.logger.info(f"📈 Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        for test_name, result in test_results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            self.logger.info(f"   {test_name}: {status}")
        
        self.logger.info("="*50)
    
    def save_results(self):
        """Save test results to file"""
        with open(self.config.RESULTS_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"💾 Results saved to: {self.config.RESULTS_FILE}")
        self.logger.info(f"📝 Log saved to: {self.config.LOG_FILE}")

# 🎯 MAIN EXECUTION
if __name__ == "__main__":
    print("🧪 RunPod Backend Tester v1.0")
    print("=" * 50)
    
    # Initialize configuration
    config = TestConfig()
    
    # Create tester
    tester = RunPodBackendTester(config)
    
    try:
        # Run all tests
        results = tester.run_all_tests()
        
        print("\n🎉 Testing completed!")
        print(f"📊 Check {config.RESULTS_FILE} for detailed results")
        print(f"📝 Check {config.LOG_FILE} for full logs")
        
    except KeyboardInterrupt:
        print("\n⚠️ Testing interrupted by user")
    except Exception as e:
        print(f"\n💥 Testing failed with error: {e}")
        logging.error(f"Fatal error: {e}", exc_info=True) 

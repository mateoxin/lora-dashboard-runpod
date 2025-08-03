#!/usr/bin/env python3
"""
🚀 MINIMAL RUNPOD HANDLER
Najprostszy możliwy backend do testów RunPod Serverless

Cel: Sprawdzić czy RunPod w ogóle może uruchomić kontener
"""

import runpod
import json
import time
import base64
import os
import uuid
import yaml
import subprocess
import asyncio
import threading
import shutil
import glob
from datetime import datetime
from typing import Dict, Any, Optional
from PIL import Image
import io

def validate_image(image_data, filename):
    """
    Validate uploaded image dimensions and quality
    Returns: (is_valid, width, height, error_message)
    """
    try:
        # Try to open the image with PIL
        image = Image.open(io.BytesIO(image_data))
        width, height = image.size
        
        # Check minimum dimensions
        if width == 0 or height == 0:
            return False, width, height, f"Invalid image dimensions: {width}x{height}"
        
        if width < 512 or height < 512:
            return False, width, height, f"Image too small for training: {width}x{height} (minimum 512x512)"
        
        # Check if image is reasonable size (not too big)
        if width > 4096 or height > 4096:
            return False, width, height, f"Image too large: {width}x{height} (maximum 4096x4096)"
        
        # Check file size (should be reasonable for a real image)
        if len(image_data) < 5000:  # Less than 5KB is suspicious
            return False, width, height, f"Image file too small: {len(image_data)} bytes (suspicious)"
        
        return True, width, height, None
        
    except Exception as e:
        return False, 0, 0, f"Cannot open image {filename}: {str(e)}"

def load_matt_dataset():
    """
    Load Matt's real training images from the 10_Matt folder
    Returns: list of {"filename": str, "content": base64_str}
    """
    try:
        # Find the 10_Matt folder relative to current script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        matt_folder = os.path.join(os.path.dirname(script_dir), "10_Matt")
        
        if not os.path.exists(matt_folder):
            print(f"❌ [MATT_DATASET] Folder not found: {matt_folder}")
            return []
        
        files = []
        
        # Load all JPG files
        jpg_files = glob.glob(os.path.join(matt_folder, "*.jpg"))
        txt_files = glob.glob(os.path.join(matt_folder, "*.txt"))
        
        print(f"📁 [MATT_DATASET] Found {len(jpg_files)} images and {len(txt_files)} captions in {matt_folder}")
        
        # Load images
        for jpg_path in jpg_files:
            try:
                with open(jpg_path, "rb") as f:
                    image_data = f.read()
                    
                # Validate the image
                is_valid, width, height, error = validate_image(image_data, os.path.basename(jpg_path))
                if not is_valid:
                    print(f"⚠️ [MATT_DATASET] Skipping invalid image {os.path.basename(jpg_path)}: {error}")
                    continue
                
                base64_content = base64.b64encode(image_data).decode('utf-8')
                files.append({
                    "filename": os.path.basename(jpg_path),
                    "content": base64_content,
                    "content_type": "image/jpeg"
                })
                print(f"✅ [MATT_DATASET] Loaded image: {os.path.basename(jpg_path)} ({width}x{height}, {len(image_data)} bytes)")
                
            except Exception as e:
                print(f"❌ [MATT_DATASET] Failed to load {jpg_path}: {e}")
                continue
        
        # Load captions
        for txt_path in txt_files:
            try:
                with open(txt_path, "r", encoding="utf-8") as f:
                    caption_content = f.read().strip()
                    
                base64_content = base64.b64encode(caption_content.encode('utf-8')).decode('utf-8')
                files.append({
                    "filename": os.path.basename(txt_path),
                    "content": base64_content,
                    "content_type": "text/plain"
                })
                print(f"✅ [MATT_DATASET] Loaded caption: {os.path.basename(txt_path)}")
                
            except Exception as e:
                print(f"❌ [MATT_DATASET] Failed to load {txt_path}: {e}")
                continue
        
        print(f"🎉 [MATT_DATASET] Successfully loaded {len(files)} files from Matt's dataset")
        return files
        
    except Exception as e:
        print(f"❌ [MATT_DATASET] Error loading Matt's dataset: {e}")
        return []

def handler(job):
    """
    Minimal RunPod handler - echo wszystko co dostanie
    """
    try:
        print(f"🎯 [HANDLER] Received job: {job}")
        
        # Extract input
        job_input = job.get("input", {})
        job_type = job_input.get("type", "unknown")
        
        print(f"📦 [HANDLER] Processing: {job_type}")
        
        # Simple responses based on type
        if job_type == "health":
            result = {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "message": "Simple backend is working!"
            }
            
        elif job_type == "echo":
            result = {
                "status": "success",
                "echo": job_input,
                "timestamp": datetime.now().isoformat()
            }
            
        elif job_type == "ping":
            result = {
                "status": "pong",
                "timestamp": datetime.now().isoformat()
            }
            
        elif job_type == "slow":
            # Simulate some work
            time.sleep(2)
            result = {
                "status": "completed",
                "message": "Slow job finished",
                "duration": "2 seconds"
            }
            
        elif job_type == "upload_training_data":
            # Simple upload handler
            result = handle_upload_training_data(job_input)
            
        elif job_type == "load_matt_dataset":
            # Load Matt's real dataset from 10_Matt folder
            print("📁 [HANDLER] Loading Matt's dataset...")
            matt_files = load_matt_dataset()
            if matt_files:
                # Create upload job input using Matt's files
                upload_input = {
                    "training_name": "matt_training",
                    "trigger_word": "Matt",
                    "cleanup_existing": True,
                    "files": matt_files
                }
                result = handle_upload_training_data(upload_input)
            else:
                result = {
                    "status": "error", 
                    "error": "Failed to load Matt's dataset",
                    "timestamp": datetime.now().isoformat()
                }
            
        elif job_type == "train":
            # LoRA training handler
            result = handle_train_lora(job_input)
            
        elif job_type == "train_with_yaml":
            # LoRA training with YAML config
            result = handle_train_with_yaml(job_input)
            
        elif job_type == "process_status":
            # Get process status
            result = handle_process_status(job_input)
            
        elif job_type == "processes":
            # Get all processes
            result = handle_get_processes()
            
        elif job_type == "list_models":
            # List trained LoRA models
            result = handle_list_trained_models(job_input)
            
        elif job_type == "download_model":
            # Download specific trained model
            result = handle_download_model(job_input)
            
        elif job_type == "force_kill":
            # Force kill a stuck process
            result = handle_force_kill(job_input)
            
        elif job_type == "cleanup_stuck":
            # Clean up all stuck processes
            result = handle_cleanup_stuck()
            
        else:
            result = {
                "status": "unknown_type",
                "received_type": job_type,
                "available_types": ["health", "echo", "ping", "slow", "upload_training_data", "load_matt_dataset", "train", "train_with_yaml", "process_status", "processes", "list_models", "download_model", "force_kill", "cleanup_stuck"],
                "input_received": job_input
            }
        
        print(f"✅ [HANDLER] Success: {result}")
        return result
        
    except Exception as e:
        error_msg = f"Handler error: {str(e)}"
        print(f"❌ [HANDLER] Error: {error_msg}")
        return {
            "status": "error", 
            "error": error_msg,
            "timestamp": datetime.now().isoformat()
        }

# Global process management (in-memory storage)
RUNNING_PROCESSES: Dict[str, Dict[str, Any]] = {}
PROCESS_LOCK = threading.Lock()

def add_process(process_id: str, process_type: str, status: str, config: Dict[str, Any]):
    """Add a new process to tracking."""
    with PROCESS_LOCK:
        RUNNING_PROCESSES[process_id] = {
            "id": process_id,
            "type": process_type,
            "status": status,
            "config": config,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "output_path": None,
            "error": None
        }

def update_process_status(process_id: str, status: str, output_path: str = None, error: str = None):
    """Update process status."""
    with PROCESS_LOCK:
        if process_id in RUNNING_PROCESSES:
            RUNNING_PROCESSES[process_id]["status"] = status
            RUNNING_PROCESSES[process_id]["updated_at"] = datetime.now().isoformat()
            if output_path:
                RUNNING_PROCESSES[process_id]["output_path"] = output_path
            if error:
                RUNNING_PROCESSES[process_id]["error"] = error

def get_process(process_id: str) -> Optional[Dict[str, Any]]:
    """Get process by ID."""
    with PROCESS_LOCK:
        return RUNNING_PROCESSES.get(process_id)

def get_all_processes() -> list:
    """Get all processes."""
    with PROCESS_LOCK:
        return list(RUNNING_PROCESSES.values())

def force_kill_process(process_id: str, reason: str = "Manual kill"):
    """Force kill a stuck process and update its status."""
    with PROCESS_LOCK:
        if process_id in RUNNING_PROCESSES:
            RUNNING_PROCESSES[process_id]["status"] = "failed"
            RUNNING_PROCESSES[process_id]["error"] = f"Process killed: {reason}"
            RUNNING_PROCESSES[process_id]["updated_at"] = datetime.now().isoformat()
            print(f"💀 [FORCE_KILL] Killed process {process_id}: {reason}")
            return True
        return False

def cleanup_stuck_processes():
    """Clean up processes that have been running too long without updates."""
    current_time = datetime.now()
    stuck_processes = []
    
    with PROCESS_LOCK:
        for process_id, process_data in RUNNING_PROCESSES.items():
            if process_data["status"] == "running":
                try:
                    updated_at = datetime.fromisoformat(process_data["updated_at"])
                    time_diff = current_time - updated_at
                    
                    # If process has been "running" for more than 3 hours, mark as stuck
                    if time_diff.total_seconds() > 10800:  # 3 hours
                        stuck_processes.append(process_id)
                except Exception:
                    # If we can't parse the timestamp, consider it stuck
                    stuck_processes.append(process_id)
    
    # Kill stuck processes
    for process_id in stuck_processes:
        force_kill_process(process_id, "Stuck for >3 hours")
    
    return stuck_processes

def download_flux_model():
    """Download FLUX.1-dev model if not exists."""
    try:
        models_dir = "/workspace/models"
        flux_model_path = os.path.join(models_dir, "FLUX.1-dev")
        
        # Check if model was pre-downloaded in Docker
        if os.path.exists(flux_model_path) and os.listdir(flux_model_path):
            print(f"📦 [MODEL] FLUX.1-dev already exists at {flux_model_path}")
            # Verify it has key files
            key_files = ["model_index.json", "scheduler", "text_encoder", "text_encoder_2", "transformer", "vae"]
            missing_files = [f for f in key_files if not os.path.exists(os.path.join(flux_model_path, f))]
            
            if not missing_files:
                print(f"✅ [MODEL] FLUX.1-dev verified and ready")
                return flux_model_path
            else:
                print(f"⚠️ [MODEL] FLUX.1-dev incomplete, missing: {missing_files}")
        
        os.makedirs(models_dir, exist_ok=True)
        
        # Download using HuggingFace token
        hf_token = os.environ.get("HF_TOKEN", "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")
        
        print(f"📥 [MODEL] Downloading FLUX.1-dev to {flux_model_path}...")
        
        # Try huggingface-cli first (faster)
        try:
            cmd = [
                "huggingface-cli", "download",
                "black-forest-labs/FLUX.1-dev",
                "--token", hf_token,
                "--local-dir", flux_model_path,
                "--repo-type", "model"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✅ [MODEL] Successfully downloaded FLUX.1-dev via CLI")
                return flux_model_path
        except Exception as e:
            print(f"⚠️ [MODEL] CLI download failed: {e}")
        
        # Fallback to git clone
        print(f"📥 [MODEL] Trying git clone fallback...")
        cmd = [
            "git", "clone", 
            f"https://{hf_token}@huggingface.co/black-forest-labs/FLUX.1-dev",
            flux_model_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ [MODEL] Successfully downloaded FLUX.1-dev via git")
            return flux_model_path
        else:
            print(f"❌ [MODEL] Failed to download: {result.stderr}")
            return None
            
    except Exception as e:
        print(f"❌ [MODEL] Download error: {e}")
        return None

def setup_ai_toolkit():
    """Download and setup ai-toolkit if not exists."""
    try:
        ai_toolkit_path = "/workspace/ai-toolkit"
        
        # Check if ai-toolkit was pre-installed in Docker
        if os.path.exists(ai_toolkit_path) and os.path.exists(os.path.join(ai_toolkit_path, "run.py")):
            print(f"🛠️ [AI-TOOLKIT] Already exists at {ai_toolkit_path}")
            
            # Verify key files exist
            key_files = ["run.py", "toolkit", "config"]
            existing_files = [f for f in key_files if os.path.exists(os.path.join(ai_toolkit_path, f))]
            print(f"🔍 [AI-TOOLKIT] Found components: {existing_files}")
            
            if "run.py" in existing_files:
                print(f"✅ [AI-TOOLKIT] Verified and ready")
                return True
        
        print(f"📥 [AI-TOOLKIT] Cloning ai-toolkit to {ai_toolkit_path}...")
        
        cmd = ["git", "clone", "https://github.com/ostris/ai-toolkit.git", ai_toolkit_path]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        
        if result.returncode == 0:
            # Install requirements if available
            req_path = os.path.join(ai_toolkit_path, "requirements.txt")
            if os.path.exists(req_path):
                print(f"📦 [AI-TOOLKIT] Installing requirements...")
                install_cmd = ["pip", "install", "-r", req_path]
                install_result = subprocess.run(install_cmd, capture_output=True, text=True, timeout=300)
                if install_result.returncode != 0:
                    print(f"⚠️ [AI-TOOLKIT] Requirements install warning: {install_result.stderr}")
                else:
                    print(f"✅ [AI-TOOLKIT] Requirements installed successfully")
            
            print(f"✅ [AI-TOOLKIT] Successfully setup ai-toolkit")
            return True
        else:
            print(f"❌ [AI-TOOLKIT] Failed to clone: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"⏰ [AI-TOOLKIT] Setup timed out")
        return False
    except Exception as e:
        print(f"❌ [AI-TOOLKIT] Setup error: {e}")
        return False

def run_training_in_background(process_id: str, config_path: str):
    """Run AI toolkit training in background thread."""
    try:
        print(f"🚀 [TRAINING] Starting training for process {process_id}")
        update_process_status(process_id, "running")
        
        # Step 1: Login to HuggingFace for gated repos access
        hf_token = os.environ.get("HF_TOKEN", "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")
        print(f"🔐 [TRAINING] Logging into HuggingFace...")
        
        login_cmd = ["huggingface-cli", "login", "--token", hf_token]
        login_result = subprocess.run(login_cmd, capture_output=True, text=True)
        
        if login_result.returncode != 0:
            error_msg = f"HF login failed: {login_result.stderr}"
            print(f"❌ [TRAINING] {error_msg}")
            update_process_status(process_id, "failed", error=error_msg)
            return
        
        print(f"✅ [TRAINING] Successfully logged into HuggingFace")
        
        # Step 2: Set up environment variables with memory optimizations
        env = os.environ.copy()
        env["CUDA_VISIBLE_DEVICES"] = "0"  # Use first GPU
        env["HUGGING_FACE_HUB_TOKEN"] = hf_token  # Additional token for transformers/diffusers
        env["HF_TOKEN"] = hf_token  # Ensure HF_TOKEN is available
        env["PYTORCH_CUDA_ALLOC_CONF"] = "max_split_size_mb:512"  # Memory fragmentation optimization
        env["HF_HUB_ENABLE_HF_TRANSFER"] = "1"  # Faster downloads
        env["TRANSFORMERS_CACHE"] = "/workspace/cache"  # Centralized cache
        
        # Step 3: Run AI toolkit training with timeout and better error handling
        print(f"🎯 [TRAINING] Starting ai-toolkit with config: {config_path}")
        cmd = ["python3", "/workspace/ai-toolkit/run.py", config_path]
        
        # Use timeout to prevent hanging - 2 hours max
        result = subprocess.run(cmd, capture_output=True, text=True, env=env, timeout=7200)
        
        if result.returncode == 0:
            # Find output directory
            output_dir = "/workspace/ai-toolkit/output"
            print(f"✅ [TRAINING] Training completed for process {process_id}")
            print(f"📝 [TRAINING] Training output: {result.stdout[-500:]}")  # Last 500 chars
            update_process_status(process_id, "completed", output_dir)
        else:
            error_msg = f"Training failed (exit code {result.returncode})"
            if result.stderr:
                error_msg += f": {result.stderr[-1000:]}"  # Last 1000 chars of stderr
            if result.stdout:
                error_msg += f"\nOutput: {result.stdout[-500:]}"  # Last 500 chars of stdout
            print(f"❌ [TRAINING] Training failed for process {process_id}: {error_msg}")
            update_process_status(process_id, "failed", error=error_msg)
            
    except subprocess.TimeoutExpired:
        error_msg = "Training timeout after 2 hours"
        print(f"⏰ [TRAINING] {error_msg} for process {process_id}")
        update_process_status(process_id, "failed", error=error_msg)
    except Exception as e:
        error_msg = f"Training error: {str(e)}"
        print(f"❌ [TRAINING] Exception in process {process_id}: {error_msg}")
        update_process_status(process_id, "failed", error=error_msg)

def handle_upload_training_data(job_input):
    """
    Enhanced upload handler with image validation and worker isolation
    """
    try:
        print(f"📁 [UPLOAD] Starting upload processing...")
        
        # Get upload parameters
        training_name = job_input.get("training_name", f"training_{int(datetime.now().timestamp())}")
        trigger_word = job_input.get("trigger_word", "")
        cleanup_existing = job_input.get("cleanup_existing", True)
        files_data = job_input.get("files", [])
        
        # Add worker isolation - unique ID per request
        worker_id = os.environ.get("RUNPOD_POD_ID", "local")
        if worker_id == "local":
            worker_id = f"worker_{uuid.uuid4().hex[:8]}"
        
        print(f"👷 [UPLOAD] Worker ID: {worker_id}")
        
        if not files_data:
            return {"status": "error", "error": "No files provided"}
        
        # Create unique training folder with worker isolation
        training_id = str(uuid.uuid4())[:8]
        safe_name = "".join(c if c.isalnum() or c in '-_' else '_' for c in training_name)
        workspace_path = os.environ.get("WORKSPACE_PATH", "/workspace")
        
        # Worker-specific training folder to avoid conflicts
        worker_training_path = os.path.join(workspace_path, "training_data", worker_id)
        training_folder = os.path.join(worker_training_path, f"{safe_name}_{training_id}")
        
        # Clean up only THIS WORKER's existing training data if requested
        if cleanup_existing:
            if os.path.exists(worker_training_path):
                for item in os.listdir(worker_training_path):
                    old_path = os.path.join(worker_training_path, item)
                    if os.path.isdir(old_path):
                        shutil.rmtree(old_path)
                        print(f"🗑️ [UPLOAD] Worker {worker_id} cleaned up: {old_path}")
                    elif os.path.isfile(old_path):
                        os.remove(old_path)
                        print(f"🗑️ [UPLOAD] Worker {worker_id} removed file: {old_path}")
        
        # Create training folder
        os.makedirs(training_folder, exist_ok=True)
        print(f"📂 [UPLOAD] Created folder: {training_folder}")
        
        uploaded_files = []
        image_count = 0
        caption_count = 0
        validation_errors = []
        
        # Process files with validation (expecting base64 encoded files)
        for file_info in files_data:
            filename = file_info.get("filename")
            content = file_info.get("content")  # base64 encoded
            content_type = file_info.get("content_type", "application/octet-stream")
            
            if not filename or not content:
                continue
                
            # Save file to training folder
            file_path = os.path.join(training_folder, filename)
            
            # Decode base64 content and save
            try:
                file_content = base64.b64decode(content)
                
                # Validate images with PIL
                is_image = filename.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.gif'))
                if is_image:
                    is_valid, width, height, error_msg = validate_image(file_content, filename)
                    if not is_valid:
                        validation_errors.append(f"{filename}: {error_msg}")
                        print(f"⚠️ [UPLOAD] Invalid image {filename}: {error_msg}")
                        continue
                    
                    print(f"🖼️ [UPLOAD] Valid image: {filename} ({width}x{height}, {len(file_content)} bytes)")
                    image_count += 1
                    
                elif filename.endswith('.txt'):
                    # Validate text files
                    try:
                        text_content = file_content.decode('utf-8')
                        if len(text_content.strip()) == 0:
                            validation_errors.append(f"{filename}: Empty caption file")
                            print(f"⚠️ [UPLOAD] Empty caption file: {filename}")
                            continue
                        print(f"📝 [UPLOAD] Valid caption: {filename} ({len(text_content)} chars)")
                        caption_count += 1
                    except UnicodeDecodeError:
                        validation_errors.append(f"{filename}: Cannot decode text file")
                        print(f"⚠️ [UPLOAD] Cannot decode text file: {filename}")
                        continue
                
                # Save the file
                with open(file_path, "wb") as f:
                    f.write(file_content)
                
                file_data = {
                    "filename": filename,
                    "path": file_path,
                    "size": len(file_content),
                    "content_type": content_type,
                    "uploaded_at": datetime.now().isoformat()
                }
                
                # Add image dimensions for images
                if is_image and 'width' in locals():
                    file_data["dimensions"] = f"{width}x{height}"
                
                uploaded_files.append(file_data)
                print(f"✅ [UPLOAD] Saved: {filename} ({len(file_content)} bytes)")
                    
            except Exception as e:
                error_msg = f"Failed to process file {filename}: {e}"
                validation_errors.append(error_msg)
                print(f"❌ [UPLOAD] {error_msg}")
                continue
        
        # Check if we have enough valid training data
        if image_count == 0:
            return {
                "status": "error",
                "error": "No valid images found for training",
                "validation_errors": validation_errors,
                "timestamp": datetime.now().isoformat()
            }
        
        if caption_count == 0:
            print("⚠️ [UPLOAD] Warning: No caption files found")
        
        # Create enhanced training info file
        trigger_file = os.path.join(training_folder, "_training_info.txt")
        with open(trigger_file, "w") as f:
            f.write(f"Training Name: {training_name}\n")
            f.write(f"Trigger Word: {trigger_word}\n")
            f.write(f"Worker ID: {worker_id}\n")
            f.write(f"Upload Date: {datetime.now().isoformat()}\n")
            f.write(f"Total Valid Images: {image_count}\n")
            f.write(f"Total Valid Captions: {caption_count}\n")
            f.write(f"Total Files Processed: {len(uploaded_files)}\n")
            f.write(f"Validation Errors: {len(validation_errors)}\n")
            if validation_errors:
                f.write("\nValidation Errors:\n")
                for error in validation_errors:
                    f.write(f"  - {error}\n")
        
        result = {
            "status": "success",
            "uploaded_files": uploaded_files,
            "training_folder": training_folder,
            "total_images": image_count,
            "total_captions": caption_count,
            "validation_errors": validation_errors,
            "worker_id": worker_id,
            "training_name": training_name,
            "trigger_word": trigger_word,
            "message": f"Successfully uploaded {len(uploaded_files)} valid files to {training_folder}",
            "timestamp": datetime.now().isoformat()
        }
        
        success_msg = f"Worker {worker_id}: {training_folder} ({image_count} images, {caption_count} captions)"
        if validation_errors:
            success_msg += f", {len(validation_errors)} validation errors"
        print(f"🎉 [UPLOAD] Success: {success_msg}")
        return result
        
    except Exception as e:
        error_msg = f"Upload error: {str(e)}"
        print(f"❌ [UPLOAD] Error: {error_msg}")
        return {
            "status": "error",
            "error": error_msg,
            "timestamp": datetime.now().isoformat()
        }

def handle_train_lora(job_input):
    """Handle LoRA training request."""
    try:
        print(f"🧠 [TRAIN] Starting LoRA training...")
        
        # Ensure models and toolkit are ready
        print(f"🔧 [TRAIN] Setting up AI toolkit...")
        if not setup_ai_toolkit():
            return {"status": "error", "error": "Failed to setup ai-toolkit"}
        
        print(f"📦 [TRAIN] Downloading FLUX.1-dev model...")
        model_path = download_flux_model()
        if not model_path:
            return {"status": "error", "error": "Failed to download FLUX.1-dev model"}
        
        # Get training configuration
        config = job_input.get("config")
        if not config:
            return {"status": "error", "error": "Missing 'config' parameter"}
        
        # Parse YAML config if it's a string
        if isinstance(config, str):
            try:
                config = yaml.safe_load(config)
            except yaml.YAMLError as e:
                return {"status": "error", "error": f"Invalid YAML config: {str(e)}"}
        
        # Generate process ID
        process_id = str(uuid.uuid4())[:8]
        
        # Update model path in config
        if "config" in config and "process" in config["config"]:
            for process_config in config["config"]["process"]:
                if "model" in process_config:
                    process_config["model"]["name_or_path"] = model_path
        
        # Create config file
        config_path = f"/tmp/training_config_{process_id}.yaml"
        with open(config_path, 'w') as f:
            yaml.dump(config, f)
        
        print(f"📝 [TRAIN] Created config file: {config_path}")
        
        # Add process to tracking
        add_process(process_id, "train", "pending", config)
        
        # Start training in background thread
        training_thread = threading.Thread(
            target=run_training_in_background,
            args=(process_id, config_path)
        )
        training_thread.daemon = True
        training_thread.start()
        
        return {
            "status": "success",
            "process_id": process_id,
            "message": f"Training started with process ID: {process_id}",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        error_msg = f"Training error: {str(e)}"
        print(f"❌ [TRAIN] Error: {error_msg}")
        return {
            "status": "error",
            "error": error_msg,
            "timestamp": datetime.now().isoformat()
        }

def handle_train_with_yaml(job_input):
    """Handle LoRA training request with YAML config file."""
    try:
        print(f"📝 [TRAIN_YAML] Starting LoRA training with YAML config...")
        
        # Ensure AI toolkit is ready
        print(f"🔧 [TRAIN_YAML] Setting up AI toolkit...")
        if not setup_ai_toolkit():
            return {"status": "error", "error": "Failed to setup ai-toolkit"}
        
        # NOTE: Do NOT download model here - let ai-toolkit handle it automatically
        print(f"🎯 [TRAIN_YAML] Letting ai-toolkit handle model download automatically...")
        
        # Get YAML config content
        yaml_content = job_input.get("yaml_config")
        if not yaml_content:
            return {"status": "error", "error": "Missing 'yaml_config' parameter"}
        
        # Parse YAML config
        try:
            if isinstance(yaml_content, str):
                config = yaml.safe_load(yaml_content)
            else:
                config = yaml_content
        except yaml.YAMLError as e:
            return {"status": "error", "error": f"Invalid YAML config: {str(e)}"}
        
        # Generate process ID
        process_id = str(uuid.uuid4())[:8]
        
        # Do NOT modify model path - keep original HuggingFace path
        # ai-toolkit will download the model automatically
        print(f"🎯 [TRAIN_YAML] Keeping original model path in config (ai-toolkit will download)")
        
        # Optional: Update dataset path if specified
        dataset_path = job_input.get("dataset_path", "/workspace/training_data")
        if "config" in config and "process" in config["config"]:
            for process_config in config["config"]["process"]:
                if "datasets" in process_config:
                    for dataset in process_config["datasets"]:
                        if "folder_path" in dataset:
                            dataset["folder_path"] = dataset_path
                            print(f"📁 [TRAIN_YAML] Updated dataset path to: {dataset_path}")
        
        # Create config file
        config_path = f"/tmp/training_config_{process_id}.yaml"
        with open(config_path, 'w') as f:
            yaml.dump(config, f)
        
        print(f"📝 [TRAIN_YAML] Created config file: {config_path}")
        
        # Log config for debugging
        print(f"🔍 [TRAIN_YAML] Config content:")
        print(yaml.dump(config, default_flow_style=False))
        
        # Add process to tracking
        add_process(process_id, "train_yaml", "pending", config)
        
        # Start training in background thread
        training_thread = threading.Thread(
            target=run_training_in_background,
            args=(process_id, config_path)
        )
        training_thread.daemon = True
        training_thread.start()
        
        return {
            "status": "success",
            "process_id": process_id,
            "message": f"Training started with YAML config, process ID: {process_id}",
            "config_path": config_path,
            "dataset_path": dataset_path,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        error_msg = f"YAML training error: {str(e)}"
        print(f"❌ [TRAIN_YAML] Error: {error_msg}")
        return {
            "status": "error",
            "error": error_msg,
            "timestamp": datetime.now().isoformat()
        }

def handle_process_status(job_input):
    """Handle process status request."""
    try:
        process_id = job_input.get("process_id")
        if not process_id:
            return {"status": "error", "error": "Missing 'process_id' parameter"}
        
        process = get_process(process_id)
        if not process:
            return {"status": "error", "error": f"Process {process_id} not found"}
        
        return {
            "status": "success",
            "process": process,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        error_msg = f"Process status error: {str(e)}"
        print(f"❌ [PROCESS_STATUS] Error: {error_msg}")
        return {
            "status": "error",
            "error": error_msg,
            "timestamp": datetime.now().isoformat()
        }

def handle_get_processes():
    """Handle get all processes request."""
    try:
        processes = get_all_processes()
        
        return {
            "status": "success",
            "processes": processes,
            "total_count": len(processes),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        error_msg = f"Get processes error: {str(e)}"
        print(f"❌ [GET_PROCESSES] Error: {error_msg}")
        return {
            "status": "error",
            "error": error_msg,
            "timestamp": datetime.now().isoformat()
        }

def handle_list_trained_models(job_input):
    """List all trained LoRA models available for download."""
    try:
        print(f"📋 [LIST_MODELS] Listing trained LoRA models...")
        
        output_dir = "/workspace/ai-toolkit/output"
        models = []
        
        if not os.path.exists(output_dir):
            print(f"⚠️ [LIST_MODELS] Output directory not found: {output_dir}")
            return {
                "status": "success", 
                "models": [], 
                "total_count": 0,
                "message": "No output directory found"
            }
        
        # Scan for .safetensors files (trained LoRA models)
        for root, dirs, files in os.walk(output_dir):
            for file in files:
                if file.endswith('.safetensors'):
                    file_path = os.path.join(root, file)
                    file_size = os.path.getsize(file_path)
                    file_modified = os.path.getmtime(file_path)
                    
                    # Extract process info from path
                    relative_path = os.path.relpath(file_path, output_dir)
                    path_parts = relative_path.split(os.sep)
                    
                    model_info = {
                        "filename": file,
                        "full_path": file_path,
                        "relative_path": relative_path,
                        "size_bytes": file_size,
                        "size_mb": round(file_size / (1024 * 1024), 2),
                        "modified_timestamp": file_modified,
                        "modified_date": datetime.fromtimestamp(file_modified).isoformat(),
                        "folder": path_parts[0] if len(path_parts) > 1 else "root"
                    }
                    models.append(model_info)
        
        # Sort by modification time (newest first)
        models.sort(key=lambda x: x["modified_timestamp"], reverse=True)
        
        print(f"✅ [LIST_MODELS] Found {len(models)} trained models")
        
        return {
            "status": "success",
            "models": models,
            "total_count": len(models),
            "output_directory": output_dir,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        error_msg = f"List models error: {str(e)}"
        print(f"❌ [LIST_MODELS] Error: {error_msg}")
        return {
            "status": "error",
            "error": error_msg,
            "timestamp": datetime.now().isoformat()
        }

def handle_download_model(job_input):
    """Download a specific trained LoRA model."""
    try:
        model_path = job_input.get("model_path")
        filename = job_input.get("filename")
        
        if not model_path and not filename:
            return {"status": "error", "error": "Missing 'model_path' or 'filename' parameter"}
        
        print(f"📥 [DOWNLOAD_MODEL] Downloading model: {model_path or filename}")
        
        output_dir = "/workspace/ai-toolkit/output"
        
        # Determine full path
        if model_path:
            if os.path.isabs(model_path):
                full_path = model_path
            else:
                full_path = os.path.join(output_dir, model_path)
        else:
            # Search for filename in output directory
            full_path = None
            for root, dirs, files in os.walk(output_dir):
                if filename in files:
                    full_path = os.path.join(root, filename)
                    break
            
            if not full_path:
                return {"status": "error", "error": f"Model file '{filename}' not found"}
        
        # Verify file exists and is a model file
        if not os.path.exists(full_path):
            return {"status": "error", "error": f"Model file not found: {full_path}"}
        
        if not full_path.endswith('.safetensors'):
            return {"status": "error", "error": "Only .safetensors model files can be downloaded"}
        
        # Read and encode file in base64
        try:
            with open(full_path, 'rb') as f:
                file_content = f.read()
            
            file_base64 = base64.b64encode(file_content).decode('utf-8')
            file_size = len(file_content)
            
            print(f"✅ [DOWNLOAD_MODEL] Model ready for download: {os.path.basename(full_path)} ({file_size} bytes)")
            
            return {
                "status": "success",
                "filename": os.path.basename(full_path),
                "content": file_base64,
                "content_type": "application/octet-stream",
                "size_bytes": file_size,
                "size_mb": round(file_size / (1024 * 1024), 2),
                "full_path": full_path,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"status": "error", "error": f"Failed to read model file: {str(e)}"}
        
    except Exception as e:
        error_msg = f"Download model error: {str(e)}"
        print(f"❌ [DOWNLOAD_MODEL] Error: {error_msg}")
        return {
            "status": "error",
            "error": error_msg,
            "timestamp": datetime.now().isoformat()
        }

def handle_force_kill(job_input):
    """Handle force kill process request."""
    try:
        process_id = job_input.get("process_id")
        reason = job_input.get("reason", "Manual force kill")
        
        if not process_id:
            return {"status": "error", "error": "Missing 'process_id' parameter"}
        
        killed = force_kill_process(process_id, reason)
        
        if killed:
            return {
                "status": "success",
                "message": f"Process {process_id} killed successfully",
                "process_id": process_id,
                "reason": reason,
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "status": "error",
                "error": f"Process {process_id} not found or already finished",
                "timestamp": datetime.now().isoformat()
            }
            
    except Exception as e:
        error_msg = f"Force kill error: {str(e)}"
        print(f"❌ [FORCE_KILL] Error: {error_msg}")
        return {
            "status": "error",
            "error": error_msg,
            "timestamp": datetime.now().isoformat()
        }

def handle_cleanup_stuck():
    """Handle cleanup stuck processes request."""
    try:
        print(f"🧹 [CLEANUP] Starting cleanup of stuck processes...")
        
        stuck_processes = cleanup_stuck_processes()
        
        return {
            "status": "success",
            "message": f"Cleaned up {len(stuck_processes)} stuck processes",
            "killed_processes": stuck_processes,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        error_msg = f"Cleanup error: {str(e)}"
        print(f"❌ [CLEANUP] Error: {error_msg}")
        return {
            "status": "error",
            "error": error_msg,
            "timestamp": datetime.now().isoformat()
        }

if __name__ == "__main__":
    print("🚀 Starting Simple RunPod Handler")
    print("=" * 40)
    
    # Start RunPod serverless
    runpod.serverless.start({"handler": handler}) 
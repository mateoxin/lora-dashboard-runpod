"""
RunPod Serverless Handler for LoRA Dashboard Backend
Wraps FastAPI logic for serverless deployment
"""

import runpod
import asyncio
import logging
import os
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import your existing services
try:
    from app.services.gpu_manager import GPUManager
    from app.services.process_manager import ProcessManager
    from app.services.storage_service import StorageService
    from app.services.lora_service import LoRAService
    from app.core.config import get_settings
except ImportError as e:
    logger.error(f"Failed to import services: {e}")
    # Fallback for testing
    GPUManager = None
    ProcessManager = None
    StorageService = None
    LoRAService = None

# Global service instances (initialized on first use)
_services_initialized = False
_gpu_manager = None
_process_manager = None
_storage_service = None
_lora_service = None

async def initialize_services():
    """Initialize services once"""
    global _services_initialized, _gpu_manager, _process_manager, _storage_service, _lora_service
    
    if _services_initialized:
        return
    
    try:
        logger.info("Initializing LoRA Dashboard services...")
        
        settings = get_settings() if get_settings else None
        
        # Initialize services
        _storage_service = StorageService() if StorageService else None
        _lora_service = LoRAService(_storage_service) if LoRAService and _storage_service else None
        _gpu_manager = GPUManager(max_concurrent=10) if GPUManager else None
        _process_manager = ProcessManager(
            gpu_manager=_gpu_manager,
            storage_service=_storage_service,
            redis_url=os.environ.get("REDIS_URL", "redis://localhost:6379/0")
        ) if ProcessManager else None
        
        if _process_manager:
            await _process_manager.initialize()
        
        _services_initialized = True
        logger.info("Services initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize services: {e}")
        raise

async def async_handler(event: Dict[str, Any]) -> Dict[str, Any]:
    """
    Main RunPod Serverless handler function
    
    Expected input format:
    {
        "input": {
            "type": "train" | "generate" | "health" | "processes" | "lora",
            "config": "YAML configuration string",
            "process_id": "optional process ID for status check"
        }
    }
    """
    try:
        # Initialize services if needed
        await initialize_services()
        
        job_input = event.get("input", {})
        job_type = job_input.get("type")
        
        logger.info(f"Processing job type: {job_type}")
        
        if job_type == "health":
            return await handle_health_check()
            
        elif job_type == "train":
            return await handle_training(job_input)
            
        elif job_type == "generate":
            return await handle_generation(job_input)
            
        elif job_type == "processes":
            return await handle_get_processes(job_input)
            
        elif job_type == "process_status":
            return await handle_process_status(job_input)
            
        elif job_type == "lora":
            return await handle_get_lora_models()
            
        elif job_type == "cancel":
            return await handle_cancel_process(job_input)
            
        elif job_type == "download":
            return await handle_download_url(job_input)
            
        else:
            return {
                "error": f"Unknown job type: {job_type}",
                "supported_types": ["health", "train", "generate", "processes", "process_status", "lora", "cancel", "download"]
            }
            
    except Exception as e:
        logger.error(f"Handler error: {e}", exc_info=True)
        return {"error": str(e)}

async def handle_health_check() -> Dict[str, Any]:
    """Health check endpoint"""
    try:
        services_status = {}
        
        if _process_manager:
            services_status["process_manager"] = "healthy"
        if _storage_service:
            services_status["storage"] = await _storage_service.health_check()
        if _gpu_manager:
            services_status["gpu_manager"] = _gpu_manager.get_status()
            
        return {
            "success": True,
            "data": {
                "status": "healthy",
                "services": services_status,
                "worker_id": os.environ.get("RUNPOD_WORKER_ID", "local"),
                "environment": "serverless"
            },
            "message": "LoRA Dashboard API is healthy"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Health check failed: {str(e)}"
        }

async def handle_training(job_input: Dict[str, Any]) -> Dict[str, Any]:
    """Handle training request"""
    try:
        config = job_input.get("config")
        if not config:
            return {"error": "Missing 'config' parameter"}
        
        if not _process_manager:
            return {"error": "Process manager not initialized"}
        
        process_id = await _process_manager.start_training(config)
        
        return {
            "success": True,
            "data": {"process_id": process_id},
            "message": "Training process started successfully"
        }
    except Exception as e:
        logger.error(f"Training error: {e}")
        return {"error": f"Failed to start training: {str(e)}"}

async def handle_generation(job_input: Dict[str, Any]) -> Dict[str, Any]:
    """Handle generation request"""
    try:
        config = job_input.get("config")
        if not config:
            return {"error": "Missing 'config' parameter"}
        
        if not _process_manager:
            return {"error": "Process manager not initialized"}
        
        process_id = await _process_manager.start_generation(config)
        
        return {
            "success": True,
            "data": {"process_id": process_id},
            "message": "Generation process started successfully"
        }
    except Exception as e:
        logger.error(f"Generation error: {e}")
        return {"error": f"Failed to start generation: {str(e)}"}

async def handle_get_processes(job_input: Dict[str, Any]) -> Dict[str, Any]:
    """Handle get processes request"""
    try:
        if not _process_manager:
            return {"error": "Process manager not initialized"}
        
        processes = await _process_manager.get_all_processes()
        return {"processes": processes}
    except Exception as e:
        logger.error(f"Get processes error: {e}")
        return {"error": f"Failed to get processes: {str(e)}"}

async def handle_process_status(job_input: Dict[str, Any]) -> Dict[str, Any]:
    """Handle process status request"""
    try:
        process_id = job_input.get("process_id")
        if not process_id:
            return {"error": "Missing 'process_id' parameter"}
        
        if not _process_manager:
            return {"error": "Process manager not initialized"}
        
        process = await _process_manager.get_process(process_id)
        if not process:
            return {"error": "Process not found"}
            
        return {
            "success": True,
            "data": process
        }
    except Exception as e:
        logger.error(f"Process status error: {e}")
        return {"error": f"Failed to get process status: {str(e)}"}

async def handle_get_lora_models() -> Dict[str, Any]:
    """Handle get LoRA models request"""
    try:
        if not _lora_service:
            return {"error": "LoRA service not initialized"}
        
        models = await _lora_service.get_available_models()
        return {"models": models}
    except Exception as e:
        logger.error(f"Get LoRA models error: {e}")
        return {"error": f"Failed to get LoRA models: {str(e)}"}

async def handle_cancel_process(job_input: Dict[str, Any]) -> Dict[str, Any]:
    """Handle cancel process request"""
    try:
        process_id = job_input.get("process_id")
        if not process_id:
            return {"error": "Missing 'process_id' parameter"}
        
        if not _process_manager:
            return {"error": "Process manager not initialized"}
        
        success = await _process_manager.cancel_process(process_id)
        if not success:
            return {"error": "Process not found or cannot be cancelled"}
            
        return {
            "success": True,
            "message": "Process cancelled successfully"
        }
    except Exception as e:
        logger.error(f"Cancel process error: {e}")
        return {"error": f"Failed to cancel process: {str(e)}"}

async def handle_download_url(job_input: Dict[str, Any]) -> Dict[str, Any]:
    """Handle download URL request"""
    try:
        process_id = job_input.get("process_id")
        if not process_id:
            return {"error": "Missing 'process_id' parameter"}
        
        if not _process_manager:
            return {"error": "Process manager not initialized"}
        
        # Check if process exists and is completed
        process = await _process_manager.get_process(process_id)
        if not process:
            return {"error": "Process not found"}
            
        if process.status != "completed":
            return {"error": "Process not completed"}
        
        if not _storage_service:
            return {"error": "Storage service not initialized"}
            
        # Get download URL
        url = await _storage_service.get_download_url(process_id)
        
        return {
            "success": True,
            "data": {"url": url}
        }
    except Exception as e:
        logger.error(f"Download URL error: {e}")
        return {"error": f"Failed to get download URL: {str(e)}"}

# Sync wrapper for RunPod
def handler(event: Dict[str, Any]) -> Dict[str, Any]:
    """Synchronous wrapper for async handler"""
    try:
        # Run async handler in event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(async_handler(event))
        loop.close()
        return result
    except Exception as e:
        logger.error(f"Handler wrapper error: {e}", exc_info=True)
        return {"error": str(e)}

# Start RunPod Serverless
if __name__ == "__main__":
    logger.info("Starting LoRA Dashboard RunPod Serverless Handler")
    runpod.serverless.start({
        "handler": handler,
        "return_aggregate_stream": True
    }) 
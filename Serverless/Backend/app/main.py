"""
LoRA Dashboard FastAPI Backend
Serverless Training & Generation Suite
"""

import asyncio
import logging
import os
import yaml
from contextlib import asynccontextmanager
from typing import Any, Dict, List

from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import get_settings
from app.core.models import (
    ApiResponse,
    GenerateRequest,
    TrainRequest,
    Process,
    LoRAModel,
    ProcessesResponse,
    LoRAResponse,
)
from app.services.gpu_manager import GPUManager
from app.services.process_manager import ProcessManager
from app.services.storage_service import StorageService
from app.services.lora_service import LoRAService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Global service instances
gpu_manager: GPUManager = None
process_manager: ProcessManager = None
storage_service: StorageService = None
lora_service: LoRAService = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize and cleanup services."""
    global gpu_manager, process_manager, storage_service, lora_service
    
    try:
        settings = get_settings()
        
        if settings.mock_mode:
            logger.info("🧪 Starting in MOCK MODE - using fake services for testing")
            from app.services.mock_services import (
                MockProcessManager, MockStorageService, 
                MockGPUManager, MockLoRAService
            )
            
            # Initialize mock services
            storage_service = MockStorageService()
            lora_service = MockLoRAService(storage_service)
            gpu_manager = MockGPUManager()
            process_manager = MockProcessManager()
            
            logger.info("✅ Mock services initialized - ready for testing!")
        else:
            logger.info("🚀 Starting in PRODUCTION MODE - using real services")
            
            # Initialize real services
            storage_service = StorageService()
            lora_service = LoRAService(storage_service)
            gpu_manager = GPUManager(max_concurrent=settings.max_concurrent_jobs)
            process_manager = ProcessManager(
                gpu_manager=gpu_manager,
                storage_service=storage_service,
                redis_url=settings.redis_url
            )
            
            await process_manager.initialize()
            logger.info("✅ Real services initialized successfully")
        
        yield
        
    except Exception as e:
        logger.error(f"Failed to initialize services: {e}")
        raise
    finally:
        # Cleanup
        logger.info("Cleaning up services...")
        if process_manager:
            await process_manager.cleanup()


# Create FastAPI app
app = FastAPI(
    title="LoRA Dashboard API",
    description="Serverless Training & Generation Suite",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Dependency to get services
def get_process_manager() -> ProcessManager:
    if process_manager is None:
        raise HTTPException(status_code=500, detail="Process manager not initialized")
    return process_manager


def get_lora_service() -> LoRAService:
    if lora_service is None:
        raise HTTPException(status_code=500, detail="LoRA service not initialized")
    return lora_service


def get_storage_service() -> StorageService:
    if storage_service is None:
        raise HTTPException(status_code=500, detail="Storage service not initialized")
    return storage_service


# Initialize adapter conditionally
from app.core.config import get_settings
settings = get_settings()

if not settings.mock_mode:
    from app.adapters.runpod_adapter import RunPodAdapter
    adapter = RunPodAdapter()
else:
    adapter = None  # Will use direct services in mock mode

# Health endpoint
@app.get("/api/health", response_model=ApiResponse)
async def health_check() -> ApiResponse:
    """Health check endpoint."""
    try:
        if settings.mock_mode:
            # Mock mode - return mock health status
            return ApiResponse(
                success=True,
                data={
                    "status": "healthy",
                    "services": {
                        "process_manager": "healthy",
                        "storage": "healthy", 
                        "gpu_manager": gpu_manager.get_status() if gpu_manager else {"status": "mock"}
                    }
                },
                message="API is healthy (Mock Mode)"
            )
        else:
            result = await adapter.health_check()
            return ApiResponse(**result)
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return ApiResponse(
            success=False,
            error=f"Health check failed: {str(e)}"
        )


# Training endpoint
@app.post("/api/train", response_model=ApiResponse)
async def start_training(
    request: TrainRequest,
    background_tasks: BackgroundTasks
) -> ApiResponse:
    """Start a new training process."""
    try:
        if settings.mock_mode:
            # Mock mode - use mock service directly
            process_id = await process_manager.start_training(request.config)
            return ApiResponse(
                success=True,
                data={"process_id": process_id},
                message="Training process started successfully (Mock Mode)"
            )
        else:
            result = await adapter.start_training(request)
            return ApiResponse(**result)
    except Exception as e:
        logger.error(f"Failed to start training: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start training: {str(e)}")


# Generation endpoint
@app.post("/api/generate", response_model=ApiResponse)
async def start_generation(
    request: GenerateRequest,
    background_tasks: BackgroundTasks
) -> ApiResponse:
    """Start a new generation process."""
    try:
        if settings.mock_mode:
            # Mock mode - use mock service directly
            process_id = await process_manager.start_generation(request.config)
            return ApiResponse(
                success=True,
                data={"process_id": process_id},
                message="Generation started successfully (Mock Mode)"
            )
        else:
            result = await adapter.start_generation(request)
            return ApiResponse(**result)
    except Exception as e:
        logger.error(f"Failed to start generation: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start generation: {str(e)}")


# Processes endpoint
@app.get("/api/processes", response_model=ProcessesResponse)
async def get_processes() -> ProcessesResponse:
    """Get all processes with their current status."""
    try:
        if settings.mock_mode:
            # Mock mode - use mock service directly
            processes = await process_manager.get_all_processes()
            return ProcessesResponse(processes=processes)
        else:
            result = await adapter.get_processes()
            return ProcessesResponse(processes=result.get("processes", []))
    except Exception as e:
        logger.error(f"Failed to get processes: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get processes: {str(e)}")


# Process detail endpoint
@app.get("/api/processes/{process_id}", response_model=ApiResponse[Process])
async def get_process(process_id: str) -> ApiResponse[Process]:
    """Get specific process details."""
    try:
        result = await adapter.get_process(process_id)
        if result.get("error"):
            raise HTTPException(status_code=404, detail=result["error"])
            
        return ApiResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get process {process_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get process: {str(e)}")


# Cancel process endpoint
@app.delete("/api/processes/{process_id}", response_model=ApiResponse)
async def cancel_process(process_id: str) -> ApiResponse:
    """Cancel a running process."""
    try:
        result = await adapter.cancel_process(process_id)
        if result.get("error"):
            raise HTTPException(status_code=404, detail=result["error"])
            
        return ApiResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to cancel process {process_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to cancel process: {str(e)}")


# LoRA models endpoint
@app.get("/api/lora", response_model=LoRAResponse)
async def get_lora_models() -> LoRAResponse:
    """Get available LoRA models."""
    try:
        if settings.mock_mode:
            # Mock mode - use mock service directly
            models = await lora_service.get_available_models()
            return LoRAResponse(models=models)
        else:
            result = await adapter.get_lora_models()
            return LoRAResponse(models=result.get("models", []))
    except Exception as e:
        logger.error(f"Failed to get LoRA models: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get LoRA models: {str(e)}")


# Download endpoint
@app.get("/api/download/{process_id}", response_model=ApiResponse[Dict[str, str]])
async def get_download_url(process_id: str) -> ApiResponse[Dict[str, str]]:
    """Get presigned download URL for process results."""
    try:
        result = await adapter.get_download_url(process_id)
        if result.get("error"):
            if "not found" in result["error"].lower():
                raise HTTPException(status_code=404, detail=result["error"])
            else:
                raise HTTPException(status_code=400, detail=result["error"])
        
        return ApiResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get download URL for {process_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get download URL: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    
    settings = get_settings()
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.port,
        reload=settings.debug
    ) 
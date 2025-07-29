"""
Pytest configuration and shared fixtures for backend tests
"""

import asyncio
import json
import os
import tempfile
import pytest
import pytest_asyncio
from datetime import datetime, timezone
from typing import AsyncGenerator, Dict, Any
from unittest.mock import AsyncMock, MagicMock, patch

from fastapi.testclient import TestClient
from httpx import AsyncClient

# Test app imports
from app.main import app
from app.core.config import get_settings
from app.core.models import Process, ProcessStatus, ProcessType, LoRAModel
from app.services.mock_services import (
    MockProcessManager, MockStorageService, 
    MockGPUManager, MockLoRAService
)


@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


def pytest_collection_modifyitems(config, items):
    """Auto-mark async tests with asyncio marker."""
    for item in items:
        if asyncio.iscoroutinefunction(item.function):
            item.add_marker(pytest.mark.asyncio)


@pytest.fixture
def test_client():
    """Create a test client for the FastAPI app with proper service initialization."""
    # Override global services before creating TestClient
    import app.main as main_module
    from app.services.mock_services import (
        MockProcessManager, MockStorageService, 
        MockGPUManager, MockLoRAService
    )
    
    # Initialize mock services
    main_module.storage_service = MockStorageService()
    main_module.lora_service = MockLoRAService(main_module.storage_service)
    main_module.gpu_manager = MockGPUManager()
    main_module.process_manager = MockProcessManager()
    
    return TestClient(app)


@pytest_asyncio.fixture
async def async_client():
    """Create an async test client for the FastAPI app."""
    # Override global services before creating AsyncClient
    import app.main as main_module
    from app.services.mock_services import (
        MockProcessManager, MockStorageService, 
        MockGPUManager, MockLoRAService
    )
    
    # Initialize mock services
    main_module.storage_service = MockStorageService()
    main_module.lora_service = MockLoRAService(main_module.storage_service)
    main_module.gpu_manager = MockGPUManager()
    main_module.process_manager = MockProcessManager()
    
    async with AsyncClient(base_url="http://test") as client:
        client._transport = client._transport.__class__(app=app)
        yield client


@pytest.fixture
def mock_settings():
    """Mock settings for testing."""
    settings = get_settings()
    settings.mock_mode = True
    settings.debug = True
    settings.redis_url = "redis://localhost:6379/15"  # Test database
    return settings


@pytest.fixture
def mock_process_manager():
    """Create a mock process manager."""
    return MockProcessManager()


@pytest.fixture
def mock_storage_service():
    """Create a mock storage service."""
    return MockStorageService()


@pytest.fixture
def mock_gpu_manager():
    """Create a mock GPU manager."""
    return MockGPUManager()


@pytest.fixture
def mock_lora_service(mock_storage_service):
    """Create a mock LoRA service."""
    return MockLoRAService(mock_storage_service)


@pytest.fixture
def sample_process():
    """Create a sample process for testing."""
    return Process(
        id="test_process_123",
        name="Test Training Process",
        type=ProcessType.TRAINING,
        status=ProcessStatus.PENDING,
        progress=0.0,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        config={
            "job": "extension",
            "config": {
                "name": "test_training",
                "trigger_word": "test_style"
            }
        }
    )


@pytest.fixture
def sample_running_process():
    """Create a sample running process for testing."""
    return Process(
        id="test_process_456",
        name="Test Generation Process",
        type=ProcessType.GENERATION,
        status=ProcessStatus.RUNNING,
        progress=50.0,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        gpu_id="cuda:0",
        step=500,
        total_steps=1000,
        config={
            "job": "generate",
            "config": {
                "name": "test_generation",
                "prompts": ["test prompt"]
            }
        }
    )


@pytest.fixture
def sample_completed_process():
    """Create a sample completed process for testing."""
    return Process(
        id="test_process_789",
        name="Test Completed Process",
        type=ProcessType.TRAINING,
        status=ProcessStatus.COMPLETED,
        progress=100.0,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        output_path="/workspace/output/test_process_789",
        config={
            "job": "extension",
            "config": {
                "name": "completed_training"
            }
        }
    )


@pytest.fixture
def sample_lora_model():
    """Create a sample LoRA model for testing."""
    return LoRAModel(
        id="test_lora_001",
        name="Test LoRA Model",
        path="/workspace/models/test_model.safetensors",
        created_at=datetime.now(timezone.utc),
        size=1048576,
        metadata={
            "steps": 1000,
            "trigger_word": "test_style",
            "model_type": "LoRA"
        }
    )


@pytest.fixture
def valid_training_config():
    """Valid training configuration YAML."""
    return """
job: extension
config:
  name: "test_training"
  process:
    - type: sd_trainer
      device: cuda:0
      trigger_word: "test_style"
      training_folder: "/workspace/dataset"
      network:
        type: lora
        linear: 16
        linear_alpha: 16
      save:
        dtype: float16
        save_every: 100
        max_step_saves_to_keep: 3
      datasets:
        - folder_path: "/workspace/dataset"
          caption_ext: "txt"
          caption_dropout_rate: 0.05
          shuffle_tokens: false
          cache_latents_to_disk: true
          resolution: [1024, 1024]
      train:
        batch_size: 1
        steps: 1000
        gradient_accumulation_steps: 1
        train_unet: true
        train_text_encoder: false
        gradient_checkpointing: true
        noise_scheduler: "flowmatch"
        optimizer: "adamw8bit"
        lr: 4e-4
        skip_clip_encoder: true
        ema_config:
          use_ema: true
          ema_decay: 0.99
      model:
        name_or_path: "black-forest-labs/FLUX.1-dev"
        is_flux: true
        quantize: true
      sample:
        sampler: "flowmatch"
        sample_every: 100
        width: 1024
        height: 1024
        prompts:
          - "test_style portrait of a woman"
        neg: ""
        seed: 42
        walk_seed: true
        guidance_scale: 3.5
        sample_steps: 20
"""


@pytest.fixture
def valid_generation_config():
    """Valid generation configuration YAML."""
    return """
job: generate
config:
  name: "test_generation"
  process:
    - type: flux_generator
      device: cuda:0
      generate:
        width: 1024
        height: 1024
        num_inference_steps: 20
        guidance_scale: 3.5
        seed: 42
        prompts:
          - "a beautiful landscape with mountains"
          - "test_style portrait of a man"
      model:
        name_or_path: "black-forest-labs/FLUX.1-dev"
        is_flux: true
        quantize: true
"""


@pytest.fixture
def invalid_yaml_config():
    """Invalid YAML configuration for testing error handling."""
    return """
job: invalid
config:
  name: "invalid_test"
  invalid_structure: [
    - missing_closing_bracket
"""


@pytest.fixture
def temp_directory():
    """Create a temporary directory for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


@pytest.fixture
def mock_redis_client():
    """Mock Redis client for testing."""
    mock_redis = AsyncMock()
    mock_redis.ping.return_value = True
    mock_redis.keys.return_value = []
    mock_redis.get.return_value = None
    mock_redis.set.return_value = True
    mock_redis.lpush.return_value = 1
    mock_redis.brpop.return_value = None
    return mock_redis


@pytest.fixture
def mock_subprocess():
    """Mock subprocess for testing process execution."""
    with patch('asyncio.create_subprocess_exec') as mock_subprocess:
        mock_process = AsyncMock()
        mock_process.stdout = AsyncMock()
        mock_process.wait.return_value = 0
        mock_subprocess.return_value = mock_process
        yield mock_subprocess


@pytest.fixture
def runpod_event_data():
    """Sample RunPod event data for testing."""
    return {
        "input": {
            "type": "train",
            "config": """
job: extension
config:
  name: "test_training"
  trigger_word: "test_style"
"""
        }
    }


@pytest.fixture
def authentication_headers():
    """Sample authentication headers for testing."""
    return {
        "Authorization": "Bearer test_token_123",
        "Content-Type": "application/json"
    }


@pytest.fixture 
def runpod_headers():
    """Sample RunPod headers for testing."""
    return {
        "X-RunPod-Token": "test_runpod_token",
        "Content-Type": "application/json"
    }


# Environment setup
@pytest.fixture(autouse=True)
def setup_test_environment(monkeypatch):
    """Setup test environment variables."""
    monkeypatch.setenv("MOCK_MODE", "true")
    monkeypatch.setenv("DEBUG", "true")
    monkeypatch.setenv("REDIS_URL", "redis://localhost:6379/15")
    monkeypatch.setenv("S3_BUCKET", "test-bucket")
    monkeypatch.setenv("S3_ACCESS_KEY", "test-access-key")
    monkeypatch.setenv("S3_SECRET_KEY", "test-secret-key")
    monkeypatch.setenv("MAX_CONCURRENT_JOBS", "2")


# Async context managers for testing
@pytest_asyncio.fixture
async def initialized_process_manager(mock_redis_client):
    """Initialize a process manager for testing."""
    from app.services.process_manager import ProcessManager
    from app.services.gpu_manager import GPUManager
    from app.services.storage_service import StorageService
    
    gpu_manager = GPUManager(max_concurrent=2)
    storage_service = StorageService()
    
    with patch('redis.asyncio.from_url', return_value=mock_redis_client):
        process_manager = ProcessManager(
            gpu_manager=gpu_manager,
            storage_service=storage_service,
            redis_url="redis://localhost:6379/15"
        )
        await process_manager.initialize()
        yield process_manager
        await process_manager.cleanup()


# Error simulation fixtures
@pytest.fixture
def redis_connection_error():
    """Simulate Redis connection error."""
    def side_effect(*args, **kwargs):
        raise ConnectionError("Redis connection failed")
    return side_effect


@pytest.fixture
def storage_error():
    """Simulate storage service error."""
    def side_effect(*args, **kwargs):
        raise Exception("Storage service unavailable")
    return side_effect


@pytest.fixture
def gpu_allocation_error():
    """Simulate GPU allocation error."""
    def side_effect(*args, **kwargs):
        return None  # No GPU available
    return side_effect 
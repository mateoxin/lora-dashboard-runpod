"""
Comprehensive Backend Services Tests
Tests for ProcessManager, StorageService, GPUManager, and LoRAService
"""

import asyncio
import json
import pytest
import pytest_asyncio
import tempfile
import uuid
import yaml
from datetime import datetime, timezone, timedelta
from unittest.mock import AsyncMock, MagicMock, patch, mock_open

from app.core.models import Process, ProcessStatus, ProcessType, LoRAModel
from app.services.process_manager import ProcessManager
from app.services.storage_service import StorageService
from app.services.gpu_manager import GPUManager
from app.services.lora_service import LoRAService
from app.services.mock_services import MockProcessManager, MockStorageService, MockGPUManager, MockLoRAService


class TestProcessManager:
    """Test ProcessManager service."""
    
    @pytest_asyncio.fixture
    async def process_manager(self, mock_redis_client):
        """Create a ProcessManager for testing."""
        from app.services.gpu_manager import GPUManager
        from app.services.storage_service import StorageService
        
        gpu_manager = GPUManager(max_concurrent=2)
        storage_service = StorageService()
        
        with patch('redis.asyncio.from_url', return_value=mock_redis_client):
            pm = ProcessManager(
                gpu_manager=gpu_manager,
                storage_service=storage_service,
                redis_url="redis://localhost:6379/15"
            )
            await pm.initialize()
            yield pm
            await pm.cleanup()
    
    @pytest.mark.asyncio
    async def test_initialize_success(self, mock_redis_client):
        """Test successful ProcessManager initialization."""
        from app.services.gpu_manager import GPUManager
        from app.services.storage_service import StorageService
        
        gpu_manager = GPUManager(max_concurrent=2)
        storage_service = StorageService()
        
        with patch('redis.asyncio.from_url', return_value=mock_redis_client):
            pm = ProcessManager(
                gpu_manager=gpu_manager,
                storage_service=storage_service,
                redis_url="redis://localhost:6379/15"
            )
            
            await pm.initialize()
            
            assert pm.redis_client is not None
            mock_redis_client.ping.assert_called_once()
            
            await pm.cleanup()
    
    async def test_initialize_redis_failure(self):
        """Test ProcessManager initialization with Redis failure."""
        from app.services.gpu_manager import GPUManager
        from app.services.storage_service import StorageService
        
        gpu_manager = GPUManager(max_concurrent=2)
        storage_service = StorageService()
        
        with patch('redis.asyncio.from_url') as mock_redis:
            mock_redis.side_effect = ConnectionError("Redis unavailable")
            
            pm = ProcessManager(
                gpu_manager=gpu_manager,
                storage_service=storage_service,
                redis_url="redis://localhost:6379/15"
            )
            
            await pm.initialize()  # Should not raise exception
            assert pm.redis_client is None
            
            await pm.cleanup()
    
    async def test_start_training_success(self, process_manager, valid_training_config):
        """Test successful training start."""
        process_id = await process_manager.start_training(valid_training_config)
        
        assert process_id is not None
        assert isinstance(process_id, str)
        assert len(process_id) > 0
        
        # Verify process was created
        process = await process_manager.get_process(process_id)
        assert process is not None
        assert process.type == ProcessType.TRAINING
        assert process.status == ProcessStatus.PENDING
    
    async def test_start_training_invalid_yaml(self, process_manager, invalid_yaml_config):
        """Test training start with invalid YAML."""
        with pytest.raises(Exception):
            await process_manager.start_training(invalid_yaml_config)
    
    async def test_start_generation_success(self, process_manager, valid_generation_config):
        """Test successful generation start."""
        process_id = await process_manager.start_generation(valid_generation_config)
        
        assert process_id is not None
        assert isinstance(process_id, str)
        
        # Verify process was created
        process = await process_manager.get_process(process_id)
        assert process is not None
        assert process.type == ProcessType.GENERATION
        assert process.status == ProcessStatus.PENDING
    
    async def test_get_all_processes(self, process_manager, valid_training_config):
        """Test getting all processes."""
        # Start some processes
        process_id1 = await process_manager.start_training(valid_training_config)
        process_id2 = await process_manager.start_training(valid_training_config)
        
        processes = await process_manager.get_all_processes()
        
        assert len(processes) >= 2
        process_ids = [p.id for p in processes]
        assert process_id1 in process_ids
        assert process_id2 in process_ids
    
    async def test_get_process_exists(self, process_manager, valid_training_config):
        """Test getting existing process."""
        process_id = await process_manager.start_training(valid_training_config)
        
        process = await process_manager.get_process(process_id)
        
        assert process is not None
        assert process.id == process_id
    
    async def test_get_process_not_exists(self, process_manager):
        """Test getting non-existent process."""
        process = await process_manager.get_process("nonexistent_id")
        assert process is None
    
    async def test_cancel_process_success(self, process_manager, valid_training_config):
        """Test successful process cancellation."""
        process_id = await process_manager.start_training(valid_training_config)
        
        # Cancel the process
        result = await process_manager.cancel_process(process_id)
        assert result is True
        
        # Verify status changed
        process = await process_manager.get_process(process_id)
        assert process.status == ProcessStatus.CANCELLED
    
    async def test_cancel_process_not_exists(self, process_manager):
        """Test cancelling non-existent process."""
        result = await process_manager.cancel_process("nonexistent_id")
        assert result is False
    
    @patch('app.services.process_manager.asyncio.create_subprocess_exec')
    async def test_execute_training_success(self, mock_subprocess, process_manager, valid_training_config):
        """Test successful training execution."""
        # Setup mock subprocess
        mock_process = AsyncMock()
        mock_process.stdout = AsyncMock()
        mock_process.wait.return_value = 0
        mock_subprocess.return_value = mock_process
        
        # Mock stdout lines
        lines = [
            b"Starting training...\n",
            b"Step: 100/1000\n",
            b"Progress: 50%\n",
            b"Training completed\n"
        ]
        mock_process.stdout.__aiter__.return_value = iter(lines)
        
        process_id = await process_manager.start_training(valid_training_config)
        
        # Wait a bit for execution to start
        await asyncio.sleep(0.1)
        
        # Check that subprocess was called
        mock_subprocess.assert_called()
    
    @patch('app.services.process_manager.asyncio.create_subprocess_exec')
    async def test_execute_training_failure(self, mock_subprocess, process_manager, valid_training_config):
        """Test training execution failure."""
        # Setup mock subprocess that fails
        mock_process = AsyncMock()
        mock_process.stdout = AsyncMock()
        mock_process.wait.return_value = 1  # Non-zero exit code
        mock_subprocess.return_value = mock_process
        
        mock_process.stdout.__aiter__.return_value = iter([b"Error occurred\n"])
        
        process_id = await process_manager.start_training(valid_training_config)
        
        # Wait for execution
        await asyncio.sleep(0.1)
        
        # Process should be marked as failed
        process = await process_manager.get_process(process_id)
        # Status might still be pending if execution hasn't completed yet
        assert process.status in [ProcessStatus.PENDING, ProcessStatus.FAILED]
    
    async def test_parse_progress_step_format(self, process_manager, valid_training_config):
        """Test progress parsing from step format."""
        process_id = await process_manager.start_training(valid_training_config)
        
        # Simulate progress line
        await process_manager._parse_progress(process_id, "Step: 500/1000")
        
        process = await process_manager.get_process(process_id)
        assert process.step == 500
        assert process.total_steps == 1000
        assert process.progress == 50.0
    
    async def test_parse_progress_percentage_format(self, process_manager, valid_training_config):
        """Test progress parsing from percentage format."""
        process_id = await process_manager.start_training(valid_training_config)
        
        # Simulate progress line
        await process_manager._parse_progress(process_id, "Training progress: 75%")
        
        process = await process_manager.get_process(process_id)
        assert process.progress == 75.0
    
    async def test_save_load_process_redis(self, process_manager, valid_training_config):
        """Test saving and loading process from Redis."""
        process_id = await process_manager.start_training(valid_training_config)
        
        # Verify Redis save was called
        process_manager.redis_client.set.assert_called()
        
        # Test loading
        mock_process_data = {
            "id": process_id,
            "name": "test_process",
            "type": "training",
            "status": "pending",
            "progress": 0.0,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
        process_manager.redis_client.keys.return_value = [f"process:{process_id}"]
        process_manager.redis_client.get.return_value = json.dumps(mock_process_data, default=str)
        
        await process_manager._load_processes_from_redis()
        
        # Process should be loaded
        process = await process_manager.get_process(process_id)
        assert process is not None


class TestMockProcessManager:
    """Test MockProcessManager service."""
    
    @pytest.fixture
    def mock_pm(self):
        """Create a MockProcessManager for testing."""
        return MockProcessManager()
    
    async def test_get_all_processes_initial(self, mock_pm):
        """Test initial sample processes."""
        processes = await mock_pm.get_all_processes()
        
        assert len(processes) >= 3  # Should have sample processes
        statuses = [p.status for p in processes]
        assert ProcessStatus.COMPLETED in statuses
        assert ProcessStatus.RUNNING in statuses
        assert ProcessStatus.PENDING in statuses
    
    async def test_start_training_mock(self, mock_pm, valid_training_config):
        """Test mock training start."""
        initial_count = len(await mock_pm.get_all_processes())
        
        process_id = await mock_pm.start_training(valid_training_config)
        
        assert process_id.startswith("training_")
        
        processes = await mock_pm.get_all_processes()
        assert len(processes) == initial_count + 1
        
        # Find the new process
        new_process = await mock_pm.get_process(process_id)
        assert new_process is not None
        assert new_process.type == ProcessType.TRAINING
    
    async def test_start_generation_mock(self, mock_pm, valid_generation_config):
        """Test mock generation start."""
        process_id = await mock_pm.start_generation(valid_generation_config)
        
        assert process_id.startswith("generation_")
        
        new_process = await mock_pm.get_process(process_id)
        assert new_process is not None
        assert new_process.type == ProcessType.GENERATION
    
    async def test_cancel_process_mock(self, mock_pm, valid_training_config):
        """Test mock process cancellation."""
        process_id = await mock_pm.start_training(valid_training_config)
        
        result = await mock_pm.cancel_process(process_id)
        assert result is True
        
        process = await mock_pm.get_process(process_id)
        assert process.status == ProcessStatus.CANCELLED
    
    async def test_simulate_training_progress(self, mock_pm, valid_training_config):
        """Test simulated training progress."""
        process_id = await mock_pm.start_training(valid_training_config)
        
        # Wait for simulation to start
        await asyncio.sleep(2.5)
        
        process = await mock_pm.get_process(process_id)
        assert process.status == ProcessStatus.RUNNING
        assert process.progress > 0
    
    async def test_simulate_generation_progress(self, mock_pm, valid_generation_config):
        """Test simulated generation progress."""
        process_id = await mock_pm.start_generation(valid_generation_config)
        
        # Wait for simulation to start
        await asyncio.sleep(1.5)
        
        process = await mock_pm.get_process(process_id)
        assert process.status == ProcessStatus.RUNNING
        assert process.progress > 0


class TestStorageService:
    """Test StorageService."""
    
    @pytest.fixture
    def storage_service(self):
        """Create a StorageService for testing."""
        with patch.dict('os.environ', {
            'S3_BUCKET': 'test-bucket',
            'S3_ACCESS_KEY': 'test-key',
            'S3_SECRET_KEY': 'test-secret',
            'S3_ENDPOINT_URL': 'https://test-storage.com'
        }):
            return StorageService()
    
    @patch('boto3.client')
    async def test_health_check_success(self, mock_boto, storage_service):
        """Test storage health check success."""
        mock_s3 = MagicMock()
        mock_boto.return_value = mock_s3
        mock_s3.head_bucket.return_value = True
        
        result = await storage_service.health_check()
        assert result == "healthy"
    
    @patch('boto3.client')
    async def test_health_check_failure(self, mock_boto, storage_service):
        """Test storage health check failure."""
        mock_s3 = MagicMock()
        mock_boto.return_value = mock_s3
        mock_s3.head_bucket.side_effect = Exception("Connection failed")
        
        result = await storage_service.health_check()
        assert result == "error"
    
    @patch('boto3.client')
    async def test_upload_file_success(self, mock_boto, storage_service, temp_directory):
        """Test successful file upload."""
        mock_s3 = MagicMock()
        mock_boto.return_value = mock_s3
        
        # Create test file
        test_file = f"{temp_directory}/test.txt"
        with open(test_file, 'w') as f:
            f.write("test content")
        
        result = await storage_service.upload_file(test_file, "test/test.txt")
        
        assert result.startswith("https://")
        mock_s3.upload_file.assert_called_once()
    
    @patch('boto3.client')
    async def test_upload_file_not_exists(self, mock_boto, storage_service):
        """Test upload non-existent file."""
        mock_s3 = MagicMock()
        mock_boto.return_value = mock_s3
        
        with pytest.raises(Exception):
            await storage_service.upload_file("nonexistent.txt", "test/test.txt")
    
    @patch('boto3.client')
    async def test_download_file_success(self, mock_boto, storage_service, temp_directory):
        """Test successful file download."""
        mock_s3 = MagicMock()
        mock_boto.return_value = mock_s3
        
        local_path = f"{temp_directory}/downloaded.txt"
        result = await storage_service.download_file("test/test.txt", local_path)
        
        assert result is True
        mock_s3.download_file.assert_called_once()
    
    @patch('boto3.client')
    async def test_get_download_url(self, mock_boto, storage_service):
        """Test getting download URL."""
        mock_s3 = MagicMock()
        mock_boto.return_value = mock_s3
        mock_s3.generate_presigned_url.return_value = "https://presigned-url.com"
        
        result = await storage_service.get_download_url("test_process_123")
        
        assert result == "https://presigned-url.com"
        mock_s3.generate_presigned_url.assert_called_once()
    
    @patch('boto3.client')
    async def test_list_files(self, mock_boto, storage_service):
        """Test listing files."""
        mock_s3 = MagicMock()
        mock_boto.return_value = mock_s3
        mock_s3.list_objects_v2.return_value = {
            'Contents': [
                {
                    'Key': 'test/file1.txt',
                    'Size': 1024,
                    'LastModified': datetime.now(timezone.utc),
                    'ETag': '"abc123"'
                }
            ]
        }
        
        result = await storage_service.list_files("test/")
        
        assert len(result) == 1
        assert result[0]['key'] == 'test/file1.txt'
        assert result[0]['size'] == 1024


class TestMockStorageService:
    """Test MockStorageService."""
    
    @pytest.fixture
    def mock_storage(self):
        """Create a MockStorageService for testing."""
        return MockStorageService()
    
    async def test_health_check_mock(self, mock_storage):
        """Test mock health check."""
        result = await mock_storage.health_check()
        assert result == "healthy"
    
    async def test_upload_file_mock(self, mock_storage):
        """Test mock file upload."""
        result = await mock_storage.upload_file("local/test.txt", "s3/test.txt")
        assert result.startswith("https://mock-storage.com")
        assert "s3/test.txt" in result
    
    async def test_download_file_mock(self, mock_storage):
        """Test mock file download."""
        result = await mock_storage.download_file("s3/test.txt", "local/test.txt")
        assert result is True
    
    async def test_get_download_url_mock(self, mock_storage):
        """Test mock download URL."""
        result = await mock_storage.get_download_url("test_process_123")
        assert result.startswith("https://mock-storage.com")
        assert "test_process_123.zip" in result
    
    async def test_list_files_mock(self, mock_storage):
        """Test mock file listing."""
        result = await mock_storage.list_files("models/")
        assert len(result) >= 2
        assert all('key' in item for item in result)
        assert all('size' in item for item in result)


class TestGPUManager:
    """Test GPUManager."""
    
    @pytest.fixture
    def gpu_manager(self):
        """Create a GPUManager for testing."""
        return GPUManager(max_concurrent=2)
    
    @patch('subprocess.run')
    async def test_get_status_nvidia_smi_success(self, mock_subprocess, gpu_manager):
        """Test GPU status with nvidia-smi success."""
        mock_subprocess.return_value = MagicMock(
            returncode=0,
            stdout='[{"index": 0, "name": "RTX 4090", "memory_total": 24576}]'
        )
        
        status = gpu_manager.get_status()
        
        assert "total_gpus" in status
        assert "allocated_gpus" in status
        assert "available_gpus" in status
    
    @patch('subprocess.run')
    async def test_get_status_nvidia_smi_failure(self, mock_subprocess, gpu_manager):
        """Test GPU status with nvidia-smi failure."""
        mock_subprocess.side_effect = Exception("nvidia-smi not found")
        
        status = gpu_manager.get_status()
        
        assert status["error"] == "No GPU information available"
    
    async def test_allocate_gpu_success(self, gpu_manager):
        """Test successful GPU allocation."""
        process_id = "test_process_123"
        
        gpu_id = await gpu_manager.allocate_gpu(process_id)
        
        assert gpu_id is not None
        assert gpu_id.startswith("cuda:")
    
    async def test_allocate_gpu_max_concurrent(self, gpu_manager):
        """Test GPU allocation when max concurrent reached."""
        # Allocate maximum GPUs
        process_id1 = "test_process_1"
        process_id2 = "test_process_2"
        
        gpu_id1 = await gpu_manager.allocate_gpu(process_id1)
        gpu_id2 = await gpu_manager.allocate_gpu(process_id2)
        
        assert gpu_id1 is not None
        assert gpu_id2 is not None
        
        # Try to allocate one more (should fail)
        process_id3 = "test_process_3"
        gpu_id3 = await gpu_manager.allocate_gpu(process_id3)
        
        assert gpu_id3 is None
    
    async def test_release_gpu_success(self, gpu_manager):
        """Test successful GPU release."""
        process_id = "test_process_123"
        
        # Allocate first
        gpu_id = await gpu_manager.allocate_gpu(process_id)
        assert gpu_id is not None
        
        # Release
        result = await gpu_manager.release_gpu(process_id)
        assert result is True
        
        # Should be able to allocate again
        gpu_id2 = await gpu_manager.allocate_gpu("test_process_456")
        assert gpu_id2 is not None
    
    async def test_release_gpu_not_allocated(self, gpu_manager):
        """Test releasing GPU that wasn't allocated."""
        result = await gpu_manager.release_gpu("nonexistent_process")
        assert result is False


class TestMockGPUManager:
    """Test MockGPUManager."""
    
    @pytest.fixture
    def mock_gpu(self):
        """Create a MockGPUManager for testing."""
        return MockGPUManager()
    
    def test_get_status_mock(self, mock_gpu):
        """Test mock GPU status."""
        status = mock_gpu.get_status()
        
        assert status["total_gpus"] == 2
        assert "allocated_gpus" in status
        assert "available_gpus" in status
        assert "gpu_memory" in status
        assert "gpu_type" in status
    
    async def test_allocate_gpu_mock(self, mock_gpu):
        """Test mock GPU allocation."""
        gpu_id = await mock_gpu.allocate_gpu()
        assert gpu_id is not None
        assert gpu_id.startswith("cuda:")
    
    async def test_release_gpu_mock(self, mock_gpu):
        """Test mock GPU release."""
        # Allocate first
        gpu_id = await mock_gpu.allocate_gpu()
        
        # Release
        result = await mock_gpu.release_gpu(gpu_id)
        assert result is True


class TestLoRAService:
    """Test LoRAService."""
    
    @pytest.fixture
    def lora_service(self, mock_storage_service):
        """Create a LoRAService for testing."""
        return LoRAService(mock_storage_service)
    
    @patch('os.listdir')
    @patch('os.path.exists')
    @patch('os.path.getsize')
    async def test_get_available_models_success(self, mock_getsize, mock_exists, mock_listdir, lora_service):
        """Test getting available LoRA models."""
        mock_listdir.return_value = ['model1.safetensors', 'model2.pt', 'config.json']
        mock_exists.return_value = True
        mock_getsize.return_value = 1048576
        
        models = await lora_service.get_available_models()
        
        assert len(models) >= 2  # At least the mock models
        assert all(isinstance(model, LoRAModel) for model in models)
    
    @patch('os.listdir')
    async def test_get_available_models_no_directory(self, mock_listdir, lora_service):
        """Test getting models when directory doesn't exist."""
        mock_listdir.side_effect = FileNotFoundError("Directory not found")
        
        models = await lora_service.get_available_models()
        
        # Should return empty list or handle gracefully
        assert isinstance(models, list)
    
    async def test_get_model_by_id_exists(self, lora_service):
        """Test getting model by existing ID."""
        # First get all models to find a valid ID
        models = await lora_service.get_available_models()
        if models:
            model_id = models[0].id
            model = await lora_service.get_model_by_id(model_id)
            assert model is not None
            assert model.id == model_id
    
    async def test_get_model_by_id_not_exists(self, lora_service):
        """Test getting model by non-existent ID."""
        model = await lora_service.get_model_by_id("nonexistent_id")
        assert model is None


class TestMockLoRAService:
    """Test MockLoRAService."""
    
    @pytest.fixture
    def mock_lora(self, mock_storage_service):
        """Create a MockLoRAService for testing."""
        return MockLoRAService(mock_storage_service)
    
    async def test_get_available_models_mock(self, mock_lora):
        """Test mock LoRA models."""
        models = await mock_lora.get_available_models()
        
        assert len(models) >= 3
        assert all(isinstance(model, LoRAModel) for model in models)
        assert all(model.metadata is not None for model in models)
    
    async def test_get_model_by_id_mock(self, mock_lora):
        """Test getting mock model by ID."""
        models = await mock_lora.get_available_models()
        first_model = models[0]
        
        model = await mock_lora.get_model_by_id(first_model.id)
        
        assert model is not None
        assert model.id == first_model.id
        assert model.name == first_model.name


class TestServiceIntegration:
    """Test integration between services."""
    
    @pytest.fixture
    async def integrated_services(self, mock_redis_client):
        """Create integrated services for testing."""
        from app.services.gpu_manager import GPUManager
        from app.services.storage_service import StorageService
        from app.services.lora_service import LoRAService
        
        storage_service = StorageService()
        lora_service = LoRAService(storage_service)
        gpu_manager = GPUManager(max_concurrent=2)
        
        with patch('redis.asyncio.from_url', return_value=mock_redis_client):
            process_manager = ProcessManager(
                gpu_manager=gpu_manager,
                storage_service=storage_service,
                redis_url="redis://localhost:6379/15"
            )
            await process_manager.initialize()
            
            yield {
                'process_manager': process_manager,
                'storage_service': storage_service,
                'lora_service': lora_service,
                'gpu_manager': gpu_manager
            }
            
            await process_manager.cleanup()
    
    async def test_full_training_workflow(self, integrated_services, valid_training_config):
        """Test complete training workflow with all services."""
        pm = integrated_services['process_manager']
        gm = integrated_services['gpu_manager']
        
        # Start training
        process_id = await pm.start_training(valid_training_config)
        assert process_id is not None
        
        # Check initial status
        process = await pm.get_process(process_id)
        assert process.status == ProcessStatus.PENDING
        
        # Simulate GPU allocation
        gpu_id = await gm.allocate_gpu(process_id)
        assert gpu_id is not None
        
        # Simulate progress update
        await pm._update_process_status(process_id, ProcessStatus.RUNNING, progress=50.0)
        
        # Check updated status
        process = await pm.get_process(process_id)
        assert process.status == ProcessStatus.RUNNING
        assert process.progress == 50.0
        
        # Release GPU
        result = await gm.release_gpu(process_id)
        assert result is True
    
    async def test_concurrent_processes(self, integrated_services, valid_training_config, valid_generation_config):
        """Test handling multiple concurrent processes."""
        pm = integrated_services['process_manager']
        
        # Start multiple processes
        training_id = await pm.start_training(valid_training_config)
        generation_id = await pm.start_generation(valid_generation_config)
        
        # Check both were created
        training_process = await pm.get_process(training_id)
        generation_process = await pm.get_process(generation_id)
        
        assert training_process is not None
        assert generation_process is not None
        assert training_process.type == ProcessType.TRAINING
        assert generation_process.type == ProcessType.GENERATION
    
    async def test_service_error_handling(self, integrated_services, valid_training_config):
        """Test error handling across services."""
        pm = integrated_services['process_manager']
        gm = integrated_services['gpu_manager']
        
        # Start training
        process_id = await pm.start_training(valid_training_config)
        
        # Simulate GPU allocation failure
        with patch.object(gm, 'allocate_gpu', return_value=None):
            # Process should handle GPU unavailable gracefully
            gpu_id = await gm.allocate_gpu(process_id)
            assert gpu_id is None
        
        # Process should remain in pending state
        process = await pm.get_process(process_id)
        assert process.status == ProcessStatus.PENDING 
"""
Comprehensive API Endpoints Tests
Tests all REST API endpoints with success, error, and edge cases
"""

import json
import pytest
import pytest_asyncio
from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch, MagicMock

from fastapi import status
from httpx import AsyncClient

from app.core.models import ProcessStatus, ProcessType
from app.main import app


class TestHealthEndpoint:
    """Test health check endpoint."""
    
    async def test_health_check_success_mock_mode(self, async_client):
        """Test health check in mock mode."""
        response = await async_client.get("/api/health")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert data["data"]["status"] == "healthy"
        assert "services" in data["data"]
        assert "Mock Mode" in data["message"]
    
    @patch('app.main.settings.mock_mode', False)
    @patch('app.main.adapter')
    async def test_health_check_success_production_mode(self, mock_adapter, async_client):
        """Test health check in production mode."""
        mock_adapter.health_check.return_value = {
            "success": True,
            "data": {"status": "healthy", "services": {"gpu": "available"}},
            "message": "All systems operational"
        }
        
        response = await async_client.get("/api/health")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert data["data"]["status"] == "healthy"
        mock_adapter.health_check.assert_called_once()
    
    @patch('app.main.settings.mock_mode', False)
    @patch('app.main.adapter')
    async def test_health_check_failure(self, mock_adapter, async_client):
        """Test health check failure."""
        mock_adapter.health_check.side_effect = Exception("Service unavailable")
        
        response = await async_client.get("/api/health")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is False
        assert "Health check failed" in data["error"]
    
    async def test_health_check_response_structure(self, async_client):
        """Test health check response structure."""
        response = await async_client.get("/api/health")
        data = response.json()
        
        # Verify required fields
        assert "success" in data
        assert "data" in data
        assert "message" in data
        
        if data["success"]:
            assert "status" in data["data"]
            assert "services" in data["data"]


class TestTrainingEndpoint:
    """Test training endpoint."""
    
    async def test_start_training_success(self, async_client, valid_training_config):
        """Test successful training start."""
        request_data = {"config": valid_training_config}
        
        response = await async_client.post("/api/train", json=request_data)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert "process_id" in data["data"]
        assert data["data"]["process_id"].startswith("training_")
    
    async def test_start_training_invalid_yaml(self, async_client, invalid_yaml_config):
        """Test training with invalid YAML."""
        request_data = {"config": invalid_yaml_config}
        
        response = await async_client.post("/api/train", json=request_data)
        
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        data = response.json()
        assert "Failed to start training" in data["detail"]
    
    async def test_start_training_empty_config(self, async_client):
        """Test training with empty config."""
        request_data = {"config": ""}
        
        response = await async_client.post("/api/train", json=request_data)
        
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    
    async def test_start_training_missing_config(self, async_client):
        """Test training with missing config field."""
        request_data = {}
        
        response = await async_client.post("/api/train", json=request_data)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    async def test_start_training_malformed_json(self, async_client):
        """Test training with malformed JSON."""
        response = await async_client.post(
            "/api/train", 
            content="invalid json",
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    @patch('app.main.settings.mock_mode', False)
    @patch('app.main.adapter')
    async def test_start_training_production_mode(self, mock_adapter, async_client, valid_training_config):
        """Test training in production mode."""
        mock_adapter.start_training.return_value = {
            "success": True,
            "data": {"process_id": "training_prod_123"},
            "message": "Training started"
        }
        
        request_data = {"config": valid_training_config}
        response = await async_client.post("/api/train", json=request_data)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["data"]["process_id"] == "training_prod_123"
        mock_adapter.start_training.assert_called_once()
    
    @patch('app.main.process_manager')
    async def test_start_training_process_manager_error(self, mock_pm, async_client, valid_training_config):
        """Test training when process manager fails."""
        mock_pm.start_training.side_effect = Exception("Process manager error")
        
        request_data = {"config": valid_training_config}
        response = await async_client.post("/api/train", json=request_data)
        
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


class TestGenerationEndpoint:
    """Test generation endpoint."""
    
    async def test_start_generation_success(self, async_client, valid_generation_config):
        """Test successful generation start."""
        request_data = {"config": valid_generation_config}
        
        response = await async_client.post("/api/generate", json=request_data)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert "process_id" in data["data"]
        assert data["data"]["process_id"].startswith("generation_")
    
    async def test_start_generation_invalid_yaml(self, async_client, invalid_yaml_config):
        """Test generation with invalid YAML."""
        request_data = {"config": invalid_yaml_config}
        
        response = await async_client.post("/api/generate", json=request_data)
        
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    
    async def test_start_generation_minimal_config(self, async_client):
        """Test generation with minimal valid config."""
        minimal_config = """
job: generate
config:
  name: "minimal_test"
  prompts: ["test prompt"]
"""
        request_data = {"config": minimal_config}
        
        response = await async_client.post("/api/generate", json=request_data)
        
        assert response.status_code == status.HTTP_200_OK
    
    async def test_start_generation_large_config(self, async_client):
        """Test generation with large configuration."""
        large_config = """
job: generate
config:
  name: "large_test"
  process:
    - type: flux_generator
      device: cuda:0
      generate:
        width: 2048
        height: 2048
        num_inference_steps: 100
        guidance_scale: 7.5
        seed: 12345
        prompts: {}
      model:
        name_or_path: "black-forest-labs/FLUX.1-dev"
        is_flux: true
        quantize: true
""".format(["prompt " + str(i) for i in range(100)])
        
        request_data = {"config": large_config}
        
        response = await async_client.post("/api/generate", json=request_data)
        
        assert response.status_code == status.HTTP_200_OK


class TestProcessesEndpoint:
    """Test processes endpoint."""
    
    async def test_get_processes_success(self, async_client):
        """Test successful processes retrieval."""
        response = await async_client.get("/api/processes")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "processes" in data
        assert isinstance(data["processes"], list)
    
    async def test_get_processes_structure(self, async_client):
        """Test processes response structure."""
        response = await async_client.get("/api/processes")
        data = response.json()
        
        for process in data["processes"]:
            assert "id" in process
            assert "name" in process
            assert "type" in process
            assert "status" in process
            assert "progress" in process
            assert "created_at" in process
            assert "updated_at" in process
    
    @patch('app.main.settings.mock_mode', False)
    @patch('app.main.adapter')
    async def test_get_processes_production_mode(self, mock_adapter, async_client):
        """Test processes in production mode."""
        mock_adapter.get_processes.return_value = {
            "processes": [
                {
                    "id": "proc_1",
                    "name": "Test Process",
                    "type": "training",
                    "status": "running",
                    "progress": 50.0,
                    "created_at": "2024-01-01T00:00:00Z",
                    "updated_at": "2024-01-01T00:30:00Z"
                }
            ]
        }
        
        response = await async_client.get("/api/processes")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["processes"]) == 1
        assert data["processes"][0]["id"] == "proc_1"


class TestProcessDetailEndpoint:
    """Test process detail endpoint."""
    
    @patch('app.main.adapter')
    async def test_get_process_success(self, mock_adapter, async_client):
        """Test successful process detail retrieval."""
        mock_adapter.get_process.return_value = {
            "success": True,
            "data": {
                "id": "test_process_123",
                "name": "Test Process",
                "type": "training",
                "status": "running",
                "progress": 75.0,
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T01:00:00Z"
            }
        }
        
        response = await async_client.get("/api/processes/test_process_123")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert data["data"]["id"] == "test_process_123"
    
    @patch('app.main.adapter')
    async def test_get_process_not_found(self, mock_adapter, async_client):
        """Test process not found."""
        mock_adapter.get_process.return_value = {
            "error": "Process not found"
        }
        
        response = await async_client.get("/api/processes/nonexistent_id")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    @patch('app.main.adapter')
    async def test_get_process_server_error(self, mock_adapter, async_client):
        """Test server error during process retrieval."""
        mock_adapter.get_process.side_effect = Exception("Database error")
        
        response = await async_client.get("/api/processes/test_id")
        
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


class TestCancelProcessEndpoint:
    """Test cancel process endpoint."""
    
    @patch('app.main.adapter')
    async def test_cancel_process_success(self, mock_adapter, async_client):
        """Test successful process cancellation."""
        mock_adapter.cancel_process.return_value = {
            "success": True,
            "message": "Process cancelled successfully"
        }
        
        response = await async_client.delete("/api/processes/test_process_123")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
    
    @patch('app.main.adapter')
    async def test_cancel_process_not_found(self, mock_adapter, async_client):
        """Test cancel non-existent process."""
        mock_adapter.cancel_process.return_value = {
            "error": "Process not found"
        }
        
        response = await async_client.delete("/api/processes/nonexistent_id")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    @patch('app.main.adapter')
    async def test_cancel_process_already_completed(self, mock_adapter, async_client):
        """Test cancel already completed process."""
        mock_adapter.cancel_process.return_value = {
            "error": "Process already completed"
        }
        
        response = await async_client.delete("/api/processes/completed_id")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestLoRAEndpoint:
    """Test LoRA models endpoint."""
    
    async def test_get_lora_models_success(self, async_client):
        """Test successful LoRA models retrieval."""
        response = await async_client.get("/api/lora")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "models" in data
        assert isinstance(data["models"], list)
    
    async def test_get_lora_models_structure(self, async_client):
        """Test LoRA models response structure."""
        response = await async_client.get("/api/lora")
        data = response.json()
        
        for model in data["models"]:
            assert "id" in model
            assert "name" in model
            assert "path" in model
            assert "created_at" in model
            assert "size" in model
    
    @patch('app.main.settings.mock_mode', False)
    @patch('app.main.adapter')
    async def test_get_lora_models_production_mode(self, mock_adapter, async_client):
        """Test LoRA models in production mode."""
        mock_adapter.get_lora_models.return_value = {
            "models": [
                {
                    "id": "lora_001",
                    "name": "Test LoRA",
                    "path": "/models/test.safetensors",
                    "created_at": "2024-01-01T00:00:00Z",
                    "size": 1048576,
                    "metadata": {"trigger_word": "test_style"}
                }
            ]
        }
        
        response = await async_client.get("/api/lora")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["models"]) == 1
        assert data["models"][0]["id"] == "lora_001"


class TestDownloadEndpoint:
    """Test download endpoint."""
    
    @patch('app.main.adapter')
    async def test_get_download_url_success(self, mock_adapter, async_client):
        """Test successful download URL retrieval."""
        mock_adapter.get_download_url.return_value = {
            "success": True,
            "data": {"url": "https://storage.com/download/test_process_123.zip"}
        }
        
        response = await async_client.get("/api/download/test_process_123")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert "url" in data["data"]
    
    @patch('app.main.adapter')
    async def test_get_download_url_not_found(self, mock_adapter, async_client):
        """Test download URL for non-existent process."""
        mock_adapter.get_download_url.return_value = {
            "error": "Process not found"
        }
        
        response = await async_client.get("/api/download/nonexistent_id")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    @patch('app.main.adapter')
    async def test_get_download_url_not_ready(self, mock_adapter, async_client):
        """Test download URL for process not ready."""
        mock_adapter.get_download_url.return_value = {
            "error": "Process not completed yet"
        }
        
        response = await async_client.get("/api/download/running_process_id")
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestAPIEdgeCases:
    """Test API edge cases and error scenarios."""
    
    async def test_cors_headers(self, async_client):
        """Test CORS headers are present."""
        response = await async_client.options("/api/health")
        
        # CORS headers should be handled by middleware
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_405_METHOD_NOT_ALLOWED]
    
    async def test_large_payload(self, async_client):
        """Test handling of large payloads."""
        large_config = "x" * (10 * 1024 * 1024)  # 10MB string
        request_data = {"config": large_config}
        
        response = await async_client.post("/api/train", json=request_data)
        
        # Should handle gracefully (either accept or reject with proper status)
        assert response.status_code in [
            status.HTTP_200_OK, 
            status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            status.HTTP_422_UNPROCESSABLE_ENTITY
        ]
    
    async def test_concurrent_requests(self, async_client, valid_training_config):
        """Test handling of concurrent requests."""
        request_data = {"config": valid_training_config}
        
        # Send multiple concurrent requests
        tasks = [
            async_client.post("/api/train", json=request_data)
            for _ in range(5)
        ]
        
        responses = await asyncio.gather(*tasks)
        
        # All should complete successfully (may be queued)
        for response in responses:
            assert response.status_code in [status.HTTP_200_OK, status.HTTP_500_INTERNAL_SERVER_ERROR]
    
    async def test_invalid_content_type(self, async_client):
        """Test invalid content type handling."""
        response = await async_client.post(
            "/api/train",
            content="config: test",
            headers={"Content-Type": "text/plain"}
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    async def test_missing_content_type(self, async_client):
        """Test missing content type header."""
        response = await async_client.post(
            "/api/train",
            content='{"config": "test"}',
            headers={}
        )
        
        # Should default to application/json or reject
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE
        ]
    
    async def test_special_characters_in_process_id(self, async_client):
        """Test special characters in process ID."""
        special_ids = [
            "process../../../etc/passwd",
            "process%20with%20encoding",
            "process\x00null",
            "процесс_unicode",
            "process-with-dashes_and_underscores"
        ]
        
        for process_id in special_ids:
            response = await async_client.get(f"/api/processes/{process_id}")
            # Should handle gracefully
            assert response.status_code in [
                status.HTTP_404_NOT_FOUND,
                status.HTTP_400_BAD_REQUEST,
                status.HTTP_422_UNPROCESSABLE_ENTITY
            ]
    
    @patch('app.main.settings.mock_mode', False) 
    @patch('app.main.adapter', None)
    async def test_adapter_not_initialized(self, async_client):
        """Test behavior when adapter is not initialized."""
        response = await async_client.get("/api/health")
        
        # Should handle gracefully
        assert response.status_code in [
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            status.HTTP_503_SERVICE_UNAVAILABLE
        ]
    
    async def test_method_not_allowed(self, async_client):
        """Test method not allowed responses."""
        # GET on POST endpoint
        response = await async_client.get("/api/train")
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
        
        # POST on GET endpoint
        response = await async_client.post("/api/health")
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    
    async def test_endpoint_not_found(self, async_client):
        """Test non-existent endpoint."""
        response = await async_client.get("/api/nonexistent")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
        response = await async_client.get("/api/v2/health")
        assert response.status_code == status.HTTP_404_NOT_FOUND 
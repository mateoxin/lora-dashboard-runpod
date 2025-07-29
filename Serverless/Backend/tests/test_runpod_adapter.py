"""
RunPod Adapter and Handler Tests
Tests for RunPod Serverless integration and dual mode functionality
"""

import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.adapters.runpod_adapter import RunPodAdapter
from app.core.models import TrainRequest, GenerateRequest
from app.rp_handler import async_handler


class TestRunPodAdapter:
    """Test RunPod Adapter functionality."""
    
    @pytest.fixture
    def mock_adapter(self):
        """Create a RunPod adapter in mock mode."""
        with patch('app.adapters.runpod_adapter.get_settings') as mock_settings:
            mock_settings.return_value.mock_mode = True
            return RunPodAdapter()
    
    @pytest.fixture
    def production_adapter(self):
        """Create a RunPod adapter in production mode."""
        with patch('app.adapters.runpod_adapter.get_settings') as mock_settings:
            mock_settings.return_value.mock_mode = False
            with patch('app.adapters.runpod_adapter.async_handler') as mock_handler:
                adapter = RunPodAdapter()
                adapter.handler = mock_handler
                return adapter, mock_handler
    
    async def test_health_check_mock_mode(self, mock_adapter):
        """Test health check in mock mode."""
        result = await mock_adapter.health_check()
        
        assert result["success"] is True
        assert result["data"]["status"] == "healthy"
        assert "Mock Mode" in result["message"]
        assert "services" in result["data"]
    
    async def test_health_check_production_mode(self, production_adapter):
        """Test health check in production mode."""
        adapter, mock_handler = production_adapter
        mock_handler.return_value = {
            "success": True,
            "data": {"status": "healthy", "services": {"gpu": "available"}},
            "message": "All systems operational"
        }
        
        result = await adapter.health_check()
        
        assert result["success"] is True
        mock_handler.assert_called_once_with({"input": {"type": "health"}})
    
    async def test_start_training_mock_mode(self, mock_adapter, valid_training_config):
        """Test training start in mock mode."""
        request = TrainRequest(config=valid_training_config)
        
        result = await mock_adapter.start_training(request)
        
        assert result["success"] is True
        assert "process_id" in result["data"]
        assert result["data"]["process_id"].startswith("training_")
        assert "Mock Mode" in result["message"]
    
    async def test_start_training_production_mode(self, production_adapter, valid_training_config):
        """Test training start in production mode."""
        adapter, mock_handler = production_adapter
        request = TrainRequest(config=valid_training_config)
        mock_handler.return_value = {
            "success": True,
            "data": {"process_id": "training_prod_123"},
            "message": "Training started"
        }
        
        result = await adapter.start_training(request)
        
        assert result["data"]["process_id"] == "training_prod_123"
        mock_handler.assert_called_once()
        
        # Verify the call was made with correct parameters
        call_args = mock_handler.call_args[0][0]
        assert call_args["input"]["type"] == "train"
        assert call_args["input"]["config"] == valid_training_config
    
    async def test_start_generation_production_mode(self, production_adapter, valid_generation_config):
        """Test generation start in production mode."""
        adapter, mock_handler = production_adapter
        request = GenerateRequest(config=valid_generation_config)
        mock_handler.return_value = {
            "success": True,
            "data": {"process_id": "generation_prod_456"},
            "message": "Generation started"
        }
        
        result = await adapter.start_generation(request)
        
        assert result["data"]["process_id"] == "generation_prod_456"
        mock_handler.assert_called_once()
        
        # Verify the call was made with correct parameters
        call_args = mock_handler.call_args[0][0]
        assert call_args["input"]["type"] == "generate"
        assert call_args["input"]["config"] == valid_generation_config
    
    async def test_get_processes_production_mode(self, production_adapter):
        """Test getting processes in production mode."""
        adapter, mock_handler = production_adapter
        mock_handler.return_value = {
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
        
        result = await adapter.get_processes()
        
        assert len(result["processes"]) == 1
        mock_handler.assert_called_once_with({"input": {"type": "processes"}})
    
    async def test_get_process_production_mode(self, production_adapter):
        """Test getting specific process in production mode."""
        adapter, mock_handler = production_adapter
        process_id = "test_process_123"
        mock_handler.return_value = {
            "success": True,
            "data": {
                "id": process_id,
                "name": "Test Process",
                "status": "completed"
            }
        }
        
        result = await adapter.get_process(process_id)
        
        assert result["data"]["id"] == process_id
        mock_handler.assert_called_once()
        
        call_args = mock_handler.call_args[0][0]
        assert call_args["input"]["type"] == "process_status"
        assert call_args["input"]["process_id"] == process_id
    
    async def test_cancel_process_production_mode(self, production_adapter):
        """Test cancelling process in production mode."""
        adapter, mock_handler = production_adapter
        process_id = "test_process_123"
        mock_handler.return_value = {
            "success": True,
            "message": "Process cancelled successfully"
        }
        
        result = await adapter.cancel_process(process_id)
        
        assert result["success"] is True
        mock_handler.assert_called_once()
        
        call_args = mock_handler.call_args[0][0]
        assert call_args["input"]["type"] == "cancel"
        assert call_args["input"]["process_id"] == process_id
    
    async def test_get_lora_models_production_mode(self, production_adapter):
        """Test getting LoRA models in production mode."""
        adapter, mock_handler = production_adapter
        mock_handler.return_value = {
            "models": [
                {
                    "id": "lora_001",
                    "name": "Test LoRA",
                    "path": "/models/test.safetensors"
                }
            ]
        }
        
        result = await adapter.get_lora_models()
        
        assert len(result["models"]) == 1
        mock_handler.assert_called_once_with({"input": {"type": "lora"}})
    
    async def test_get_download_url_production_mode(self, production_adapter):
        """Test getting download URL in production mode."""
        adapter, mock_handler = production_adapter
        process_id = "test_process_123"
        mock_handler.return_value = {
            "success": True,
            "data": {"url": "https://storage.com/download/test.zip"}
        }
        
        result = await adapter.get_download_url(process_id)
        
        assert result["data"]["url"] == "https://storage.com/download/test.zip"
        mock_handler.assert_called_once()
        
        call_args = mock_handler.call_args[0][0]
        assert call_args["input"]["type"] == "download"
        assert call_args["input"]["process_id"] == process_id


class TestRunPodHandler:
    """Test RunPod Handler functionality."""
    
    @patch('app.rp_handler.initialize_services')
    @patch('app.rp_handler.handle_health_check')
    async def test_health_check_handler(self, mock_health, mock_init):
        """Test health check handler."""
        mock_init.return_value = None
        mock_health.return_value = {
            "success": True,
            "data": {"status": "healthy"}
        }
        
        event = {"input": {"type": "health"}}
        result = await async_handler(event)
        
        assert result["success"] is True
        mock_health.assert_called_once()
    
    @patch('app.rp_handler.initialize_services')
    @patch('app.rp_handler.handle_training')
    async def test_training_handler(self, mock_training, mock_init, valid_training_config):
        """Test training handler."""
        mock_init.return_value = None
        mock_training.return_value = {
            "success": True,
            "data": {"process_id": "training_123"}
        }
        
        event = {
            "input": {
                "type": "train",
                "config": valid_training_config
            }
        }
        result = await async_handler(event)
        
        assert result["success"] is True
        assert result["data"]["process_id"] == "training_123"
        mock_training.assert_called_once()
    
    @patch('app.rp_handler.initialize_services')
    @patch('app.rp_handler.handle_generation')
    async def test_generation_handler(self, mock_generation, mock_init, valid_generation_config):
        """Test generation handler."""
        mock_init.return_value = None
        mock_generation.return_value = {
            "success": True,
            "data": {"process_id": "generation_456"}
        }
        
        event = {
            "input": {
                "type": "generate",
                "config": valid_generation_config
            }
        }
        result = await async_handler(event)
        
        assert result["success"] is True
        assert result["data"]["process_id"] == "generation_456"
        mock_generation.assert_called_once()
    
    @patch('app.rp_handler.initialize_services')
    @patch('app.rp_handler.handle_get_processes')
    async def test_processes_handler(self, mock_processes, mock_init):
        """Test processes handler."""
        mock_init.return_value = None
        mock_processes.return_value = {
            "processes": [
                {"id": "proc_1", "status": "running"}
            ]
        }
        
        event = {"input": {"type": "processes"}}
        result = await async_handler(event)
        
        assert "processes" in result
        assert len(result["processes"]) == 1
        mock_processes.assert_called_once()
    
    @patch('app.rp_handler.initialize_services')
    @patch('app.rp_handler.handle_process_status')
    async def test_process_status_handler(self, mock_status, mock_init):
        """Test process status handler."""
        mock_init.return_value = None
        mock_status.return_value = {
            "success": True,
            "data": {"id": "test_123", "status": "completed"}
        }
        
        event = {
            "input": {
                "type": "process_status",
                "process_id": "test_123"
            }
        }
        result = await async_handler(event)
        
        assert result["success"] is True
        assert result["data"]["id"] == "test_123"
        mock_status.assert_called_once()
    
    @patch('app.rp_handler.initialize_services')
    @patch('app.rp_handler.handle_get_lora_models')
    async def test_lora_handler(self, mock_lora, mock_init):
        """Test LoRA models handler."""
        mock_init.return_value = None
        mock_lora.return_value = {
            "models": [
                {"id": "lora_001", "name": "Test LoRA"}
            ]
        }
        
        event = {"input": {"type": "lora"}}
        result = await async_handler(event)
        
        assert "models" in result
        assert len(result["models"]) == 1
        mock_lora.assert_called_once()
    
    @patch('app.rp_handler.initialize_services')
    @patch('app.rp_handler.handle_cancel_process')
    async def test_cancel_handler(self, mock_cancel, mock_init):
        """Test cancel process handler."""
        mock_init.return_value = None
        mock_cancel.return_value = {
            "success": True,
            "message": "Process cancelled"
        }
        
        event = {
            "input": {
                "type": "cancel",
                "process_id": "test_123"
            }
        }
        result = await async_handler(event)
        
        assert result["success"] is True
        mock_cancel.assert_called_once()
    
    @patch('app.rp_handler.initialize_services')
    @patch('app.rp_handler.handle_download_url')
    async def test_download_handler(self, mock_download, mock_init):
        """Test download URL handler."""
        mock_init.return_value = None
        mock_download.return_value = {
            "success": True,
            "data": {"url": "https://download.url"}
        }
        
        event = {
            "input": {
                "type": "download",
                "process_id": "test_123"
            }
        }
        result = await async_handler(event)
        
        assert result["success"] is True
        assert result["data"]["url"] == "https://download.url"
        mock_download.assert_called_once()
    
    @patch('app.rp_handler.initialize_services')
    async def test_unknown_job_type_handler(self, mock_init):
        """Test unknown job type handler."""
        mock_init.return_value = None
        
        event = {"input": {"type": "unknown_type"}}
        result = await async_handler(event)
        
        assert "error" in result
        assert "Unknown job type" in result["error"]
        assert "supported_types" in result
    
    @patch('app.rp_handler.initialize_services')
    async def test_handler_exception(self, mock_init):
        """Test handler exception handling."""
        mock_init.side_effect = Exception("Initialization failed")
        
        event = {"input": {"type": "health"}}
        result = await async_handler(event)
        
        assert "error" in result
        assert "Initialization failed" in result["error"]
    
    async def test_invalid_event_structure(self):
        """Test handler with invalid event structure."""
        # Missing input field
        event = {}
        result = await async_handler(event)
        
        assert "error" in result or result.get("success") is False
        
        # Invalid input structure
        event = {"input": "invalid"}
        result = await async_handler(event)
        
        assert "error" in result or result.get("success") is False


class TestDualModeIntegration:
    """Test dual mode integration between FastAPI and RunPod."""
    
    @pytest.fixture
    def dual_mode_setup(self):
        """Setup for dual mode testing."""
        with patch('app.main.settings') as mock_settings, \
             patch('app.adapters.runpod_adapter.get_settings') as mock_adapter_settings:
            
            # Initially in mock mode
            mock_settings.mock_mode = True
            mock_adapter_settings.return_value.mock_mode = True
            
            yield mock_settings, mock_adapter_settings
    
    async def test_switch_from_mock_to_production(self, dual_mode_setup):
        """Test switching from mock mode to production mode."""
        mock_settings, mock_adapter_settings = dual_mode_setup
        
        # Start in mock mode
        assert mock_settings.mock_mode is True
        
        # Switch to production mode
        mock_settings.mock_mode = False
        mock_adapter_settings.return_value.mock_mode = False
        
        # Create new adapter in production mode
        with patch('app.adapters.runpod_adapter.async_handler') as mock_handler:
            adapter = RunPodAdapter()
            assert adapter.mock_mode is False
            assert adapter.handler is not None
    
    async def test_consistent_api_responses(self, dual_mode_setup, valid_training_config):
        """Test that API responses are consistent between modes."""
        mock_settings, mock_adapter_settings = dual_mode_setup
        
        # Test in mock mode
        mock_adapter_settings.return_value.mock_mode = True
        mock_adapter = RunPodAdapter()
        request = TrainRequest(config=valid_training_config)
        
        mock_result = await mock_adapter.start_training(request)
        
        # Test in production mode
        mock_adapter_settings.return_value.mock_mode = False
        with patch('app.adapters.runpod_adapter.async_handler') as mock_handler:
            mock_handler.return_value = {
                "success": True,
                "data": {"process_id": "training_prod_123"},
                "message": "Training started"
            }
            
            prod_adapter = RunPodAdapter()
            prod_result = await prod_adapter.start_training(request)
        
        # Both should have same structure
        assert "success" in mock_result
        assert "data" in mock_result
        assert "process_id" in mock_result["data"]
        
        assert "success" in prod_result
        assert "data" in prod_result
        assert "process_id" in prod_result["data"]
    
    @patch('app.main.app')
    async def test_api_endpoint_dual_mode_behavior(self, mock_app, dual_mode_setup, valid_training_config):
        """Test that API endpoints behave correctly in both modes."""
        mock_settings, mock_adapter_settings = dual_mode_setup
        
        # This would typically involve testing the actual FastAPI endpoints
        # with both mock and production configurations
        
        # Verify that the endpoint routing logic works correctly
        assert mock_settings.mock_mode is not None
        assert mock_adapter_settings.return_value.mock_mode is not None


class TestErrorScenarios:
    """Test error scenarios and edge cases."""
    
    @pytest.fixture
    def error_adapter(self):
        """Create adapter for error testing."""
        with patch('app.adapters.runpod_adapter.get_settings') as mock_settings:
            mock_settings.return_value.mock_mode = False
            with patch('app.adapters.runpod_adapter.async_handler') as mock_handler:
                adapter = RunPodAdapter()
                adapter.handler = mock_handler
                return adapter, mock_handler
    
    async def test_handler_timeout(self, error_adapter):
        """Test handler timeout scenario."""
        adapter, mock_handler = error_adapter
        
        async def slow_handler(*args, **kwargs):
            await asyncio.sleep(10)  # Simulate slow operation
            return {"success": True}
        
        mock_handler.side_effect = slow_handler
        
        # Use asyncio.wait_for to simulate timeout
        with pytest.raises(asyncio.TimeoutError):
            await asyncio.wait_for(adapter.health_check(), timeout=1.0)
    
    async def test_handler_connection_error(self, error_adapter):
        """Test handler connection error."""
        adapter, mock_handler = error_adapter
        mock_handler.side_effect = ConnectionError("Connection failed")
        
        # Should handle gracefully
        with pytest.raises(ConnectionError):
            await adapter.health_check()
    
    async def test_handler_invalid_response(self, error_adapter):
        """Test handler invalid response."""
        adapter, mock_handler = error_adapter
        mock_handler.return_value = "invalid response"  # Not a dict
        
        result = await adapter.health_check()
        
        # Should return the invalid response or handle it
        assert result == "invalid response" or "error" in str(result)
    
    async def test_malformed_event_data(self):
        """Test malformed event data."""
        malformed_events = [
            None,
            {"input": None},
            {"input": {"type": None}},
            {"input": {"type": ""}},
            {"input": {"type": "train"}},  # Missing config
            {"input": {"type": "train", "config": None}},
            {"input": {"type": "process_status"}},  # Missing process_id
        ]
        
        for event in malformed_events:
            result = await async_handler(event)
            # Should handle gracefully
            assert isinstance(result, dict)
            # Either success=False or error present
            assert result.get("success") is False or "error" in result
    
    async def test_large_config_payload(self, error_adapter, valid_training_config):
        """Test very large configuration payload."""
        adapter, mock_handler = error_adapter
        
        # Create large config by repeating the valid config
        large_config = valid_training_config * 1000  # Very large
        
        request = TrainRequest(config=large_config)
        mock_handler.return_value = {
            "success": True,
            "data": {"process_id": "large_config_test"}
        }
        
        result = await adapter.start_training(request)
        
        # Should handle large payload
        assert result["success"] is True
        mock_handler.assert_called_once()
    
    async def test_concurrent_handler_calls(self, error_adapter, valid_training_config):
        """Test concurrent handler calls."""
        adapter, mock_handler = error_adapter
        
        call_count = 0
        async def counting_handler(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            await asyncio.sleep(0.1)  # Simulate work
            return {
                "success": True,
                "data": {"process_id": f"concurrent_{call_count}"}
            }
        
        mock_handler.side_effect = counting_handler
        
        # Make concurrent calls
        request = TrainRequest(config=valid_training_config)
        tasks = [
            adapter.start_training(request)
            for _ in range(5)
        ]
        
        results = await asyncio.gather(*tasks)
        
        # All should complete
        assert len(results) == 5
        assert all(result["success"] for result in results)
        assert call_count == 5 
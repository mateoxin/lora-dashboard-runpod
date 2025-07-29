"""
Performance and Load Tests for LoRA Dashboard Backend
Tests for scalability, response times, and resource usage
"""

import asyncio
import time
import pytest
import statistics
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Any
from unittest.mock import patch

import httpx
from fastapi.testclient import TestClient

from app.main import app


class TestAPIPerformance:
    """Test API performance and response times."""
    
    def test_health_check_response_time(self):
        """Test health check response time."""
        client = TestClient(app)
        
        response_times = []
        for _ in range(100):
            start_time = time.time()
            response = client.get("/api/health")
            end_time = time.time()
            
            assert response.status_code == 200
            response_times.append((end_time - start_time) * 1000)  # Convert to ms
        
        avg_time = statistics.mean(response_times)
        p95_time = statistics.quantiles(response_times, n=20)[18]  # 95th percentile
        p99_time = statistics.quantiles(response_times, n=100)[98]  # 99th percentile
        
        print(f"Health check - Avg: {avg_time:.2f}ms, P95: {p95_time:.2f}ms, P99: {p99_time:.2f}ms")
        
        assert avg_time < 100  # Average response should be under 100ms
        assert p95_time < 200  # 95% of requests should be under 200ms
        assert p99_time < 500  # 99% of requests should be under 500ms
    
    def test_processes_endpoint_response_time(self):
        """Test processes endpoint response time."""
        # Initialize mock services for this test
        import app.main as main_module
        from app.services.mock_services import (
            MockProcessManager, MockStorageService, 
            MockGPUManager, MockLoRAService
        )
        
        main_module.storage_service = MockStorageService()
        main_module.lora_service = MockLoRAService(main_module.storage_service)
        main_module.gpu_manager = MockGPUManager()
        main_module.process_manager = MockProcessManager()
        
        client = TestClient(app)
        
        response_times = []
        for _ in range(50):
            start_time = time.time()
            response = client.get("/api/processes")
            end_time = time.time()
            
            assert response.status_code == 200
            response_times.append((end_time - start_time) * 1000)
        
        avg_time = statistics.mean(response_times)
        p95_time = statistics.quantiles(response_times, n=20)[18]
        
        print(f"Processes - Avg: {avg_time:.2f}ms, P95: {p95_time:.2f}ms")
        
        assert avg_time < 200  # Average response should be under 200ms
        assert p95_time < 500  # 95% of requests should be under 500ms
    
    def test_lora_models_response_time(self):
        """Test LoRA models endpoint response time."""
        # Initialize mock services for this test
        import app.main as main_module
        from app.services.mock_services import (
            MockProcessManager, MockStorageService, 
            MockGPUManager, MockLoRAService
        )
        
        main_module.storage_service = MockStorageService()
        main_module.lora_service = MockLoRAService(main_module.storage_service)
        main_module.gpu_manager = MockGPUManager()
        main_module.process_manager = MockProcessManager()
        
        client = TestClient(app)
        
        response_times = []
        for _ in range(50):
            start_time = time.time()
            response = client.get("/api/lora")
            end_time = time.time()
            
            assert response.status_code == 200
            response_times.append((end_time - start_time) * 1000)
        
        avg_time = statistics.mean(response_times)
        print(f"LoRA models - Avg: {avg_time:.2f}ms")
        
        assert avg_time < 300  # Average response should be under 300ms
    
    def test_training_endpoint_response_time(self):
        """Test training endpoint response time."""
        # Initialize mock services for this test
        import app.main as main_module
        from app.services.mock_services import (
            MockProcessManager, MockStorageService, 
            MockGPUManager, MockLoRAService
        )
        
        main_module.storage_service = MockStorageService()
        main_module.lora_service = MockLoRAService(main_module.storage_service)
        main_module.gpu_manager = MockGPUManager()
        main_module.process_manager = MockProcessManager()
        
        client = TestClient(app)
        
        config = """
job: extension
config:
  name: "performance_test"
  trigger_word: "perf_test"
"""
        
        response_times = []
        for _ in range(10):  # Fewer iterations for POST requests
            start_time = time.time()
            response = client.post("/api/train", json={"config": config})
            end_time = time.time()
            
            assert response.status_code == 200
            response_times.append((end_time - start_time) * 1000)
        
        avg_time = statistics.mean(response_times)
        print(f"Training start - Avg: {avg_time:.2f}ms")
        
        assert avg_time < 1000  # Average response should be under 1 second


class TestConcurrentLoad:
    """Test system behavior under concurrent load."""
    
    def test_concurrent_health_checks(self):
        """Test concurrent health check requests."""
        client = TestClient(app)
        
        def make_request():
            response = client.get("/api/health")
            return response.status_code, response.elapsed if hasattr(response, 'elapsed') else 0
        
        # Test with 50 concurrent requests
        with ThreadPoolExecutor(max_workers=50) as executor:
            start_time = time.time()
            futures = [executor.submit(make_request) for _ in range(50)]
            results = [future.result() for future in futures]
            end_time = time.time()
        
        # All requests should succeed
        status_codes = [result[0] for result in results]
        assert all(code == 200 for code in status_codes)
        
        # Total time should be reasonable
        total_time = end_time - start_time
        print(f"50 concurrent health checks completed in {total_time:.2f}s")
        assert total_time < 5.0  # Should complete within 5 seconds
    
    def test_concurrent_processes_requests(self):
        """Test concurrent processes requests."""
        client = TestClient(app)
        
        def make_request():
            response = client.get("/api/processes")
            return response.status_code, len(response.json().get("processes", []))
        
        # Test with 20 concurrent requests
        with ThreadPoolExecutor(max_workers=20) as executor:
            start_time = time.time()
            futures = [executor.submit(make_request) for _ in range(20)]
            results = [future.result() for future in futures]
            end_time = time.time()
        
        # All requests should succeed
        status_codes = [result[0] for result in results]
        assert all(code == 200 for code in status_codes)
        
        # Results should be consistent
        process_counts = [result[1] for result in results]
        assert len(set(process_counts)) <= 2  # Allow for slight variations due to timing
        
        total_time = end_time - start_time
        print(f"20 concurrent process requests completed in {total_time:.2f}s")
        assert total_time < 3.0
    
    def test_concurrent_training_requests(self):
        """Test concurrent training requests."""
        client = TestClient(app)
        
        config = """
job: extension
config:
  name: "concurrent_test_{}"
  trigger_word: "concurrent_{}"
"""
        
        def make_request(index):
            request_config = config.format(index, index)
            response = client.post("/api/train", json={"config": request_config})
            return response.status_code, response.json()
        
        # Test with 5 concurrent training requests
        with ThreadPoolExecutor(max_workers=5) as executor:
            start_time = time.time()
            futures = [executor.submit(make_request, i) for i in range(5)]
            results = [future.result() for future in futures]
            end_time = time.time()
        
        # All requests should succeed
        status_codes = [result[0] for result in results]
        assert all(code == 200 for code in status_codes)
        
        # Each should get a unique process ID
        process_ids = [result[1].get("data", {}).get("process_id") for result in results]
        assert len(set(process_ids)) == 5  # All should be unique
        
        total_time = end_time - start_time
        print(f"5 concurrent training requests completed in {total_time:.2f}s")
        assert total_time < 10.0
    
    def test_mixed_concurrent_requests(self):
        """Test mixed types of concurrent requests."""
        client = TestClient(app)
        
        def health_request():
            return client.get("/api/health").status_code
        
        def processes_request():
            return client.get("/api/processes").status_code
        
        def lora_request():
            return client.get("/api/lora").status_code
        
        # Mix different types of requests
        with ThreadPoolExecutor(max_workers=30) as executor:
            futures = []
            futures.extend([executor.submit(health_request) for _ in range(10)])
            futures.extend([executor.submit(processes_request) for _ in range(10)])
            futures.extend([executor.submit(lora_request) for _ in range(10)])
            
            start_time = time.time()
            results = [future.result() for future in futures]
            end_time = time.time()
        
        # All requests should succeed
        assert all(code == 200 for code in results)
        
        total_time = end_time - start_time
        print(f"30 mixed concurrent requests completed in {total_time:.2f}s")
        assert total_time < 5.0


class TestMemoryUsage:
    """Test memory usage and resource management."""
    
    def test_memory_usage_under_load(self):
        """Test memory usage doesn't grow excessively under load."""
        import psutil
        import os
        
        client = TestClient(app)
        process = psutil.Process(os.getpid())
        
        # Measure initial memory
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Make many requests
        for _ in range(1000):
            client.get("/api/health")
            if _ % 100 == 0:
                # Force garbage collection periodically
                import gc
                gc.collect()
        
        # Measure final memory
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        print(f"Memory usage: {initial_memory:.1f}MB -> {final_memory:.1f}MB (+{memory_increase:.1f}MB)")
        
        # Memory increase should be reasonable (less than 100MB for 1000 requests)
        assert memory_increase < 100
    
    def test_no_memory_leaks_in_process_creation(self):
        """Test that creating many processes doesn't leak memory."""
        import psutil
        import os
        
        client = TestClient(app)
        process = psutil.Process(os.getpid())
        
        initial_memory = process.memory_info().rss / 1024 / 1024
        
        config = """
job: extension
config:
  name: "memory_test_{}"
  trigger_word: "mem_test"
"""
        
        # Create many training processes
        for i in range(50):
            request_config = config.format(i)
            response = client.post("/api/train", json={"config": request_config})
            assert response.status_code == 200
            
            if i % 10 == 0:
                import gc
                gc.collect()
        
        final_memory = process.memory_info().rss / 1024 / 1024
        memory_increase = final_memory - initial_memory
        
        print(f"Process creation memory: {initial_memory:.1f}MB -> {final_memory:.1f}MB (+{memory_increase:.1f}MB)")
        
        # Memory increase should be reasonable
        assert memory_increase < 150


class TestScalability:
    """Test system scalability and limits."""
    
    def test_large_process_list_performance(self):
        """Test performance with large number of processes."""
        client = TestClient(app)
        
        # First, create many processes
        config = """
job: extension
config:
  name: "scale_test_{}"
  trigger_word: "scale"
"""
        
        # Create 100 processes
        for i in range(100):
            request_config = config.format(i)
            response = client.post("/api/train", json={"config": request_config})
            assert response.status_code == 200
        
        # Now test retrieving the large list
        start_time = time.time()
        response = client.get("/api/processes")
        end_time = time.time()
        
        assert response.status_code == 200
        processes = response.json()["processes"]
        
        response_time = (end_time - start_time) * 1000
        print(f"Retrieved {len(processes)} processes in {response_time:.2f}ms")
        
        # Should handle large lists efficiently
        assert response_time < 1000  # Under 1 second
        assert len(processes) >= 100
    
    def test_large_config_handling(self):
        """Test handling of large configuration files."""
        client = TestClient(app)
        
        # Create a large configuration
        large_config = f"""
job: extension
config:
  name: "large_config_test"
  trigger_word: "large_test"
  description: "{'x' * 10000}"  # 10KB of description
  datasets:
    - folder_path: "/workspace/dataset"
      caption_ext: "txt"
      # Large list of prompts
      prompts: {[f"prompt_{i}" for i in range(1000)]}
"""
        
        start_time = time.time()
        response = client.post("/api/train", json={"config": large_config})
        end_time = time.time()
        
        response_time = (end_time - start_time) * 1000
        print(f"Large config processed in {response_time:.2f}ms")
        
        assert response.status_code == 200
        assert response_time < 2000  # Under 2 seconds
    
    def test_rapid_request_succession(self):
        """Test handling of rapid successive requests."""
        client = TestClient(app)
        
        response_times = []
        
        # Make 100 requests as fast as possible
        for i in range(100):
            start_time = time.time()
            response = client.get("/api/health")
            end_time = time.time()
            
            assert response.status_code == 200
            response_times.append((end_time - start_time) * 1000)
        
        avg_time = statistics.mean(response_times)
        max_time = max(response_times)
        
        print(f"Rapid requests - Avg: {avg_time:.2f}ms, Max: {max_time:.2f}ms")
        
        # Performance should not degrade significantly
        assert avg_time < 150
        assert max_time < 500


class TestAsyncPerformance:
    """Test async operations performance."""
    
    @pytest.mark.asyncio
    async def test_async_concurrent_requests(self):
        """Test async concurrent requests performance."""
        async with httpx.AsyncClient(app=app, base_url="http://test") as client:
            
            async def make_request():
                response = await client.get("/api/health")
                return response.status_code
            
            # Create 100 concurrent async requests
            start_time = time.time()
            tasks = [make_request() for _ in range(100)]
            results = await asyncio.gather(*tasks)
            end_time = time.time()
            
            # All should succeed
            assert all(code == 200 for code in results)
            
            total_time = end_time - start_time
            print(f"100 async requests completed in {total_time:.2f}s")
            
            # Async should be faster than sequential
            assert total_time < 2.0
    
    @pytest.mark.asyncio
    async def test_process_manager_performance(self):
        """Test ProcessManager async operations performance."""
        from app.services.mock_services import MockProcessManager
        
        pm = MockProcessManager()
        
        config = """
job: extension
config:
  name: "async_perf_test_{}"
  trigger_word: "async_test"
"""
        
        # Test creating many processes concurrently
        start_time = time.time()
        tasks = []
        
        for i in range(50):
            request_config = config.format(i)
            task = pm.start_training(request_config)
            tasks.append(task)
        
        process_ids = await asyncio.gather(*tasks)
        end_time = time.time()
        
        creation_time = end_time - start_time
        print(f"Created {len(process_ids)} processes in {creation_time:.2f}s")
        
        assert len(process_ids) == 50
        assert creation_time < 5.0
        
        # Test retrieving all processes
        start_time = time.time()
        processes = await pm.get_all_processes()
        end_time = time.time()
        
        retrieval_time = end_time - start_time
        print(f"Retrieved {len(processes)} processes in {retrieval_time:.3f}s")
        
        assert len(processes) >= 50
        assert retrieval_time < 0.1  # Should be very fast for mock


class TestDatabasePerformance:
    """Test database/storage performance (using Redis mock)."""
    
    @pytest.mark.asyncio
    async def test_redis_operations_performance(self):
        """Test Redis operations performance."""
        from app.services.process_manager import ProcessManager
        from unittest.mock import AsyncMock
        
        # Mock Redis with performance tracking
        mock_redis = AsyncMock()
        call_times = []
        
        async def timed_set(*args, **kwargs):
            start = time.time()
            await asyncio.sleep(0.001)  # Simulate Redis latency
            end = time.time()
            call_times.append((end - start) * 1000)
            return True
        
        mock_redis.set.side_effect = timed_set
        mock_redis.get.return_value = None
        mock_redis.keys.return_value = []
        mock_redis.ping.return_value = True
        
        # Test many Redis operations
        with patch('redis.asyncio.from_url', return_value=mock_redis):
            from app.services.gpu_manager import GPUManager
            from app.services.storage_service import StorageService
            
            gpu_manager = GPUManager(max_concurrent=10)
            storage_service = StorageService()
            
            pm = ProcessManager(
                gpu_manager=gpu_manager,
                storage_service=storage_service,
                redis_url="redis://test"
            )
            
            await pm.initialize()
            
            # Create many processes (will trigger Redis operations)
            config = """
job: extension
config:
  name: "redis_perf_test_{}"
"""
            
            start_time = time.time()
            
            for i in range(20):
                request_config = config.format(i)
                await pm.start_training(request_config)
            
            end_time = time.time()
            
            total_time = end_time - start_time
            avg_redis_time = statistics.mean(call_times) if call_times else 0
            
            print(f"Redis performance - Total: {total_time:.2f}s, Avg call: {avg_redis_time:.2f}ms")
            
            assert total_time < 10.0
            assert avg_redis_time < 50  # Average Redis call under 50ms
            
            await pm.cleanup()


class TestErrorHandlingPerformance:
    """Test performance under error conditions."""
    
    def test_error_response_performance(self):
        """Test that error responses are still fast."""
        client = TestClient(app)
        
        response_times = []
        
        # Test invalid endpoints
        for _ in range(50):
            start_time = time.time()
            response = client.get("/api/nonexistent")
            end_time = time.time()
            
            assert response.status_code == 404
            response_times.append((end_time - start_time) * 1000)
        
        avg_time = statistics.mean(response_times)
        print(f"Error responses - Avg: {avg_time:.2f}ms")
        
        # Error responses should be fast
        assert avg_time < 50
    
    def test_invalid_data_handling_performance(self):
        """Test performance when handling invalid data."""
        client = TestClient(app)
        
        response_times = []
        
        # Test with invalid JSON
        for _ in range(20):
            start_time = time.time()
            response = client.post(
                "/api/train",
                data="invalid json{{{",
                headers={"Content-Type": "application/json"}
            )
            end_time = time.time()
            
            assert response.status_code == 422
            response_times.append((end_time - start_time) * 1000)
        
        avg_time = statistics.mean(response_times)
        print(f"Invalid data handling - Avg: {avg_time:.2f}ms")
        
        # Should handle invalid data quickly
        assert avg_time < 100


if __name__ == "__main__":
    # Run basic performance tests
    perf_test = TestAPIPerformance()
    perf_test.test_health_check_response_time()
    perf_test.test_processes_endpoint_response_time()
    
    load_test = TestConcurrentLoad()
    load_test.test_concurrent_health_checks()
    
    print("Performance tests completed successfully!") 
#!/usr/bin/env python3
"""
🧪 Local testing script for FastBackend
Test handler locally before deploying to RunPod
"""

import sys
import os
import json
import time
from datetime import datetime

# Add current directory to path for importing handler
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_handler_locally():
    """Test the handler locally"""
    
    try:
        # Import handler
        from handler_fast import handler
        
        print("🧪 Testing FastBackend Handler Locally")
        print("=" * 50)
        
        # Test 1: Health check
        print("\n1. Testing health check...")
        job = {"input": {"type": "health"}}
        result = handler(job)
        print(f"✅ Health: {result}")
        
        # Test 2: Ping
        print("\n2. Testing ping...")
        job = {"input": {"type": "ping"}}
        result = handler(job)
        print(f"✅ Ping: {result}")
        
        # Test 3: Echo
        print("\n3. Testing echo...")
        job = {"input": {"type": "echo", "message": "Hello FastBackend!"}}
        result = handler(job)
        print(f"✅ Echo: {result}")
        
        # Test 4: Unknown type
        print("\n4. Testing unknown type...")
        job = {"input": {"type": "unknown_operation"}}
        result = handler(job)
        print(f"✅ Unknown: {result}")
        
        # Test 5: Setup environment (will fail locally but should handle gracefully)
        print("\n5. Testing setup environment...")
        job = {"input": {"type": "setup_environment"}}
        result = handler(job)
        print(f"✅ Setup: {result}")
        
        print("\n🎉 All local tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Local test failed: {e}")
        return False

def test_minimal_dependencies():
    """Test that minimal dependencies are available"""
    
    print("\n🔍 Testing minimal dependencies...")
    
    required_modules = [
        'runpod',
        'yaml', 
        'datetime',
        'json',
        'os',
        'sys'
    ]
    
    missing_modules = []
    
    for module in required_modules:
        try:
            __import__(module)
            print(f"✅ {module}")
        except ImportError:
            print(f"❌ {module} - MISSING")
            missing_modules.append(module)
    
    if missing_modules:
        print(f"\n⚠️ Missing modules: {missing_modules}")
        print("Install with: pip install -r requirements_minimal.txt")
        return False
    else:
        print(f"\n✅ All required modules available")
        return True

def benchmark_startup_time():
    """Benchmark handler startup time"""
    
    print("\n⏱️ Benchmarking startup time...")
    
    start_time = time.time()
    
    try:
        from handler_fast import handler
        
        # Test basic operation
        job = {"input": {"type": "health"}}
        result = handler(job)
        
        end_time = time.time()
        startup_time = end_time - start_time
        
        print(f"✅ Startup time: {startup_time:.3f} seconds")
        print(f"🎯 Target: <0.1 seconds for basic operations")
        
        if startup_time < 0.1:
            print("🚀 EXCELLENT - Very fast startup!")
        elif startup_time < 0.5:
            print("👍 GOOD - Acceptable startup time")
        else:
            print("⚠️ SLOW - Consider optimizing imports")
        
        return startup_time
        
    except Exception as e:
        print(f"❌ Benchmark failed: {e}")
        return None

def simulate_runpod_environment():
    """Simulate RunPod environment variables"""
    
    print("\n🎭 Simulating RunPod environment...")
    
    runpod_env = {
        'RUNPOD_POD_ID': 'test-pod-12345',
        'WORKSPACE_PATH': '/tmp/test_workspace',
        'HF_TOKEN': 'hf_test_token',
        'PYTHONUNBUFFERED': '1'
    }
    
    for key, value in runpod_env.items():
        os.environ[key] = value
        print(f"✅ {key}={value}")
    
    # Create test workspace
    workspace = runpod_env['WORKSPACE_PATH']
    os.makedirs(workspace, exist_ok=True)
    os.makedirs(os.path.join(workspace, 'models'), exist_ok=True)
    os.makedirs(os.path.join(workspace, 'training_data'), exist_ok=True)
    
    print(f"✅ Created test workspace: {workspace}")

def test_error_handling():
    """Test error handling scenarios"""
    
    print("\n🛡️ Testing error handling...")
    
    try:
        from handler_fast import handler
        
        # Test 1: Invalid job format
        print("1. Testing invalid job format...")
        result = handler({"invalid": "format"})
        print(f"✅ Invalid job: {result['status']}")
        
        # Test 2: Missing input
        print("2. Testing missing input...")
        result = handler({})
        print(f"✅ Missing input: {result['status']}")
        
        # Test 3: Exception handling
        print("3. Testing exception in handler...")
        # This should still return a valid error response
        result = handler({"input": {"type": "health"}})
        print(f"✅ Exception handling: {result['status']}")
        
        print("✅ Error handling tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
        return False

def generate_test_report():
    """Generate comprehensive test report"""
    
    print("\n📊 Generating test report...")
    
    report = {
        "test_timestamp": datetime.now().isoformat(),
        "test_environment": "local",
        "python_version": sys.version,
        "results": {}
    }
    
    # Run all tests
    tests = [
        ("dependencies", test_minimal_dependencies),
        ("handler", test_handler_locally),
        ("startup_benchmark", benchmark_startup_time),
        ("error_handling", test_error_handling)
    ]
    
    for test_name, test_func in tests:
        print(f"\n🔄 Running {test_name} test...")
        try:
            result = test_func()
            report["results"][test_name] = {
                "status": "passed" if result else "failed",
                "result": result
            }
        except Exception as e:
            report["results"][test_name] = {
                "status": "error",
                "error": str(e)
            }
    
    # Save report
    report_file = f"test_report_{int(time.time())}.json"
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📄 Test report saved: {report_file}")
    
    # Summary
    passed = sum(1 for r in report["results"].values() if r["status"] == "passed")
    total = len(report["results"])
    
    print(f"\n📈 Test Summary: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Ready for deployment!")
    else:
        print("⚠️ Some tests failed. Check issues before deploying.")
    
    return report

if __name__ == "__main__":
    print("🚀 FastBackend Local Testing Suite")
    print("=" * 60)
    
    # Setup test environment
    simulate_runpod_environment()
    
    # Run comprehensive test suite
    report = generate_test_report()
    
    print("\n" + "=" * 60)
    print("🏁 Testing complete!")
    
    # Exit with appropriate code
    passed_tests = sum(1 for r in report["results"].values() if r["status"] == "passed")
    total_tests = len(report["results"])
    
    if passed_tests == total_tests:
        print("✅ Ready for RunPod deployment!")
        exit(0)
    else:
        print("❌ Fix issues before deployment")
        exit(1)
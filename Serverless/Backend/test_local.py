#!/usr/bin/env python3
"""
Local Testing Script for LoRA Dashboard RunPod Handler
Run different test scenarios locally before deployment
"""

import os
import sys
import json
import asyncio
import argparse
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent))

def load_test_input(test_name: str) -> dict:
    """Load test input from test_inputs directory"""
    test_file = Path(f"test_inputs/{test_name}.json")
    if not test_file.exists():
        raise FileNotFoundError(f"Test file not found: {test_file}")
    
    with open(test_file, 'r') as f:
        return json.load(f)

def run_handler_test(test_input: dict):
    """Run the handler with test input"""
    try:
        # Import and run handler
        from app.rp_handler import handler
        result = handler(test_input)
        return result
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure you're in the correct directory and dependencies are installed")
        return {"error": str(e)}
    except Exception as e:
        print(f"❌ Handler error: {e}")
        return {"error": str(e)}

def print_result(test_name: str, result: dict):
    """Pretty print test result"""
    print(f"\n{'='*60}")
    print(f"🧪 TEST: {test_name.upper()}")
    print(f"{'='*60}")
    
    if result.get("error"):
        print(f"❌ ERROR: {result['error']}")
    elif result.get("success"):
        print(f"✅ SUCCESS: {result.get('message', 'Operation completed')}")
        if result.get("data"):
            print(f"📊 Data: {json.dumps(result['data'], indent=2, default=str)}")
    else:
        print(f"📋 Result: {json.dumps(result, indent=2, default=str)}")

def main():
    parser = argparse.ArgumentParser(description="Test LoRA Dashboard RunPod Handler locally")
    parser.add_argument("--test", "-t", type=str, help="Specific test to run (health, train, generate, processes, lora)")
    parser.add_argument("--all", "-a", action="store_true", help="Run all tests")
    parser.add_argument("--input", "-i", type=str, help="Custom JSON input string")
    parser.add_argument("--file", "-f", type=str, help="Custom input file path")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    # Available tests
    available_tests = ["health_check", "train_test", "generate_test", "processes_test", "lora_models_test"]
    
    if args.verbose:
        print("🔧 Setting up local testing environment...")
        print(f"📁 Working directory: {os.getcwd()}")
        print(f"🐍 Python path: {sys.path}")
    
    try:
        if args.input:
            # Custom JSON input
            test_input = json.loads(args.input)
            result = run_handler_test(test_input)
            print_result("CUSTOM INPUT", result)
            
        elif args.file:
            # Custom file input
            with open(args.file, 'r') as f:
                test_input = json.load(f)
            result = run_handler_test(test_input)
            print_result(f"FILE: {args.file}", result)
            
        elif args.test:
            # Specific test
            test_name = args.test
            if not test_name.endswith("_test") and test_name != "health_check":
                test_name = f"{test_name}_test"
            
            if test_name not in available_tests:
                print(f"❌ Unknown test: {test_name}")
                print(f"Available tests: {', '.join(available_tests)}")
                return
            
            test_input = load_test_input(test_name)
            result = run_handler_test(test_input)
            print_result(test_name, result)
            
        elif args.all:
            # Run all tests
            print("🚀 Running all tests...")
            for test_name in available_tests:
                try:
                    test_input = load_test_input(test_name)
                    result = run_handler_test(test_input)
                    print_result(test_name, result)
                except Exception as e:
                    print(f"❌ Test {test_name} failed: {e}")
        else:
            # Default: run health check
            print("🔍 Running default health check...")
            test_input = load_test_input("health_check")
            result = run_handler_test(test_input)
            print_result("health_check", result)
            
            print(f"\n💡 Use --help to see all options")
            print(f"💡 Available tests: {', '.join(available_tests)}")
            
    except FileNotFoundError as e:
        print(f"❌ File not found: {e}")
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    main() 
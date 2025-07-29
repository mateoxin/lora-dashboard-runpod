#!/usr/bin/env python3
"""
Comprehensive Test Runner for LoRA Dashboard Backend
Runs all test suites with proper configuration and reporting
"""

import os
import sys
import subprocess
import argparse
import time
from pathlib import Path
from typing import List, Dict, Any
import json


class TestRunner:
    """Test runner with multiple test categories and configurations."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.test_categories = {
            'unit': {
                'description': 'Fast unit tests for individual components',
                'markers': 'unit and not slow',
                'timeout': 300
            },
            'integration': {
                'description': 'Integration tests for service interactions',
                'markers': 'integration',
                'timeout': 600
            },
            'api': {
                'description': 'API endpoint tests',
                'markers': 'api',
                'timeout': 300
            },
            'performance': {
                'description': 'Performance and load tests',
                'markers': 'performance',
                'timeout': 900
            },
            'mock': {
                'description': 'Tests using mock services',
                'markers': 'mock',
                'timeout': 300
            },
            'production': {
                'description': 'Tests for production mode',
                'markers': 'production',
                'timeout': 600
            },
            'all': {
                'description': 'All tests',
                'markers': '',
                'timeout': 1800
            }
        }
    
    def setup_environment(self):
        """Setup test environment variables."""
        env_vars = {
            'MOCK_MODE': 'true',
            'DEBUG': 'true',
            'REDIS_URL': 'redis://localhost:6379/15',
            'S3_BUCKET': 'test-bucket',
            'S3_ACCESS_KEY': 'test-access-key',
            'S3_SECRET_KEY': 'test-secret-key',
            'MAX_CONCURRENT_JOBS': '2',
            'PYTHONPATH': str(self.project_root)
        }
        
        for key, value in env_vars.items():
            os.environ[key] = value
        
        print("✅ Test environment configured")
    
    def install_dependencies(self):
        """Install test dependencies."""
        print("📦 Installing test dependencies...")
        
        dependencies = [
            'pytest',
            'pytest-asyncio',
            'pytest-cov',
            'pytest-timeout',
            'pytest-mock',
            'pytest-xdist',
            'httpx',
            'psutil'
        ]
        
        try:
            subprocess.run([
                sys.executable, '-m', 'pip', 'install'
            ] + dependencies, check=True, capture_output=True)
            print("✅ Dependencies installed")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install dependencies: {e}")
            return False
        
        return True
    
    def run_tests(self, category: str, verbose: bool = False, coverage: bool = True,
                  parallel: bool = False, exit_on_fail: bool = False) -> Dict[str, Any]:
        """Run tests for a specific category."""
        
        if category not in self.test_categories:
            print(f"❌ Unknown test category: {category}")
            return {'success': False, 'error': f'Unknown category: {category}'}
        
        test_config = self.test_categories[category]
        print(f"🧪 Running {category} tests: {test_config['description']}")
        
        # Build pytest command
        cmd = [sys.executable, '-m', 'pytest']
        
        # Add markers if specified
        if test_config['markers']:
            cmd.extend(['-m', test_config['markers']])
        
        # Add coverage if requested
        if coverage:
            cmd.extend([
                '--cov=app',
                '--cov-report=html:htmlcov',
                '--cov-report=term-missing',
                '--cov-report=xml'
            ])
        
        # Add verbosity
        if verbose:
            cmd.append('-v')
        else:
            cmd.extend(['-q', '--tb=short'])
        
        # Add parallel execution
        if parallel and category != 'performance':  # Don't parallelize performance tests
            import multiprocessing
            cpu_count = multiprocessing.cpu_count()
            cmd.extend(['-n', str(min(cpu_count, 4))])  # Max 4 workers
        
        # Add timeout
        cmd.extend(['--timeout', str(test_config['timeout'])])
        
        # Add exit on first failure option
        if exit_on_fail:
            cmd.append('-x')
        
        # Add test directory
        cmd.append('tests/')
        
        # Add output format
        cmd.extend([
            '--junit-xml=test-results.xml',
            '--html=test-report.html',
            '--self-contained-html'
        ])
        
        print(f"Running command: {' '.join(cmd)}")
        
        # Run tests
        start_time = time.time()
        try:
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=not verbose,
                text=True,
                timeout=test_config['timeout'] + 60  # Add buffer time
            )
            
            end_time = time.time()
            duration = end_time - start_time
            
            success = result.returncode == 0
            
            return {
                'success': success,
                'returncode': result.returncode,
                'duration': duration,
                'stdout': result.stdout if hasattr(result, 'stdout') else '',
                'stderr': result.stderr if hasattr(result, 'stderr') else ''
            }
            
        except subprocess.TimeoutExpired:
            print(f"❌ Tests timed out after {test_config['timeout']} seconds")
            return {'success': False, 'error': 'timeout'}
        
        except Exception as e:
            print(f"❌ Test execution failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def run_quality_checks(self) -> Dict[str, Any]:
        """Run code quality checks."""
        print("🔍 Running code quality checks...")
        
        checks = {}
        
        # Flake8 linting
        try:
            result = subprocess.run([
                sys.executable, '-m', 'flake8', 'app/', 'tests/', 
                '--max-line-length=120',
                '--extend-ignore=E203,W503'
            ], capture_output=True, text=True, cwd=self.project_root)
            
            checks['flake8'] = {
                'success': result.returncode == 0,
                'output': result.stdout + result.stderr
            }
        except FileNotFoundError:
            checks['flake8'] = {'success': False, 'error': 'flake8 not installed'}
        
        # mypy type checking
        try:
            result = subprocess.run([
                sys.executable, '-m', 'mypy', 'app/', 
                '--ignore-missing-imports',
                '--no-strict-optional'
            ], capture_output=True, text=True, cwd=self.project_root)
            
            checks['mypy'] = {
                'success': result.returncode == 0,
                'output': result.stdout + result.stderr
            }
        except FileNotFoundError:
            checks['mypy'] = {'success': False, 'error': 'mypy not installed'}
        
        # bandit security checks
        try:
            result = subprocess.run([
                sys.executable, '-m', 'bandit', '-r', 'app/', 
                '-f', 'json'
            ], capture_output=True, text=True, cwd=self.project_root)
            
            checks['bandit'] = {
                'success': result.returncode == 0,
                'output': result.stdout + result.stderr
            }
        except FileNotFoundError:
            checks['bandit'] = {'success': False, 'error': 'bandit not installed'}
        
        return checks
    
    def generate_report(self, results: Dict[str, Any], quality_checks: Dict[str, Any]):
        """Generate comprehensive test report."""
        print("\n" + "="*60)
        print("📊 TEST REPORT")
        print("="*60)
        
        total_tests = len(results)
        passed_tests = sum(1 for r in results.values() if r.get('success', False))
        
        print(f"Total test categories: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        
        print("\n📋 Test Categories:")
        for category, result in results.items():
            status = "✅" if result.get('success', False) else "❌"
            duration = result.get('duration', 0)
            print(f"  {status} {category}: {duration:.2f}s")
            
            if not result.get('success', False) and 'error' in result:
                print(f"    Error: {result['error']}")
        
        print("\n🔍 Code Quality:")
        for check, result in quality_checks.items():
            status = "✅" if result.get('success', False) else "❌"
            print(f"  {status} {check}")
            
            if not result.get('success', False):
                if 'error' in result:
                    print(f"    Error: {result['error']}")
                elif 'output' in result and result['output'].strip():
                    print(f"    Issues found: {len(result['output'].splitlines())} lines")
        
        # Save detailed report
        report_data = {
            'timestamp': time.time(),
            'summary': {
                'total_categories': total_tests,
                'passed': passed_tests,
                'failed': total_tests - passed_tests
            },
            'test_results': results,
            'quality_checks': quality_checks
        }
        
        with open(self.project_root / 'test_report.json', 'w') as f:
            json.dump(report_data, f, indent=2)
        
        print(f"\n💾 Detailed report saved to: test_report.json")
        
        return passed_tests == total_tests and all(
            check.get('success', False) for check in quality_checks.values()
        )
    
    def main(self):
        """Main test runner function."""
        parser = argparse.ArgumentParser(description='LoRA Dashboard Backend Test Runner')
        parser.add_argument('categories', nargs='*', default=['all'], 
                           help='Test categories to run')
        parser.add_argument('-v', '--verbose', action='store_true',
                           help='Verbose output')
        parser.add_argument('--no-coverage', action='store_true',
                           help='Disable coverage reporting')
        parser.add_argument('--no-parallel', action='store_true',
                           help='Disable parallel test execution')
        parser.add_argument('--exit-on-fail', action='store_true',
                           help='Exit on first test failure')
        parser.add_argument('--no-quality', action='store_true',
                           help='Skip code quality checks')
        parser.add_argument('--install-deps', action='store_true',
                           help='Install test dependencies before running')
        parser.add_argument('--list-categories', action='store_true',
                           help='List available test categories')
        
        args = parser.parse_args()
        
        if args.list_categories:
            print("Available test categories:")
            for category, config in self.test_categories.items():
                print(f"  {category}: {config['description']}")
            return
        
        print("🚀 LoRA Dashboard Backend Test Suite")
        print("="*50)
        
        # Install dependencies if requested
        if args.install_deps:
            if not self.install_dependencies():
                sys.exit(1)
        
        # Setup environment
        self.setup_environment()
        
        # Validate categories
        invalid_categories = [cat for cat in args.categories 
                            if cat not in self.test_categories]
        if invalid_categories:
            print(f"❌ Invalid categories: {invalid_categories}")
            print("Use --list-categories to see available options")
            sys.exit(1)
        
        # Run tests
        results = {}
        for category in args.categories:
            result = self.run_tests(
                category=category,
                verbose=args.verbose,
                coverage=not args.no_coverage,
                parallel=not args.no_parallel,
                exit_on_fail=args.exit_on_fail
            )
            results[category] = result
            
            if args.exit_on_fail and not result.get('success', False):
                print(f"❌ Exiting due to failure in {category} tests")
                sys.exit(1)
        
        # Run quality checks
        quality_checks = {}
        if not args.no_quality:
            quality_checks = self.run_quality_checks()
        
        # Generate report
        all_passed = self.generate_report(results, quality_checks)
        
        if all_passed:
            print("\n🎉 All tests passed!")
            sys.exit(0)
        else:
            print("\n💥 Some tests failed!")
            sys.exit(1)


if __name__ == '__main__':
    runner = TestRunner()
    runner.main() 
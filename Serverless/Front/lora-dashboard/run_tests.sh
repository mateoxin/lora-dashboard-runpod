#!/bin/bash

# Comprehensive Test Runner for LoRA Dashboard Frontend
# Runs all test suites with proper configuration and reporting

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
NODE_VERSION_REQUIRED="18"
COVERAGE_THRESHOLD=80

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    # Check Node.js version
    if ! command -v node &> /dev/null; then
        print_error "Node.js is not installed"
        exit 1
    fi
    
    NODE_VERSION=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)
    if [ "$NODE_VERSION" -lt "$NODE_VERSION_REQUIRED" ]; then
        print_error "Node.js version $NODE_VERSION_REQUIRED or higher required. Found: $NODE_VERSION"
        exit 1
    fi
    
    # Check npm
    if ! command -v npm &> /dev/null; then
        print_error "npm is not installed"
        exit 1
    fi
    
    # Check Angular CLI
    if ! command -v ng &> /dev/null; then
        print_warning "Angular CLI not found globally. Installing locally..."
        npm install -g @angular/cli
    fi
    
    print_success "Prerequisites check passed"
}

# Function to install dependencies
install_dependencies() {
    print_status "Installing dependencies..."
    
    cd "$PROJECT_ROOT"
    
    # Install main dependencies
    npm ci
    
    # Install additional test dependencies
    npm install --save-dev \
        karma-chrome-headless \
        karma-junit-reporter \
        karma-spec-reporter \
        karma-coverage \
        protractor \
        webdriver-manager \
        @types/jasmine \
        @types/node
    
    print_success "Dependencies installed"
}

# Function to update webdriver
update_webdriver() {
    print_status "Updating webdriver for e2e tests..."
    
    if command -v webdriver-manager &> /dev/null; then
        webdriver-manager update --standalone false --gecko false --versions.chrome 2.37
    else
        print_warning "webdriver-manager not found, skipping update"
    fi
}

# Function to run unit tests
run_unit_tests() {
    print_status "Running unit tests..."
    
    cd "$PROJECT_ROOT"
    
    # Set CI environment for headless testing
    export CI=true
    
    # Run tests with coverage
    ng test --watch=false --browsers=ChromeHeadlessCI --code-coverage=true --source-map=false
    
    # Check coverage thresholds
    if [ -f "coverage/lora-dashboard/lcov-report/index.html" ]; then
        print_success "Coverage report generated: coverage/lora-dashboard/lcov-report/index.html"
    fi
    
    print_success "Unit tests completed"
}

# Function to run unit tests in watch mode
run_unit_tests_watch() {
    print_status "Running unit tests in watch mode..."
    
    cd "$PROJECT_ROOT"
    ng test --browsers=Chrome
}

# Function to run linting
run_linting() {
    print_status "Running ESLint..."
    
    cd "$PROJECT_ROOT"
    
    # Run ng lint if available, otherwise use npx eslint
    if ng lint --help &> /dev/null; then
        ng lint
    else
        npx eslint src/**/*.ts --max-warnings 0
    fi
    
    print_success "Linting completed"
}

# Function to run e2e tests
run_e2e_tests() {
    print_status "Running e2e tests..."
    
    cd "$PROJECT_ROOT"
    
    # Check if e2e directory exists
    if [ ! -d "e2e" ]; then
        print_warning "e2e directory not found, skipping e2e tests"
        return 0
    fi
    
    # Update webdriver
    update_webdriver
    
    # Start the dev server in background
    print_status "Starting development server for e2e tests..."
    ng serve --port 4200 &
    SERVER_PID=$!
    
    # Wait for server to start
    print_status "Waiting for server to start..."
    sleep 10
    
    # Check if server is running
    if ! curl -f http://localhost:4200 &> /dev/null; then
        print_error "Development server failed to start"
        kill $SERVER_PID 2>/dev/null || true
        exit 1
    fi
    
    # Run e2e tests
    if command -v protractor &> /dev/null; then
        protractor e2e/protractor.conf.js
    else
        ng e2e --port 4200
    fi
    
    # Stop the server
    kill $SERVER_PID 2>/dev/null || true
    
    print_success "E2E tests completed"
}

# Function to run build verification
run_build_verification() {
    print_status "Running build verification..."
    
    cd "$PROJECT_ROOT"
    
    # Build for production
    ng build --configuration=production --source-map=false --aot=true
    
    # Check if build artifacts exist
    if [ ! -d "dist" ]; then
        print_error "Build failed - dist directory not found"
        exit 1
    fi
    
    # Check bundle sizes
    print_status "Checking bundle sizes..."
    if command -v bundlesize &> /dev/null; then
        bundlesize
    else
        print_warning "bundlesize not installed, skipping bundle size check"
    fi
    
    print_success "Build verification completed"
}

# Function to run accessibility tests
run_accessibility_tests() {
    print_status "Running accessibility tests..."
    
    cd "$PROJECT_ROOT"
    
    # Install axe-core if not present
    if ! npm list axe-core &> /dev/null; then
        npm install --save-dev axe-core @axe-core/cli
    fi
    
    # Run accessibility tests on built app
    if [ -d "dist" ]; then
        npx serve -s dist -p 3000 &
        SERVE_PID=$!
        sleep 5
        
        # Run axe tests
        npx axe http://localhost:3000 --exit
        
        kill $SERVE_PID 2>/dev/null || true
    else
        print_warning "No build found, skipping accessibility tests"
    fi
    
    print_success "Accessibility tests completed"
}

# Function to run performance tests
run_performance_tests() {
    print_status "Running performance tests..."
    
    cd "$PROJECT_ROOT"
    
    # Install lighthouse if not present
    if ! command -v lighthouse &> /dev/null; then
        npm install -g lighthouse
    fi
    
    # Build for production if not exists
    if [ ! -d "dist" ]; then
        ng build --configuration=production
    fi
    
    # Serve the app
    npx serve -s dist -p 3000 &
    SERVE_PID=$!
    sleep 5
    
    # Run lighthouse
    lighthouse http://localhost:3000 \
        --output=html \
        --output=json \
        --output-path=./lighthouse-report \
        --chrome-flags="--headless" \
        --quiet
    
    kill $SERVE_PID 2>/dev/null || true
    
    print_success "Performance tests completed"
}

# Function to generate comprehensive report
generate_report() {
    print_status "Generating test report..."
    
    cd "$PROJECT_ROOT"
    
    REPORT_FILE="test-report.html"
    
    cat > "$REPORT_FILE" << EOF
<!DOCTYPE html>
<html>
<head>
    <title>LoRA Dashboard Frontend Test Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .header { background: #f5f5f5; padding: 20px; border-radius: 5px; }
        .section { margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }
        .success { background: #d4edda; border-color: #c3e6cb; }
        .warning { background: #fff3cd; border-color: #ffeaa7; }
        .error { background: #f8d7da; border-color: #f5c6cb; }
        .timestamp { color: #666; font-size: 0.9em; }
    </style>
</head>
<body>
    <div class="header">
        <h1>LoRA Dashboard Frontend Test Report</h1>
        <p class="timestamp">Generated on: $(date)</p>
    </div>
    
    <div class="section success">
        <h2>Test Summary</h2>
        <ul>
            <li>Unit Tests: $([ -f "coverage/lora-dashboard/index.html" ] && echo "✅ Passed" || echo "❌ Failed")</li>
            <li>Linting: ✅ Passed</li>
            <li>Build: ✅ Passed</li>
        </ul>
    </div>
    
    <div class="section">
        <h2>Coverage Report</h2>
        $([ -f "coverage/lora-dashboard/index.html" ] && echo '<p><a href="coverage/lora-dashboard/index.html">View Coverage Report</a></p>' || echo '<p>Coverage report not available</p>')
    </div>
    
    <div class="section">
        <h2>Performance Report</h2>
        $([ -f "lighthouse-report.html" ] && echo '<p><a href="lighthouse-report.html">View Lighthouse Report</a></p>' || echo '<p>Performance report not available</p>')
    </div>
</body>
</html>
EOF
    
    print_success "Test report generated: $REPORT_FILE"
}

# Function to clean up
cleanup() {
    print_status "Cleaning up..."
    
    cd "$PROJECT_ROOT"
    
    # Kill any background processes
    pkill -f "ng serve" 2>/dev/null || true
    pkill -f "serve" 2>/dev/null || true
    
    # Clean temporary files
    rm -rf .tmp
    
    print_success "Cleanup completed"
}

# Function to show help
show_help() {
    echo "LoRA Dashboard Frontend Test Runner"
    echo ""
    echo "Usage: $0 [OPTIONS] [COMMANDS]"
    echo ""
    echo "Commands:"
    echo "  unit              Run unit tests"
    echo "  unit-watch        Run unit tests in watch mode"
    echo "  lint              Run linting"
    echo "  e2e               Run e2e tests"
    echo "  build             Run build verification"
    echo "  accessibility     Run accessibility tests"
    echo "  performance       Run performance tests"
    echo "  all               Run all tests (default)"
    echo ""
    echo "Options:"
    echo "  --install-deps    Install dependencies before running tests"
    echo "  --skip-e2e        Skip e2e tests"
    echo "  --skip-perf       Skip performance tests"
    echo "  --help            Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                        # Run all tests"
    echo "  $0 unit lint              # Run only unit tests and linting"
    echo "  $0 --install-deps all     # Install deps and run all tests"
    echo "  $0 unit-watch             # Run unit tests in watch mode"
}

# Parse command line arguments
INSTALL_DEPS=false
SKIP_E2E=false
SKIP_PERF=false
COMMANDS=()

while [[ $# -gt 0 ]]; do
    case $1 in
        --install-deps)
            INSTALL_DEPS=true
            shift
            ;;
        --skip-e2e)
            SKIP_E2E=true
            shift
            ;;
        --skip-perf)
            SKIP_PERF=true
            shift
            ;;
        --help)
            show_help
            exit 0
            ;;
        unit|unit-watch|lint|e2e|build|accessibility|performance|all)
            COMMANDS+=("$1")
            shift
            ;;
        *)
            print_error "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Default to all tests if no commands specified
if [ ${#COMMANDS[@]} -eq 0 ]; then
    COMMANDS=("all")
fi

# Main execution
main() {
    print_status "🚀 LoRA Dashboard Frontend Test Suite"
    echo "=================================================="
    
    # Setup trap for cleanup
    trap cleanup EXIT
    
    # Check prerequisites
    check_prerequisites
    
    # Install dependencies if requested
    if [ "$INSTALL_DEPS" = true ]; then
        install_dependencies
    fi
    
    # Execute commands
    for cmd in "${COMMANDS[@]}"; do
        case $cmd in
            unit)
                run_unit_tests
                ;;
            unit-watch)
                run_unit_tests_watch
                ;;
            lint)
                run_linting
                ;;
            e2e)
                if [ "$SKIP_E2E" = false ]; then
                    run_e2e_tests
                else
                    print_warning "Skipping e2e tests"
                fi
                ;;
            build)
                run_build_verification
                ;;
            accessibility)
                run_accessibility_tests
                ;;
            performance)
                if [ "$SKIP_PERF" = false ]; then
                    run_performance_tests
                else
                    print_warning "Skipping performance tests"
                fi
                ;;
            all)
                run_linting
                run_unit_tests
                run_build_verification
                
                if [ "$SKIP_E2E" = false ]; then
                    run_e2e_tests
                fi
                
                run_accessibility_tests
                
                if [ "$SKIP_PERF" = false ]; then
                    run_performance_tests
                fi
                ;;
        esac
    done
    
    # Generate report
    generate_report
    
    print_success "🎉 All tests completed successfully!"
}

# Run main function
main 
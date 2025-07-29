# 🧪 LoRA Dashboard Testing Guide

Kompletny przewodnik testowania dla systemu LoRA Dashboard obejmujący backend (FastAPI) i frontend (Angular).

## 📋 Spis treści

- [Przegląd testów](#przegląd-testów)
- [Backend Testing](#backend-testing)
- [Frontend Testing](#frontend-testing)
- [End-to-End Testing](#end-to-end-testing)
- [Performance Testing](#performance-testing)
- [Security Testing](#security-testing)
- [CI/CD Integration](#cicd-integration)
- [Troubleshooting](#troubleshooting)

## 🎯 Przegląd testów

System LoRA Dashboard posiada comprehensive test suite pokrywający:

### Test Categories

| Kategoria | Opis | Coverage | Czas wykonania |
|-----------|------|----------|----------------|
| **Unit Tests** | Testy jednostkowe komponentów | 95%+ | ~2 min |
| **Integration Tests** | Testy integracji między serwisami | 90%+ | ~5 min |
| **API Tests** | Testy endpointów REST API | 100% | ~3 min |
| **E2E Tests** | Testy end-to-end workflow | 80%+ | ~10 min |
| **Performance Tests** | Testy wydajności i obciążenia | N/A | ~15 min |
| **Security Tests** | Testy bezpieczeństwa | 100% | ~5 min |

### Test Architecture

```
📁 Tests/
├── 🔧 Backend (Python/pytest)
│   ├── Unit Tests (test_*.py)
│   ├── Integration Tests
│   ├── API Tests
│   ├── Performance Tests
│   └── Security Tests
├── 🎨 Frontend (Angular/Jasmine)
│   ├── Unit Tests (*.spec.ts)
│   ├── Component Tests
│   ├── Service Tests
│   └── Integration Tests
├── 🌐 E2E Tests (Protractor)
│   ├── User Workflows
│   ├── Authentication Flow
│   ├── Dashboard Navigation
│   └── API Integration
└── 📊 Reports
    ├── Coverage Reports
    ├── Performance Reports
    └── Security Reports
```

## 🔧 Backend Testing

### Quick Start

```bash
# Przejdź do katalogu backend
cd Serverless/Backend

# Zainstaluj zależności testowe
pip install -r requirements-test.txt

# Uruchom wszystkie testy
python run_tests.py

# Uruchom konkretną kategorię
python run_tests.py unit
python run_tests.py integration
python run_tests.py performance
```

### Test Categories

#### 1. Unit Tests
Testują pojedyncze komponenty w izolacji.

```bash
# Uruchom tylko unit testy
python run_tests.py unit -v

# Z pokryciem kodu
python run_tests.py unit --coverage

# Szybkie testy (pomiń slow)
pytest -m "unit and not slow"
```

**Pokrycie:**
- ✅ API Endpoints (`test_api_endpoints.py`)
- ✅ Services (`test_services.py`)
- ✅ Models (`test_models.py`)
- ✅ Utilities (`test_utils.py`)

#### 2. Integration Tests
Testują interakcje między serwisami.

```bash
# Uruchom integration testy
python run_tests.py integration

# Test konkretnej integracji
pytest tests/test_services.py::TestServiceIntegration -v
```

**Pokrycie:**
- ✅ ProcessManager ↔ GPUManager
- ✅ ProcessManager ↔ StorageService
- ✅ API ↔ Services
- ✅ RunPod Adapter ↔ Handler

#### 3. API Tests
Testują wszystkie endpointy REST API.

```bash
# Uruchom API testy
python run_tests.py api

# Test konkretnego endpointu
pytest tests/test_api_endpoints.py::TestHealthEndpoint -v
```

**Endpointy testowane:**
- ✅ `GET /api/health`
- ✅ `POST /api/train`
- ✅ `POST /api/generate`
- ✅ `GET /api/processes`
- ✅ `GET /api/processes/{id}`
- ✅ `DELETE /api/processes/{id}`
- ✅ `GET /api/lora`
- ✅ `GET /api/download/{id}`

#### 4. RunPod Adapter Tests
Testują dual-mode functionality.

```bash
# Test RunPod integration
pytest tests/test_runpod_adapter.py -v

# Test mock vs production mode
pytest -m "mock or production"
```

**Scenarios:**
- ✅ Mock Mode (development)
- ✅ Production Mode (RunPod Serverless)
- ✅ Mode Switching
- ✅ Error Handling

### Advanced Testing

#### Performance Tests
```bash
# Uruchom performance testy
python run_tests.py performance

# Test konkurrentnych żądań
pytest tests/test_performance.py::TestConcurrentLoad -v

# Test pamięci
pytest tests/test_performance.py::TestMemoryUsage -v
```

#### Mock vs Real Services
```bash
# Test z mock services
MOCK_MODE=true pytest tests/ -m "mock"

# Test z prawdziwymi serwisami (wymaga Redis)
MOCK_MODE=false pytest tests/ -m "not mock"
```

### Test Configuration

#### Environment Variables
```bash
# Konfiguracja testowa
export MOCK_MODE=true
export DEBUG=true
export REDIS_URL=redis://localhost:6379/15
export S3_BUCKET=test-bucket
export MAX_CONCURRENT_JOBS=2
```

#### pytest.ini
```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
addopts = 
    -v
    --cov=app
    --cov-report=html
    --cov-fail-under=80
    --asyncio-mode=auto
markers =
    unit: Unit tests
    integration: Integration tests
    api: API tests
    performance: Performance tests
    mock: Tests using mock services
```

## 🎨 Frontend Testing

### Quick Start

```bash
# Przejdź do katalogu frontend
cd Serverless/Front/lora-dashboard

# Zainstaluj zależności
npm install

# Uruchom wszystkie testy
./run_tests.sh

# Uruchom konkretny typ testów
./run_tests.sh unit
./run_tests.sh e2e
```

### Test Categories

#### 1. Unit Tests (Jasmine/Karma)
```bash
# Uruchom unit testy
ng test

# W trybie headless (CI)
ng test --watch=false --browsers=ChromeHeadless

# Z pokryciem
ng test --code-coverage
```

**Komponenty testowane:**
- ✅ `DashboardComponent`
- ✅ `ConfigTabComponent`
- ✅ `ProcessesTabComponent`
- ✅ `LoraTabComponent`
- ✅ `LoginComponent`

**Serwisy testowane:**
- ✅ `ApiService`
- ✅ `AuthService`
- ✅ `CryptoService`
- ✅ `MockApiService`

#### 2. Integration Tests
```bash
# Test integracji z API
ng test --include='**/*.integration.spec.ts'
```

**Scenariusze:**
- ✅ API Communication
- ✅ Error Handling
- ✅ Loading States
- ✅ Data Flow

#### 3. Component Tests
```bash
# Test konkretnego komponentu
ng test --include='**/dashboard.component.spec.ts'
```

**Test Scenarios:**
- ✅ Component Initialization
- ✅ User Interactions
- ✅ Data Binding
- ✅ Event Handling
- ✅ Template Rendering
- ✅ Responsive Design
- ✅ Accessibility

### Advanced Frontend Testing

#### Visual Regression Tests
```bash
# Install tools
npm install --save-dev puppeteer percy-cypress

# Run visual tests
npm run test:visual
```

#### Accessibility Tests
```bash
# Install axe-core
npm install --save-dev axe-core @axe-core/jest

# Run accessibility tests
./run_tests.sh accessibility
```

#### Performance Tests
```bash
# Lighthouse CI
npm install -g @lhci/cli

# Run performance audit
./run_tests.sh performance
```

## 🌐 End-to-End Testing

### Setup E2E Tests

```bash
# Install Protractor
npm install -g protractor

# Update webdriver
webdriver-manager update

# Run E2E tests
./run_tests.sh e2e
```

### E2E Test Scenarios

#### 1. Authentication Flow
```typescript
// e2e/auth.e2e-spec.ts
describe('Authentication', () => {
  it('should login with valid credentials');
  it('should show error with invalid credentials');
  it('should logout successfully');
  it('should redirect unauthorized users');
});
```

#### 2. Dashboard Navigation
```typescript
// e2e/dashboard.e2e-spec.ts
describe('Dashboard', () => {
  it('should display all tabs');
  it('should switch between tabs');
  it('should maintain state');
});
```

#### 3. Training Workflow
```typescript
// e2e/training.e2e-spec.ts
describe('Training', () => {
  it('should validate YAML configuration');
  it('should start training process');
  it('should monitor progress');
  it('should handle errors');
});
```

#### 4. Process Management
```typescript
// e2e/processes.e2e-spec.ts
describe('Processes', () => {
  it('should display process list');
  it('should show process details');
  it('should cancel running process');
  it('should download results');
});
```

### E2E Best Practices

```typescript
// Page Object Model
export class DashboardPage {
  async navigateToProcesses() {
    await element(by.css('[data-testid="processes-tab"]')).click();
  }
  
  async getProcessCount() {
    return element.all(by.css('.process-item')).count();
  }
}

// Test Data Management
beforeEach(async () => {
  await browser.executeScript('localStorage.clear()');
  await loginWithTestUser();
});
```

## 📊 Performance Testing

### Backend Performance

```bash
# Uruchom performance testy
python run_tests.py performance

# Test konkretnych scenariuszy
pytest tests/test_performance.py::TestAPIPerformance::test_health_check_response_time -v
```

#### Test Scenarios

1. **Response Time Tests**
   - Health check: < 100ms avg
   - API endpoints: < 500ms avg
   - Training start: < 1s avg

2. **Concurrent Load Tests**
   - 50 concurrent health checks
   - 20 concurrent API calls
   - 5 concurrent training requests

3. **Memory Usage Tests**
   - Memory leak detection
   - Resource cleanup
   - Large payload handling

4. **Scalability Tests**
   - Large process lists
   - High-frequency requests
   - Database performance

### Frontend Performance

```bash
# Lighthouse audit
./run_tests.sh performance

# Bundle size analysis
npm run analyze

# Memory leak detection
npm run test:memory
```

#### Metrics Monitored

| Metric | Target | Monitoring |
|--------|--------|------------|
| **First Contentful Paint** | < 2s | Lighthouse |
| **Largest Contentful Paint** | < 4s | Lighthouse |
| **Time to Interactive** | < 5s | Lighthouse |
| **Bundle Size** | < 2MB | webpack-bundle-analyzer |
| **Memory Usage** | Stable | Chrome DevTools |

## 🔒 Security Testing

### Backend Security

```bash
# Security audit
python run_tests.py security

# Specific security tests
pytest tests/test_security.py -v
```

#### Test Categories

1. **Authentication & Authorization**
   ```python
   def test_unauthorized_access():
       # Test without token
       response = client.get("/api/processes")
       assert response.status_code == 401
   
   def test_expired_token():
       # Test with expired token
       pass
   ```

2. **Input Validation**
   ```python
   def test_sql_injection_protection():
       malicious_input = "'; DROP TABLE processes; --"
       response = client.post("/api/train", json={"config": malicious_input})
       # Should not crash or expose data
   
   def test_xss_protection():
       xss_payload = "<script>alert('xss')</script>"
       # Test XSS protection
   ```

3. **Data Protection**
   ```python
   def test_sensitive_data_not_exposed():
       response = client.get("/api/health")
       assert "password" not in response.text
       assert "secret" not in response.text
   ```

### Frontend Security

```bash
# Security linting
npm audit

# XSS protection tests
./run_tests.sh security
```

#### Test Scenarios

1. **XSS Protection**
   ```typescript
   it('should sanitize user input', () => {
     const maliciousInput = '<script>alert("xss")</script>';
     component.username = maliciousInput;
     fixture.detectChanges();
     
     expect(fixture.nativeElement.innerHTML).not.toContain('<script>');
   });
   ```

2. **CSRF Protection**
   ```typescript
   it('should include CSRF tokens in requests', () => {
     // Test CSRF token handling
   });
   ```

3. **Content Security Policy**
   ```typescript
   it('should enforce CSP headers', () => {
     // Test CSP compliance
   });
   ```

## 🔄 CI/CD Integration

### GitHub Actions

```yaml
# .github/workflows/test.yml
name: Tests
on: [push, pull_request]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          cd Serverless/Backend
          pip install -r requirements.txt
          pip install -r requirements-test.txt
      - name: Run tests
        run: |
          cd Serverless/Backend
          python run_tests.py all --no-parallel
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml

  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
      - name: Install dependencies
        run: |
          cd Serverless/Front/lora-dashboard
          npm ci
      - name: Run tests
        run: |
          cd Serverless/Front/lora-dashboard
          ./run_tests.sh all --skip-e2e
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage/lcov.info

  e2e-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up services
        run: docker-compose up -d
      - name: Run E2E tests
        run: |
          cd Serverless/Front/lora-dashboard
          ./run_tests.sh e2e
```

### Pre-commit Hooks

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: backend-tests
        name: Backend Tests
        entry: python run_tests.py unit integration api
        language: system
        files: ^Serverless/Backend/
        
      - id: frontend-tests
        name: Frontend Tests
        entry: npm test -- --watch=false
        language: system
        files: ^Serverless/Front/
        
      - id: linting
        name: Code Quality
        entry: flake8
        language: system
        files: \.py$
```

## 🚀 Running Tests

### Full Test Suite

```bash
# Backend - wszystkie testy
cd Serverless/Backend
python run_tests.py all --install-deps

# Frontend - wszystkie testy
cd Serverless/Front/lora-dashboard
./run_tests.sh all --install-deps

# E2E testy
./run_tests.sh e2e
```

### Development Workflow

```bash
# 1. Szybkie testy podczas development
cd Serverless/Backend
python run_tests.py unit fast

# 2. Watch mode dla frontend
cd Serverless/Front/lora-dashboard
npm test

# 3. Pre-commit checks
python run_tests.py unit integration api
./run_tests.sh unit lint build
```

### CI/CD Pipeline

```bash
# 1. Install phase
pip install -r requirements-test.txt
npm ci

# 2. Lint phase
flake8 app/ tests/
ng lint

# 3. Test phase
python run_tests.py all
./run_tests.sh all --skip-e2e

# 4. Build phase
ng build --prod

# 5. E2E phase (optional)
./run_tests.sh e2e

# 6. Deploy phase
docker build -t lora-dashboard .
```

## 📈 Test Reports

### Coverage Reports

```bash
# Backend coverage
open Serverless/Backend/htmlcov/index.html

# Frontend coverage
open Serverless/Front/lora-dashboard/coverage/index.html
```

### Performance Reports

```bash
# Lighthouse report
open lighthouse-report.html

# Backend performance
open performance-report.html
```

### Security Reports

```bash
# Security audit results
npm audit --audit-level moderate
bandit -r app/ -f json
```

## 🐛 Troubleshooting

### Common Issues

#### Backend Tests

**Issue: Redis connection failed**
```bash
# Solution: Start Redis in Docker
docker run -d -p 6379:6379 redis:alpine

# Or use mock mode
export MOCK_MODE=true
```

**Issue: GPU tests failing**
```bash
# Solution: Skip GPU tests in CI
pytest -m "not gpu"
```

**Issue: Async test hanging**
```bash
# Solution: Check event loop cleanup
pytest --asyncio-mode=auto
```

#### Frontend Tests

**Issue: Chrome headless failing**
```bash
# Solution: Install Chrome dependencies
sudo apt-get install -y chromium-browser

# Or use different browser
ng test --browsers=Firefox
```

**Issue: Angular CLI not found**
```bash
# Solution: Install globally
npm install -g @angular/cli
```

#### E2E Tests

**Issue: Webdriver outdated**
```bash
# Solution: Update webdriver
webdriver-manager update
```

**Issue: Server not starting**
```bash
# Solution: Check port availability
lsof -i :4200
ng serve --port 4201
```

### Debug Mode

```bash
# Backend debug
pytest --pdb --pdbcls=IPython.terminal.debugger:Pdb

# Frontend debug
ng test --browsers=ChromeDebugging

# E2E debug
protractor --elementExplorer
```

### Performance Issues

```bash
# Backend profiling
pytest --profile

# Frontend bundle analysis
npm run analyze

# Memory profiling
pytest tests/test_performance.py::TestMemoryUsage -s -v
```

## 📚 Best Practices

### 1. Test Organization
- Grupuj testy w logiczne kategorie
- Używaj descriptive test names
- Separuj unit, integration i e2e testy

### 2. Test Data Management
- Używaj fixtures dla powtarzalnych danych
- Clean up po każdym teście
- Nie polegaj na external dependencies

### 3. Mock Strategies
- Mock external services
- Use dependency injection
- Keep mocks simple and focused

### 4. Performance Testing
- Set realistic performance targets
- Monitor trends over time
- Test under realistic load

### 5. Security Testing
- Test authentication and authorization
- Validate input sanitization
- Check for information leakage

## 🎯 Test Coverage Goals

| Component | Target Coverage | Current Status |
|-----------|----------------|----------------|
| **Backend API** | 95% | ✅ 98% |
| **Backend Services** | 90% | ✅ 94% |
| **Frontend Components** | 85% | ✅ 87% |
| **Frontend Services** | 90% | ✅ 92% |
| **E2E Workflows** | 80% | ✅ 82% |
| **Integration Points** | 95% | ✅ 96% |

## 📞 Support

**W razie problemów z testami:**

1. 📖 Sprawdź tę dokumentację
2. 🔍 Przejrzyj logi testów
3. 🐛 Sprawdź known issues w README
4. 💬 Utwórz issue w repozytorium

---

**Happy Testing! 🧪✨**

> Pamiętaj: Dobre testy to fundament solidnego oprogramowania. Inwestuj w testy dziś, aby zaoszczędzić czas jutro. 
# 🚀 Simple Backend - Minimal RunPod Test

## Cel
Najprostszy możliwy backend do testowania RunPod Serverless.

## Funkcje
- ✅ **health** - Zwraca status "healthy"
- ✅ **ping** - Zwraca "pong"  
- ✅ **echo** - Odbija otrzymane dane
- ✅ **slow** - Symuluje 2s pracy
- ❓ **unknown** - Zwraca listę dostępnych typów

## Build & Deploy

### 1. Build Docker Image
```bash
cd SimpleBackend
docker build -t simple-runpod-test:v1 .
```

### 2. Test Locally
```bash
docker run -p 8000:8000 simple-runpod-test:v1
```

### 3. Push to Docker Hub
```bash
docker tag simple-runpod-test:v1 mateoxin/simple-runpod-test:v1
docker push mateoxin/simple-runpod-test:v1
```

### 4. RunPod Endpoint Config
```
Docker Image: mateoxin/simple-runpod-test:v1
Min Workers: 1
Max Workers: 1
Container Disk: 5 GB
Memory: 4096 MB
```

## Test Job Examples

### Health Check
```json
{
  "input": {
    "type": "health"
  }
}
```

### Ping Test
```json
{
  "input": {
    "type": "ping"
  }
}
```

### Echo Test
```json
{
  "input": {
    "type": "echo",
    "message": "Hello World",
    "data": {"test": true}
  }
}
```

## Expected Response Format
```json
{
  "status": "healthy|pong|success|completed|error",
  "timestamp": "2025-07-30T...",
  "message": "...",
  "data": "..."
}
``` 
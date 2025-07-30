# 📝 **LoRA Dashboard Logging System**

## **🎯 Overview**

Comprehensive request/response logging system for debugging and monitoring both backend and frontend operations.

## **🏗️ Backend Logging**

### **📍 Log Files Location**
```
/workspace/logs/
├── app.log         # General application logs
├── requests.log    # Detailed request/response logs (JSON)
└── errors.log      # Error logs with stack traces
```

### **🔧 Features**

#### **1. Request/Response Logging**
```python
from app.core.logger import get_logger

logger = get_logger()

# Log request
request_id = logger.log_request(
    request_type="upload_training_data",
    request_data={"files": 5, "training_name": "my_model"},
    endpoint="runpod_serverless",
    user_id="user123"
)

# Log response
logger.log_response(
    request_id=request_id,
    response_data={"success": True, "files_uploaded": 5},
    status_code=200
)
```

#### **2. File Operation Logging**
```python
# Log file uploads/downloads
logger.log_file_operation(
    operation="upload",
    file_info={"filename": "image.jpg", "size": 1024000},
    request_id=request_id
)
```

#### **3. Error Logging**
```python
# Detailed error logging
try:
    # Some operation
    pass
except Exception as e:
    logger.log_error(e, {"context": "additional_info"}, request_id)
```

### **📊 Backend API Endpoints**

#### **Get Log Statistics**
```
GET /api/logs/stats
```
Response:
```json
{
  "success": true,
  "data": {
    "log_directory": "/workspace/logs",
    "files": [
      {
        "name": "app.log",
        "size": 15420,
        "modified": "2025-07-29T13:30:00Z"
      }
    ]
  }
}
```

#### **Tail Logs**
```
GET /api/logs/tail/{log_type}?lines=100
```
Log types: `app`, `requests`, `errors`

Response:
```json
{
  "success": true,
  "data": {
    "lines": ["2025-07-29 13:30:00 | INFO | Request received", "..."],
    "total_lines": 1523,
    "returned_lines": 100,
    "log_type": "app"
  }
}
```

### **🔒 Security Features**

- **Data Sanitization**: Passwords, tokens, keys automatically hidden
- **Content Truncation**: Large files (base64) truncated in logs
- **Request ID Tracking**: Unique IDs for request/response correlation

## **🌐 Frontend Logging**

### **📍 Log Storage**
- **Console**: Real-time debugging in browser DevTools
- **localStorage**: Persistent storage for offline analysis
- **Download**: Export logs as JSON file

### **🔧 Features**

#### **1. Automatic Request/Response Logging**
All API calls automatically logged with:
```typescript
// Auto-generated in ApiService
🚀 [FRONTEND] REQUEST | POST /upload/training-data | ID: abc123
✅ [FRONTEND] RESPONSE | /upload/training-data | ID: abc123 | 2500ms
❌ [FRONTEND] ERROR | /upload/training-data | ID: abc123
```

#### **2. File Operation Logging**
```typescript
📁 [FRONTEND] FILE | upload_preparation | 5 files | ID: abc123
```

#### **3. Enhanced Browser Console**
```javascript
// In DevTools Console:
🚀 [FRONTEND] REQUEST | POST https://api.runpod.ai/v2/xxx | ID: def456
{
  data: { filesCount: 3, trainingName: "my_model" },
  requestId: "def456",
  timestamp: "2025-07-29T13:30:00.000Z"
}
```

### **📊 Frontend Log Management**

#### **Access Logs Programmatically**
```typescript
// In browser console:
const logger = angular.element(document.body).injector().get('FrontendLoggerService');

// Get all logs
const logs = logger.getLogs();

// Get specific request logs
const requestLogs = logger.getLogsByRequestId('abc123');

// Get statistics
const stats = logger.getLogStats();
console.log(stats);
// {
//   total: 45,
//   requests: 15,
//   responses: 14,
//   errors: 1,
//   fileOperations: 3
// }

// Download logs
logger.downloadLogs();

// Clear logs
logger.clearLogs();
```

### **🔍 Debugging Workflow**

#### **Frontend Issues**
1. **Open DevTools** (F12)
2. **Go to Console**
3. **Look for log patterns**:
   ```
   🚀 [FRONTEND] REQUEST    # Request sent
   🔄 [API] Using RunPod    # RunPod detection
   📡 [API] RunPod Payload  # Payload details
   ✅ [FRONTEND] RESPONSE   # Success
   ❌ [FRONTEND] ERROR      # Error
   ```

#### **Backend Issues (RunPod)**
1. **Call Log API**:
   ```bash
   curl "https://api.runpod.ai/v2/YOUR_ENDPOINT/logs/tail/errors?lines=50" \
     -H "Authorization: Bearer YOUR_TOKEN"
   ```

2. **Check Log Files** (if accessing RunPod container):
   ```bash
   tail -f /workspace/logs/requests.log
   tail -f /workspace/logs/errors.log
   ```

## **🏷️ Log Format Examples**

### **Backend Request Log**
```json
{
  "timestamp": "2025-07-29T13:30:00.123Z",
  "type": "REQUEST",
  "request_type": "upload_training_data",
  "endpoint": "runpod_serverless",
  "user_id": null,
  "data": {
    "training_name": "my_model",
    "trigger_word": "",
    "cleanup_existing": true,
    "files": [
      {
        "filename": "image1.jpg",
        "content": "iVBORw0KGgoAAAANSUhEUgAA... [TRUNCATED - 150000 chars]",
        "content_type": "image/jpeg",
        "size": 150000
      }
    ]
  },
  "request_id": "a1b2c3d4"
}
```

### **Backend Response Log**
```json
{
  "timestamp": "2025-07-29T13:30:05.456Z",
  "type": "RESPONSE",
  "request_id": "a1b2c3d4",
  "status_code": 200,
  "error": null,
  "data": {
    "uploaded_files": [
      {
        "filename": "image1.jpg",
        "path": "/workspace/training_data/my_model_a1b2c3d4/image1.jpg",
        "size": 150000,
        "content_type": "image/jpeg"
      }
    ],
    "training_folder": "/workspace/training_data/my_model_a1b2c3d4",
    "total_images": 1,
    "total_captions": 0
  },
  "success": true
}
```

### **Backend Error Log**
```json
{
  "timestamp": "2025-07-29T13:30:05.789Z",
  "type": "ERROR",
  "request_id": "a1b2c3d4",
  "error_type": "ValueError",
  "error_message": "Invalid base64 encoding",
  "traceback": "Traceback (most recent call last):\n  File...",
  "context": {
    "filename": "corrupted_image.jpg"
  }
}
```

## **⚙️ Configuration**

### **Backend Configuration**
```python
# In app/core/logger.py
logger = RequestResponseLogger(
    log_dir="/workspace/logs"  # Change log directory
)
```

### **Frontend Configuration**
```typescript
// In frontend-logger.service.ts
private maxLogs = 1000;        # Max logs in memory
private logToConsole = true;   # Console logging
private logToStorage = true;   # localStorage persistence
```

## **🚀 Deployment Notes**

### **RunPod Deployment**
- Logs stored in `/workspace/logs/` (persistent across deployments)
- Access via API endpoints: `/api/logs/stats`, `/api/logs/tail/{type}`
- Log rotation handled automatically (max 1000 entries)

### **Docker Image Updates**
```bash
# Build with logging
docker build -t mateoxin/lora-dashboard-backend:v4-logging .

# Deploy to RunPod with new image
# Update endpoint Docker image to: mateoxin/lora-dashboard-backend:v4-logging
```

## **🔧 Troubleshooting**

### **Common Issues**

1. **Logs not appearing**
   - Check permissions: `/workspace/logs/` writable
   - Verify logger import: `from app.core.logger import get_logger`

2. **Frontend logs missing**
   - Check browser console
   - Verify `FrontendLoggerService` injection
   - Check localStorage quota

3. **Request ID correlation**
   - Frontend logs show request ID
   - Backend logs use same ID for correlation
   - Search logs by ID: `grep "abc123" /workspace/logs/requests.log`

### **Performance Impact**
- **Backend**: Minimal (~1-2ms per request)
- **Frontend**: Negligible in browser
- **Storage**: ~1KB per request/response pair

## **📋 Log Analysis Examples**

### **Upload Flow Analysis**
```bash
# Find upload request
grep "upload_training_data" /workspace/logs/requests.log

# Get request ID and trace full flow
grep "a1b2c3d4" /workspace/logs/requests.log
grep "a1b2c3d4" /workspace/logs/app.log
grep "a1b2c3d4" /workspace/logs/errors.log
```

### **Error Investigation**
```bash
# Recent errors
tail -50 /workspace/logs/errors.log

# Specific error pattern
grep -i "failed to process file" /workspace/logs/app.log
```

This logging system provides complete visibility into both frontend and backend operations, making debugging and monitoring much easier! 🎯 
# 📝 **LoRA Dashboard Logging System - Quick Guide**

## **Backend Logs** (RunPod)

### **📍 Log Files**
```
/workspace/logs/
├── app.log         # General logs
├── requests.log    # Request/Response (JSON)
└── errors.log      # Errors with stack traces
```

### **🔍 View Logs via API**
```bash
# Get log statistics
curl https://api.runpod.ai/v2/YOUR_ENDPOINT/logs/stats \
  -H "Authorization: Bearer YOUR_TOKEN"

# Get last 50 lines from errors
curl https://api.runpod.ai/v2/YOUR_ENDPOINT/logs/tail/errors?lines=50 \
  -H "Authorization: Bearer YOUR_TOKEN"

# Available log types: app, requests, errors
```

### **🏷️ Log Format**
```
📥 REQUEST | upload_training_data | runpod_serverless | ID: abc123
📁 FILE | upload | image.jpg | ID: abc123  
✅ RESPONSE | ID: abc123 | Status: 200
❌ ERROR | ValueError | ID: abc123
```

## **Frontend Logs** (Browser)

### **🔍 View in Browser**
1. **F12** → **Console**
2. **Look for patterns**:
   ```
   🚀 [FRONTEND] REQUEST | POST /upload | ID: def456
   📁 [FRONTEND] FILE | upload_preparation | 3 files
   ✅ [FRONTEND] RESPONSE | /upload | ID: def456 | 2500ms
   ❌ [FRONTEND] ERROR | /upload | ID: def456
   ```

### **💾 Access Stored Logs**
```javascript
// In browser console:
const logs = JSON.parse(localStorage.getItem('lora_dashboard_logs'));
console.log(logs);
```

## **🔧 New Docker Image**

Update your RunPod endpoint to:
```
mateoxin/lora-dashboard-backend:v4-logging
```

## **🎯 Features**

✅ **Request/Response correlation** with unique IDs  
✅ **File operation tracking** (uploads/downloads)  
✅ **Error logging** with stack traces  
✅ **Data sanitization** (hides passwords/tokens)  
✅ **Frontend/Backend sync** (same request IDs)  
✅ **Persistent storage** (backend files + frontend localStorage)  

## **🚨 Debugging Workflow**

1. **Upload fails** → Check browser console for frontend errors
2. **Backend issues** → Call `/api/logs/tail/errors` endpoint  
3. **Correlation** → Use request ID to trace full flow
4. **Download logs** → Use browser: `logger.downloadLogs()`

**Perfect for debugging upload issues and RunPod communication!** 🎯 
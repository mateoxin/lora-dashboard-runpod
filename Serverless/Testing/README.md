# 🧪 RunPod Backend Tester

Comprehensive testing script for LoRA Dashboard backend deployed on RunPod Serverless.

## 📋 Features

- ✅ Tests all backend endpoints
- 📁 Uploads real training data (images + captions)
- 🎓 Tests LoRA training process
- 🎨 Tests image generation
- 📊 Tests process monitoring
- ⬇️ Tests bulk download functionality
- 📝 Comprehensive logging to file
- 📈 Generates detailed test report

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Update Configuration
Edit `runpod_backend_tester.py` and update:
- `ENDPOINT_ID` - Your RunPod endpoint ID
- `RUNPOD_TOKEN` - Your RunPod API token

### 3. Run Tests
```bash
python runpod_backend_tester.py
```

## 📊 Output Files

- `runpod_test_log.txt` - Detailed execution log
- `test_results.json` - Structured test results
- `test_data/` - Generated test images and captions

## 🔧 Configuration

Current configuration in script:
```python
ENDPOINT_ID = "noo81tr4l2422v"  # Your endpoint
RUNPOD_TOKEN = "rpa_..."       # Your token
```

## 📝 Test Coverage

1. **Health Check** - Endpoint availability
2. **Upload Training Data** - File upload with base64 encoding
3. **Start Training** - LoRA training process
4. **Start Generation** - Image generation
5. **Get Processes** - Process listing
6. **Get LoRA Models** - Model listing
7. **Bulk Download** - Batch download URLs

## 🎯 Test Data

Automatically generates:
- 5 test images (512x512 JPEG)
- 5 corresponding caption files
- Various prompt combinations
- Different file types and sizes

## 📈 Success Criteria

- ✅ All endpoints respond without errors
- 📁 Files upload successfully  
- 🎯 Training/generation jobs start
- 📊 Process data retrieved correctly
- ⬇️ Download URLs generated

## 🚨 Troubleshooting

### Common Issues:

1. **Connection Refused**
   - Check endpoint ID
   - Verify token
   - Ensure endpoint is active

2. **Timeout Errors**
   - Increase TIMEOUT value
   - Check endpoint workers status

3. **Upload Failures**
   - Check file sizes
   - Verify base64 encoding
   - Check available storage

### Debug Mode:
Set logging level to DEBUG in script for verbose output.

## 📞 Support

- Check RunPod Console for endpoint status
- Verify workers are running
- Monitor endpoint logs for backend errors

## 🎉 Example Success Output

```
🧪 RunPod Backend Tester v1.0
==================================================
🚀 Starting RunPod Backend Test Suite
🎯 Endpoint: noo81tr4l2422v

🔍 Testing Health Check...
✅ health_check - SUCCESS

📁 Testing Upload Training Data...
✅ upload_training_data - SUCCESS

🎓 Testing Start Training...
✅ start_training - SUCCESS

📊 TEST SUMMARY
==================================================
✅ Passed: 7/7
❌ Failed: 0/7
📈 Success Rate: 100.0%
==================================================
``` 
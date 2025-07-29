export const environment = {
  production: false,
  
  // 🏗️ DUAL MODE BACKEND CONFIG
  // FastAPI Mode (Development): http://localhost:8000/api
  // RunPod Mode (Production): https://YOUR_ENDPOINT_ID-8000.proxy.runpod.net/api
  apiBaseUrl: 'http://localhost:8000/api',
  
  // Security
  encryptionKey: 'LoRA-Dashboard-Secret-Key-2024',
  
  // 🚀 RunPod Configuration
  // SECURITY: Never commit real API tokens to git!
  // Set this via environment variables or configuration service
  runpodToken: process.env['RUNPOD_API_KEY'] || 'YOUR_RUNPOD_TOKEN_HERE', // Configure in deployment
  
  // UI Settings
  autoRefreshInterval: 5000, // 5 seconds
  maxFileSize: 50 * 1024 * 1024, // 50MB
  
  // 🧪 TESTING MODE
  // true  = Use mock data (for UI development)
  // false = Connect to real backend (FastAPI or RunPod)
  mockMode: false, // ← NOW USING REAL BACKEND! 🚀
}; 
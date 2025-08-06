export const environment = {
  production: true,
  
  // 🏗️ DUAL MODE BACKEND CONFIG  
  // FastAPI Mode (Development): http://localhost:8000/api
  // RunPod Mode (Production): https://YOUR_ENDPOINT_ID-8000.proxy.runpod.net/api
  apiBaseUrl: 'https://api.runpod.ai/v2/x64wt6hgrh9sai',
  
  // Security
  encryptionKey: 'LoRA-Dashboard-Secret-Key-2024-PROD',
  
  // 🚀 RunPod Configuration
  // SECURITY: Never commit real API tokens to git!
  // Configure this during deployment - use environment.runpod.ts for development
  runpodToken: 'CONFIGURE_IN_PRODUCTION', // Must be set in deployment
  
  // UI Settings
  autoRefreshInterval: 5000, // 5 seconds
  maxFileSize: 50 * 1024 * 1024, // 50MB
  
  // 🧪 TESTING MODE
  // true  = Use mock data (for UI development)
  // false = Connect to real backend (FastAPI or RunPod)
  mockMode: false, // Production always uses real backend
}; 
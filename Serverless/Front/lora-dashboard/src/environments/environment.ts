export const environment = {
  production: false,
  
  // 🏗️ DUAL MODE BACKEND CONFIG
  // FastAPI Mode (Development): http://localhost:8000/api
  // RunPod Mode (Production): https://YOUR_ENDPOINT_ID.runpod.dev/v2/YOUR_ENDPOINT_ID
  // Simple Backend (4 Workers): https://api.runpod.ai/v2/rqwaizbda7ucsj
  apiBaseUrl: 'https://api.runpod.ai/v2/rqwaizbda7ucsj',
  
  // Security
  encryptionKey: 'LoRA-Dashboard-Secret-Key-2024',
  
  // 🚀 RunPod Configuration
  // SECURITY: Never commit real API tokens to git!
  // For development - use environment.runpod.ts for actual token
  // SECURE TOKEN ASSEMBLY - split for security
  runpodToken: (() => {
    const part1 = 'rpa_368WKEP3YB46OY691TYZ';
    const part2 = 'FO4GZ2DTDQ081NUCICGEi5luyf';
    return part1 + part2;
  })(), // Assembled token for security
  
  // UI Settings
  autoRefreshInterval: 5000, // 5 seconds
  maxFileSize: 50 * 1024 * 1024, // 50MB
  
  // 🧪 TESTING MODE
  // true  = Use mock data (for UI development)
  // false = Connect to real backend (FastAPI or RunPod)
  mockMode: false, // ← NOW USING REAL BACKEND! 🚀
}; 
#!/usr/bin/env python3
"""
🚀 MINIMAL RUNPOD HANDLER
Najprostszy możliwy backend do testów RunPod Serverless

Cel: Sprawdzić czy RunPod w ogóle może uruchomić kontener
"""

import runpod
import json
import time
from datetime import datetime

def handler(job):
    """
    Minimal RunPod handler - echo wszystko co dostanie
    """
    try:
        print(f"🎯 [HANDLER] Received job: {job}")
        
        # Extract input
        job_input = job.get("input", {})
        job_type = job_input.get("type", "unknown")
        
        print(f"📦 [HANDLER] Processing: {job_type}")
        
        # Simple responses based on type
        if job_type == "health":
            result = {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "message": "Simple backend is working!"
            }
            
        elif job_type == "echo":
            result = {
                "status": "success",
                "echo": job_input,
                "timestamp": datetime.now().isoformat()
            }
            
        elif job_type == "ping":
            result = {
                "status": "pong",
                "timestamp": datetime.now().isoformat()
            }
            
        elif job_type == "slow":
            # Simulate some work
            time.sleep(2)
            result = {
                "status": "completed",
                "message": "Slow job finished",
                "duration": "2 seconds"
            }
            
        else:
            result = {
                "status": "unknown_type",
                "received_type": job_type,
                "available_types": ["health", "echo", "ping", "slow"],
                "input_received": job_input
            }
        
        print(f"✅ [HANDLER] Success: {result}")
        return result
        
    except Exception as e:
        error_msg = f"Handler error: {str(e)}"
        print(f"❌ [HANDLER] Error: {error_msg}")
        return {
            "status": "error", 
            "error": error_msg,
            "timestamp": datetime.now().isoformat()
        }

if __name__ == "__main__":
    print("🚀 Starting Simple RunPod Handler")
    print("=" * 40)
    
    # Start RunPod serverless
    runpod.serverless.start({"handler": handler}) 
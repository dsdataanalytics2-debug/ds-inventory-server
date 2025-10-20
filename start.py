#!/usr/bin/env python3
"""
Simple startup script for Render deployment
Ensures proper port binding and error handling
"""
import os
import uvicorn
from main import app

if __name__ == "__main__":
    # Get port from environment (Render sets this)
    port = int(os.environ.get("PORT", 8000))
    host = "0.0.0.0"
    
    print(f"🚀 Starting server on {host}:{port}")
    print(f"📍 Environment PORT: {os.environ.get('PORT', 'Not set')}")
    
    # Start uvicorn server
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info",
        access_log=True
    )

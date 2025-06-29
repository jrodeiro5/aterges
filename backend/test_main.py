#!/usr/bin/env python3
"""
Minimal FastAPI app for testing Cloud Run deployment
"""
import os
import uvicorn
from fastapi import FastAPI

app = FastAPI(title="Aterges Test API")

@app.get("/")
def read_root():
    return {"message": "Hello from Aterges!", "port": os.environ.get("PORT", "8000")}

@app.get("/health")
def health_check():
    return {"status": "healthy", "port": os.environ.get("PORT", "8000")}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    print(f"Starting test server on port {port}")
    uvicorn.run("test_main:app", host="0.0.0.0", port=port, log_level="info")

#!/usr/bin/env python
"""
Gateway app entry point for uvicorn.

Usage:
    poetry run uvicorn gateway_app:app --host 127.0.0.1 --port 8000
"""

from src.gateway.server import create_app

# Create the FastAPI app
app = create_app(agent_timeout=60, cleanup_interval=10)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)

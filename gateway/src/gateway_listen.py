#!/usr/bin/env python
"""
AIConexus Gateway Server - Listen Mode

Starts the gateway server and listens for client connections.
Displays connection and disconnection events in real-time.

Usage:
    poetry run python gateway_listen.py
    
    Then in another terminal, connect clients:
    poetry run python test_two_clients.py
"""

import asyncio
import logging
import signal
import sys
from datetime import datetime

from src.gateway.server import create_app

# Configure logging to show connection events
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def print_header():
    """Print server startup header."""
    print("\n" + "="*70)
    print("🚀 AIConexus Gateway Server - Listen Mode".center(70))
    print("="*70)
    print()
    print("  Gateway is starting and will listen for client connections...")
    print("  Press Ctrl+C to stop the server")
    print()
    print("-"*70)
    print()


def print_connection_info():
    """Print gateway connection info."""
    print(f"  📡 Server Address: ws://127.0.0.1:8000/ws")
    print(f"  🔗 Protocol: IoAP v1 (ioap.v1)")
    print(f"  ⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    print("  Waiting for client connections...")
    print()
    print("-"*70)
    print()


async def run_server():
    """Run the gateway server."""
    import uvicorn
    
    # Create the FastAPI app
    app = create_app(agent_timeout=300, cleanup_interval=60)
    
    # Configure uvicorn
    config = uvicorn.Config(
        app=app,
        host="127.0.0.1",
        port=8000,
        log_level="info",
    )
    server = uvicorn.Server(config)
    
    # Setup signal handlers
    def signal_handler(signum, frame):
        logger.info("Shutdown signal received")
        print()
        print("="*70)
        print("Server shutting down...".center(70))
        print("="*70)
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    # Run server
    await server.serve()


def main():
    """Main entry point."""
    print_header()
    print_connection_info()
    
    try:
        asyncio.run(run_server())
    except KeyboardInterrupt:
        print()
        print("="*70)
        print("⛔ Server stopped by user".center(70))
        print("="*70)
        print()
        sys.exit(0)


if __name__ == "__main__":
    main()

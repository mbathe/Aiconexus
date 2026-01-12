# AIConexus - Quick Start Guide

## Installation

```bash
# Clone and navigate
cd AIConexus

# Install dependencies
poetry install

# Verify installation
poetry run pytest tests/ -q
```

## Running Tests

### All Tests
```bash
poetry run pytest tests/ -q
# Expected: 207 passed ✅
```

### Unit Tests Only
```bash
poetry run pytest tests/unit/ -q
# Expected: 176 passed ✅
```

### Load Tests Only
```bash
poetry run pytest tests/load/test_load.py -v
# Tests: 100, 250, 500 concurrent connections
```

### Integration Tests
```bash
poetry run python run_server_test.py
# Tests: health, routing, concurrency, disconnection
```

## Running the Server

### Start Gateway Server
```bash
# Terminal 1: Start server
uvicorn gateway:app --host 127.0.0.1 --port 8000

# Terminal 2: Run integration tests
poetry run python run_server_test.py
```

### Using Docker
```bash
# Development
docker-compose -f docker-compose.yml --profile dev up dev

# Testing
docker-compose -f docker-compose.yml --profile test up test

# Production
docker-compose -f docker-compose.yml --profile production up -d app
```

## Using the Client SDK

```python
from aiconexus.client.socket import GatewayClient
from aiconexus.protocol.security import DIDKey

# Generate identity
did_key = DIDKey.generate()

# Create client
client = GatewayClient(
    gateway_url="ws://localhost:8000/ws",
    did_key=did_key
)

# Register handlers
async def on_message(msg_dict):
    print(f"Received: {msg_dict}")

client.on_message(on_message)

# Connect
async with client:
    await client.register(did_key.public_key_base58)
    # Send and receive messages...
```

## Using Retry Logic

```python
from aiconexus.webrtc.retry import ConnectionRetryManager, RetryConfig

# Configure retry
config = RetryConfig(
    max_retries=3,
    initial_delay=0.1,
    backoff_multiplier=2.0,
    strategy="exponential",
    jitter=0.1
)

manager = ConnectionRetryManager(config)

# Execute with retry
async def create_connection():
    # Your connection code here
    pass

peer = await manager.execute_with_retry(create_connection)
```

## Monitoring

### View Metrics
```python
from aiconexus.monitoring.metrics import get_collector

collector = get_collector()
metrics_text = collector.export_prometheus()
print(metrics_text)
```

### Health Checks
```python
from aiconexus.monitoring.health import get_checker

async def check_system():
    checker = get_checker()
    result = await checker.check_health()
    print(f"Status: {result.status}")
    for name, component in result.components.items():
        print(f"  {name}: {component.status}")

import asyncio
asyncio.run(check_system())
```

## Project Structure

```
AIConexus/
├── src/
│   ├── aiconexus/
│   │   ├── protocol/          # Core protocol
│   │   ├── client/            # Client SDK
│   │   ├── webrtc/            # WebRTC & Retry
│   │   └── monitoring/        # Metrics & Health
│   └── gateway/               # Gateway server
├── tests/
│   ├── unit/                  # 176 unit tests
│   ├── integration/           # Integration tests
│   └── load/                  # Load tests
├── Dockerfile                 # Multi-stage build
├── docker-compose.yml         # Orchestration
├── run_server_test.py         # Integration test
└── SPRINT_5_REPORT.md         # Full documentation
```

## Documentation

- **SPRINT_5_REPORT.md** - Complete sprint 5 documentation
- **PROJECT_STATUS_FINAL.md** - Final project status
- **DOCKER.md** - Docker guide
- **PROTOCOL_DESIGN.md** - Protocol specification

## Key Metrics

- **Tests**: 207/207 passing (100%)
- **Performance**: <100ms connection time
- **Scalability**: 500+ concurrent connections
- **Code Quality**: 100% type hints, full docstrings
- **Coverage**: All features tested

## Support

For issues or questions:
1. Check documentation files
2. Review test examples
3. Check inline code comments
4. Review git history for implementation details

## What's Next?

- Deploy to production
- Add DTLS encryption
- Implement TURN server support
- Add Kubernetes manifests
- Set up CI/CD pipeline

---

**Status**: Production Ready ✅  
**Last Updated**: 12 January 2026

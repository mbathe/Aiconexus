# AIConexus - Agent Internet Protocol

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A universal infrastructure for autonomous AI agents to communicate, cooperate, and transact in a decentralized network.

## Vision

Create the "Internet for AI Agents" - enabling:
- **Discovery**: Agents dynamically find other agents and their capabilities
- **Communication**: Standardized protocol for agent-to-agent interaction
- **Negotiation**: Smart contracts and SLA agreements between agents
- **Execution**: Reliable task execution with retry and timeout handling
- **Transactions**: Autonomous M2M payments and economic interactions
- **Governance**: Security, audit, reputation, and trust management

## Quick Start

### Prerequisites
- Python 3.10+
- Poetry (Python package manager)

### Installation

```bash
# Clone the repository
git clone https://github.com/aiconexus/aiconexus.git
cd aiconexus

# Install dependencies
/home/paul/.local/bin/poetry install
```

### Running the Gateway Server

The AIConexus Gateway is a WebSocket server that manages agent connections and routes messages between agents.

#### Start the Gateway in Listen Mode

```bash
/home/paul/.local/bin/poetry run python gateway_listen.py
```

The gateway will start on `ws://127.0.0.1:8000/ws` and wait for client connections.

Output:
```
======================================================================
               Gateway Server - Listen Mode               
======================================================================

  Server Address: ws://127.0.0.1:8000/ws
  Protocol: IoAP v1 (ioap.v1)
  Started at: 2026-01-12 06:20:29

  Waiting for client connections...
======================================================================

INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000
```

### Connecting Clients

In a separate terminal, you can test client connections to the gateway.

#### Option 1: Test Two Clients Connecting

```bash
/home/paul/.local/bin/poetry run python test_two_clients.py
```

This launches two test clients that connect to the gateway, register themselves, and maintain connection for 10 seconds before gracefully disconnecting.

Expected output:
```
============================================================
LAUNCHING TWO TEST CLIENTS
============================================================

[CLIENT 1] DID: did:key:z6MkXXX...
[CLIENT 2] DID: did:key:z6MkYYY...

[CLIENT 1] Connected to gateway
[CLIENT 2] Connected to gateway
[CLIENT 1] Registered
[CLIENT 2] Registered

All clients connected successfully!
```

#### Option 2: Test Message Exchange Between Clients

```bash
/home/paul/.local/bin/poetry run python test_message_exchange.py
```

This launches two clients that exchange WebRTC signaling messages (OFFER and ANSWER) through the gateway.

Expected output:
```
======================================================================
TWO-CLIENT MESSAGE EXCHANGE TEST
======================================================================

[CLIENT 1] DID: did:key:z6MkXXX...
[CLIENT 2] DID: did:key:z6MkYYY...

[CLIENT 1] Connected to gateway
[CLIENT 2] Connected to gateway

[CLIENT 1] Registered with gateway
[CLIENT 2] Registered with gateway

[CLIENT 1] Sending OFFER to CLIENT 2...
[CLIENT 2] Received OFFER
[CLIENT 2] Sending ANSWER to CLIENT 1...
[CLIENT 1] Received ANSWER

======================================================================
EXCHANGE SUMMARY
======================================================================
[CLIENT 1] Received 1 message(s)
[CLIENT 2] Received 1 message(s)

Two-way message exchange SUCCESSFUL!
```

#### Option 3: Run All Tests

```bash
./test_all_features.sh
```

This runs the complete test suite including unit tests, load tests, and integration tests.

### Creating a Custom Client

You can create your own client to connect to the gateway:

```python
import asyncio
from aiconexus.client.socket import GatewayClient
from aiconexus.protocol.security import DIDKey

async def main():
    # Generate a unique agent identity
    did_key = DIDKey.generate()
    print(f"Agent DID: {did_key.did}")
    
    # Create a client
    client = GatewayClient(
        gateway_url="ws://127.0.0.1:8000/ws",
        did_key=did_key
    )
    
    # Register a message handler
    async def on_message(msg_dict):
        print(f"Received message: {msg_dict.get('type')}")
        print(f"From: {msg_dict.get('from')}")
        print(f"Payload: {msg_dict.get('payload')}")
    
    client.on_message(on_message)
    
    # Connect and register
    async with client:
        await client.register(did_key.did)
        print(f"Connected and registered with gateway")
        
        # Keep connection alive
        await asyncio.sleep(60)
        print("Disconnected")

if __name__ == "__main__":
    asyncio.run(main())
```

Save this as `my_client.py` and run:
```bash
/home/paul/.local/bin/poetry run python my_client.py
```

## Architecture Overview

### Gateway Server

The Gateway is a FastAPI-based WebSocket server that:
- Accepts WebSocket connections from agents on `ws://127.0.0.1:8000/ws`
- Maintains an agent registry tracking all connected agents
- Routes signaling messages (OFFER, ANSWER, ICE_CANDIDATE) between agents
- Enforces protocol compliance and validates messages
- Provides HTTP endpoints for health checks and agent discovery

### Message Types

The protocol defines 11 message types for agent communication:

1. **REGISTER** - Agent announces itself to the gateway
2. **UNREGISTER** - Agent disconnects from gateway
3. **OFFER** - WebRTC SDP offer for establishing peer connection
4. **ANSWER** - WebRTC SDP answer accepting connection
5. **ICE_CANDIDATE** - Network candidate for NAT traversal
6. **INTENT** - Task request (natural language or structured)
7. **EXEC_REQUEST** - Execute a capability with parameters
8. **EXEC_RESPONSE** - Result of capability execution
9. **ERROR** - Error message from either party
10. **PING** - Keep-alive request
11. **PONG** - Keep-alive response

### Connection Lifecycle

1. Client establishes WebSocket connection to gateway
2. Client sends REGISTER message with its DID and public key
3. Gateway validates and adds client to agent registry
4. Client can now send and receive messages through gateway
5. Gateway routes OFFER/ANSWER/ICE_CANDIDATE messages between agents
6. When client disconnects, gateway removes from registry

### Payload Types

Each message type carries a specific payload structure:

**REGISTER Payload:**
```json
{
  "public_key": "base58-encoded-ed25519-key"
}
```

**INTENT Payload (Natural Language Mode):**
```json
{
  "query": "Extract non-compete clauses from this PDF",
  "context": "Legal document"
}
```

**INTENT Payload (Structured Mode):**
```json
{
  "task": "extract_clauses",
  "params": {
    "file_id": "doc_123",
    "clause_types": ["non_compete"]
  }
}
```

**OFFER/ANSWER Payload:**
```json
{
  "sdp": "v=0\r\no=..."
}
```

**ICE_CANDIDATE Payload:**
```json
{
  "candidate": "candidate:1 1 UDP...",
  "sdp_mid": "0",
  "sdp_mline_index": 0
}
```

**EXEC_REQUEST Payload:**
```json
{
  "args": {
    "param1": "value1"
  },
  "timeout_ms": 5000,
  "stream": false
}
```

**EXEC_RESPONSE Payload:**
```json
{
  "status": "success",
  "result": {"key": "value"},
  "execution_time_ms": 1234.5
}
```

**ERROR Payload:**
```json
{
  "code": "INVALID_SIGNATURE",
  "message": "Message signature verification failed",
  "details": {}
}
```


## Gateway API

### Health Check Endpoint

```bash
curl http://127.0.0.1:8000/health
```

Response:
```json
{
  "status": "healthy",
  "connected_agents": 2,
  "timestamp": "2026-01-12T06:20:29.123456"
}
```

### List Connected Agents

```bash
curl http://127.0.0.1:8000/agents
```

Response:
```json
{
  "agents": [
    {
      "did": "did:key:z6MkXXX...",
      "connected_at": "2026-01-12T06:20:30.123456",
      "last_activity": "2026-01-12T06:20:35.123456"
    },
    {
      "did": "did:key:z6MkYYY...",
      "connected_at": "2026-01-12T06:20:31.123456",
      "last_activity": "2026-01-12T06:20:36.123456"
    }
  ],
  "count": 2
}
```

## Testing

### Unit Tests

```bash
/home/paul/.local/bin/poetry run pytest tests/unit/ -v
```

### Load Tests

```bash
/home/paul/.local/bin/poetry run pytest tests/load/test_load.py -v
```

Tests connections with 100, 250, and 500 concurrent agents.

### Integration Tests

The integration tests validate the complete gateway server with client connections:

```bash
/home/paul/.local/bin/poetry run python run_server_test.py
```

### Full Test Suite

Run all tests (unit, load, integration):

```bash
./test_all_features.sh
```

## Project Structure

```
aiconexus/
├── src/
│   ├── aiconexus/
│   │   ├── protocol/          # Message models and serialization
│   │   ├── client/            # GatewayClient SDK
│   │   ├── webrtc/            # WebRTC peer connection
│   │   ├── monitoring/        # Metrics and health checks
│   │   └── (other modules)
│   └── gateway/               # Gateway server (FastAPI)
│
├── tests/
│   ├── unit/                  # Unit tests (176 tests)
│   ├── load/                  # Load tests (6 tests)
│   └── integration/           # Integration tests
│
├── gateway_listen.py          # Gateway server entry point
├── gateway_app.py             # Uvicorn app entry point
├── test_two_clients.py        # Test two client connections
├── test_message_exchange.py   # Test message routing
├── test_all_features.sh       # Complete test suite
│
└── (documentation and config files)
```

## Development

### Setup Development Environment

```bash
/home/paul/.local/bin/poetry install
```

### Run Tests with Coverage

```bash
/home/paul/.local/bin/poetry run pytest tests/ --cov=src/aiconexus --cov-report=html
```

### Code Quality

Type checking:
```bash
/home/paul/.local/bin/poetry run mypy src/aiconexus
```

## Features

### WebSocket Gateway
- Accepts multiple concurrent agent connections
- Subprotocol negotiation (ioap.v1)
- Graceful connection/disconnection handling
- Automatic timeout and cleanup (300 seconds)

### Agent Management
- Agent registration with DID and public key
- Agent presence tracking in registry
- Connection metadata (IP address, timestamp)
- Automatic removal of disconnected agents

### Message Routing
- Routes OFFER messages for WebRTC negotiation
- Routes ANSWER messages for connection establishment
- Routes ICE_CANDIDATE messages for NAT traversal
- Preserves message payload integrity
- Validates message signatures

### Monitoring
- Health check endpoint for server status
- Agent listing endpoint showing connected agents
- Metrics collection for performance monitoring
- Connection statistics

### Error Handling
- Message signature validation
- Invalid message rejection
- Graceful error recovery
- Connection timeout management
- Detailed error reporting

## Performance Characteristics

- Connection Time: Under 100ms
- Message Latency: Under 50ms
- Concurrent Connections: 500+
- Memory Usage: Approximately 50MB base
- CPU Usage: Less than 5% idle

## Files Overview

### Core Components

**gateway_listen.py** (104 lines)
Entry point for running the gateway server in listen mode. Displays server status, connection information, and waits for client connections.

**gateway_app.py** (14 lines)
FastAPI application factory. Used as entry point for uvicorn when deployed.

**src/gateway/server.py** (311 lines)
Main gateway server implementation. Contains the GatewayServer class with:
- WebSocket connection handling
- Agent registry management
- Message routing logic
- Health check and agent listing endpoints
- Automatic timeout and cleanup tasks

**src/gateway/registry.py** (188 lines)
Agent presence registry. Maintains in-memory list of connected agents with:
- Agent metadata (DID, public key, IP, timestamps)
- Async-safe operations
- Automatic expiration checking

**src/aiconexus/client/socket.py** (381 lines)
GatewayClient SDK for connecting to the gateway. Provides:
- Automatic connection management
- Message sending and receiving
- Event handler dispatch
- Automatic reconnection with exponential backoff
- Context manager support

### Test Files

**test_two_clients.py** (65 lines)
Launches two test clients that connect to the gateway, register, and maintain connection for 10 seconds.

**test_message_exchange.py** (155 lines)
Launches two test clients that exchange OFFER/ANSWER messages through the gateway, validating message routing.

**run_server_test.py** (304 lines)
Comprehensive server integration test runner with 6 test scenarios:
1. Health check endpoint
2. List agents endpoint
3. Client connection
4. Message routing
5. Concurrent agents (5+ agents)
6. Disconnection and cleanup

**test_all_features.sh** (74 lines)
Shell script running complete test pipeline:
1. Unit tests (176 tests)
2. Load tests (6 tests)
3. Integration tests (2 tests)

## Command Reference

| Command | Purpose |
|---------|---------|
| `/home/paul/.local/bin/poetry run python gateway_listen.py` | Start gateway server |
| `/home/paul/.local/bin/poetry run python test_two_clients.py` | Test two client connections |
| `/home/paul/.local/bin/poetry run python test_message_exchange.py` | Test message exchange |
| `/home/paul/.local/bin/poetry run pytest tests/unit/ -v` | Run unit tests |
| `/home/paul/.local/bin/poetry run pytest tests/load/test_load.py -v` | Run load tests |
| `./test_all_features.sh` | Run all tests |
| `curl http://127.0.0.1:8000/health` | Check gateway health |
| `curl http://127.0.0.1:8000/agents` | List connected agents |


## Documentation

- [PROTOCOL_DESIGN.md](PROTOCOL_DESIGN.md) - Complete protocol specification
- [ARCHITECTURE.md](ARCHITECTURE.md) - Detailed technical architecture
- [SPRINT_5_REPORT.md](SPRINT_5_REPORT.md) - Sprint 5 completion report
- [PROJECT_STATUS_FINAL.md](PROJECT_STATUS_FINAL.md) - Final project status
- [QUICK_START.md](QUICK_START.md) - Quick start guide
- [DOCKER.md](DOCKER.md) - Docker deployment guide

## Contributing

We welcome contributions! Please see CONTRIBUTING.md for guidelines.

## License

This project is licensed under the MIT License - see LICENSE file.

# AIConexus Architecture: SDK vs Gateway Separation

**Date**: January 12, 2026  
**Status**: Architecture Finalized

---

## Overview

AIConexus is split into two distinct layers:

1. **SDK (aiconexus package)** - Agent development library
2. **Gateway** - Central signaling server infrastructure

This separation follows best practices for distributed systems and enables independent evolution.

---

## Layer 1: SDK (Agent SDK)

### Purpose
Library for developing and running agents that use the AIConexus protocol.

### What It Includes
```
src/aiconexus/
├── protocol/              # Core protocol (models, security, serialization)
│   ├── models.py          # Message types, payloads
│   ├── security.py        # DID + Ed25519
│   ├── serialization.py   # JSON utilities
│   └── errors.py
├── core/                  # Agent base classes
│   ├── agent.py           # Base Agent class
│   └── __init__.py
├── client/                # Client SDK (NEW)
│   ├── socket.py          # GatewayClient for WebSocket communication
│   └── __init__.py
└── __init__.py
```

### Deployment
- Published on PyPI as `aiconexus` package
- Used by: Any agent developer
- Installation: `pip install aiconexus`

### Example Agent Code
```python
from aiconexus import Agent
from aiconexus.client import GatewayClient
from aiconexus.protocol import DIDKey

# Create identity
did_key = DIDKey.generate()

# Create client connection
client = GatewayClient(
    gateway_url="ws://gateway.example.com/ws",
    agent_did=did_key.did
)

# Connect and communicate
async with client:
    await client.register(did_key.public_key_bytes)
    # Send/receive messages...
```

### Technologies
- Python 3.10+
- Pydantic (validation)
- Cryptography (Ed25519)
- asyncio (async operations)

---

## Layer 2: Gateway

### Purpose
Central signaling server that enables agents to discover and negotiate with each other.

### Responsibilities
1. **Presence Management**: Track which agents are online
2. **Message Routing**: Forward OFFER, ANSWER, ICE_CANDIDATE messages
3. **Connection Lifecycle**: Handle agent registration, disconnection, timeouts
4. **NOT Involved In**: Data plane messages (INTENT, EXEC_REQUEST, EXEC_RESPONSE)

### What It Includes
```
src/gateway/
├── server.py              # FastAPI WebSocket server
├── registry.py            # In-memory agent registry
└── __init__.py
```

### Deployment
- Self-contained service
- Docker image: `aiconexus-gateway:latest`
- Kubernetes-ready
- Scalable (can replicate instances, use Redis for shared registry)

### Architecture
```
┌──────────────┐         ┌──────────────┐
│   Agent A    │         │   Agent B    │
│  (SDK user)  │         │  (SDK user)  │
└──────┬───────┘         └──────┬───────┘
       │                        │
       │    WebSocket           │
       │    (REGISTER)          │
       └──────────┬─────────────┘
                  │
            ┌─────▼─────┐
            │  Gateway  │  ← Central Signaling
            │ (Server)  │
            └─────┬─────┘
                  │
       ┌──────────┴──────────┐
       │                     │
   Routes OFFER         Routes ANSWER
     ICE_CANDIDATE      ICE_CANDIDATE
       │                     │
       ▼                     ▼
   ┌────────────────────────────┐
   │  P2P WebRTC DataChannel    │
   │  (Direct A ↔ B)           │
   │  (Gateway out of picture) │
   └────────────────────────────┘
   
   Data Plane:
   - INTENT
   - EXEC_REQUEST
   - EXEC_RESPONSE
```

### Evolution Path
- **V1 (Sprint 2)**: Python + FastAPI
- **V2 (Later)**: Go or Rust (for 100k+ concurrent connections)

The SDK remains Python. Gateway can change independently.

---

## Data Flow

### 1. Signaling Phase (Gateway Involved)

```
Agent A                     Gateway                    Agent B
   │                           │                          │
   ├─ REGISTER ─────────────→  │                          │
   │                      (add to registry)              │
   │                           │                          │
   │                           │ ← REGISTER ──────────────┤
   │                       (add to registry)              │
   │                           │                          │
   │─ OFFER (to B) ────────→   │                          │
   │                           ├─ OFFER (from A) ─────→  │
   │                           │                          │
   │  ← ANSWER (from B) ────────┤ ← ANSWER (to A) ───────┤
   │                           │                          │
   │─ ICE_CANDIDATE ────────→  │ ─ ICE_CANDIDATE ────→   │
   │  (multiple)               │   (multiple)            │
   │                           │ ← ICE_CANDIDATE ───────┤
   │ ← ICE_CANDIDATE ───────────┤                        │
   │  (multiple)               │  (multiple)            │
```

### 2. Data Plane Phase (Gateway Not Involved)

```
Agent A ════════ WebRTC DataChannel ════════ Agent B
(direct P2P connection)

- INTENT
- EXEC_REQUEST
- EXEC_RESPONSE
- Error messages
- Keep-alive PING/PONG
```

---

## Separation Benefits

### For Development
- SDK can add new features (capabilities, tools) without touching Gateway
- Gateway can optimize for performance without affecting SDK API
- Different development teams possible (SDK team, Infra team)

### For Deployment
- SDK: Distributed to agent developers (PyPI)
- Gateway: Single/few instances (centralized infrastructure)
- Scaling: Gateway horizontal scaling (load balance, replicate)

### For Technology Evolution
- SDK: Stable Python interface (backcompat guaranteed)
- Gateway: Can migrate to Go/Rust without breaking agents
- Protocol: Versioning independent of implementation

### For Security
- SDK contains only agent-facing code
- Gateway isolated for security hardening
- Each can be audited independently

### For Cost
- SDK: Small footprint (agents don't need much compute)
- Gateway: CPU+network optimized (handles thousands of connections)
- Can run Gateway in high-performance infrastructure

---

## Module Responsibilities

### SDK Modules

**protocol/** (Shared by all)
- `models.py`: Message structures (11 types)
- `security.py`: Ed25519 signing, DID:key format
- `serialization.py`: JSON handling
- `errors.py`: Protocol exceptions

**core/** (Agent development)
- `agent.py`: Base Agent class for inheritance

**client/** (NEW - Agent connection)
- `socket.py`: GatewayClient for WebSocket communication
- Handles: connect, register, send, reconnect logic

### Gateway Modules

**server.py**
- FastAPI WebSocket endpoint
- Message routing (OFFER/ANSWER/ICE_CANDIDATE)
- Connection lifecycle

**registry.py**
- AgentRegistry: Track online agents
- RegistryEntry: Agent metadata + presence

---

## Future: Multi-Gateway Setup

For production (Phase 3+), Gateway can be distributed:

```
┌────────────┐         ┌────────────┐
│  Gateway1  │◄───────►│  Redis     │
│ (Instance)│         │ (Shared    │
└────────────┘         │  Registry) │
       ▲               └────────────┘
       │                    ▲
   ┌───┴────┐                │
   │         │             ┌──┴─────┐
  Agent    Agent         │ Gateway2  │
    A        B          │(Instance) │
                         └──────────┘
                              ▲
                          Agent C
```

Shared registry via Redis enables:
- Multiple Gateway instances
- Load balancing across Gateways
- Presence visible across all instances

---

## Project Structure Summary

```
aiconexus/                         (This repo - Multi-package)
├── src/
│   ├── aiconexus/                 (SDK Package)
│   │   ├── protocol/              (Core protocol - reusable)
│   │   ├── core/                  (Agent base classes)
│   │   ├── client/                (Agent client SDK)
│   │   └── __init__.py
│   │
│   └── gateway/                   (Gateway Package - separate service)
│       ├── server.py
│       ├── registry.py
│       └── __init__.py
│
├── tests/
│   ├── unit/
│   │   ├── protocol/              (Protocol tests)
│   │   └── gateway/               (Gateway unit tests)
│   └── integration/
│       └── gateway/               (Gateway integration tests)
│
├── examples/                       (Example agents using SDK)
│   ├── hello_world/
│   └── ...
│
├── PROTOCOL_DESIGN.md             (Protocol specification - shared)
└── pyproject.toml                 (Both packages in one repo)
```

## Installation & Usage

### For Agent Developers
```bash
pip install aiconexus
```

Then in their code:
```python
from aiconexus import Agent
from aiconexus.client import GatewayClient
from aiconexus.protocol import DIDKey
```

### For Gateway Operators
```bash
cd aiconexus
poetry install
python -m gateway.server
# OR
docker run aiconexus-gateway:latest
```

---

## Next: Sprint 2

With this separation in place:

**Sprint 2a: Client SDK**
- Complete `client/socket.py` (GatewayClient)
- Connection management, reconnection logic
- Message validation before sending

**Sprint 2b: Gateway Server**
- Complete `gateway/server.py` (WebSocket handling)
- Complete `gateway/registry.py` (Presence management)
- Route OFFER/ANSWER/ICE_CANDIDATE messages
- Handle disconnections, timeouts

**Tests:**
- Unit tests for both
- Integration tests for client ↔ gateway communication

---

**Architecture Finalized. Ready to implement in Sprint 2.**

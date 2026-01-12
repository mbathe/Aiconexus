# 🐳 Gateway Service

The AIConexus Gateway is a standalone WebSocket signaling server for agent communication.

This is a **completely separate service** from the SDK client library. It can be:
- Deployed independently
- Scaled separately  
- Updated independently
- Used by multiple SDK clients

## 📁 Directory Structure

```
gateway/
├── README.md (this file)
├── src/              # Gateway source code
│   ├── gateway_app.py       # FastAPI application
│   ├── gateway_listen.py    # Server startup
│   ├── agent_registry.py    # Agent management
│   ├── message_handler.py   # Message routing
│   └── __init__.py
│
└── docker/           # Docker files
    ├── Dockerfile           # Container image
    ├── docker-compose.yml   # Service orchestration
    └── .dockerignore
```

## 🚀 Quick Start

### Local Development

```bash
# Start gateway in listen mode
python gateway/src/gateway_listen.py

# Gateway will listen on ws://127.0.0.1:8000/ws
```

### Docker Deployment

```bash
# Build image
docker build -f gateway/docker/Dockerfile -t aiconexus-gateway:latest .

# Run container
docker-compose -f gateway/docker/docker-compose.yml up -d
```

## 📖 Documentation

- **[Docker Deployment](../docs/deployment/DOCKER_GATEWAY.md)** - Complete Docker guide
- **[Gateway Administration](../docs/guides/GATEWAY_ADMIN.md)** - Managing the gateway
- **[API Reference](../docs/api/PROTOCOL_MESSAGES.md)** - Message types and endpoints

## 🔧 Configuration

Configuration via environment variables (see `config/.env.gateway.example`):

```bash
LOG_LEVEL=INFO
GATEWAY_HOST=0.0.0.0
GATEWAY_PORT=8000
AGENT_TIMEOUT=300
```

## 📊 Features

- ✅ WebSocket signaling server
- ✅ Agent registration and discovery
- ✅ Message routing (OFFER/ANSWER/ICE)
- ✅ Health check endpoints
- ✅ Automatic cleanup of inactive agents
- ✅ Configurable timeouts
- ✅ Docker containerization
- ✅ Production-ready

## 🏗️ Architecture

```
┌─────────────────────────────────┐
│   FastAPI Application           │
├─────────────────────────────────┤
│ gateway_app.py:                 │
│ - HTTP endpoints (/health, /agents)
│ - WebSocket route (/ws)         │
├─────────────────────────────────┤
│ Agent Registry:                 │
│ - Register/unregister agents    │
│ - Track active connections      │
│ - Auto-cleanup on timeout       │
├─────────────────────────────────┤
│ Message Handler:                │
│ - Route messages between agents │
│ - Validate signatures           │
│ - Log activity                  │
└─────────────────────────────────┘
```

## 🧪 Testing

Test the gateway:

```bash
# Verify setup
make gateway-verify

# Test deployment
make gateway-test

# Run integration tests
make test-integration
```

## 📦 Requirements

- Python 3.13+
- FastAPI
- Uvicorn
- See `pyproject.toml` for full list

## 🔐 Security

- Ed25519 signature verification
- DID-based authentication
- Non-root execution in Docker
- Health check validation
- Message validation

## 🌍 Deployment Options

### Local (Development)
```bash
python gateway/src/gateway_listen.py
```

### Docker (Recommended)
```bash
docker-compose -f gateway/docker/docker-compose.yml up -d
```

### Kubernetes
See [Kubernetes Deployment Guide](../docs/deployment/KUBERNETES.md)

### Cloud Platforms
- AWS ECS
- Google Cloud Run
- Azure Container Instances
- DigitalOcean App Platform

See [Deployment Guide](../docs/deployment/DOCKER_GATEWAY.md) for details

## 📊 Monitoring

### Health Endpoint
```bash
curl http://localhost:8000/health
```

Response:
```json
{
  "status": "healthy",
  "connected_agents": 2,
  "timestamp": "2026-01-12T10:00:00Z"
}
```

### List Agents
```bash
curl http://localhost:8000/agents
```

### View Logs
```bash
docker-compose -f gateway/docker/docker-compose.yml logs -f
```

## 🔄 Lifecycle Management

Use the management script (see `scripts/gateway-docker.sh`):

```bash
./scripts/gateway-docker.sh build      # Build image
./scripts/gateway-docker.sh start      # Start container
./scripts/gateway-docker.sh stop       # Stop container
./scripts/gateway-docker.sh logs -f    # View logs
./scripts/gateway-docker.sh status     # Check status
```

Or with Make:
```bash
make gateway-build
make gateway-start
make gateway-stop
```

## 🐛 Troubleshooting

**Port already in use:**
```bash
lsof -i :8000  # Find process
kill -9 <PID>  # Kill it
```

**WebSocket connection refused:**
- Check gateway is running: `make gateway-status`
- Check firewall rules
- Verify correct URL: `ws://127.0.0.1:8000/ws`

**Health check failing:**
```bash
curl http://localhost:8000/health
```

For more, see [Troubleshooting Guide](../docs/guides/TROUBLESHOOTING.md)

## 📈 Performance

- **Tested with:** 500+ concurrent agents
- **CPU:** Low (async I/O)
- **Memory:** ~100MB baseline
- **Latency:** <10ms message routing

## 🔍 More Information

- [Architecture](../docs/ARCHITECTURE.md)
- [Protocol Design](../docs/PROTOCOL_DESIGN.md)
- [Docker Deployment](../docs/deployment/DOCKER_GATEWAY.md)
- [API Reference](../docs/api/PROTOCOL_MESSAGES.md)

---

**Gateway Status:** Production Ready ✅
**Last Updated:** 2026-01-12

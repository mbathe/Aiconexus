# AIConexus Gateway Docker Deployment

This document explains how to deploy the AIConexus Gateway as a standalone Docker service.

## Overview

The AIConexus Gateway is a separate service that acts as the signaling server for agent communication. It should be deployed independently from the SDK client libraries.

**Architecture:**
- SDK Clients: Installed locally by developers/users
- Gateway Service: Deployed centrally (cloud, server, etc.)

## Prerequisites

- Docker 20.10+
- Docker Compose 1.29+
- 512MB RAM minimum
- 100MB disk space

## Quick Start

### 1. Build the Gateway Image

```bash
chmod +x gateway-docker.sh
./gateway-docker.sh build
```

This creates a Docker image from `Dockerfile.gateway` with all dependencies.

### 2. Start the Gateway

```bash
./gateway-docker.sh start
```

The gateway will:
- Start in background
- Listen on `ws://127.0.0.1:8000/ws`
- Expose HTTP endpoints on port 8000
- Automatically restart if it crashes

### 3. Verify Gateway is Running

```bash
./gateway-docker.sh status
```

Or check health:
```bash
./gateway-docker.sh health
```

Expected response:
```json
{
  "status": "healthy",
  "connected_agents": 0,
  "timestamp": "2026-01-12T06:20:29.123456"
}
```

### 4. View Logs

```bash
./gateway-docker.sh logs
```

For real-time logs:
```bash
./gateway-docker.sh logs -f
```

## Testing with Clients

Once the gateway is running, test client connections from another terminal:

### Test Basic Connectivity

```bash
poetry run python test_two_clients.py
```

### Test Message Exchange

```bash
poetry run python test_message_exchange.py
```

## Gateway Management

### Start Gateway
```bash
./gateway-docker.sh start
```

### Stop Gateway
```bash
./gateway-docker.sh stop
```

### Restart Gateway
```bash
./gateway-docker.sh restart
```

### Open Container Shell
```bash
./gateway-docker.sh shell
```

### Full Cleanup
```bash
./gateway-docker.sh cleanup
```

## Docker Compose Configuration

The `docker-compose.gateway.yml` file defines:

- Service name: `gateway`
- Container name: `aiconexus-gateway`
- Port mapping: 8000:8000
- Health checks every 30 seconds
- Auto-restart policy
- Log volume for persistence

### Manual Docker Compose Commands

Instead of using the script, you can use docker-compose directly:

```bash
# Start
docker-compose -f docker-compose.gateway.yml up -d

# Stop
docker-compose -f docker-compose.gateway.yml down

# Logs
docker-compose -f docker-compose.gateway.yml logs -f

# Restart
docker-compose -f docker-compose.gateway.yml restart
```

## Environment Variables

Configure gateway behavior via environment variables:

```bash
export LOG_LEVEL=INFO
export PYTHONUNBUFFERED=1

./gateway-docker.sh start
```

Available options:
- `LOG_LEVEL`: DEBUG, INFO, WARNING, ERROR (default: INFO)
- `PYTHONUNBUFFERED`: Set to 1 to see real-time logs

## Network Configuration

### Localhost (Single Machine Testing)

```bash
# Gateway runs on
ws://127.0.0.1:8000/ws
http://127.0.0.1:8000/health
http://127.0.0.1:8000/agents
```

### Network Access (Multiple Machines)

To allow other machines to connect:

1. Edit `docker-compose.gateway.yml`:
```yaml
ports:
  - "0.0.0.0:8000:8000"  # Listen on all interfaces
```

2. Connect clients using:
```python
client = GatewayClient(
    gateway_url="ws://server-ip:8000/ws",
    did_key=did_key
)
```

### Behind Reverse Proxy (Production)

For HTTPS support with nginx:

```nginx
server {
    listen 443 ssl http2;
    server_name gateway.example.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## API Endpoints

### Health Check

```bash
curl http://localhost:8000/health
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
curl http://localhost:8000/agents
```

Response:
```json
{
  "agents": [
    {
      "did": "did:key:z6MkXXX...",
      "connected_at": "2026-01-12T06:20:30",
      "last_activity": "2026-01-12T06:20:35"
    }
  ],
  "count": 1
}
```

### WebSocket Connection

```javascript
const ws = new WebSocket('ws://localhost:8000/ws', 'ioap.v1');

ws.onopen = () => {
    console.log('Connected to gateway');
};

ws.onmessage = (event) => {
    const message = JSON.parse(event.data);
    console.log('Received:', message);
};

ws.onerror = (error) => {
    console.error('WebSocket error:', error);
};
```

## Performance Tuning

### Increase Resource Limits

Edit `docker-compose.gateway.yml`:

```yaml
services:
  gateway:
    mem_limit: 2g
    cpus: 2
```

### Scale Gateway (Multiple Instances)

```bash
docker-compose -f docker-compose.gateway.yml up -d --scale gateway=3
```

Note: This requires external load balancing and distributed registry.

## Troubleshooting

### Container won't start

```bash
./gateway-docker.sh logs
```

Check for:
- Port 8000 already in use
- Insufficient disk space
- Python syntax errors

### Health check failing

```bash
./gateway-docker.sh shell
python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"
```

### WebSocket connection refused

- Verify gateway is running: `./gateway-docker.sh status`
- Check firewall rules
- Verify correct address: `ws://127.0.0.1:8000/ws`
- Check logs for errors: `./gateway-docker.sh logs`

### High memory usage

Monitor with:
```bash
docker stats aiconexus-gateway
```

If high:
- Check for connection leaks
- Reduce `agent_timeout` in gateway_listen.py
- Review client code for issues

## Production Deployment

### 1. Kubernetes

Create deployment YAML:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: aiconexus-gateway
spec:
  replicas: 3
  selector:
    matchLabels:
      app: gateway
  template:
    metadata:
      labels:
        app: gateway
    spec:
      containers:
      - name: gateway
        image: aiconexus-gateway:latest
        ports:
        - containerPort: 8000
        env:
        - name: LOG_LEVEL
          value: INFO
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 30
```

### 2. Docker Swarm

```bash
docker service create \
  --name aiconexus-gateway \
  --publish 8000:8000 \
  --replicas 3 \
  aiconexus-gateway:latest
```

### 3. Cloud Platforms

Supported platforms:
- AWS ECS
- Google Cloud Run
- Azure Container Instances
- DigitalOcean App Platform
- Heroku (with custom buildpack)

## Security Considerations

### 1. Network Security

- Run behind firewall
- Use TLS/SSL in production
- Validate client certificates
- Implement rate limiting

### 2. Container Security

```bash
# Run with minimal privileges
docker run --user 1000:1000 ...

# Use read-only filesystem
docker run --read-only ...

# Drop unnecessary capabilities
docker run --cap-drop=ALL ...
```

### 3. Message Validation

The gateway validates:
- Message signatures
- DID format
- Payload structure
- Agent registration

## Monitoring

### View Metrics

```bash
docker stats aiconexus-gateway
```

### Integration with Monitoring Tools

- Prometheus: Expose `/metrics` endpoint
- ELK Stack: Send logs to Elasticsearch
- Datadog: Use Docker integration
- New Relic: APM monitoring

## FAQ

**Q: Can multiple gateway instances run together?**
A: Currently no. Use a single gateway instance or deploy behind a load balancer with distributed state.

**Q: How many concurrent agents can one gateway handle?**
A: Tested with 500+ concurrent connections. Scale horizontally for larger deployments.

**Q: Can I run gateway and clients on same machine?**
A: Yes, for development/testing. In production, separate them.

**Q: How do I update the gateway?**
A: Pull new code, rebuild image, restart container:
```bash
git pull
./gateway-docker.sh build
./gateway-docker.sh restart
```

**Q: Is the gateway stateless?**
A: Yes. Agent registry is in-memory and rebuilt on restart.

**Q: Can I persist the agent registry?**
A: Not currently. Future versions will support Redis/database backend.

## Related Documentation

- [README.md](../README.md) - Main project documentation
- [PROTOCOL_DESIGN.md](../PROTOCOL_DESIGN.md) - Protocol specification
- [ARCHITECTURE.md](../ARCHITECTURE.md) - System architecture

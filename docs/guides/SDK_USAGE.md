# AIConexus SDK Installation & Usage Guide

## What is AIConexus?

AIConexus is a distributed protocol for agents to communicate and coordinate. It consists of two components:

1. **Gateway**: A central WebSocket signaling server (deployed separately)
2. **SDK**: Python client library for creating agents (what you install locally)

## Installation

### Via pip (Recommended)

```bash
pip install aiconexus-sdk
```

### From Source

```bash
git clone https://github.com/yourusername/aiconexus.git
cd aiconexus
poetry install
```

## Quick Start

### 1. Create Your First Agent

```python
from aiconexus import Agent, GatewayClient
import asyncio

async def main():
    # Connect to the gateway (assuming it's running on localhost)
    gateway = GatewayClient(
        gateway_url="ws://127.0.0.1:8000/ws",
        did_key="did:key:z6MkXXXXXXXX"  # Your DID key
    )
    
    # Connect to gateway
    await gateway.connect()
    
    # Create an agent
    agent = Agent(
        name="MyAgent",
        gateway=gateway
    )
    
    # Handle incoming connections
    @agent.on_message
    async def handle_message(message):
        print(f"Received: {message}")
        return {"response": "Hello!"}
    
    # Keep running
    await asyncio.sleep(float('inf'))

if __name__ == "__main__":
    asyncio.run(main())
```

### 2. Generate Your DID Key

```python
from aiconexus.security import generate_did_key

# Generate a new DID key
did_key, private_key = generate_did_key()

print(f"DID: {did_key}")
print(f"Private Key: {private_key}")

# Save these securely!
```

### 3. Connect to a Remote Gateway

```python
# For gateway deployed on example.com
gateway = GatewayClient(
    gateway_url="wss://gateway.example.com/ws",  # Use wss:// for secure connection
    did_key="your-did-key-here"
)

await gateway.connect()
```

## Gateway Deployment

The Gateway needs to be deployed separately. If you're just using the SDK:

### Gateway Running Locally (Development)

The examples and tests assume the gateway is running on `localhost:8000`. To start it:

```bash
# If you have the full AIConexus repository
./gateway-docker.sh start

# Or with docker-compose directly
docker-compose -f docker-compose.gateway.yml up -d
```

### Gateway Running Remotely (Production)

```python
# Connect to a deployed gateway
gateway = GatewayClient(
    gateway_url="wss://gateway.mycompany.com/ws",
    did_key="your-did-key"
)
```

## API Reference

### GatewayClient

```python
client = GatewayClient(gateway_url, did_key, timeout=30)

# Connect to gateway
await client.connect()

# Send a message to another agent
await client.send_message(target_did, message)

# Register this agent on the gateway
await client.register()

# Unregister this agent
await client.unregister()

# Disconnect from gateway
await client.disconnect()

# Check connection status
is_connected = client.is_connected()
```

### Agent

```python
agent = Agent(name, gateway)

# Handle incoming messages
@agent.on_message
async def handler(message):
    return {"processed": True}

# Send message to another agent
await agent.send_to(target_did, message)

# Get agent information
agent.did
agent.name
agent.gateway
```

### Message Format

```python
# All messages follow this structure
message = {
    "type": "message",  # message type
    "payload": {...},   # message content
    "timestamp": "2026-01-12T06:00:00Z",
    "sender": "did:key:...",
    "signature": "..."  # Ed25519 signature
}
```

## WebSocket Message Types

The protocol supports these message types:

1. **REGISTER**: Register agent on gateway
2. **UNREGISTER**: Unregister agent from gateway
3. **OFFER**: Initiate connection (WebRTC-like)
4. **ANSWER**: Accept connection
5. **ICE_CANDIDATE**: Network routing info
6. **INTENT**: Send a task/request
7. **EXEC_REQUEST**: Execute remote code
8. **EXEC_RESPONSE**: Execution result
9. **ERROR**: Error notification
10. **PING/PONG**: Keep-alive messages

## Examples

### Example 1: Simple Echo Agent

```python
from aiconexus import Agent, GatewayClient
import asyncio

async def main():
    gateway = GatewayClient(
        gateway_url="ws://127.0.0.1:8000/ws",
        did_key="did:key:z6MkXXXXXXXX"
    )
    
    await gateway.connect()
    agent = Agent("EchoAgent", gateway)
    
    @agent.on_message
    async def echo(msg):
        return msg  # Echo back the same message
    
    await asyncio.sleep(float('inf'))

asyncio.run(main())
```

### Example 2: Agent Pair Communication

```python
from aiconexus import GatewayClient
import asyncio

async def agent_a():
    gateway = GatewayClient(
        gateway_url="ws://127.0.0.1:8000/ws",
        did_key="did:key:agent-a"
    )
    await gateway.connect()
    
    # Send message to Agent B
    await gateway.send_message(
        "did:key:agent-b",
        {"type": "greeting", "content": "Hello from Agent A"}
    )

async def agent_b():
    gateway = GatewayClient(
        gateway_url="ws://127.0.0.1:8000/ws",
        did_key="did:key:agent-b"
    )
    await gateway.connect()
    
    # Wait for messages
    await asyncio.sleep(float('inf'))

async def main():
    await asyncio.gather(
        agent_a(),
        agent_b()
    )

asyncio.run(main())
```

### Example 3: Authentication

```python
from aiconexus import Agent, GatewayClient
from aiconexus.security import sign_message

async def main():
    gateway = GatewayClient(
        gateway_url="ws://127.0.0.1:8000/ws",
        did_key="did:key:your-key"
    )
    
    # Optionally verify signatures on received messages
    @gateway.on_message
    async def verify_message(message):
        if verify_signature(message):
            print("Message verified!")
        else:
            print("Invalid signature!")

asyncio.run(main())
```

## Troubleshooting

### Connection Refused

```
ConnectionRefusedError: [Errno 111] Connection refused
```

**Solution**: Ensure the gateway is running on the correct address:

```python
# Check if gateway is running
# For local: http://127.0.0.1:8000/health
# For remote: https://gateway.example.com/health

# Update your gateway URL
gateway = GatewayClient(gateway_url="correct-url", did_key=did_key)
```

### Invalid DID Key

```
ValueError: Invalid DID format
```

**Solution**: Generate a valid DID key:

```python
from aiconexus.security import generate_did_key

did_key, private_key = generate_did_key()
print(f"Your DID: {did_key}")
```

### Message Signature Verification Failed

```
SignatureError: Signature verification failed
```

**Solution**: Ensure you're signing messages with the correct private key:

```python
from aiconexus.security import sign_message

# Use the private key that corresponds to your DID
signature = sign_message(message, private_key)
```

### Timeout Issues

If messages are taking too long to arrive:

```python
# Increase timeout
gateway = GatewayClient(
    gateway_url="ws://gateway.example.com/ws",
    did_key=did_key,
    timeout=60  # Increase from default 30s
)
```

## Security Best Practices

1. **Protect Your Private Key**
   - Never commit private keys to version control
   - Use environment variables or secure vaults
   - Rotate keys periodically

2. **Use HTTPS/WSS in Production**
   ```python
   # For production
   gateway_url = "wss://gateway.example.com/ws"  # Note: wss:// not ws://
   ```

3. **Validate Incoming Messages**
   - Always verify sender identity
   - Check message signatures
   - Validate message schema

4. **Rate Limiting**
   - Implement rate limiting in your handlers
   - Prevent message flooding attacks
   - Monitor connection behavior

## Advanced Usage

### Custom Message Handler

```python
from aiconexus import Agent, GatewayClient

async def main():
    gateway = GatewayClient(gateway_url, did_key)
    await gateway.connect()
    
    agent = Agent("AdvancedAgent", gateway)
    
    @agent.on_message
    async def custom_handler(message):
        msg_type = message.get("type")
        
        if msg_type == "greeting":
            return {"response": "Hello!"}
        elif msg_type == "query":
            return {"result": await process_query(message)}
        else:
            return {"error": "Unknown message type"}
    
    await asyncio.sleep(float('inf'))
```

### Connection Pooling

For multiple agents connecting to the same gateway:

```python
from aiconexus import GatewayClient

class GatewayPool:
    def __init__(self, gateway_url, num_connections=10):
        self.gateway_url = gateway_url
        self.connections = []
    
    async def create_agents(self, num, did_prefix="agent"):
        for i in range(num):
            did_key = f"did:key:{did_prefix}-{i}"
            gateway = GatewayClient(self.gateway_url, did_key)
            await gateway.connect()
            self.connections.append(gateway)
```

## Configuration

### Environment Variables

```bash
# Gateway connection
GATEWAY_URL=ws://127.0.0.1:8000/ws
DID_KEY=did:key:your-key-here

# Logging
LOG_LEVEL=INFO

# Timeout
GATEWAY_TIMEOUT=30
```

### Async Setup

```python
# Use asyncio.create_task for concurrent operations
import asyncio

async def main():
    tasks = [
        agent_a(),
        agent_b(),
        agent_c(),
    ]
    await asyncio.gather(*tasks)

asyncio.run(main())
```

## Performance Tips

1. **Reuse Gateway Connections**
   - Don't create new connections for each message
   - Keep connection open for agent lifetime

2. **Batch Messages**
   - Group messages when possible
   - Reduce connection overhead

3. **Use Async/Await**
   - Don't block on I/O operations
   - Allow concurrent message processing

4. **Monitor Resources**
   ```python
   import psutil
   
   process = psutil.Process()
   print(f"Memory: {process.memory_info().rss / 1024 / 1024}MB")
   print(f"Connections: {len(process.connections())}")
   ```

## Migration Guide

### From Other Protocols

If migrating from other agent communication systems:

```python
# Old way (example with other protocol)
# client = OtherProtocolClient(...)

# New way with AIConexus
from aiconexus import GatewayClient, Agent

gateway = GatewayClient(gateway_url, did_key)
agent = Agent(name, gateway)
```

## Support & Resources

- **Documentation**: [README.md](./README.md)
- **Protocol Spec**: [PROTOCOL_DESIGN.md](./PROTOCOL_DESIGN.md)
- **Architecture**: [ARCHITECTURE.md](./ARCHITECTURE.md)
- **Docker Deployment**: [DOCKER_GATEWAY.md](./DOCKER_GATEWAY.md)
- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions

## Contributing

Found a bug or want a feature? See [CONTRIBUTING.md](./CONTRIBUTING.md)

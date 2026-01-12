# 💡 Code Examples

Practical examples showing how to use AIConexus.

## 📁 Directory Structure

```
examples/
├── README.md (this file)
│
├── agents/                     # Agent examples
│   ├── simple_agent.py         # Basic agent
│   ├── two_agents.py           # Multi-agent communication
│   ├── message_handler.py      # Custom message handling
│   ├── authentication.py       # With authentication
│   └── advanced_usage.py       # Advanced patterns
│
└── gateway/                    # Gateway examples
    └── custom_server.py        # Custom gateway setup
```

## 🚀 Quick Start Examples

### Simple Agent

```python
from aiconexus import Agent, GatewayClient
import asyncio

async def main():
    gateway = GatewayClient(
        gateway_url="ws://127.0.0.1:8000/ws",
        did_key="did:key:your-key"
    )
    await gateway.connect()
    agent = Agent("MyAgent", gateway)
    print("Agent created!")

asyncio.run(main())
```

Run:
```bash
python examples/agents/simple_agent.py
```

### Two Agents Communicating

See `examples/agents/two_agents.py` for full code.

Run:
```bash
python examples/agents/two_agents.py
```

## 📚 Example Categories

### 🤖 Agent Examples

#### 1. Simple Agent (`simple_agent.py`)
Basic agent that connects to gateway:
- Connect to gateway
- Create agent
- Wait for connections

#### 2. Two Agents (`two_agents.py`)
Agent-to-agent communication:
- Create two agents
- Exchange messages
- Handle responses

#### 3. Message Handler (`message_handler.py`)
Custom message handling:
- Receive messages
- Process data
- Send responses

#### 4. Authentication (`authentication.py`)
Secure agent setup:
- Generate DID keys
- Sign messages
- Verify signatures

#### 5. Advanced Usage (`advanced_usage.py`)
Advanced patterns:
- Connection pooling
- Concurrent agents
- Error handling
- Graceful shutdown

### 🐳 Gateway Examples

#### Custom Server Setup

Create a custom gateway:
```python
from fastapi import FastAPI
from fastapi.websockets import WebSocket

app = FastAPI()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    # Custom logic here
```

## 🎯 Learning Path

1. **Start Here:** `examples/agents/simple_agent.py`
   - Basic agent setup
   - Gateway connection

2. **Then:** `examples/agents/two_agents.py`
   - Multi-agent communication
   - Message exchange

3. **Next:** `examples/agents/message_handler.py`
   - Custom message handling
   - Processing logic

4. **Advanced:** `examples/agents/authentication.py`
   - Security
   - Signing

5. **Expert:** `examples/agents/advanced_usage.py`
   - Patterns
   - Optimization
   - Error handling

## 📖 Running Examples

### Setup

```bash
# Install dependencies
pip install aiconexus-sdk

# Or from source
poetry install
```

### Start Gateway

```bash
# Terminal 1: Start gateway
./scripts/gateway-docker.sh start

# Or locally
python gateway/src/gateway_listen.py
```

### Run Examples

```bash
# Terminal 2: Run example
python examples/agents/simple_agent.py
```

### Clean Up

```bash
# Stop gateway
./scripts/gateway-docker.sh stop
```

## 💻 Example Code Structure

Each example follows this pattern:

```python
import asyncio
from aiconexus import Agent, GatewayClient

async def main():
    # Setup
    gateway = GatewayClient(...)
    await gateway.connect()
    
    # Create agent
    agent = Agent("Name", gateway)
    
    # Setup handlers
    @agent.on_message
    async def handle(msg):
        # Process message
        return response
    
    # Run
    await asyncio.sleep(float('inf'))

if __name__ == "__main__":
    asyncio.run(main())
```

## 🧪 Testing Examples

All examples are tested and working:

```bash
# Run example tests
python -m pytest tests/integration/ -v -k example
```

## 📊 Example Complexity

| Example | Level | Time | Topics |
|---------|-------|------|--------|
| simple_agent.py | Beginner | 5 min | Basics, connection |
| two_agents.py | Beginner | 10 min | Communication |
| message_handler.py | Intermediate | 15 min | Handlers, processing |
| authentication.py | Intermediate | 20 min | Security, signing |
| advanced_usage.py | Advanced | 30 min | Patterns, pooling |

## 🔗 Related Resources

- **[SDK Usage Guide](../docs/guides/SDK_USAGE.md)** - Full SDK reference
- **[API Documentation](../docs/api/)** - API reference
- **[Code Examples](./README.md)** - All examples
- **[Architecture](../docs/ARCHITECTURE.md)** - System design

## 💡 Tips & Tricks

### Debugging

Enable debug logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Timeout Issues

Increase timeout:
```python
gateway = GatewayClient(
    gateway_url="ws://localhost:8000/ws",
    did_key=your_did,
    timeout=60  # seconds
)
```

### Connection Pooling

Create multiple agents:
```python
async def create_agents(num):
    tasks = [create_agent(i) for i in range(num)]
    return await asyncio.gather(*tasks)
```

## 🎓 Learning Outcomes

After running these examples, you'll understand:
- ✅ How to create agents
- ✅ How to connect to gateway
- ✅ How to send/receive messages
- ✅ How to handle custom logic
- ✅ How to secure communications
- ✅ Advanced patterns and optimization

## 🐛 Troubleshooting

**Connection refused:**
- Ensure gateway is running
- Check URL: `ws://127.0.0.1:8000/ws`
- Check firewall

**Timeout:**
- Increase timeout value
- Check gateway logs
- Verify network connectivity

**Message not received:**
- Check both agents are connected
- Verify message format
- Check DID keys match

See [Troubleshooting Guide](../docs/guides/TROUBLESHOOTING.md) for more.

## 📞 Help

- [Documentation](../docs/)
- [SDK Guide](../docs/guides/SDK_USAGE.md)
- [API Reference](../docs/api/)
- [Troubleshooting](../docs/guides/TROUBLESHOOTING.md)

---

**Last Updated:** 2026-01-12
**Status:** All examples tested and working
**Python:** 3.13+

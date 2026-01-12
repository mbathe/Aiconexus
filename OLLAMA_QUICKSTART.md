# Quick Start: Ollama Agent + AIConexus Gateway

A quick step-by-step guide to get a local Ollama agent connected to the AIConexus gateway.

## Setup (5 minutes)

### Step 1: Install Ollama

Download from: https://ollama.ai

Verify installation:
```bash
ollama --version
```

### Step 2: Start Ollama (keep running)

```bash
ollama serve
```

You should see:
```
Ollama is running...
```

### Step 3: Pull a Model

In a new terminal:
```bash
# Small & fast (3B params, 2GB RAM)
ollama pull phi

# Or balanced (7B params, 4GB RAM) 
ollama pull mistral

# Or conversational (13B params, 6GB RAM)
ollama pull neural-chat
```

This downloads the model (takes 1-5 minutes depending on your internet).

### Step 4: Test Ollama

```bash
ollama run mistral "Hello, what is AI?"
```

You should get a response.

## Run Agent + Gateway (3 terminals)

### Terminal 1: Ollama (already running from Step 2)

```bash
ollama serve
```

### Terminal 2: Start Gateway

```bash
cd /home/paul/codes/python/Aiconexus
poetry run python gateway_listen.py
```

You should see:
```
======================================================================
               Gateway Server - Listen Mode               
======================================================================

  Server Address: ws://127.0.0.1:8000/ws
  Waiting for client connections...
```

### Terminal 3: Run Agent

```bash
cd /home/paul/codes/python/Aiconexus
poetry run python examples/ollama_agent.py
```

You should see the agent:
1. Connect to Ollama
2. Register capabilities
3. Connect to gateway
4. Test reasoning & QA

## Test Connectivity (Optional)

Before running the full agent, you can test connections:

```bash
cd /home/paul/codes/python/Aiconexus
poetry run python test_ollama_gateway.py
```

This verifies:
- Ollama is reachable
- Ollama can run inference
- Gateway is reachable

## What's Running

```
Terminal 1: Ollama (localhost:11434)
            ↓
Terminal 3: Agent (connects via HTTP REST)
            ↓ (WebSocket)
Terminal 2: Gateway (ws://127.0.0.1:8000/ws)
```

## Architecture

```
Agent (Python)
    ↓
Ollama API (http://localhost:11434)
    ↓
Ollama LLM Model
    
Agent (Python)
    ↓
WebSocket (ws://127.0.0.1:8000/ws)
    ↓
Gateway
    ↓
Other Agents
```

## What the Agent Can Do

### 1. Reasoning
Ask the agent complex questions:
```
Prompt: "What are the main benefits of machine learning?"
Response: Detailed analysis from Ollama model
```

### 2. Question Answering
Simple Q&A:
```
Question: "What is Python?"
Answer: Concise answer with confidence score
```

### 3. Inter-agent Communication
Multiple agents can:
- Discover each other
- Send messages
- Share capabilities
- Collaborate on tasks

## Troubleshooting

### "Cannot connect to Ollama"
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# If it fails, start Ollama
ollama serve
```

### "Cannot connect to gateway"
```bash
# Check if gateway is running
# In another terminal:
poetry run python gateway_listen.py
```

### Model not found
```bash
# Check what models you have
ollama list

# Download a model
ollama pull mistral
```

### Slow responses
This is normal! The first response loads the model (~5-30 seconds).
Subsequent responses are faster (1-5 seconds).

To speed up:
- Use a smaller model: `phi` instead of `mistral`
- Run on GPU (if available)
- Check your system RAM

## Next Steps

1. Run the connectivity test
2. Start all three components (Ollama, Gateway, Agent)
3. See the agent execute reasoning and QA
4. Modify the agent to add your own capabilities
5. Create multiple agents and have them communicate

## Advanced

### Run Multiple Agents

Terminal 3a:
```bash
poetry run python examples/ollama_agent.py
```

Terminal 3b (in new terminal):
```bash
# Modify name in code or use environment variable
AGENT_NAME="agent-2" poetry run python examples/ollama_agent.py
```

Both agents will register with the gateway and discover each other!

### Customize Agent

Edit `examples/ollama_agent.py`:

```python
# Change model
ollama_model="neural-chat"  # Instead of mistral

# Change gateway URL
gateway_url="ws://192.168.1.100:8000/ws"  # Remote gateway

# Add new capability
self.register_capability(
    capability_id="translation",
    name="Translator",
    # ... etc
)
```

## Files

- `examples/ollama_agent.py` - Full agent implementation
- `examples/ollama_agent/README.md` - Detailed documentation
- `test_ollama_gateway.py` - Connectivity test
- `scripts/run_ollama_agent.sh` - Launcher script
- `gateway_listen.py` - Gateway server

## Support

For detailed setup and troubleshooting:
- See `examples/ollama_agent/README.md`
- Check Ollama docs: https://github.com/ollama/ollama
- Check AIConexus docs: https://github.com/aiconexus/aiconexus

Enjoy your Ollama agent!

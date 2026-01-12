# Ollama Agent Example

This example demonstrates how to create a simple AI agent powered by **Ollama** (a lightweight local LLM) that connects to the **AIConexus gateway** and can communicate with other agents.

## What You'll Learn

- How to integrate Ollama (local LLM) with AIConexus
- How to create a custom agent that handles capabilities
- How to connect an agent to the AIConexus gateway
- How to enable agent-to-agent communication

## Prerequisites

### 1. Install Ollama

Download and install Ollama from: https://ollama.ai

After installation, verify it works:

```bash
ollama --version
```

### 2. Pull a Lightweight Model

Ollama has several lightweight models perfect for running on local machines:

**Recommended for most systems (4GB RAM):**
```bash
ollama pull mistral
```

**Other options:**
```bash
ollama pull neural-chat       # Fast, good quality
ollama pull phi               # Very lightweight (3B params)
ollama pull dolphin-mixtral   # Powerful, requires 16GB RAM
ollama pull openchat          # Good balance
```

You can see all available models at: https://ollama.ai/library

### 3. Verify Ollama Installation

```bash
# Start Ollama (keep running in background)
ollama serve

# In another terminal, test a model
ollama run mistral "What is Python?"
```

## Quick Start

### Step 1: Start Ollama

```bash
ollama serve
```

This starts Ollama on `http://localhost:11434`

### Step 2: Start the AIConexus Gateway

In a new terminal:

```bash
cd /home/paul/codes/python/Aiconexus
poetry run python gateway_listen.py
```

The gateway will start on `ws://127.0.0.1:8000/ws`

### Step 3: Run the Agent

In another terminal:

```bash
cd /home/paul/codes/python/Aiconexus
poetry run python examples/ollama_agent.py
```

## What Happens

The agent will:

1. **Connect to Ollama** - Verify local LLM is available
2. **Register capabilities** - Tell the system what it can do:
   - Reasoning (complex analysis)
   - Question Answering (simple QA)
3. **Connect to gateway** - Register itself in the agent network
4. **Test capabilities** - Demonstrate reasoning and QA with Ollama
5. **Stay connected** - Keep connection open for 30 seconds to allow other agents to discover it

## Architecture

```
┌─────────────────────────────────────────────────────┐
│           Your Local Machine                        │
├─────────────────────────────────────────────────────┤
│                                                     │
│  ┌─────────────────────────────────────────────┐  │
│  │  Ollama (Local LLM)                         │  │
│  │  Running on http://localhost:11434          │  │
│  │  Model: mistral, neural-chat, phi, etc.    │  │
│  └────────────────────┬────────────────────────┘  │
│                       │                            │
│  ┌────────────────────▼────────────────────────┐  │
│  │  OllamaAgent                                │  │
│  │  - Reasoning capability                    │  │
│  │  - QA capability                           │  │
│  │  - Message handling                        │  │
│  └────────────────────┬────────────────────────┘  │
│                       │                            │
│                    WebSocket                       │
│                       │                            │
│  ┌────────────────────▼────────────────────────┐  │
│  │  AIConexus Gateway                          │  │
│  │  Running on ws://127.0.0.1:8000/ws          │  │
│  │  - Agent discovery                          │  │
│  │  - Message routing                          │  │
│  │  - Capability matching                      │  │
│  └────────────────────────────────────────────┘  │
│                       │                            │
└───────────────────────┼────────────────────────────┘
                        │
        ┌───────────────┴────────────────┐
        │                                │
    ┌───▼────┐                      ┌───▼────┐
    │ Agent  │                      │ Agent  │
    │   A    │                      │   B    │
    └────────┘                      └────────┘
```

## Code Structure

### OllamaAgent Class

The agent inherits from `Agent` and adds:

```python
class OllamaAgent(Agent):
    def __init__(self, name, ollama_model, gateway_url):
        # Initialize with Ollama model and gateway connection
    
    async def initialize(self):
        # Check Ollama connectivity
        # Register capabilities
        # Connect to gateway
    
    async def execute_capability(self, capability_id, input_params):
        # Handle reasoning or QA
    
    def _call_ollama(self, prompt, temperature):
        # Make API call to Ollama
```

### Capabilities

The agent registers two capabilities:

**1. Reasoning**
- Input: Complex prompt or question
- Output: Detailed reasoning and analysis
- Temperature: 0.7 (more creative)

**2. Question Answering**
- Input: Direct question
- Output: Concise answer with confidence
- Temperature: 0.3 (more factual)

## Testing Communication

Once the agent is running, you can test agent-to-agent communication:

### Option 1: Run Two Agents

Start two Ollama agents (using different models if desired):

Terminal 1: Ollama
```bash
ollama serve
```

Terminal 2: Gateway
```bash
poetry run python gateway_listen.py
```

Terminal 3: Agent 1
```bash
poetry run python examples/ollama_agent.py
```

Terminal 4: Agent 2 (modify agent name in code)
```bash
poetry run python examples/ollama_agent.py
```

Both agents will register with the gateway and can discover each other.

### Option 2: Use Test Client

After running the agent, you can test it with:

```bash
poetry run python test_message_exchange.py
```

This will send messages to your agent through the gateway.

## Performance Notes

### Model Selection Guide

| Model | Size | Speed | Quality | VRAM |
|-------|------|-------|---------|------|
| phi | 2.7B | Very Fast | Good | 1-2GB |
| neural-chat | 13B | Fast | Good | 4-6GB |
| mistral | 7B | Fast | Very Good | 4-5GB |
| openchat | 13B | Medium | Good | 6-8GB |
| dolphin-mixtral | 45B | Slow | Excellent | 16GB+ |

### Latency

- First response: 2-5 seconds (model loading)
- Subsequent responses: 500-2000ms (depending on model and prompt)

### Tips for Faster Response

1. Use smaller models (phi, neural-chat)
2. Set lower context length
3. Use shorter prompts
4. Run Ollama on GPU if available

## Troubleshooting

### "Cannot connect to Ollama"

**Problem:** Agent can't reach Ollama at http://localhost:11434

**Solution:**
```bash
# Start Ollama
ollama serve

# In another terminal, verify
curl http://localhost:11434/api/tags
```

### "Cannot connect to gateway"

**Problem:** Agent can't reach gateway at ws://127.0.0.1:8000/ws

**Solution:**
```bash
# Start the gateway
poetry run python gateway_listen.py
```

### "Model not found"

**Problem:** Ollama model not downloaded

**Solution:**
```bash
ollama pull mistral
ollama list
```

### Slow responses

**Problem:** Responses are very slow

**Solution:**
1. Check Ollama is running on GPU: `ollama -v` (if CUDA available)
2. Use faster model: `ollama pull phi`
3. Check system resources: available RAM, CPU usage

## Extending the Agent

### Add New Capability

```python
def _register_capabilities(self) -> None:
    # Existing code...
    
    # Add new capability
    self.register_capability(
        capability_id="summarization",
        name="Text Summarization",
        description="Summarize text content",
        input_schema={
            "type": "object",
            "properties": {
                "text": {"type": "string"}
            }
        },
        output_schema={
            "type": "object",
            "properties": {
                "summary": {"type": "string"}
            }
        },
        # ... SLA and pricing
    )

async def execute_capability(self, capability_id: str, input_params: dict):
    # ... existing code ...
    elif capability_id == "summarization":
        return await self._handle_summarization(input_params)

async def _handle_summarization(self, input_params: dict) -> dict:
    text = input_params.get("text", "")
    prompt = f"Summarize this text:\n{text}"
    response = await asyncio.to_thread(self._call_ollama, prompt)
    return {"summary": response}
```

### Use Different Model

```python
agent = OllamaAgent(
    name="qa-agent",
    ollama_model="neural-chat",  # Different model
    gateway_url="ws://127.0.0.1:8000/ws"
)
```

### Customize Agent Behavior

```python
# More creative responses
response = self._call_ollama(prompt, temperature=0.9)

# More factual responses
response = self._call_ollama(prompt, temperature=0.1)
```

## Next Steps

1. Run the agent and verify it connects
2. Test agent-to-agent communication
3. Extend with your own capabilities
4. Deploy multiple agents
5. Experiment with different Ollama models
6. Integrate with your own backend services

## References

- [Ollama Documentation](https://github.com/ollama/ollama)
- [Ollama Models](https://ollama.ai/library)
- [AIConexus Documentation](https://github.com/aiconexus/aiconexus)
- [Agent Framework Guide](https://github.com/aiconexus/aiconexus/tree/main/docs)

## Support

If you encounter issues:

1. Check Prerequisites section above
2. Verify Ollama and gateway are running
3. Check logs for error messages
4. Try with `mistral` model first
5. Ensure port 8000 is available (gateway)
6. Ensure port 11434 is available (Ollama)

Good luck with your Ollama agent!

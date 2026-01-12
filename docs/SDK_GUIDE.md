# AIConexus SDK - Next-Generation Agent Framework

## 🚀 What Makes It Special

The AIConexus SDK is built on a fundamental insight:

**Instead of creating yet another orchestration framework, we created a middleware that makes ANY LLM model work like an intelligent, collaborative agent.**

### Key Differentiators

✅ **ONE API for ALL Models**
- Works with GPT-4, Claude, Llama, Mistral, local models
- Automatic tool calling (even for models without native support)
- No code changes needed - just swap the model name

✅ **True Agent Autonomy**
- Agents decide when and how to collaborate
- SDK provides tools, agents choose when to use them
- Transparent and auditable

✅ **P2P Agent Communication**
- Direct agent-to-agent messaging
- Automatic expert discovery and routing
- Contract validation ensures data integrity

✅ **Developer-First Design**
- 3 lines of code = powerful agent
- Everything else is auto-configured
- Sensible defaults that just work

✅ **Production-Ready**
- Retry logic with exponential backoff
- Timeout handling
- Error recovery
- Comprehensive logging and tracing

---

## 📚 Architecture Overview

```
┌─────────────────────────────────────┐
│   Developer Code                    │
│   agent.execute(task)               │
└────────────┬────────────────────────┘
             │
┌────────────▼────────────────────────┐
│   SDKAgent (High-Level API)         │
│   - Expertise definition            │
│   - Tool setup                      │
│   - System prompt generation        │
└────────────┬────────────────────────┘
             │
┌────────────▼────────────────────────┐
│   ReAct Executor                    │
│   - Reasoning loop                  │
│   - Tool calling orchestration      │
│   - Response handling               │
└────────────┬────────────────────────┘
             │
┌────────────▼────────────────────────┐
│   Tool Calling Manager              │
│   - Native tool support (GPT, Claude)
│   - Synthetic tool calling (Llama)  │
│   - Automatic format detection      │
└────────────┬────────────────────────┘
             │
┌────────────▼────────────────────────┐
│   SDK Toolkit                       │
│   - Agent discovery (Registry)      │
│   - Message validation              │
│   - P2P communication (Connector)    │
│   - Inter-agent messaging           │
└────────────┬────────────────────────┘
             │
┌────────────▼────────────────────────┐
│   LLM Layer                         │
│   - ChatOpenAI, Claude, Ollama...   │
└─────────────────────────────────────┘
```

---

## 🎯 Quick Start

### Installation

```bash
pip install aiconexus
```

### Basic Usage

```python
from aiconexus.sdk import SDKAgent, ExpertiseArea

# Create an agent in 3 lines
agent = SDKAgent(
    name="my-agent",
    expertise=[ExpertiseArea("planning", confidence=0.95)],
)

# Execute
result = await agent.execute("Plan a project...")
print(result.answer)
```

### Multi-Agent Collaboration

```python
# Create specialized agents
planner = SDKAgent(
    name="planner",
    expertise=[ExpertiseArea("planning", 0.95)]
)

analyzer = SDKAgent(
    name="analyzer",
    expertise=[ExpertiseArea("analysis", 0.92)]
)

# Planner automatically finds and contacts analyzer
result = await planner.execute(
    "Plan and analyze a marketing strategy"
)
```

---

## 🔧 How It Works

### Step-by-Step Execution

1. **Task Received**
   - Developer calls `agent.execute(task)`

2. **ReAct Loop Starts**
   - LLM receives task and system prompt
   - LLM thinks about what to do
   - LLM can call tools or provide answer

3. **Tool Calling (Automatic)**
   - If GPT-4/Claude: Uses native tool calling
   - If Llama/Mistral: Uses synthetic XML-based calling
   - SDK handles conversion transparently

4. **Agent Communication**
   - If agent needs to contact another:
     - Searches registry for experts
     - Validates message format
     - Sends via P2P with retry/timeout
     - Validates response
     - Returns to LLM

5. **Loop Continues**
   - LLM integrates tool results
   - Loops until answer is complete
   - Returns final result

### Tool Calling Magic

The SDK's secret sauce is **Automatic Tool Calling Adaptation**:

```
GPT-4 Model:
  ┌─────────────────────┐
  │ LLM (native tools)  │
  └──────────┬──────────┘
             │
    Uses OpenAI tool_calls
             │
  ┌──────────▼──────────┐
  │ Native Executor     │
  └─────────────────────┘

Llama Model (NO native support):
  ┌─────────────────────┐
  │ LLM (no tools)      │
  └──────────┬──────────┘
             │
    Gets prompt: "To use tools, write:"
    "<tool name="x"><arg>y</arg></tool>"
             │
  ┌──────────▼──────────┐
  │ Synthetic Executor  │
  │ (parses XML tags)   │
  └─────────────────────┘

Developer sees: SAME API, works perfectly
```

---

## 🎨 Advanced Features

### Custom Tools

```python
def my_custom_tool(x: int, y: int) -> int:
    return x + y

agent = SDKAgent(
    name="calculator",
    expertise=[ExpertiseArea("math", 0.9)],
    custom_tools=[
        Tool(
            name="add",
            description="Add two numbers",
            func=my_custom_tool
        )
    ]
)
```

### Delegation Rules

Force agents to contact specific experts for certain tasks:

```python
agent = SDKAgent(
    name="coordinator",
    expertise=[ExpertiseArea("general", 0.7)],
    delegation_rules={
        "legal*": "legal-expert",
        "*optimization*": "optimizer",
        "*analysis*": "analyst"
    }
)
```

### Custom Schemas

Define input/output contracts:

```python
from aiconexus.sdk import InputSchema, OutputSchema, FieldSchema

input_schema = InputSchema(
    fields={
        "data": FieldSchema("data", "array", required=True),
        "threshold": FieldSchema("threshold", "number", required=False)
    },
    required_fields=["data"]
)

agent = SDKAgent(
    name="processor",
    expertise=[...],
    input_schema=input_schema
)
```

### Model-Specific Configuration

```python
# GPT-4 with custom temp
agent = SDKAgent(
    name="precise",
    expertise=[...],
    llm_model="gpt-4",
    temperature=0.1  # More deterministic
)

# Llama (synthetic tools)
agent = SDKAgent(
    name="local",
    expertise=[...],
    llm_model="llama-2",
    # No code change needed! SDK adapts automatically
)
```

---

## 🔍 Result Structure

```python
result = await agent.execute(task)

# result contains:
{
    "answer": "The final answer",
    "success": True,
    "reasoning_steps": [
        {"iteration": 0, "thought": "I should...", "action": "find_experts"},
        {"iteration": 1, "thought": "Got experts, now...", "action": "send_message"}
    ],
    "tool_calls": [
        {
            "iteration": 0,
            "tool_name": "find_experts",
            "tool_args": {"expertise": ["optimization"]},
            "result": "[...]",
            "execution_time_ms": 245
        }
    ],
    "interactions": [
        {
            "type": "single_message",
            "to_agent": "optimizer",
            "status": "success",
            "execution_time_ms": 1234
        }
    ],
    "execution_time_ms": 2500
}
```

---

## 🎯 Use Cases

### 1. Autonomous Planning
```python
planner = SDKAgent(
    name="planner",
    expertise=[ExpertiseArea("planning", 0.95)]
)
result = await planner.execute("Plan a product launch")
```

### 2. Multi-Specialist System
```python
# Create team of specialists
coordinator = SDKAgent(
    name="coordinator",
    expertise=[ExpertiseArea("coordination", 0.9)],
    auto_delegation=True
)
result = await coordinator.execute("Handle customer inquiry about legal/tech/business")
```

### 3. Data Processing Pipeline
```python
processor = SDKAgent(
    name="processor",
    expertise=[ExpertiseArea("data-processing", 0.92)],
    custom_tools=[data_loading_tool, validation_tool, export_tool]
)
result = await processor.execute("Process and validate dataset")
```

### 4. Research Assistant
```python
researcher = SDKAgent(
    name="researcher",
    expertise=[
        ExpertiseArea("research", 0.9),
        ExpertiseArea("writing", 0.85)
    ]
)
result = await researcher.execute("Research and write about AI trends")
```

---

## 🧪 Testing & Deployment

### Local Testing

```python
# Works with mock LLM
agent = SDKAgent(
    name="test-agent",
    expertise=[...],
    llm_model="mock"  # Built-in mock for testing
)
result = await agent.execute("test")
```

### Production Deployment

```python
# Use real models
agent = SDKAgent(
    name="prod-agent",
    expertise=[...],
    llm_model="gpt-4",  # Production model
    verbose=False,  # Disable logging overhead
    gateway_url="https://gateway.production.com"
)
```

---

## 📊 Performance

- **Native tool calling** (GPT-4): ~50-100ms per tool call
- **Synthetic tool calling** (Llama): ~40-80ms per tool call
- **Agent discovery**: ~10-50ms (cached)
- **Message validation**: ~5-10ms
- **P2P communication**: 100ms-5s (network dependent)

---

## 🔒 Security

- Message validation against schemas
- Type checking on all inputs
- Timeout protection
- Retry logic prevents thundering herd
- Audit trails for all interactions

---

## 🚀 What's Next

- Streaming responses
- Batch processing
- Advanced caching strategies
- Multi-hop agent chains
- Knowledge base integration
- Persistent memory
- Fine-tuning support

---

## 💡 Philosophy

The SDK doesn't try to be everything. It does ONE thing exceptionally well:

**Make it trivially easy for developers to create intelligent, collaborative agents that work with any LLM model.**

Everything else flows from that principle.

---

## 🤝 Contributing

We welcome contributions! Areas we're looking for:

- New transport protocols
- Additional LLM model support
- Caching strategies
- Tool libraries
- Documentation
- Examples

---

## 📄 License

MIT - See LICENSE file

---

**Made with ❤️ for the future of AI agents**

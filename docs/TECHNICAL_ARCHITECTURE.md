# AIConexus SDK - Technical Architecture

## Executive Summary

The AIConexus SDK is a **production-ready middleware framework** that transforms any LLM into a collaborative, intelligent agent capable of autonomous reasoning, tool usage, agent discovery, and resilient P2P communication.

**Core Philosophy**:
- **Model-Agnostic**: Works with GPT-4, Claude, Llama, Mistral, local models
- **Developer-First**: 3 lines of code to get a powerful agent
- **Transparent**: SDK helps agents decide, not the other way around
- **Resilient**: Retry logic, validation, timeouts, error handling
- **Extensible**: Custom tools, registries, transports, validators

---

## 7-Layer Architecture

```
┌─────────────────────────────────────────┐
│  Layer 7: Public API (SDKAgent)         │
│  Developer-facing single entry point    │
└────────────┬────────────────────────────┘
             │
┌────────────▼────────────────────────────┐
│  Layer 6: Orchestration (ReActExecutor) │
│  Reasoning loop + action execution      │
└────────────┬────────────────────────────┘
             │
┌────────────▼────────────────────────────┐
│  Layer 5: Tool Abstraction              │
│  Native vs Synthetic tool calling       │
└────────────┬────────────────────────────┘
             │
┌────────────▼────────────────────────────┐
│  Layer 4: Coordination (SDKOrchestrator)│
│  Component factory & tool provisioning  │
└────────────┬────────────────────────────┘
             │
     ┌───────┴───────┐
     │               │
┌────▼────┐   ┌─────▼──────┐
│Layer 3a: │   │ Layer 3b:  │
│Commun.   │   │ Validation │
└────┬────┘   └─────┬──────┘
     │               │
     └───────┬───────┘
             │
     ┌───────┴───────┐
     │               │
┌────▼────┐   ┌─────▼──────┐
│Layer 2a: │   │ Layer 2b:  │
│Registry  │   │ Types      │
└────┬────┘   └─────┬──────┘
     │               │
     └───────┬───────┘
             │
        ┌────▼──────┐
        │ LangChain  │
        │ (LLMs)     │
        └───────────┘
```

---

## Component Details

### Layer 7: SDKAgent (Public API)

**File**: `src/sdk/agent.py`

**Purpose**: Single entry point for developers

**Key Methods**:
```python
agent = SDKAgent(
    name="DataAnalyst",
    expertise=[ExpertiseArea("data-analysis", ExpertiseLevel.EXPERT)],
    tools=[custom_analyze_tool],
    llm=ChatOpenAI()
)
result = await agent.execute("Analyze this dataset...")
```

**Responsibilities**:
- LLM auto-initialization (with fallback to mock)
- Tool building (SDK tools + custom tools)
- System prompt generation
- ReAct executor orchestration
- Result formatting

---

### Layer 6: ReActExecutor (Orchestration)

**File**: `src/sdk/executor.py`

**Algorithm** (Reasoning + Acting):

```
iteration = 0
while iteration < max_iterations:
    # REASONING PHASE
    llm_response = await llm.call(messages)
    reasoning_step = ReasoningStep(
        iteration=iteration,
        thought=extract_thought(llm_response),
        action_needed=has_tool_call(llm_response)
    )
    
    if not reasoning_step.action_needed:
        # Final answer - return it
        return AgentResult(final_answer=llm_response.content)
    
    # ACTION PHASE
    tool_call = parse_tool_call(llm_response)
    tool_result = await manager.call_tool(
        name=tool_call.name,
        args=tool_call.args
    )
    
    # UPDATE HISTORY
    messages.append({
        "role": "assistant",
        "content": tool_call_text
    })
    messages.append({
        "role": "user",
        "content": f"Tool result: {tool_result}"
    })
    
    iteration += 1
```

**Key Features**:
- Iteration bounds (prevent infinite loops)
- Conversation history tracking
- Tool parsing (JSON and XML)
- Result formatting for next iteration
- Logging at each step

---

### Layer 5: ToolCallingManager (Abstraction)

**File**: `src/sdk/tools.py`

**Problem Solved**: Not all LLMs support native tool calling

**Solution**: Two executors with automatic selection

#### Strategy 1: NativeToolCallingExecutor

**For**: GPT-4, Claude-3, Cohere

**Implementation**:
```python
# 1. Build tool definitions
tools_definitions = [
    {
        "type": "function",
        "function": {
            "name": "find_experts",
            "description": "Find other agents by expertise",
            "parameters": {
                "type": "object",
                "properties": {
                    "expertise": {"type": "array", "items": {"type": "string"}}
                },
                "required": ["expertise"]
            }
        }
    }
]

# 2. Call LLM with tools
response = await llm.invoke(
    messages=messages,
    tools=tools_definitions
)

# 3. Parse native tool_calls
for tool_call in response.tool_calls:
    result = await execute_tool(tool_call.name, tool_call.args)
```

#### Strategy 2: SyntheticToolCallingExecutor

**For**: Llama, Mistral, local models

**Implementation**:
```python
# 1. Inject schema into system prompt
SYSTEM_PROMPT = """
You have access to these tools:
- find_experts: Find agents by expertise

To use a tool, write:
<tool name="tool_name">
  <arg name="param_name">value</arg>
</tool>
"""

# 2. Call LLM normally
response = await llm.invoke(
    messages=system_prompt + user_messages
)

# 3. Parse XML tool calls
import re
pattern = r'<tool name="(\w+)">(.+?)</tool>'
for match in re.finditer(pattern, response.content):
    tool_name = match.group(1)
    xml_content = match.group(2)
    # Parse XML to extract args
    result = await execute_tool(tool_name, parsed_args)
```

**Auto-Detection**:
```python
def detect_tool_support(model_name):
    native_models = ["gpt-4", "claude-3", "cohere"]
    return any(m in model_name.lower() for m in native_models)
```

---

### Layer 4: SDKOrchestrator (Coordination)

**File**: `src/sdk/orchestrator.py`

**Purpose**: Wire components together + expose SDK tools

**Tool Suite** (what agents can call):

```python
class SDKOrchestrator:
    # Discovery
    async def find_experts(expertise: List[str]) -> List[AgentInfo]:
        """Find agents by expertise"""
    
    # Communication
    async def send_message(
        agent_id: str,
        message: Message
    ) -> Message:
        """Send message to another agent"""
    
    async def send_messages_parallel(
        messages: Dict[str, Message]
    ) -> Dict[str, Message]:
        """Send multiple messages concurrently"""
    
    # Validation
    async def validate_message(
        message: Message,
        target_schema: AgentSchema
    ) -> ValidationResult:
        """Validate message matches target schema"""
```

---

### Layer 3a: AgentConnector (P2P Communication)

**File**: `src/sdk/connector.py`

**Protocol Abstraction**:

```python
# Transport interface
class TransportProtocol(Protocol):
    async def send(
        self,
        connection_info: ConnectionInfo,
        message: Message,
        timeout: float = 30.0
    ) -> Message:
        """Send message and get response"""

# HTTP Implementation
class HTTPTransport:
    async def send(self, connection_info, message, timeout=30.0):
        url = f"{connection_info.endpoint}/messages"
        payload = message.to_dict()
        headers = self._get_headers(connection_info)
        
        try:
            response = await asyncio.wait_for(
                self._post(url, payload, headers),
                timeout=timeout
            )
            return Message.from_dict(response)
        except asyncio.TimeoutError:
            raise ConnectionError(f"Request timeout after {timeout}s")

# WebSocket Implementation  
class WebSocketTransport:
    async def send(self, connection_info, message, timeout=30.0):
        async with websockets.connect(
            connection_info.endpoint
        ) as websocket:
            await websocket.send(message.to_json())
            response = await asyncio.wait_for(
                websocket.recv(),
                timeout=timeout
            )
            return Message.from_json(response)
```

**Resilience Strategy**:

```python
async def send_with_retries(
    transport,
    connection_info,
    message,
    max_retries=3
):
    for attempt in range(max_retries):
        try:
            return await transport.send(
                connection_info,
                message
            )
        except (ConnectionError, TimeoutError) as e:
            if attempt == max_retries - 1:
                raise
            
            # Exponential backoff: 1s, 2s, 4s
            wait_time = 2 ** attempt
            logger.warning(
                f"Attempt {attempt+1} failed, retrying in {wait_time}s..."
            )
            await asyncio.sleep(wait_time)
```

---

### Layer 3b: MessageValidator (Contract Enforcement)

**File**: `src/sdk/validator.py`

**Validation Levels**:

```python
class MessageValidator:
    async def validate_request(
        self,
        message: Message,
        target_schema: AgentSchema
    ) -> ValidationResult:
        """Validate incoming request against contract"""
        
        # Level 1: JSON structure
        try:
            data = message.data
        except:
            return ValidationResult(
                valid=False,
                errors=["Invalid JSON structure"]
            )
        
        # Level 2: Required fields
        missing = set(target_schema.input_schema.required_fields) - set(data.keys())
        if missing:
            return ValidationResult(
                valid=False,
                errors=[f"Missing required fields: {missing}"]
            )
        
        # Level 3: Type validation
        errors = []
        for field, schema in target_schema.input_schema.fields.items():
            if field not in data:
                continue
            
            validator = self._get_validator(schema.type)
            if not validator.validate(data[field], schema):
                errors.append(f"Invalid type for field '{field}'")
        
        if errors:
            return ValidationResult(valid=False, errors=errors)
        
        # Level 4: Constraint validation
        for field, schema in target_schema.input_schema.fields.items():
            if field in data and schema.constraints:
                # Check min/max, pattern, enum, etc.
                pass
        
        return ValidationResult(valid=True)
```

---

### Layer 2a: AgentRegistry (Discovery)

**File**: `src/sdk/registry.py`

**Two Discovery Strategies**:

#### Strategy 1: Exact Domain Matching

```python
# Simple: Match if expertise domain is requested
def find_by_exact_domain(query_expertise: List[str]) -> List[AgentInfo]:
    results = []
    for agent in agents:
        matches = set(query_expertise) & set(agent.expertise_domains)
        if matches:
            results.append((agent, len(matches) / len(query_expertise)))
    
    # Sort by match percentage
    return sorted(results, key=lambda x: x[1], reverse=True)
```

#### Strategy 2: Semantic Matching

```python
# Smart: Embed query and expertise, measure similarity
def find_by_semantic_similarity(
    query_expertise: List[str],
    min_confidence: float = 0.7
) -> List[AgentInfo]:
    # Embed the query
    query_embedding = embedder.embed(" ".join(query_expertise))
    
    results = []
    for agent in agents:
        # Embed each agent's expertise
        agent_embedding = embedder.embed(" ".join(agent.expertise_domains))
        
        # Calculate similarity (cosine)
        similarity = cosine_similarity(query_embedding, agent_embedding)
        
        if similarity >= min_confidence:
            results.append((agent, similarity))
    
    # Sort by similarity score
    return sorted(results, key=lambda x: x[1], reverse=True)
```

#### Hybrid Approach

```python
async def find_agents_by_expertise(
    expertise: List[str],
    strategy: str = "hybrid"
) -> List[AgentInfo]:
    if strategy == "exact":
        return find_by_exact_domain(expertise)
    elif strategy == "semantic":
        return find_by_semantic_similarity(expertise)
    else:  # hybrid
        exact_results = find_by_exact_domain(expertise)
        semantic_results = find_by_semantic_similarity(expertise)
        
        # Merge and deduplicate
        seen = set()
        merged = []
        for agent, score in exact_results + semantic_results:
            if agent.id not in seen:
                merged.append(agent)
                seen.add(agent.id)
        
        return merged
```

---

### Layer 2b: Type System

**File**: `src/sdk/types.py`

**Core Data Classes**:

```python
@dataclass
class ExpertiseArea:
    """Agent specialization"""
    domain: str
    level: ExpertiseLevel  # novice, intermediate, expert, master

@dataclass
class AgentInfo:
    """Agent metadata"""
    id: str
    name: str
    endpoint: str
    expertise: List[ExpertiseArea]
    schema: AgentSchema
    status: str  # active, inactive, degraded
    created_at: datetime
    last_heartbeat: datetime

@dataclass
class InputSchema:
    """Input contract specification"""
    fields: Dict[str, FieldSchema]
    required_fields: List[str]

@dataclass
class FieldSchema:
    """Single field specification"""
    type: str  # string, number, boolean, array, object
    description: str
    constraints: Optional[Dict]  # min, max, pattern, enum

@dataclass
class Message:
    """Inter-agent message"""
    id: str
    sender_id: str
    recipient_id: str
    data: Dict[str, Any]
    timestamp: datetime
    request_id: Optional[str]

@dataclass
class AgentResult:
    """Execution result"""
    final_answer: str
    reasoning_steps: List[ReasoningStep]
    tool_calls: List[ToolCall]
    interactions: List[Message]
    total_iterations: int
    execution_time_ms: float
```

---

## Data Flow Diagram

### Single Agent Execution

```
User Input
    │
    ├─→ SDKAgent.execute(task)
    │
    └─→ ReActExecutor.run()
        ├─→ LLM Call #1
        │   ├─ Input: task, tools available
        │   └─ Output: thought + action
        │
        ├─→ Tool Execution
        │   ├─ ToolCallingManager.call_tool()
        │   │   ├─ IF native tools: NativeToolCallingExecutor
        │   │   └─ IF synthetic: SyntheticToolCallingExecutor
        │   └─ Result: tool output
        │
        ├─→ History Update
        │   └─ Add action + result to conversation
        │
        └─→ [Loop to LLM Call #2, #3, ...]
            └─ Until: Final answer given
                │
                └─ Return AgentResult
```

### Multi-Agent Collaboration

```
Agent A (ReActExecutor)
    │
    └─→ LLM decides: "I need optimization help"
        │
        ├─→ find_experts(["optimization"])
        │   │
        │   └─→ AgentRegistry
        │       ├─ Exact match: optimization domain
        │       ├─ Semantic match: embedding similarity
        │       └─ Return: Agent B, Agent C (ranked)
        │
        ├─→ send_message(agent_b, request)
        │   │
        │   └─→ AgentConnector
        │       ├─ MessageValidator.validate_request()
        │       │   └─ Check Agent B's input schema
        │       │
        │       ├─ HTTPTransport.send()
        │       │   ├─ POST to http://agent-b:8000/messages
        │       │   └─ Retry with backoff if fails
        │       │
        │       └─ Receive response
        │           └─ MessageValidator.validate_response()
        │               └─ Check response format
        │
        └─→ Integrate result into reasoning
            └─ Continue iteration
```

---

## Performance Profile

### Latency Components

| Component | Typical | Range | Notes |
|-----------|---------|-------|-------|
| LLM inference | 2-5s | 0.5-30s | Varies by model |
| Tool parsing | 20ms | 10-100ms | JSON/XML regex |
| SDK overhead | 50ms | 20-200ms | Validation, registry |
| P2P communication | 500ms-2s | 100-5000ms | Network + LLM |
| Total per iteration | 2.5-7s | 1-35s | Depends on tool |

### Throughput

- **Sequential agents**: 1 agent per 2-7 seconds
- **Concurrent agents**: Multiple agents in parallel (async/await)
- **Message batch**: 10-100 messages/second (depends on network)

### Memory Profile

- **Per agent**: ~50MB (LLM model loaded)
- **Per message**: ~1KB (typical)
- **Registry cache**: ~1MB per 1000 agents

---

## Extensibility Patterns

### Custom Tool

```python
class AnalyzeTool(Tool):
    name = "analyze_data"
    description = "Analyze dataset statistically"
    
    async def execute(self, dataset_path: str, metrics: List[str]):
        df = pd.read_csv(dataset_path)
        return {metric: df[metric].describe() for metric in metrics}

agent = SDKAgent(
    tools=[AnalyzeTool()]
)
```

### Custom Transport

```python
class GRPCTransport:
    async def send(self, connection_info, message, timeout=30.0):
        # Custom GRPC implementation
        pass

connector = AgentConnector(
    transport=GRPCTransport()
)
```

### Custom Registry Backend

```python
class RedisRegistry:
    async def find_agents(self, expertise, min_confidence):
        # Query Redis for agent info
        pass

orchestrator = SDKOrchestrator(
    registry_backend=RedisRegistry()
)
```

---

## Security Model

### Message Validation
✅ Type checking prevents injection  
✅ Schema validation ensures expected format  
✅ Unknown fields rejected in strict mode

### Transport Security
✅ HTTPS for HTTP transport  
✅ WSS for WebSocket transport  
✅ API key authentication  
✅ Request signing (future)

### Timeout Protection
✅ Default 30s timeout per message  
✅ Configurable per request  
✅ Prevents hung processes

### Audit Trail
✅ All interactions logged  
✅ Request/response captured  
✅ Execution metrics recorded

---

## Testing Strategy

### Unit Tests (Fast)
- Component in isolation
- Mock dependencies
- Deterministic assertions

### Integration Tests (Medium)
- Component interactions
- Mock LLM responses
- Real validation/parsing logic

### E2E Tests (Slow)
- Full agent execution
- Mock HTTP servers
- Multi-agent scenarios

### Performance Tests
- Latency benchmarks
- Throughput tests
- Memory profiling

---

**Version**: 1.0  
**Status**: Production-Ready  
**Last Updated**: January 2026

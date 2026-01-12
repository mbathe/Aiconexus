# AIConexus SDK - Advanced Implementation Guide

## Introduction

This guide covers advanced patterns, optimization techniques, and design decisions in the AIConexus SDK implementation.

---

## Part 1: Tool Calling Strategy

### The Problem

Different LLMs have different capabilities:

- **GPT-4, Claude-3**: Native `tool_calls` in response
- **Llama, Mistral**: Text-based, no structured output
- **Local models**: Unpredictable behavior

**Traditional solution**: Write different code for each model. ❌

**AIConexus solution**: One interface, automatic adaptation. ✅

### Implementation

#### Auto-Detection at Init

```python
class ToolCallingManager:
    def __init__(self, llm):
        self.llm = llm
        self.has_native_tools = self._detect_native_tool_support()
        
        if self.has_native_tool_support:
            self.executor = NativeToolCallingExecutor(llm)
        else:
            self.executor = SyntheticToolCallingExecutor(llm)
    
    def _detect_native_tool_support(self) -> bool:
        """Detect if LLM supports native tool_calls"""
        model_name = self.llm.model_name.lower()
        
        native_models = {
            "gpt-4": True,
            "gpt-3.5": False,
            "claude-3": True,
            "claude-2": False,
            "llama": False,
            "mistral": False,
            "codellama": False,
        }
        
        for model_key, supports_tools in native_models.items():
            if model_key in model_name:
                return supports_tools
        
        # Default: assume no tools for unknown models
        return False
```

#### Native Tool Calling

```python
class NativeToolCallingExecutor(ToolCallingExecutor):
    async def prepare_tools(self, tools: List[Tool]) -> List[Dict]:
        """Convert SDK tools to OpenAI format"""
        prepared = []
        
        for tool in tools:
            prepared.append({
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": {
                        "type": "object",
                        "properties": self._build_properties(tool),
                        "required": self._extract_required(tool),
                    }
                }
            })
        
        return prepared
    
    async def call_llm_with_tools(
        self,
        llm,
        messages: List[Dict],
        tools: List[Dict]
    ):
        """Call LLM with native tool support"""
        response = await llm.ainvoke(
            messages,
            tools=tools,
            tool_choice="auto"  # Let LLM decide if tools needed
        )
        
        return response  # Contains tool_calls attribute
    
    async def parse_tool_calls(self, response) -> List[ToolCall]:
        """Extract tool_calls from native response"""
        if not hasattr(response, 'tool_calls'):
            return []
        
        tool_calls = []
        for call in response.tool_calls:
            tool_calls.append(ToolCall(
                id=call.id,
                name=call.function.name,
                args=json.loads(call.function.arguments)
            ))
        
        return tool_calls
```

#### Synthetic Tool Calling

```python
class SyntheticToolCallingExecutor(ToolCallingExecutor):
    async def prepare_system_prompt(
        self,
        base_prompt: str,
        tools: List[Tool]
    ) -> str:
        """Inject tool descriptions into system prompt"""
        
        tools_desc = "You have access to these tools:\n\n"
        
        for tool in tools:
            tools_desc += f"""
- **{tool.name}**: {tool.description}
  Parameters:
"""
            for param_name, param_type in tool.parameters.items():
                tools_desc += f"    - {param_name} ({param_type})\n"
        
        tools_usage = """
To use a tool, write this exact format:
<tool name="TOOL_NAME">
  <arg name="PARAM_NAME">PARAM_VALUE</arg>
  <arg name="PARAM_NAME2">PARAM_VALUE2</arg>
</tool>

You must include all required parameters. After the tool output, continue your response.
"""
        
        return f"{base_prompt}\n\n{tools_desc}\n{tools_usage}"
    
    async def parse_tool_calls(self, response_text: str) -> List[ToolCall]:
        """Extract tool calls from XML-formatted response"""
        
        import re
        pattern = r'<tool name="([^"]+)">(.+?)</tool>'
        tool_calls = []
        
        for match in re.finditer(pattern, response_text, re.DOTALL):
            tool_name = match.group(1)
            tool_content = match.group(2)
            
            # Parse arguments
            args_pattern = r'<arg name="([^"]+)">([^<]+)</arg>'
            args = {}
            
            for arg_match in re.finditer(args_pattern, tool_content):
                arg_name = arg_match.group(1)
                arg_value = arg_match.group(2).strip()
                
                # Try to parse as JSON for complex types
                try:
                    args[arg_name] = json.loads(arg_value)
                except:
                    args[arg_name] = arg_value
            
            tool_calls.append(ToolCall(
                id=str(uuid.uuid4()),
                name=tool_name,
                args=args
            ))
        
        return tool_calls
```

### Why This Works

1. **At init**: Detect model capability once
2. **At runtime**: Use the appropriate executor
3. **To caller**: No difference! Same interface

Result: **Same code works with all models**.

---

## Part 2: Resilient P2P Communication

### Challenge

When Agent A sends to Agent B:
- Network might be down
- Agent B might be slow
- Agent B might be temporarily offline
- Request might timeout

**Strategy**: Exponential backoff with bounded retries

### Implementation

```python
class AgentConnector:
    def __init__(
        self,
        transport: TransportProtocol,
        max_retries: int = 3,
        initial_backoff: float = 1.0,
        max_backoff: float = 32.0
    ):
        self.transport = transport
        self.max_retries = max_retries
        self.initial_backoff = initial_backoff
        self.max_backoff = max_backoff
    
    async def send_message(
        self,
        agent_id: str,
        message: Message,
        timeout: float = 30.0
    ) -> Message:
        """Send message with automatic retry"""
        
        # Lookup agent info
        agent_info = await self.registry.get_agent(agent_id)
        if not agent_info:
            raise AgentNotFoundError(f"Agent {agent_id} not found")
        
        return await self._send_with_retries(
            connection_info=agent_info.connection_info,
            message=message,
            timeout=timeout
        )
    
    async def _send_with_retries(
        self,
        connection_info: ConnectionInfo,
        message: Message,
        timeout: float
    ) -> Message:
        """Execute with exponential backoff"""
        
        last_error = None
        
        for attempt in range(self.max_retries):
            try:
                logger.debug(
                    f"Attempt {attempt + 1}/{self.max_retries} "
                    f"to send message {message.id}"
                )
                
                response = await asyncio.wait_for(
                    self.transport.send(
                        connection_info=connection_info,
                        message=message
                    ),
                    timeout=timeout
                )
                
                # Success!
                logger.info(
                    f"Message {message.id} sent successfully "
                    f"to {connection_info.endpoint}"
                )
                return response
                
            except (ConnectionError, asyncio.TimeoutError) as e:
                last_error = e
                
                if attempt < self.max_retries - 1:
                    # Calculate backoff
                    backoff = min(
                        self.initial_backoff * (2 ** attempt),
                        self.max_backoff
                    )
                    
                    logger.warning(
                        f"Message send failed (attempt {attempt + 1}), "
                        f"retrying in {backoff}s... "
                        f"Error: {str(e)}"
                    )
                    
                    await asyncio.sleep(backoff)
                else:
                    # Final attempt failed
                    logger.error(
                        f"Message {message.id} failed after "
                        f"{self.max_retries} attempts"
                    )
        
        raise MessageSendError(
            f"Failed to send message after {self.max_retries} retries",
            last_error
        )
```

### Backoff Schedule

```
Attempt 1: Fail immediately
          Wait 2^0 = 1 second
Attempt 2: Try again
          Wait 2^1 = 2 seconds
Attempt 3: Try again
          Wait 2^2 = 4 seconds
Attempt 4: Try again
          FAIL - Give up
```

### Why Exponential?

- **Too fast (no backoff)**: Thundering herd, overwhelms recipient
- **Linear backoff**: Predictable, easy to DoS
- **Exponential backoff**: Spreads retry load, standard in distributed systems

### Real Example

```python
# Network glitch at second 1
# Agent retries at: 1s, 2s, 4s
# By 4s, network recovered → success

await connector.send_message(
    agent_id="optimization_agent",
    message=optimization_request,
    timeout=30.0  # Timeout per attempt, not total
)
```

---

## Part 3: Message Validation

### Contract-Based Communication

Each agent declares its input/output schema:

```python
agent_b_schema = AgentSchema(
    name="OptimizationAgent",
    input_schema=InputSchema(
        fields={
            "data": FieldSchema(
                type="array",
                description="Dataset to optimize",
                constraints={"min_items": 1}
            ),
            "objective": FieldSchema(
                type="string",
                description="Optimization objective",
                constraints={"enum": ["cost", "speed", "accuracy"]}
            )
        },
        required_fields=["data", "objective"]
    ),
    output_schema=OutputSchema(
        fields={
            "optimized_data": FieldSchema(type="array"),
            "improvement": FieldSchema(type="number")
        },
        required_fields=["optimized_data", "improvement"]
    )
)
```

### Validation Pipeline

```python
class MessageValidator:
    async def validate_request(
        self,
        message: Message,
        target_schema: AgentSchema
    ) -> ValidationResult:
        """Validate incoming request"""
        
        # Step 1: JSON validity
        try:
            data = json.loads(message.data) if isinstance(message.data, str) else message.data
        except json.JSONDecodeError as e:
            return ValidationResult(
                valid=False,
                errors=[f"Invalid JSON: {e}"]
            )
        
        # Step 2: Required fields
        schema = target_schema.input_schema
        missing = set(schema.required_fields) - set(data.keys())
        if missing:
            return ValidationResult(
                valid=False,
                errors=[f"Missing fields: {', '.join(missing)}"]
            )
        
        # Step 3: Type validation
        errors = []
        for field_name, field_schema in schema.fields.items():
            if field_name not in data:
                continue
            
            value = data[field_name]
            validator = self._get_validator(field_schema.type)
            
            if not validator.validate(value):
                errors.append(
                    f"Field '{field_name}': Expected {field_schema.type}, "
                    f"got {type(value).__name__}"
                )
        
        if errors:
            return ValidationResult(valid=False, errors=errors)
        
        # Step 4: Constraint validation
        for field_name, field_schema in schema.fields.items():
            if field_name not in data or not field_schema.constraints:
                continue
            
            value = data[field_name]
            constraints_errors = self._validate_constraints(
                field_name,
                value,
                field_schema.constraints
            )
            errors.extend(constraints_errors)
        
        if errors:
            return ValidationResult(valid=False, errors=errors)
        
        return ValidationResult(valid=True)
    
    def _validate_constraints(
        self,
        field_name: str,
        value: Any,
        constraints: Dict
    ) -> List[str]:
        """Validate field constraints"""
        
        errors = []
        
        # Enum validation
        if "enum" in constraints:
            allowed = constraints["enum"]
            if value not in allowed:
                errors.append(
                    f"Field '{field_name}': Expected one of {allowed}, got {value}"
                )
        
        # Min/Max for numbers
        if isinstance(value, (int, float)):
            if "minimum" in constraints and value < constraints["minimum"]:
                errors.append(
                    f"Field '{field_name}': Value {value} is less than minimum {constraints['minimum']}"
                )
            
            if "maximum" in constraints and value > constraints["maximum"]:
                errors.append(
                    f"Field '{field_name}': Value {value} exceeds maximum {constraints['maximum']}"
                )
        
        # Min/Max for arrays
        if isinstance(value, list):
            if "min_items" in constraints and len(value) < constraints["min_items"]:
                errors.append(
                    f"Field '{field_name}': Array length {len(value)} less than minimum {constraints['min_items']}"
                )
            
            if "max_items" in constraints and len(value) > constraints["max_items"]:
                errors.append(
                    f"Field '{field_name}': Array length {len(value)} exceeds maximum {constraints['max_items']}"
                )
        
        # Pattern matching for strings
        if isinstance(value, str):
            if "pattern" in constraints:
                import re
                pattern = constraints["pattern"]
                if not re.match(pattern, value):
                    errors.append(
                        f"Field '{field_name}': Value '{value}' does not match pattern '{pattern}'"
                    )
        
        return errors
```

---

## Part 4: Semantic Agent Discovery

### Problem

Agent A needs to find agents by expertise:
- "I need optimization help"
- "Find data scientists"
- "Who knows machine learning?"

**Naive approach**: String matching. ❌  
**Better approach**: Semantic embeddings. ✅

### Implementation

```python
from sentence_transformers import SentenceTransformer

class EmbeddingMatcher:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.embedder = SentenceTransformer(model_name)
    
    def compute_similarity(self, text1: str, text2: str) -> float:
        """Cosine similarity between two texts"""
        emb1 = self.embedder.encode(text1, convert_to_tensor=True)
        emb2 = self.embedder.encode(text2, convert_to_tensor=True)
        
        # Cosine similarity
        similarity = emb1 @ emb2.T / (torch.norm(emb1) * torch.norm(emb2))
        return float(similarity)

class AgentRegistry:
    async def find_agents_by_expertise(
        self,
        expertise: List[str],
        min_confidence: float = 0.7,
        strategy: str = "semantic"
    ) -> List[AgentInfo]:
        """Find agents by expertise"""
        
        if strategy == "exact":
            return self._find_exact_match(expertise)
        
        elif strategy == "semantic":
            return await self._find_semantic_match(expertise, min_confidence)
        
        else:  # hybrid
            exact = self._find_exact_match(expertise)
            semantic = await self._find_semantic_match(expertise, min_confidence)
            
            # Merge, keeping order: exact first, then semantic
            seen = {a.id for a in exact}
            combined = exact + [a for a in semantic if a.id not in seen]
            
            return combined
    
    def _find_exact_match(self, query_expertise: List[str]) -> List[AgentInfo]:
        """Exact string matching"""
        results = []
        
        for agent in self.agents.values():
            # Check if any query matches agent domain
            agent_domains = {e.domain for e in agent.expertise}
            query_set = set(query_expertise)
            
            matches = query_set & agent_domains
            if matches:
                # Score: percentage of query matched
                score = len(matches) / len(query_set)
                results.append((agent, score))
        
        # Sort by score
        return [a for a, _ in sorted(results, key=lambda x: x[1], reverse=True)]
    
    async def _find_semantic_match(
        self,
        query_expertise: List[str],
        min_confidence: float
    ) -> List[AgentInfo]:
        """Semantic matching via embeddings"""
        
        query_text = " ".join(query_expertise)
        results = []
        
        for agent in self.agents.values():
            agent_text = " ".join(e.domain for e in agent.expertise)
            
            # Compute similarity
            similarity = await self.matcher.compute_similarity(
                query_text,
                agent_text
            )
            
            if similarity >= min_confidence:
                results.append((agent, float(similarity)))
        
        # Sort by similarity
        return [a for a, _ in sorted(results, key=lambda x: x[1], reverse=True)]
```

### Example

```python
# Query
query = ["optimization", "performance", "scalability"]

# Exact match
# Finds: OptimizationAgent (has "optimization" domain)

# Semantic match
# Finds: OptimizationAgent (exact match)
#        PerformanceCoach (similar to query)
#        ScalingExpert (related to scalability)
#
# Even if domain names are different:
# ScalingExpert might have domain="throughput"
# But semantic matching finds it because:
# "throughput" ~ "scalability" (high cosine similarity)
```

---

## Part 5: ReAct Loop Execution

### Algorithm

```
Reasoning + Acting (ReAct)

WHILE iteration < max_iterations:
    phase = "reasoning"
    response = call_llm()
    
    IF has_final_answer(response):
        RETURN response
    
    phase = "acting"
    tool_call = parse_tool_call(response)
    
    IF tool_call.is_communication():
        # Send to other agent
        result = await connector.send_message(...)
    ELSE:
        # Execute locally
        result = await execute_tool(tool_call)
    
    # Update context
    add_to_history(action, result)
    iteration += 1

RETURN AgentResult
```

### Implementation

```python
class ReActExecutor:
    async def run(
        self,
        task: str,
        context: Optional[Dict] = None,
        max_iterations: int = 10
    ) -> AgentResult:
        """Execute ReAct loop"""
        
        # Initialize
        messages = [
            {"role": "user", "content": task}
        ]
        reasoning_steps = []
        tool_calls_log = []
        interactions = []
        
        iteration = 0
        final_answer = None
        
        while iteration < max_iterations:
            logger.info(f"Iteration {iteration + 1}/{max_iterations}")
            
            # REASONING: Call LLM
            llm_response = await self.llm.ainvoke(messages)
            
            reasoning_step = ReasoningStep(
                iteration=iteration,
                thought=self._extract_thought(llm_response),
                action_name=self._extract_action_name(llm_response)
            )
            reasoning_steps.append(reasoning_step)
            
            # PARSING: Extract tool call or final answer
            if self._has_final_answer(llm_response):
                final_answer = llm_response.content
                logger.info(f"Final answer at iteration {iteration}")
                break
            
            tool_calls = await self.tool_manager.parse_tool_calls(llm_response)
            
            if not tool_calls:
                # No tool called but not final answer? Use response as answer
                final_answer = llm_response.content
                break
            
            # ACTION: Execute first tool call (could do parallel)
            tool_call = tool_calls[0]
            tool_calls_log.append(tool_call)
            
            logger.debug(f"Executing tool: {tool_call.name}")
            
            if tool_call.name in self.communication_tools:
                # Inter-agent communication
                result = await self._execute_communication(tool_call)
                interactions.append(result)
            else:
                # Local tool execution
                result = await self.tools[tool_call.name].execute(**tool_call.args)
            
            # UPDATE: Add to conversation history
            messages.append({"role": "assistant", "content": llm_response.content})
            messages.append({
                "role": "user",
                "content": f"Tool '{tool_call.name}' result: {result}"
            })
            
            iteration += 1
        
        if final_answer is None:
            final_answer = "Max iterations reached without final answer"
        
        return AgentResult(
            final_answer=final_answer,
            reasoning_steps=reasoning_steps,
            tool_calls=tool_calls_log,
            interactions=interactions,
            total_iterations=iteration,
            execution_time_ms=time.time() - start_time
        )
    
    async def _execute_communication(
        self,
        tool_call: ToolCall
    ) -> Message:
        """Execute inter-agent communication"""
        
        if tool_call.name == "find_experts":
            expertise = tool_call.args.get("expertise", [])
            agents = await self.orchestrator.find_experts(expertise)
            return Message(
                sender_id=self.agent_id,
                data={"agents": [a.to_dict() for a in agents]}
            )
        
        elif tool_call.name == "send_message":
            agent_id = tool_call.args.get("agent_id")
            message_data = tool_call.args.get("message")
            
            result = await self.orchestrator.send_message(agent_id, message_data)
            return result
```

---

## Part 6: Practical Optimizations

### 1. Message Compression

```python
def compress_message(message: Message) -> bytes:
    """Compress message for network transfer"""
    import gzip
    json_bytes = message.to_json().encode()
    return gzip.compress(json_bytes)

async def decompress_message(data: bytes) -> Message:
    """Decompress received message"""
    import gzip
    json_str = gzip.decompress(data).decode()
    return Message.from_json(json_str)
```

### 2. Embedding Caching

```python
class CachedEmbedder:
    def __init__(self, embedder):
        self.embedder = embedder
        self.cache = {}  # text -> embedding
    
    async def embed(self, text: str):
        if text in self.cache:
            return self.cache[text]
        
        embedding = await self.embedder.encode(text)
        self.cache[text] = embedding
        return embedding
```

### 3. Connection Pooling

```python
class ConnectionPool:
    def __init__(self, max_connections: int = 10):
        self.max_connections = max_connections
        self.available = asyncio.Queue(maxsize=max_connections)
        self.connections = {}
    
    async def get_connection(self, endpoint: str):
        if endpoint not in self.connections:
            conn = await self._create_connection(endpoint)
            self.connections[endpoint] = conn
        
        return self.connections[endpoint]
```

### 4. Parallel Message Sending

```python
async def send_messages_parallel(
    self,
    messages: Dict[str, Message]  # agent_id -> message
) -> Dict[str, Message]:
    """Send messages to multiple agents concurrently"""
    
    tasks = {
        agent_id: self.send_message(agent_id, msg)
        for agent_id, msg in messages.items()
    }
    
    results = await asyncio.gather(*tasks.values(), return_exceptions=True)
    
    return {
        agent_id: (result if isinstance(result, Message) else None)
        for agent_id, result in zip(tasks.keys(), results)
    }
```

---

## Conclusion

The AIConexus SDK achieves:

✅ **Model agnosticity**: One code, all models  
✅ **Resilience**: Retry logic, timeouts, validation  
✅ **Intelligence**: Semantic discovery, contract validation  
✅ **Performance**: Async/await, parallel execution, caching  
✅ **Simplicity**: 3 lines of code for developers  

---

**Version**: 1.0  
**Status**: Production-Ready  
**Last Updated**: January 2026

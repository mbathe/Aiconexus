# AIConexus - Agent Internet Protocol Specifications

**Version:** 1.0  
**Date:** January 12, 2026  
**Status:** In Progress

---

## 1. VISION & OBJECTIVES

### 1.1 Global Vision
Create a universal and distributed infrastructure enabling autonomous AI agents to:
- **Discover** dynamically other agents and their capabilities
- **Communicate** via a standardized and interoperable protocol
- **Negotiate** and establish execution contracts
- **Cooperate** to solve complex problems
- **Transact** autonomously (payments, service exchanges)
- **Maintain** reputation and complete audit history

### 1.2 Primary Objectives
1. **Universal Protocol** : Open standard, technology and domain agnostic
2. **Decentralized Network** : Distributed infrastructure with no single point of failure
3. **Agent Marketplace** : Dynamic catalog with search, filtering, and acquisition
4. **M2M Economy** : System for autonomous and secure transactions
5. **Governance** : Permissions, audit, reputation, revocation
6. **Scalability** : Support thousands to millions of agents

### 1.3 Phase 1 Scope (MVP)
- Minimal but extensible protocol
- 3-5 demonstration agent types
- Basic Python and TypeScript SDKs
- Simple marketplace search
- Agent-to-agent and agent-to-tool communication
- Documentation and "Hello World" examples

---

## 2. USERS & USE CASES

### 2.1 Personas

**Agent Developer**
- Creates specialized AI agents (analysis, learning, trading, etc.)
- Integrates via provided SDK
- Wants to monetize creations
- Needs: Clear documentation, powerful SDK, easy marketplace

**Enterprise/Orchestrator**
- Composes multi-agent workflows
- Integrates external agents in systems
- Requires security, audit, SLA
- Needs: Stable API, governance, support

**Autonomous Agent**
- Autonomous software entity (robot, AI assistant, application)
- Must be able to negotiate and cooperate with other agents
- Needs: Efficient protocol, dynamic discovery, budget management

### 2.2 Priority Use Cases

**Use Case 1: Discovery & Composition**
```
Agent A searches → "Who can do sentiment analysis?"
           ↓
        Registry finds → Agent B (sentiment analyzer)
           ↓
        Agent A → Agent B : "Analyze this text"
           ↓
        Agent B → Agent A : Result + price
```

**Use Case 2: Negotiation & Contract**
```
Agent Buyer : "I need analysis in <100ms, <$0.01"
         ↓
Agent Seller : "I can do that for $0.008"
         ↓
Contract signed (timeout, retry, SLA)
```

**Use Case 3: Processing Pipeline**
```
Input → Agent1 (cleaning) → Agent2 (analysis) 
      → Agent3 (decision) → Output
(Each step is an autonomous transaction)
```

**Use Case 4: Marketplace Acquisition**
```
Developer : "I want a financial analysis Agent"
        ↓
Search/Filter → Results with ratings, price, performance
        ↓
Deploy & Instantiate → Ready to use
```

---

## 3. SYSTEM ARCHITECTURE

### 3.1 Infrastructure Layers

```
┌─────────────────────────────────────────┐
│   Applications / Clients                │ (Layer 9: Applications)
├─────────────────────────────────────────┤
│   SDK & API (Python, TS, Rust)          │ (Layer 8: SDKs)
├─────────────────────────────────────────┤
│   Marketplace & Discovery               │ (Layer 7: Marketplace)
├─────────────────────────────────────────┤
│   Economic Layer (Budgets, Payments)    │ (Layer 6: Economics)
├─────────────────────────────────────────┤
│   Security & Governance                 │ (Layer 5: Security)
├─────────────────────────────────────────┤
│   Execution & Transaction Management    │ (Layer 4: Execution)
├─────────────────────────────────────────┤
│   Intent Negotiation Engine             │ (Layer 3: Negotiation)
├─────────────────────────────────────────┤
│   Service Discovery & Registry          │ (Layer 2: Discovery)
├─────────────────────────────────────────┤
│   Communication Protocol (JSON/HTTP/WS) │ (Layer 1: Protocol)
├─────────────────────────────────────────┤
│   Distributed Network (P2P/Federated)   │ (Network)
└─────────────────────────────────────────┘
```

### 3.2 Core Components

#### 3.2.1 Protocol Layer
**Responsibility:** Basic communication between agents

Specifications:
- Format: JSON + HTTP/WebSocket/SSE
- Message types: QUERY, OFFER, EXECUTE, RESULT, ERROR, ACK
- Message format: UUID, timestamp, sender_id, receiver_id, payload, signature
- Versioning: Backward compatible, semantic versioning

Example message:
```json
{
  "id": "uuid-v4",
  "version": "1.0",
  "timestamp": "2026-01-12T10:30:00Z",
  "sender": "agent_a",
  "receiver": "agent_b",
  "type": "EXECUTE",
  "payload": {
    "action": "analyze_sentiment",
    "params": {"text": "I love this!"},
    "timeout_ms": 5000,
    "budget": {"currency": "AIC", "max": 0.01}
  },
  "signature": "sha256_hash"
}
```

#### 3.2.2 Discovery & Registry Layer
**Responsibility:** Agent/capability registration, search, notifications

Capabilities:
- Agents register services/capabilities (enriched metadata)
- Full-text search + filtering (performance, cost, availability)
- Watch/notification (Agent X can subscribe to changes)
- Heartbeat + health checks
- Distributed replication (gossip protocol)

Data model:
```json
{
  "agent_id": "unique_id",
  "name": "Sentiment Analyzer v2",
  "description": "...",
  "capabilities": [
    {
      "id": "analyze_sentiment",
      "description": "Analyzes text sentiment",
      "input_schema": {...},
      "output_schema": {...},
      "sla": {
        "latency_ms": 100,
        "availability_percent": 99.9
      },
      "pricing": {
        "model": "per_call",
        "cost_per_unit": 0.001,
        "currency": "AIC"
      }
    }
  ],
  "reputation": {
    "score": 4.8,
    "calls_count": 10000,
    "uptime_percent": 99.95
  },
  "endpoints": [
    {"protocol": "http", "url": "https://agent.example.com/api"},
    {"protocol": "ws", "url": "ws://agent.example.com/stream"}
  ],
  "registered_at": "2026-01-01T00:00:00Z",
  "last_heartbeat": "2026-01-12T10:20:00Z"
}
```

#### 3.2.3 Negotiation Engine
**Responsibility:** Smart contracts and SLAs between agents

Flow:
1. **Intent Broadcast**: "I need X with SLA Y and budget Z"
2. **Offer Generation**: Competent agents propose their terms
3. **Contract Signature**: Agreement on conditions (timeout, retry, pricing)
4. **Execution**: Contract executed with guarantees
5. **Settlement**: Payment and audit

Contract data:
```json
{
  "contract_id": "uuid",
  "requester_id": "agent_a",
  "provider_id": "agent_b",
  "capability_id": "analyze_sentiment",
  "sla": {
    "latency_ms": 100,
    "retry_count": 3,
    "timeout_ms": 5000
  },
  "pricing": {
    "base_cost": 0.001,
    "currency": "AIC",
    "payment_method": "immediate"
  },
  "created_at": "2026-01-12T10:30:00Z",
  "expires_at": "2026-01-12T10:30:30Z",
  "status": "active|completed|failed|disputed"
}
```

#### 3.2.4 Execution & Transaction Manager
**Responsibility:** Robust execution with ACID-like guarantees

Guarantees:
- **Atomicity**: Either everything happens or nothing
- **Consistency**: Coherent state before/after
- **Isolation**: No interference between transactions
- **Durability**: Persistent recording

Features:
- Pipeline orchestration (chains of agents)
- Automatic retry with exponential backoff
- Compensation (rollback) on failure
- Timeout management
- Async/batch execution

#### 3.2.5 Economic Layer
**Responsibility:** Budgets, transactions, pricing

Components:
- **Budget Manager**: Per-agent allocation, consumption tracking
- **Payment Gateway**: Settlement, accounting, audits
- **Pricing Engine**: Dynamic cost calculation based on SLA
- **Ledger**: Blockchain-like for audit trail

Model:
```json
{
  "agent_id": "agent_a",
  "budget": {
    "currency": "AIC",
    "total_allocated": 1000.0,
    "consumed": 234.56,
    "available": 765.44,
    "period": "monthly",
    "reset_date": "2026-02-12"
  },
  "transactions": [
    {
      "id": "tx_uuid",
      "timestamp": "2026-01-12T10:30:05Z",
      "type": "charge",
      "amount": 0.001,
      "counterparty": "agent_b",
      "capability": "analyze_sentiment",
      "status": "settled",
      "reference": "contract_uuid"
    }
  ]
}
```

#### 3.2.6 Security & Governance Layer
**Responsibility:** Authentication, authorization, audit, sandbox

Components:
- **Identity & Authentication**: Certificates, API keys, OAuth2-like
- **Authorization**: Granular permissions, scopes
- **Sandbox**: Execution isolation (containers, resource limits)
- **Audit Logger**: Immutable event log
- **Reputation System**: Dynamic scoring + revocation

Features:
- TLS 1.3+ by default
- Cryptographic message signatures
- Jailing: Agents can only access their resources
- Rate limiting + DDoS protection
- Consensus for sensitive actions

#### 3.2.7 Marketplace Layer
**Responsibility:** Catalog and discovery UX

Features:
- Multi-criteria search/filter
- Sorting by reputation, performance, price
- Reviews and ratings
- Version management
- Deployment templates

UI concepts:
- Web catalog (agents, tools, templates)
- One-click installation (CLI + SDK integration)
- Ratings and reviews after use

#### 3.2.8 SDK Layer
**Responsibility:** Simple APIs for developers

Languages: Python, TypeScript, Rust (Phase 1+)

Minimal APIs:
```python
# Python example
from aiconexus import Agent, ServiceRegistry

class MyAgent(Agent):
    def __init__(self):
        super().__init__("my_agent_id")
        self.registry = ServiceRegistry()
    
    async def provide(self):
        """Register my capabilities"""
        self.register_capability(
            name="process_data",
            handler=self.process_data,
            sla={"latency_ms": 100},
            pricing=0.001
        )
    
    async def process_data(self, data):
        return {"result": processed}

# Usage
agent = MyAgent()
agent.start()
```

---

## 4. CORE DATA MODELS

### 4.1 Agent Identity
```
Agent:
  - id: UUID unique
  - public_key: For message signature
  - name: Human-readable
  - description: Details
  - owner: Controller
  - created_at: Timestamp
  - capabilities: [Capability]
  - endpoints: [Endpoint]
  - reputation: Reputation
  - settings: Config
```

### 4.2 Capability
```
Capability:
  - id: Unique within agent
  - name: Descriptive name
  - description: Details
  - version: Semantic
  - input_schema: JSON Schema
  - output_schema: JSON Schema
  - sla: LatencyMS, Availability, Timeout
  - pricing: CostPerUnit, Currency, Billing Model
  - tags: [String] for search
  - authentication_required: Boolean
```

### 4.3 Request/Response
```
Request:
  - id: UUID
  - type: QUERY|OFFER|EXECUTE|RESULT|ERROR
  - sender_id: UUID Agent
  - receiver_id: UUID Agent
  - capability_id: String
  - payload: JSON
  - timestamp: ISO8601
  - signature: Crypto hash
  - budget: Amount + Currency

Response:
  - request_id: Reference
  - status: OK|ERROR|TIMEOUT|REJECTED
  - result: JSON|null
  - error: String|null
  - cost_actual: Actual amount charged
  - timestamp: ISO8601
```

### 4.4 Contract
```
Contract:
  - id: UUID
  - requester_id: Agent UUID
  - provider_id: Agent UUID
  - capability_id: String
  - terms: JSON (SLA, pricing, etc)
  - status: PENDING|ACTIVE|COMPLETED|FAILED|DISPUTED
  - created_at: Timestamp
  - expires_at: Timestamp
  - executions: [Execution]
```

### 4.5 Reputation
```
Reputation:
  - agent_id: UUID
  - score: Float 0-5
  - total_calls: Int
  - successful_calls: Int
  - failed_calls: Int
  - avg_latency_ms: Float
  - uptime_percent: Float
  - response_quality_avg: Float
  - last_updated: Timestamp
  - history: [Event] (30-day)
```

---

## 5. FUNCTIONAL REQUIREMENTS

### 5.1 Communication & Discovery
- [ ] Agent can register with capabilities
- [ ] Agent can discover other agents via search
- [ ] Registry changes notified in real-time
- [ ] Support HTTP, WebSocket, SSE
- [ ] Messages always cryptographically signed

### 5.2 Negotiation & Execution
- [ ] Agent can broadcast intent
- [ ] Competent agents respond with offers
- [ ] Contracts signed before execution
- [ ] Execution with retry/timeout
- [ ] Compensation on error

### 5.3 Economic & Transactions
- [ ] Per-agent budgets with limits
- [ ] Per-call or subscription pricing
- [ ] Immutable transaction ledger
- [ ] Automatic settlement
- [ ] Currency support (at minimum AIC)

### 5.4 Security & Governance
- [ ] Authenticated agents (certificates)
- [ ] Granular permissions
- [ ] Complete audit trail
- [ ] Execution sandbox
- [ ] Rate limiting + DDoS protection

### 5.5 Marketplace
- [ ] Agents searchable by capabilities
- [ ] Filtering by price, performance, reputation
- [ ] Deployment templates
- [ ] Easy installation

### 5.6 SDK & Integration
- [ ] Python and TypeScript SDKs
- [ ] Agent creation in <10 lines
- [ ] Documentation + examples
- [ ] Testing utilities

---

## 6. NON-FUNCTIONAL REQUIREMENTS

### 6.1 Performance
- Latency: <100ms for registry query
- Throughput: ≥10k messages/sec
- Availability: 99.95% uptime
- Scalability: Support 1M+ agents

### 6.2 Security
- TLS 1.3+ by default
- Encryption at rest for ledger
- No single point of failure
- Zero trust architecture

### 6.3 Reliability
- Message delivery guarantee (at-least-once)
- Idempotency for payments
- Graceful degradation
- Circuit breaker patterns

### 6.4 Maintainability
- Code coverage >80%
- Clear documentation
- API versioning
- Deprecation policies

### 6.5 Open Source Ready
- License: MIT or Apache 2.0
- Clear contribution guidelines
- Automated testing + CI/CD
- Release process

---

## 7. PHASE 1 SUCCESS CRITERIA

- [DONE] Deployable and tested MVP code
- [DONE] Protocol defined and documented
- [DONE] 3 operational example agents
- [DONE] Functional Python SDK
- [DONE] Agent-to-agent communication validated
- [DONE] Basic marketplace search
- [DONE] 50+ GitHub contributors (post open-source)
- [DONE] Complete "Hello World" documentation

---

## 8. CONSTRAINTS & DEPENDENCIES

### 8.1 Technical
- Python 3.10+ (backend core)
- TypeScript 5+ (client SDK)
- PostgreSQL for registry (scalable)
- Redis for caching
- Kubernetes for orchestration (Phase 2+)

### 8.2 Organizational
- MVP in 3-6 months (2-4 devs)
- Open-source from day 1
- Community-first approach
- No intentional tech debt

---

## 9. GLOSSARY

- **Agent**: Autonomous entity capable of discovering, negotiating, executing
- **Capability**: Service/function offered by an agent
- **Contract**: Agreement between agents to execute capability
- **SLA**: Service Level Agreement (latency, availability)
- **AIC**: AIConexus token/currency
- **Registry**: Distributed catalog of agents/capabilities
- **Intent**: Formatted request (service request)
- **Settlement**: Transaction payment finalization
- **Sandbox**: Secure execution isolation
- **M2M**: Machine-to-Machine (autonomous)


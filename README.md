# AIConexus - Agent Internet Protocol

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A universal infrastructure for autonomous AI agents to communicate, cooperate, and transact in a decentralized network.

## Vision

Create the "Internet for AI Agents" - enabling:
- **Discovery**: Agents dynamically find other agents and their capabilities
- **Communication**: Standardized protocol for agent-to-agent interaction
- **Negotiation**: Smart contracts and SLA agreements between agents
- **Execution**: Reliable task execution with retry and timeout handling
- **Transactions**: Autonomous M2M payments and economic interactions
- **Governance**: Security, audit, reputation, and trust management

## Quick Start

### Prerequisites
- Python 3.10+
- PostgreSQL 13+
- Redis 6+

### Installation

```bash
# Clone the repository
git clone https://github.com/aiconexus/aiconexus.git
cd aiconexus

# Setup development environment
bash scripts/setup_dev_env.sh

# Activate virtual environment
poetry shell
```

### Hello World

```python
import asyncio
from aiconexus.core.agent import Agent

class MyAgent(Agent):
    async def initialize(self):
        self.register_capability(
            capability_id="hello",
            name="Hello",
            description="Says hello",
            input_schema={},
            output_schema={},
            sla={},
            pricing={},
        )

    async def execute_capability(self, capability_id, params):
        return {"message": "Hello, World!"}

    async def shutdown(self):
        pass

# Run it
agent = MyAgent(name="MyAgent")
asyncio.run(agent.initialize())
```

See [examples/hello_world](examples/hello_world/) for complete example.

## Documentation

- [Specifications](SPECIFICATIONS.md) - Complete requirements and architecture
- [Architecture](ARCHITECTURE.md) - Detailed technical design
- [Project Structure](PROJECT_STRUCTURE.md) - Folder organization
- [Getting Started](docs/getting_started.md) - Step-by-step guide
- [API Reference](docs/api_reference.md) - SDK documentation

## Key Features

### 1. Universal Protocol
- **Format**: JSON + HTTP/WebSocket/SSE
- **Encryption**: TLS 1.3+ with message signing
- **Backward compatible** with semantic versioning

### 2. Dynamic Discovery
- **Full-text search** for agent capabilities
- **Real-time notifications** of changes
- **Distributed registry** with gossip replication
- **Health monitoring** with heartbeats

### 3. Smart Negotiation
- **Intent broadcasting** for service requests
- **Offer collection** from competent agents
- **Contract signing** with terms
- **Automatic SLA enforcement**

### 4. Reliable Execution
- **Retry logic** with exponential backoff
- **Timeout management** and compensation
- **Pipeline orchestration** for complex workflows
- **Transactional guarantees** (ACID-like)

### 5. Economic Engine
- **Per-agent budgets** with limits
- **Multiple pricing models** (per-call, subscription, dynamic)
- **Immutable ledger** for audit trail
- **Automatic settlement** and reconciliation

### 6. Security & Governance
- **Agent authentication** with certificates
- **Granular permissions** and scopes
- **Sandbox execution** with resource limits
- **Complete audit trail** of all actions
- **Reputation system** with dynamic scoring

## Project Structure

```
aiconexus/
├── src/aiconexus/          # Main source code
│   ├── core/               # Agent, Capability, Contract
│   ├── protocol/           # Message handling
│   ├── discovery/          # Registry & search
│   ├── negotiation/        # Intent & contracts
│   ├── execution/          # Task execution
│   ├── economics/          # Budget & payments
│   ├── security/           # Auth & audit
│   ├── marketplace/        # Catalog & UX
│   ├── api/                # REST API (FastAPI)
│   └── sdk/                # Public SDK
├── tests/                  # Test suite
├── examples/               # Example agents
├── docs/                   # Documentation
└── config/                 # Configuration files
```

## Development

### Setup Development Environment

```bash
bash scripts/setup_dev_env.sh
poetry shell
```

### Run Tests

```bash
# All tests with coverage
bash scripts/run_tests.sh

# Specific test file
pytest tests/unit/test_agent.py -v

# With coverage
pytest --cov=src/aiconexus --cov-report=html
```

### Code Quality

```bash
# Format code
bash scripts/format_code.sh

# Type checking
poetry run mypy src/aiconexus

# Linting
poetry run ruff check src tests
```

## Examples

### Hello World Agent
```bash
poetry run python examples/hello_world/agent.py
```

### Sentiment Analyzer
```bash
poetry run python examples/sentiment_analyzer/agent.py
```

See [examples/](examples/) for more examples.

## Roadmap

### Phase 1: MVP (Q1 2026)
- [DONE] Core protocol & types
- [DONE] Registry & discovery
- [TODO] Negotiation engine
- [TODO] Execution manager
- [TODO] Basic economy
- [TODO] SDK (Python/TypeScript)
- [TODO] Marketplace

### Phase 2: Adoption (Q2-Q3 2026)
- Community & documentation
- Advanced SDK features
- Performance optimization
- Cloud deployment templates

### Phase 3: Maturity (Q4 2026+)
- Advanced security (sandbox)
- Full economic system
- Analytics & monitoring
- Enterprise features

## Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Areas for Contribution
- Core protocol implementation
- SDK libraries (TypeScript, Rust)
- Documentation and examples
- Testing and QA
- Performance optimization
- Security audits

## Community

- Email: team@aiconexus.io
- Discord: https://discord.gg/aiconexus
- Documentation: https://docs.aiconexus.io
- Issue Tracker: https://github.com/aiconexus/aiconexus/issues

## License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file.

## Citation

If you use AIConexus in your research or project, please cite:

```bibtex
@software{aiconexus2026,
  title={AIConexus: Universal Infrastructure for Autonomous Agent Communication},
  author={AIConexus Team},
  year={2026},
  url={https://github.com/aiconexus/aiconexus}
}
```

## Disclaimer

AIConexus is in early development (Alpha). Use at your own risk in production environments.

---

Built with ❤️ by the AIConexus community

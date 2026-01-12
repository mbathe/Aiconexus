# AIConexus - Project Structure

```
aiconexus/
├── README.md                          # Main documentation
├── LICENSE                            # MIT or Apache 2.0
├── SPECIFICATIONS.md                  # Detailed specs
├── ARCHITECTURE.md                    # Architecture design
├── CONTRIBUTING.md                    # Contribution guidelines
├── ROADMAP.md                         # Development roadmap
│
├── pyproject.toml                     # Python project config
├── poetry.lock                        # Dependency lock file
├── setup.cfg                          # Setup configuration
├── Makefile                           # Development commands
│
├── .github/
│   ├── workflows/
│   │   ├── tests.yml                  # CI/CD for tests
│   │   ├── lint.yml                   # Code quality checks
│   │   └── release.yml                # Automated releases
│   ├── ISSUE_TEMPLATE/
│   │   ├── bug.md
│   │   ├── feature.md
│   │   └── documentation.md
│   └── pull_request_template.md
│
├── .docker/
│   ├── Dockerfile.core                # Core service image
│   ├── Dockerfile.example-agent       # Example agent image
│   └── docker-compose.yml             # Local development setup
│
├── docs/
│   ├── index.md                       # Documentation home
│   ├── getting_started.md
│   ├── protocol.md                    # Protocol specification
│   ├── api_reference.md               # SDK API docs
│   ├── examples/
│   │   ├── hello_world.md
│   │   ├── sentiment_analyzer.md
│   │   ├── pipeline.md
│   │   └── marketplace.md
│   ├── deployment/
│   │   ├── local.md
│   │   ├── docker.md
│   │   ├── kubernetes.md
│   │   └── cloud.md
│   ├── security/
│   │   ├── authentication.md
│   │   ├── authorization.md
│   │   ├── sandbox.md
│   │   └── audit.md
│   └── advanced/
│       ├── economics.md
│       ├── custom_negotiation.md
│       └── performance_tuning.md
│
├── src/aiconexus/                    # Main source code
│   │
│   ├── __init__.py                   # Package exports
│   ├── version.py                    # Version info
│   ├── config.py                     # Global configuration
│   ├── constants.py                  # Constants and enums
│   ├── exceptions.py                 # Custom exceptions
│   ├── types.py                      # Type definitions
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── agent.py                  # Base Agent class
│   │   ├── capability.py             # Capability definition
│   │   ├── contract.py               # Contract management
│   │   └── types.py                  # Core type definitions
│   │
│   ├── protocol/                     # Communication protocol
│   │   ├── __init__.py
│   │   ├── message.py                # Message classes
│   │   ├── serializer.py             # JSON serialization
│   │   ├── transport.py              # Transport layer (HTTP, WS)
│   │   ├── handler.py                # Message handling
│   │   └── security.py               # Message signing/verification
│   │
│   ├── discovery/                    # Registry & discovery
│   │   ├── __init__.py
│   │   ├── registry.py               # Central registry
│   │   ├── search.py                 # Search engine
│   │   ├── metadata.py               # Metadata models
│   │   ├── replication.py            # Distributed sync
│   │   └── health.py                 # Health checks
│   │
│   ├── negotiation/                  # Intent & negotiation
│   │   ├── __init__.py
│   │   ├── intent.py                 # Intent classes
│   │   ├── engine.py                 # Negotiation logic
│   │   ├── offer.py                  # Offer handling
│   │   └── contract_manager.py       # Contract lifecycle
│   │
│   ├── execution/                    # Execution management
│   │   ├── __init__.py
│   │   ├── executor.py               # Execution engine
│   │   ├── scheduler.py              # Task scheduling
│   │   ├── retry.py                  # Retry policies
│   │   ├── timeout.py                # Timeout handling
│   │   ├── pipeline.py               # Pipeline orchestration
│   │   └── monitoring.py             # Execution monitoring
│   │
│   ├── economics/                    # Budget & transactions
│   │   ├── __init__.py
│   │   ├── budget.py                 # Budget management
│   │   ├── pricing.py                # Pricing models
│   │   ├── transaction.py            # Transaction handling
│   │   ├── ledger.py                 # Immutable ledger
│   │   ├── payment.py                # Payment gateway
│   │   └── currency.py               # Currency handling
│   │
│   ├── security/                     # Auth & security
│   │   ├── __init__.py
│   │   ├── credentials.py            # Credential management
│   │   ├── authentication.py         # Authentication service
│   │   ├── authorization.py          # Authorization & permissions
│   │   ├── sandbox.py                # Sandbox execution
│   │   ├── audit.py                  # Audit logging
│   │   └── encryption.py             # Encryption utilities
│   │
│   ├── marketplace/                  # Marketplace features
│   │   ├── __init__.py
│   │   ├── catalog.py                # Catalog management
│   │   ├── entry.py                  # Marketplace entry
│   │   ├── search.py                 # Marketplace search
│   │   ├── templates.py              # Deployment templates
│   │   └── ratings.py                # Ratings & reviews
│   │
│   ├── monitoring/                   # Metrics & health
│   │   ├── __init__.py
│   │   ├── metrics.py                # Metrics collection
│   │   ├── health.py                 # Health monitoring
│   │   ├── alerts.py                 # Alert management
│   │   └── observability.py          # Logging & tracing
│   │
│   ├── storage/                      # Storage abstraction
│   │   ├── __init__.py
│   │   ├── base.py                   # Abstract base classes
│   │   ├── postgres.py               # PostgreSQL adapter
│   │   ├── redis.py                  # Redis adapter
│   │   ├── models.py                 # ORM models
│   │   └── migrations.py             # Database migrations
│   │
│   ├── api/                          # REST API (FastAPI)
│   │   ├── __init__.py
│   │   ├── app.py                    # FastAPI application
│   │   ├── routes/
│   │   │   ├── agents.py             # Agent endpoints
│   │   │   ├── discovery.py          # Discovery endpoints
│   │   │   ├── execution.py          # Execution endpoints
│   │   │   ├── economics.py          # Economic endpoints
│   │   │   ├── marketplace.py        # Marketplace endpoints
│   │   │   └── health.py             # Health check endpoint
│   │   ├── middleware.py             # Custom middleware
│   │   ├── dependencies.py           # Dependency injection
│   │   └── schemas.py                # Pydantic schemas
│   │
│   ├── sdk/                          # SDK for developers
│   │   ├── __init__.py
│   │   ├── client.py                 # Client library
│   │   ├── async_client.py           # Async client
│   │   ├── context.py                # Execution context
│   │   └── decorators.py             # Useful decorators
│   │
│   └── utils/
│       ├── __init__.py
│       ├── logging.py                # Logging setup
│       ├── validation.py             # Input validation
│       ├── crypto.py                 # Cryptographic utilities
│       ├── time.py                   # Time utilities
│       ├── errors.py                 # Error utilities
│       └── testing.py                # Testing utilities
│
├── tests/                            # Test suite
│   ├── __init__.py
│   ├── conftest.py                   # Pytest configuration
│   ├── fixtures.py                   # Shared fixtures
│   │
│   ├── unit/
│   │   ├── test_protocol.py
│   │   ├── test_discovery.py
│   │   ├── test_negotiation.py
│   │   ├── test_execution.py
│   │   ├── test_economics.py
│   │   ├── test_security.py
│   │   ├── test_marketplace.py
│   │   └── test_utils.py
│   │
│   ├── integration/
│   │   ├── test_agent_discovery.py
│   │   ├── test_execution_flow.py
│   │   ├── test_payment_flow.py
│   │   ├── test_pipeline.py
│   │   └── test_registry_sync.py
│   │
│   ├── e2e/
│   │   ├── test_hello_world.py
│   │   ├── test_sentiment_analyzer.py
│   │   ├── test_marketplace_flow.py
│   │   └── test_multi_agent_negotiation.py
│   │
│   └── load/
│       ├── test_high_throughput.py
│       ├── test_scalability.py
│       └── test_stress.py
│
├── examples/                         # Example agents
│   ├── README.md
│   ├── hello_world/
│   │   ├── agent.py
│   │   └── README.md
│   ├── sentiment_analyzer/
│   │   ├── agent.py
│   │   ├── requirements.txt
│   │   └── README.md
│   ├── calculator/
│   │   ├── agent.py
│   │   └── README.md
│   ├── data_processor/
│   │   ├── agent.py
│   │   └── README.md
│   └── pipeline_example/
│       ├── pipeline.py
│       └── README.md
│
├── tools/
│   ├── cli.py                        # Command-line interface
│   ├── docker_build.sh               # Docker building script
│   ├── load_test.py                  # Load testing tool
│   └── benchmark.py                  # Benchmarking tool
│
├── config/
│   ├── development.yaml              # Dev environment config
│   ├── staging.yaml                  # Staging config
│   ├── production.yaml               # Production config
│   └── kubernetes/
│       ├── deployment.yaml
│       ├── service.yaml
│       ├── configmap.yaml
│       └── secrets.yaml
│
└── scripts/
    ├── setup_dev_env.sh              # Development setup
    ├── run_tests.sh                  # Test runner
    ├── format_code.sh                # Code formatting
    ├── build_docs.sh                 # Build documentation
    ├── deploy_docker.sh              # Docker deployment
    └── init_database.sh              # Database initialization
```

## Structure Explanation

### Source Code Organization

1. **`core/`** - Core domain objects and base classes
2. **`protocol/`** - Communication protocol implementation
3. **`discovery/`** - Agent registry and search
4. **`negotiation/`** - Intent and contract negotiation
5. **`execution/`** - Task execution engine
6. **`economics/`** - Budget and transaction management
7. **`security/`** - Authentication and authorization
8. **`marketplace/`** - Marketplace features
9. **`monitoring/`** - Metrics and health checks
10. **`storage/`** - Database access layer
11. **`api/`** - REST API endpoints
12. **`sdk/`** - Public SDK for developers

### Testing Strategy

- **Unit**: Test individual components in isolation
- **Integration**: Test component interactions
- **E2E**: Test complete user workflows
- **Load**: Performance and scalability testing

### Dependencies

```
Core dependencies (lightweight):
- pydantic (validation)
- sqlalchemy (ORM)
- cryptography (security)
- aiohttp (HTTP client)

API dependencies:
- fastapi
- uvicorn
- pydantic-settings

Storage dependencies:
- psycopg2-binary (PostgreSQL)
- redis

Testing dependencies:
- pytest
- pytest-asyncio
- pytest-cov
- faker

Development dependencies:
- black (formatting)
- ruff (linting)
- mypy (type checking)
- pre-commit
```

### Key Design Principles

1. **Modularity**: Each module has single responsibility
2. **Abstraction**: Storage, transport are abstractable
3. **Async-first**: All I/O operations are async
4. **Type Safety**: Full type hints throughout
5. **Testability**: Dependency injection pattern
6. **Documentation**: Every module has docstrings
7. **Security**: Security integrated at every layer


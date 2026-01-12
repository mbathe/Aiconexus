# AIConexus - New Project Structure

```
aiconexus/
│
├── README.md                          # Main project README
├── LICENSE                            # License file
├── .gitignore
├── pyproject.toml                     # Python project config (root)
├── poetry.lock
├── Makefile                           # Main Makefile
├── CONTRIBUTING.md                    # Contribution guidelines
│
├── docs/                              # 📚 ALL DOCUMENTATION
│   ├── README.md                      # Docs index
│   ├── QUICK_START.md                 # Quick start guide
│   ├── ARCHITECTURE.md                # System architecture
│   ├── PROTOCOL_DESIGN.md             # Protocol specification
│   │
│   ├── deployment/                    # 🚀 Deployment docs
│   │   ├── DOCKER_GATEWAY.md          # Gateway Docker guide
│   │   ├── KUBERNETES.md              # Kubernetes deployment
│   │   ├── AWS_DEPLOYMENT.md          # AWS setup
│   │   └── DOCKER.md                  # Docker guide
│   │
│   ├── guides/                        # 📖 Usage guides
│   │   ├── SDK_USAGE.md               # SDK usage guide
│   │   ├── GATEWAY_ADMIN.md           # Gateway administration
│   │   ├── TROUBLESHOOTING.md         # Troubleshooting
│   │   └── EXAMPLES.md                # Code examples
│   │
│   ├── api/                           # API documentation
│   │   ├── CLIENT_API.md              # GatewayClient API
│   │   ├── AGENT_API.md               # Agent API
│   │   └── PROTOCOL_MESSAGES.md       # Message types
│   │
│   └── sprints/                       # Sprint reports
│       ├── SPRINT_1_REPORT.md
│       ├── SPRINT_2_REPORT.md
│       ├── SPRINT_3_REPORT.md
│       ├── SPRINT_4_REPORT.md
│       ├── SPRINT_5_REPORT.md
│       └── SPRINT5_RESUME_FR.md
│
├── src/                               # 🐍 SOURCE CODE
│   │
│   ├── aiconexus/                     # Main package
│   │   ├── __init__.py
│   │   ├── client.py
│   │   ├── agent.py
│   │   ├── protocol.py
│   │   ├── security.py
│   │   ├── exceptions.py
│   │   └── utils.py
│   │
│   └── sdk/                           # SDK library (separate)
│       ├── __init__.py
│       ├── __version__.py
│       └── ...
│
├── gateway/                           # 🐳 GATEWAY SERVICE (separate)
│   ├── README.md                      # Gateway README
│   ├── pyproject.toml                 # Gateway dependencies (if separate)
│   │
│   ├── src/
│   │   ├── gateway_app.py             # FastAPI app
│   │   ├── gateway_listen.py          # Server startup
│   │   ├── agent_registry.py          # Agent management
│   │   ├── message_handler.py         # Message routing
│   │   └── __init__.py
│   │
│   └── docker/
│       ├── Dockerfile                 # Gateway Dockerfile
│       ├── docker-compose.yml         # Docker Compose
│       ├── .dockerignore
│       └── entrypoint.sh
│
├── scripts/                           # 🛠️  UTILITY SCRIPTS
│   ├── gateway-docker.sh              # Gateway management
│   ├── test-docker-gateway.sh         # Docker tests
│   ├── verify-docker-setup.sh         # Setup verification
│   ├── quickstart.sh                  # Interactive setup
│   ├── git-commit.sh                  # Git helper
│   │
│   └── tests/                         # Test scripts
│       ├── run-tests.sh
│       ├── run-coverage.sh
│       └── run-integration-tests.sh
│
├── examples/                          # 💡 CODE EXAMPLES
│   ├── README.md
│   │
│   ├── agents/                        # Agent examples
│   │   ├── simple_agent.py
│   │   ├── two_agents.py
│   │   ├── message_handler.py
│   │   ├── authentication.py
│   │   └── advanced_usage.py
│   │
│   └── gateway/                       # Gateway examples
│       └── custom_server.py
│
├── tests/                             # 🧪 TEST SUITE
│   ├── conftest.py
│   │
│   ├── unit/                          # Unit tests
│   │   ├── test_client.py
│   │   ├── test_agent.py
│   │   ├── test_security.py
│   │   └── test_protocol.py
│   │
│   ├── integration/                   # Integration tests
│   │   ├── test_server.py
│   │   ├── test_two_clients.py
│   │   └── test_message_exchange.py
│   │
│   └── load/                          # Load tests
│       └── test_load.py
│
├── config/                            # ⚙️  CONFIGURATION
│   ├── .env.example                   # Environment template
│   ├── .env.gateway.example           # Gateway env template
│   ├── logging.yml                    # Logging config
│   └── settings.yml                   # Application settings
│
├── .github/                           # GitHub specific
│   ├── workflows/
│   │   ├── tests.yml
│   │   ├── docker-build.yml
│   │   └── deploy.yml
│   └── ISSUE_TEMPLATE/
│
└── .dockerignore                      # Docker excludes

```

## File Organization Summary

### 📚 Documentation (`/docs`)
- All `.md` files organized by topic
- Deployment guides in `/deployment`
- Usage guides in `/guides`
- API docs in `/api`
- Sprint reports in `/sprints`

### 🐍 Source Code (`/src`)
- SDK library code in `aiconexus/` package
- Separate SDK folder for SDK-only distribution

### 🐳 Gateway (`/gateway`)
- Gateway source in `gateway/src/`
- Docker files in `gateway/docker/`
- Completely separate from SDK
- Can be deployed independently

### 🛠️  Scripts (`/scripts`)
- All shell scripts organized here
- Test scripts in `/scripts/tests`
- Makes root directory clean

### 💡 Examples (`/examples`)
- Agent examples in `/agents`
- Gateway examples in `/gateway`
- Documentation for each example

### 🧪 Tests (`/tests`)
- Unit tests in `/unit`
- Integration tests in `/integration`
- Load tests in `/load`

### ⚙️ Configuration (`/config`)
- All `.env` files in one place
- Configuration templates

## Root Directory (Clean)
- Only essential files:
  - `README.md` (main)
  - `LICENSE`
  - `pyproject.toml` (root dependencies)
  - `poetry.lock`
  - `Makefile` (main)
  - `CONTRIBUTING.md`
  - `.gitignore`

## This is open-source ready! 🚀

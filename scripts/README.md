# 🛠️ Utility Scripts

Helper scripts for development, testing, and deployment.

## 📁 Directory Structure

```
scripts/
├── README.md (this file)
├── gateway-docker.sh          # Gateway Docker management
├── verify-docker-setup.sh     # Verify Docker installation
├── quickstart.sh              # Interactive setup
├── git-commit.sh              # Git commit helper
│
└── tests/                     # Test scripts
    ├── run-all-tests.sh       # Run full test suite
    ├── run-tests.sh           # Run specific tests
    ├── run-coverage.sh        # Generate coverage report
    └── run-integration-tests.sh
```

## 🚀 Gateway Management

### gateway-docker.sh

Complete Docker lifecycle management for the gateway:

```bash
./scripts/gateway-docker.sh build      # Build Docker image
./scripts/gateway-docker.sh start      # Start container
./scripts/gateway-docker.sh stop       # Stop container
./scripts/gateway-docker.sh restart    # Restart container
./scripts/gateway-docker.sh status     # Check status
./scripts/gateway-docker.sh logs       # View logs
./scripts/gateway-docker.sh logs -f    # Follow logs
./scripts/gateway-docker.sh health     # Health check
./scripts/gateway-docker.sh shell      # Open container shell
./scripts/gateway-docker.sh cleanup    # Remove resources
./scripts/gateway-docker.sh help       # Show help
```

## ✅ Setup & Verification

### verify-docker-setup.sh

Quickly verify your Docker setup:

```bash
./scripts/verify-docker-setup.sh
```

Checks:
- All required files exist
- Docker/Docker Compose installed
- Scripts are executable
- Shows next steps

### quickstart.sh

Interactive setup assistant:

```bash
./scripts/quickstart.sh
```

Guides you through:
- Checking requirements
- Installing dependencies
- Showing quick commands
- Next steps

## 🧪 Testing Scripts

### Test Suite

```bash
./scripts/tests/run-all-tests.sh        # Run all tests
./scripts/tests/run-tests.sh            # Run specific tests
./scripts/tests/run-coverage.sh         # Generate coverage
./scripts/tests/run-integration-tests.sh # Integration tests only
```

Or use Make:

```bash
make test              # Run all tests
make test-unit        # Unit tests
make test-integration # Integration tests
make test-cov         # With coverage
```

## 📝 Other Scripts

### git-commit.sh

Helper for committing changes:

```bash
./scripts/git-commit.sh
```

Guides you through:
- Reviewing changes
- Staging files
- Creating commit with proper message
- Suggestions for next steps

## 🔧 Using Scripts

### Make Everything Executable

```bash
chmod +x scripts/*.sh
chmod +x scripts/tests/*.sh
```

### Run from Project Root

All scripts assume you're in the project root:

```bash
cd /path/to/aiconexus
./scripts/gateway-docker.sh build
```

### Or Use Make

The Makefile provides convenient targets:

```bash
make gateway-build
make gateway-start
make gateway-test
make test
```

## 📊 Script Statistics

| Script | Lines | Purpose |
|--------|-------|---------|
| gateway-docker.sh | 320 | Docker lifecycle |
| verify-docker-setup.sh | 60 | Verify setup |
| quickstart.sh | 120 | Interactive setup |
| git-commit.sh | 150 | Git helper |

## 🎯 Quick Reference

**First time setup:**
```bash
./scripts/quickstart.sh
./scripts/verify-docker-setup.sh
```

**Development:**
```bash
./scripts/gateway-docker.sh start
make test
./scripts/gateway-docker.sh stop
```

**Testing:**
```bash
./scripts/tests/run-all-tests.sh
./scripts/tests/run-coverage.sh
```

**Deployment:**
```bash
./scripts/gateway-docker.sh build
./scripts/gateway-docker.sh start
```

## 🔍 Script Breakdown

Each script has:
- Color-coded output
- Error handling
- Help messages
- Clear feedback

## 📞 Help

Most scripts have built-in help:

```bash
./scripts/gateway-docker.sh help
./scripts/quickstart.sh
./scripts/verify-docker-setup.sh
```

---

**Last Updated:** 2026-01-12
**Status:** All scripts functional and tested

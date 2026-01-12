# AIConexus Documentation Index

Quick reference to all documentation files in the AIConexus project.

## 🎯 Start Here

**New to AIConexus?**
→ Start with [README.md](./README.md)

**Want to use the SDK?**
→ Read [SDK_USAGE.md](./SDK_USAGE.md)

**Deploying the gateway?**
→ Follow [DOCKER_GATEWAY.md](./DOCKER_GATEWAY.md)

**Contributing code?**
→ Check [CONTRIBUTING.md](./CONTRIBUTING.md)

---

## 📚 Documentation Files

### Core Documentation

| File | Purpose | Audience | Length |
|------|---------|----------|--------|
| [README.md](./README.md) | Project overview, features, quick start | Everyone | 617 lines |
| [ARCHITECTURE.md](./ARCHITECTURE.md) | System design and component overview | Architects/Developers | 200+ lines |
| [PROTOCOL_DESIGN.md](./PROTOCOL_DESIGN.md) | Message protocol specification | Developers | 300+ lines |

### Deployment & Operations

| File | Purpose | Audience | Length |
|------|---------|----------|--------|
| [DOCKER_GATEWAY.md](./DOCKER_GATEWAY.md) | Gateway Docker deployment guide | DevOps/Operators | 450+ lines |
| [SDK_USAGE.md](./SDK_USAGE.md) | SDK installation and usage guide | Developers | 500+ lines |

### Development

| File | Purpose | Audience | Length |
|------|---------|----------|--------|
| [CONTRIBUTING.md](./CONTRIBUTING.md) | Contribution guidelines | Contributors | 200+ lines |
| [PROJECT_STRUCTURE.md](./PROJECT_STRUCTURE.md) | Directory structure explanation | Developers | 400+ lines |

### Sprint & Release Information

| File | Purpose | Audience | Length |
|------|---------|----------|--------|
| [SPRINT5_SUMMARY.md](./SPRINT5_SUMMARY.md) | Sprint 5 completion summary | Everyone | 600+ lines |
| [COMMIT_GUIDE.md](./COMMIT_GUIDE.md) | Git commit documentation | DevOps/Git users | 350+ lines |
| [PROJECT_STATUS_FINAL.md](./PROJECT_STATUS_FINAL.md) | Overall project status | Everyone | 200+ lines |

---

## 🛠️ Quick References

### For SDK Users

```bash
# Installation
pip install aiconexus-sdk

# Quick example
python -c "
from aiconexus import Agent, GatewayClient
import asyncio

async def main():
    gateway = GatewayClient(
        gateway_url='ws://127.0.0.1:8000/ws',
        did_key='your-did-key'
    )
    await gateway.connect()
    agent = Agent('MyAgent', gateway)
    print('Agent created!')

asyncio.run(main())
"
```

**Full guide**: [SDK_USAGE.md](./SDK_USAGE.md)

### For Gateway Operators

```bash
# Verify setup
./verify_docker_setup.sh

# Build
./gateway-docker.sh build

# Start
./gateway-docker.sh start

# Check status
./gateway-docker.sh status

# View logs
./gateway-docker.sh logs -f

# Stop
./gateway-docker.sh stop
```

**Full guide**: [DOCKER_GATEWAY.md](./DOCKER_GATEWAY.md)

### For Developers

```bash
# Setup
poetry install
poetry run pytest tests/

# Start gateway
make gateway-start

# Run examples
poetry run python examples/simple_agent.py

# Stop gateway
make gateway-stop
```

**Full guide**: [CONTRIBUTING.md](./CONTRIBUTING.md)

---

## 📋 Documentation by Task

### I want to...

**...learn what AIConexus is**
→ [README.md](./README.md) (Overview section)

**...install the SDK**
→ [SDK_USAGE.md](./SDK_USAGE.md) (Installation section)

**...create my first agent**
→ [SDK_USAGE.md](./SDK_USAGE.md) (Quick Start section)

**...connect to a deployed gateway**
→ [SDK_USAGE.md](./SDK_USAGE.md) (Gateway Running Remotely section)

**...deploy the gateway**
→ [DOCKER_GATEWAY.md](./DOCKER_GATEWAY.md) (Quick Start section)

**...understand the system architecture**
→ [ARCHITECTURE.md](./ARCHITECTURE.md)

**...understand the protocol**
→ [PROTOCOL_DESIGN.md](./PROTOCOL_DESIGN.md)

**...contribute code**
→ [CONTRIBUTING.md](./CONTRIBUTING.md)

**...troubleshoot an issue**
→ [DOCKER_GATEWAY.md](./DOCKER_GATEWAY.md) (Troubleshooting section) or [SDK_USAGE.md](./SDK_USAGE.md) (Troubleshooting section)

**...see project progress**
→ [SPRINT5_SUMMARY.md](./SPRINT5_SUMMARY.md) or [PROJECT_STATUS_FINAL.md](./PROJECT_STATUS_FINAL.md)

---

## 🔧 Scripts Reference

All scripts are executable and located in the project root.

### Docker Management

**gateway-docker.sh** (320 lines)
```bash
./gateway-docker.sh build          # Build Docker image
./gateway-docker.sh start          # Start container
./gateway-docker.sh stop           # Stop container
./gateway-docker.sh restart        # Restart container
./gateway-docker.sh status         # Show status
./gateway-docker.sh logs           # View logs
./gateway-docker.sh logs -f        # Follow logs
./gateway-docker.sh cleanup        # Remove resources
./gateway-docker.sh shell          # Open shell
./gateway-docker.sh health         # Check health
./gateway-docker.sh help           # Show help
```

**Documentation**: [DOCKER_GATEWAY.md](./DOCKER_GATEWAY.md)

### Testing & Verification

**test_docker_gateway.sh** (440 lines)
- Comprehensive Docker deployment testing
- 9 test scenarios
- **Run with**: `./test_docker_gateway.sh`

**verify_docker_setup.sh** (60 lines)
- Quick setup verification
- Checks all required files
- **Run with**: `./verify_docker_setup.sh`

**quickstart.sh** (120 lines)
- Interactive setup script
- Checks requirements
- Installs dependencies
- Shows next steps
- **Run with**: `./quickstart.sh`

---

## 📖 Reading Order (Recommended)

### For New Users

1. [README.md](./README.md) - What is AIConexus?
2. [ARCHITECTURE.md](./ARCHITECTURE.md) - How does it work?
3. [SDK_USAGE.md](./SDK_USAGE.md) - How do I use it?

### For Operators

1. [README.md](./README.md) - Project overview
2. [DOCKER_GATEWAY.md](./DOCKER_GATEWAY.md) - How to deploy
3. [SPRINT5_SUMMARY.md](./SPRINT5_SUMMARY.md) - What changed

### For Contributors

1. [CONTRIBUTING.md](./CONTRIBUTING.md) - How to contribute
2. [ARCHITECTURE.md](./ARCHITECTURE.md) - System design
3. [PROJECT_STRUCTURE.md](./PROJECT_STRUCTURE.md) - Code organization
4. [PROTOCOL_DESIGN.md](./PROTOCOL_DESIGN.md) - Protocol details

### For Understanding Recent Changes

1. [SPRINT5_SUMMARY.md](./SPRINT5_SUMMARY.md) - Sprint 5 overview
2. [COMMIT_GUIDE.md](./COMMIT_GUIDE.md) - What changed
3. [DOCKER_GATEWAY.md](./DOCKER_GATEWAY.md) - New Docker support
4. [SDK_USAGE.md](./SDK_USAGE.md) - Updated SDK guide

---

## 🎓 Learning Paths

### Path 1: SDK User (2-3 hours)

1. Read: [README.md](./README.md) (15 min)
2. Read: [SDK_USAGE.md](./SDK_USAGE.md) (45 min)
3. Install: SDK locally (10 min)
4. Practice: Code examples (45 min)
5. Create: Your first agent (30 min)

**Result**: Ready to build agents!

### Path 2: Gateway Operator (1-2 hours)

1. Read: [README.md](./README.md) (15 min)
2. Read: [DOCKER_GATEWAY.md](./DOCKER_GATEWAY.md) (45 min)
3. Setup: Docker locally (15 min)
4. Deploy: Gateway container (15 min)
5. Test: Deployment (15 min)

**Result**: Gateway deployed and running!

### Path 3: Contributor (4-6 hours)

1. Read: [README.md](./README.md) (15 min)
2. Read: [ARCHITECTURE.md](./ARCHITECTURE.md) (30 min)
3. Read: [CONTRIBUTING.md](./CONTRIBUTING.md) (30 min)
4. Read: [PROTOCOL_DESIGN.md](./PROTOCOL_DESIGN.md) (30 min)
5. Setup: Development environment (20 min)
6. Practice: Run tests (15 min)
7. Practice: Make code changes (2-3 hours)

**Result**: Ready to contribute!

---

## 📞 Support & Resources

### Getting Help

- **General Questions**: See [README.md](./README.md) FAQ section
- **SDK Usage**: See [SDK_USAGE.md](./SDK_USAGE.md) Troubleshooting section
- **Deployment Issues**: See [DOCKER_GATEWAY.md](./DOCKER_GATEWAY.md) Troubleshooting section
- **Contributing**: See [CONTRIBUTING.md](./CONTRIBUTING.md)

### Quick Links

- **GitHub Issues**: [Report a bug](https://github.com/...)
- **Discussions**: [Ask a question](https://github.com/...)
- **Email**: [support@example.com](mailto:support@example.com)

---

## 🔗 File Interdependencies

```
README.md
├── ARCHITECTURE.md (referenced for system design)
├── SDK_USAGE.md (referenced for usage guide)
└── DOCKER_GATEWAY.md (referenced for deployment)

ARCHITECTURE.md
├── PROTOCOL_DESIGN.md (referenced for protocol details)
└── PROJECT_STRUCTURE.md (referenced for code organization)

SDK_USAGE.md
├── DOCKER_GATEWAY.md (referenced for gateway setup)
└── README.md (referenced for overview)

DOCKER_GATEWAY.md
├── .env.gateway.example (configuration template)
├── docker-compose.gateway.yml (Docker configuration)
└── gateway-docker.sh (deployment script)

CONTRIBUTING.md
├── PROJECT_STRUCTURE.md (referenced for code locations)
└── ARCHITECTURE.md (referenced for system design)

SPRINT5_SUMMARY.md
├── DOCKER_GATEWAY.md (new feature)
├── SDK_USAGE.md (new documentation)
└── COMMIT_GUIDE.md (version control info)
```

---

## 📊 Documentation Statistics

| Category | Files | Lines | Purpose |
|----------|-------|-------|---------|
| Core Docs | 3 | 1,000+ | Overview & design |
| Deployment | 2 | 900+ | Gateway & SDK setup |
| Development | 2 | 600+ | Contributing & structure |
| Sprint Info | 3 | 1,200+ | Progress & release |
| **TOTAL** | **10+** | **4,000+** | Complete guide |

---

## ✅ Verification Checklist

Make sure you have all documentation:

- [ ] README.md exists and is readable
- [ ] ARCHITECTURE.md exists and is readable
- [ ] PROTOCOL_DESIGN.md exists and is readable
- [ ] DOCKER_GATEWAY.md exists and is readable
- [ ] SDK_USAGE.md exists and is readable
- [ ] CONTRIBUTING.md exists and is readable
- [ ] PROJECT_STRUCTURE.md exists and is readable
- [ ] SPRINT5_SUMMARY.md exists and is readable
- [ ] COMMIT_GUIDE.md exists and is readable
- [ ] All shell scripts are executable

**Check with**: `./verify_docker_setup.sh`

---

## 🎯 Quick Decision Tree

```
START
  ↓
Are you a user/developer?
  ├─ YES → Read SDK_USAGE.md
  │         ↓
  │       Want to use remote gateway?
  │       └─ YES → Section: "Connect to Remote Gateway"
  │       └─ NO → Need to deploy gateway?
  │             └─ YES → Read DOCKER_GATEWAY.md
  │
  └─ NO: Are you an operator?
      ├─ YES → Read DOCKER_GATEWAY.md
      │
      └─ NO: Are you a contributor?
          └─ YES → Read CONTRIBUTING.md
```

---

## 📝 Version Information

- **Project**: AIConexus
- **Sprint**: 5 (Complete)
- **Status**: Production-Ready
- **Latest**: Docker Gateway Deployment
- **Python**: 3.13+
- **License**: [To be determined]

---

## 🎉 What's Next?

**Ready to get started?**

```bash
# Quick start for SDK users
./quickstart.sh
poetry run python examples/simple_agent.py

# Quick start for operators
./quickstart.sh
make gateway-build
make gateway-start
```

**Questions?** Check the documentation index above or search for your topic.

---

**Last Updated**: 2026-01-12
**Documentation Version**: 1.0
**Status**: Complete

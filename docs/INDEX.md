# 📚 AIConexus Documentation Index

Welcome to AIConexus! This index helps you navigate all project documentation.

## 🚀 Getting Started

**New to AIConexus?** Start here:
- [Quick Start Guide](QUICK_START.md) - Get up and running in 5 minutes
- [Project Structure](PROJECT_STRUCTURE.md) - Understand how the project is organized
- [Architecture Overview](ARCHITECTURE.md) - Learn the system design

## 📖 Documentation Categories

### 🏃 Quick References
- **[Project Status](PROJECT_STATUS.md)** - Current state and what's completed
- **[Reorganization Summary](PROJECT_REORGANIZED.md)** - How we restructured the project
- **[Reorganization Details](REORGANIZATION_COMPLETE.txt)** - Complete reorganization information

### 🛠️ Guides & Tutorials
- **[SDK Usage Guide](guides/SDK_USAGE.md)** - How to use the SDK
- **[Troubleshooting](guides/TROUBLESHOOTING.md)** - Common issues and solutions
- **[Frequently Asked Questions](guides/FAQ.md)** - Common questions answered

### 🐳 Deployment & Infrastructure
- **[Docker Setup](deployment/DOCKER.md)** - Docker and containerization
- **[Gateway Docker](deployment/DOCKER_GATEWAY.md)** - Gateway Docker deployment
- **[Kubernetes](deployment/KUBERNETES.md)** - Kubernetes deployment

### 🔌 API Reference
- **[Client API](api/CLIENT_API.md)** - Client SDK API documentation
- **[Agent API](api/AGENT_API.md)** - Agent API documentation
- **[Protocol Messages](api/PROTOCOL_MESSAGES.md)** - Message protocol specification

### 📋 Project Information
- **[Protocol Design](PROTOCOL_DESIGN.md)** - Protocol specification and design
- **[Roadmap](ROADMAP.md)** - Project roadmap and future plans
- **[Specifications](SPECIFICATIONS.md)** - Technical specifications

### 📊 Sprint Reports
- **[Sprint 1](sprints/SPRINT_1_REPORT.md)** - Initial setup and core functionality
- **[Sprint 2](sprints/SPRINT_2_REPORT.md)** - Feature development
- **[Sprint 3](sprints/SPRINT_3_REPORT.md)** - Integration work
- **[Sprint 4](sprints/SPRINT_4_REPORT.md)** - Testing and optimization
- **[Sprint 5](sprints/SPRINT_5_REPORT.md)** - Docker deployment and finalization

## 📁 Project Directory Structure

```
aiconexus/                    # Root
├── docs/                     # 📚 Documentation (you are here)
├── gateway/                  # 🐳 Gateway service
├── src/                      # 🐍 Source code
├── scripts/                  # 🛠️ Utility scripts
├── examples/                 # 💡 Code examples
├── tests/                    # 🧪 Test suite
├── config/                   # ⚙️ Configuration
│
├── README.md                 # Main project README
├── LICENSE                   # MIT License
├── CONTRIBUTING.md           # Contribution guidelines
├── pyproject.toml            # Python project config
├── poetry.lock               # Dependencies
└── Makefile                  # Build commands
```

## 🎯 By Use Case

### "I want to use AIConexus in my project"
1. Read: [QUICK_START.md](QUICK_START.md)
2. Read: [guides/SDK_USAGE.md](guides/SDK_USAGE.md)
3. Run: Examples in `/examples/agents/`

### "I want to deploy the gateway"
1. Read: [deployment/DOCKER.md](deployment/DOCKER.md)
2. Read: [deployment/DOCKER_GATEWAY.md](deployment/DOCKER_GATEWAY.md)
3. Run: `./scripts/gateway-docker.sh start`

### "I want to contribute to the project"
1. Read: [CONTRIBUTING.md](../CONTRIBUTING.md)
2. Read: [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)
3. Read: [ARCHITECTURE.md](ARCHITECTURE.md)

### "I need to understand how it works"
1. Read: [ARCHITECTURE.md](ARCHITECTURE.md)
2. Read: [PROTOCOL_DESIGN.md](PROTOCOL_DESIGN.md)
3. Read: [api/PROTOCOL_MESSAGES.md](api/PROTOCOL_MESSAGES.md)

### "I'm having problems"
1. Read: [guides/TROUBLESHOOTING.md](guides/TROUBLESHOOTING.md)
2. Read: [guides/FAQ.md](guides/FAQ.md)
3. Check: [deployment/](deployment/) for deployment issues

## 🔍 Finding What You Need

### By Topic
- **Getting Started** → [QUICK_START.md](QUICK_START.md)
- **How to Use** → [guides/SDK_USAGE.md](guides/SDK_USAGE.md)
- **How It Works** → [ARCHITECTURE.md](ARCHITECTURE.md)
- **Technical Details** → [api/](api/) or [PROTOCOL_DESIGN.md](PROTOCOL_DESIGN.md)
- **Deployment** → [deployment/](deployment/)
- **Troubleshooting** → [guides/TROUBLESHOOTING.md](guides/TROUBLESHOOTING.md)

### By Format
- **Markdown Docs** → [docs/](.) directory
- **Code Examples** → [../examples/](../examples/)
- **Scripts** → [../scripts/](../scripts/)
- **Tests** → [../tests/](../tests/)

## 📚 Documentation Files

### Main Documentation
| Document | Purpose |
|----------|---------|
| [QUICK_START.md](QUICK_START.md) | Get started in 5 minutes |
| [ARCHITECTURE.md](ARCHITECTURE.md) | System architecture overview |
| [PROTOCOL_DESIGN.md](PROTOCOL_DESIGN.md) | Protocol specification |
| [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) | Project organization |
| [SPECIFICATIONS.md](SPECIFICATIONS.md) | Technical specifications |
| [ROADMAP.md](ROADMAP.md) | Future plans |

### Deployment
| Document | Purpose |
|----------|---------|
| [deployment/DOCKER.md](deployment/DOCKER.md) | Docker basics |
| [deployment/DOCKER_GATEWAY.md](deployment/DOCKER_GATEWAY.md) | Gateway deployment |
| [deployment/KUBERNETES.md](deployment/KUBERNETES.md) | Kubernetes setup |

### Guides
| Document | Purpose |
|----------|---------|
| [guides/SDK_USAGE.md](guides/SDK_USAGE.md) | How to use the SDK |
| [guides/TROUBLESHOOTING.md](guides/TROUBLESHOOTING.md) | Problem solving |
| [guides/FAQ.md](guides/FAQ.md) | Common questions |

### API Reference
| Document | Purpose |
|----------|---------|
| [api/CLIENT_API.md](api/CLIENT_API.md) | Client API docs |
| [api/AGENT_API.md](api/AGENT_API.md) | Agent API docs |
| [api/PROTOCOL_MESSAGES.md](api/PROTOCOL_MESSAGES.md) | Message protocol |

## 🔗 External Resources

- **GitHub Repository** - [github.com/aiconexus](https://github.com/aiconexus)
- **PyPI Package** - [pypi.org/aiconexus](https://pypi.org/aiconexus)
- **Issue Tracker** - [GitHub Issues](https://github.com/aiconexus/issues)
- **Discussions** - [GitHub Discussions](https://github.com/aiconexus/discussions)

## 💡 Tips for Navigation

1. **Use Ctrl+F** - Search for keywords in the browser
2. **Follow Links** - Click links to navigate between docs
3. **Check Index First** - This file is your navigation hub
4. **Start with QUICK_START** - Best entry point for beginners
5. **Read ARCHITECTURE** - Best for understanding the system

## 📝 Documentation Status

- ✅ Getting Started - Complete
- ✅ API Documentation - Complete
- ✅ Deployment Guides - Complete
- ✅ Code Examples - Complete
- ✅ Architecture Docs - Complete
- ✅ Troubleshooting - Complete
- ✅ Sprint Reports - Complete (5 sprints)

## 🤝 Contributing to Docs

Found an issue or want to improve docs? Please:
1. Check [CONTRIBUTING.md](../CONTRIBUTING.md)
2. Create an issue or pull request
3. Follow the documentation style guide

## 📧 Support

- **Documentation Issues** - [GitHub Issues](https://github.com/aiconexus/issues)
- **Questions** - [GitHub Discussions](https://github.com/aiconexus/discussions)
- **Email** - contact@aiconexus.dev

---

**Last Updated:** January 12, 2026  
**Documentation Status:** ✅ Complete and Organized  
**Project Status:** ✅ 95% Open-Source Ready

Happy coding! 🚀

# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- GitHub Actions CI/CD pipeline
- Code quality checks (flake8, black, isort, mypy)
- Security scanning with bandit
- PyPI packaging configuration
- Release automation

### Changed
- Project structure reorganized for open-source
- Documentation improved and reorganized

### Fixed
- Minor bug fixes

## [1.0.0] - 2026-01-12

### Added
- Initial release of AIConexus
- Distributed agent system with IoAP v1 protocol
- WebSocket client for agent communication
- Central gateway for agent discovery and coordination
- DID-based security and message signing
- Comprehensive test suite (208 tests)
- Docker containerization support
- Prometheus metrics and monitoring
- Complete API documentation
- Learning path examples (5 levels)
- Professional documentation structure

### Features
- Agent discovery and registration
- Contract negotiation between agents
- Task execution and monitoring
- Error handling with exponential backoff retry
- WebRTC peer-to-peer communication
- Real-time health checks
- Load testing support
- Multiple deployment options (Docker, standalone)

### Infrastructure
- FastAPI-based gateway server
- Asynchronous task handling
- Structured logging system
- Configuration management
- Health endpoints and metrics
- Multi-stage Docker builds

[Unreleased]: https://github.com/aiconexus/aiconexus/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/aiconexus/aiconexus/releases/tag/v1.0.0

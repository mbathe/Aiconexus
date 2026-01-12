# ⚙️ Configuration Files

Environment and configuration files for AIConexus.

## 📁 Files

```
config/
├── README.md (this file)
├── .env.example              # Main environment template
└── .env.gateway.example      # Gateway environment template
```

## 🔧 Configuration Files

### .env.example

Main application environment variables:

```bash
# Copy to .env
cp config/.env.example .env
```

Variables:
```bash
# Logging
LOG_LEVEL=INFO

# Gateway connection (for SDK users)
GATEWAY_URL=ws://127.0.0.1:8000/ws
GATEWAY_TIMEOUT=30

# Python
PYTHONUNBUFFERED=1

# Development
ENVIRONMENT=development
# ENVIRONMENT=production
```

### .env.gateway.example

Gateway-specific environment variables:

```bash
# Copy to .env.gateway
cp config/.env.gateway.example .env.gateway
```

Variables:
```bash
# Logging
LOG_LEVEL=INFO
PYTHONUNBUFFERED=1

# Gateway configuration
GATEWAY_HOST=0.0.0.0
GATEWAY_PORT=8000
GATEWAY_SUBPROTOCOL=ioap.v1

# Agent management
AGENT_TIMEOUT=300              # seconds
CLEANUP_INTERVAL=60            # seconds

# Connection limits
MAX_CONNECTIONS=1000
CONNECTION_TIMEOUT=30

# Performance
WORKER_THREADS=4
BUFFER_SIZE=65536

# Security
VERIFY_SIGNATURES=true
VALIDATE_DIDS=true

# Monitoring
ENABLE_METRICS=true
METRICS_PORT=9090

# Storage (future)
STORAGE_TYPE=memory

# Deployment
ENVIRONMENT=development

# CORS (if needed)
ALLOW_ORIGINS=*
ALLOW_CREDENTIALS=true
ALLOW_METHODS=GET,POST,PUT,DELETE,OPTIONS
ALLOW_HEADERS=*
```

## 📖 How to Use

### For SDK Users

1. Copy template:
   ```bash
   cp config/.env.example .env
   ```

2. Edit as needed:
   ```bash
   nano .env
   ```

3. Set gateway URL if remote:
   ```bash
   GATEWAY_URL=wss://gateway.example.com/ws
   ```

4. Load in your code:
   ```python
   import os
   from dotenv import load_dotenv
   
   load_dotenv()
   gateway_url = os.getenv('GATEWAY_URL')
   ```

### For Gateway Operators

1. Copy template:
   ```bash
   cp config/.env.gateway.example .env.gateway
   ```

2. Customize for your deployment:
   ```bash
   nano .env.gateway
   ```

3. Load in Docker:
   ```bash
   # Option 1: Via docker-compose
   docker-compose --env-file config/.env.gateway up -d
   
   # Option 2: Via script
   export $(cat config/.env.gateway)
   python gateway/src/gateway_listen.py
   ```

## 🔐 Security

### Protecting Secrets

**Do NOT commit actual secrets to git!**

1. Keep templates with example values
2. Create `.env` with actual secrets (ignored by git)
3. Use `.gitignore` to exclude `.env*` files

### .gitignore

```
# Environment variables (secrets)
.env
.env.local
.env.*.local

# Configuration
config/.env
config/.env.*
!config/.env.example
!config/.env.gateway.example
```

### Safe Environment Variables

Good practices:

1. **Never hardcode secrets**
   ```python
   # ❌ Bad
   api_key = "my-secret-key"
   
   # ✅ Good
   api_key = os.getenv('API_KEY')
   ```

2. **Use environment files**
   ```bash
   # .env file (not in git)
   GATEWAY_URL=ws://127.0.0.1:8000/ws
   ```

3. **Vault systems for production**
   ```python
   # Use HashiCorp Vault, AWS Secrets Manager, etc.
   from vault import get_secret
   token = get_secret('gateway_token')
   ```

## 🚀 Deployment Configurations

### Development

```bash
# config/.env
ENVIRONMENT=development
LOG_LEVEL=DEBUG
GATEWAY_URL=ws://127.0.0.1:8000/ws
```

### Staging

```bash
# config/.env
ENVIRONMENT=staging
LOG_LEVEL=INFO
GATEWAY_URL=wss://staging-gateway.example.com/ws
```

### Production

```bash
# config/.env
ENVIRONMENT=production
LOG_LEVEL=WARNING
GATEWAY_URL=wss://gateway.example.com/ws
GATEWAY_TIMEOUT=60
```

## 📋 Configuration Options

### Logging Levels

- `DEBUG` - Detailed information (development)
- `INFO` - General information (default)
- `WARNING` - Warning messages (production)
- `ERROR` - Error messages
- `CRITICAL` - Critical errors

### Gateway Options

| Option | Default | Purpose |
|--------|---------|---------|
| GATEWAY_HOST | 0.0.0.0 | Bind address |
| GATEWAY_PORT | 8000 | WebSocket port |
| AGENT_TIMEOUT | 300 | Inactive agent timeout (s) |
| MAX_CONNECTIONS | 1000 | Max concurrent agents |
| WORKER_THREADS | 4 | Worker threads |

### Performance Tuning

```bash
# High throughput
WORKER_THREADS=8
BUFFER_SIZE=131072
MAX_CONNECTIONS=5000

# Low latency
WORKER_THREADS=2
BUFFER_SIZE=32768
MAX_CONNECTIONS=500

# Production
WORKER_THREADS=auto
BUFFER_SIZE=65536
MAX_CONNECTIONS=1000
```

## 🔄 Loading Configuration

### Python (dotenv)

```python
import os
from dotenv import load_dotenv

# Load from file
load_dotenv('config/.env')

# Access variables
gateway_url = os.getenv('GATEWAY_URL')
log_level = os.getenv('LOG_LEVEL', 'INFO')
```

### Docker

```bash
# docker-compose.yml
env_file:
  - config/.env.gateway
```

### Shell Scripts

```bash
# Load variables
export $(cat config/.env.gateway | xargs)

# Use variables
echo $GATEWAY_PORT
```

## 📝 Creating New Configurations

1. Start with a template:
   ```bash
   cp config/.env.example config/.env.custom
   ```

2. Modify as needed:
   ```bash
   nano config/.env.custom
   ```

3. Use in your code:
   ```python
   from dotenv import load_dotenv
   load_dotenv('config/.env.custom')
   ```

## ✅ Configuration Checklist

Before deploying:

- [ ] Copy template file
- [ ] Customize values
- [ ] Never commit secrets
- [ ] Test configuration
- [ ] Document custom settings
- [ ] Back up production config

## 🔍 Troubleshooting

### Configuration Not Loading

```python
# Debug: print what's loaded
import os
from dotenv import load_dotenv

load_dotenv('config/.env')
for key, value in os.environ.items():
    if key.startswith('GATEWAY'):
        print(f"{key}={value}")
```

### Wrong Values

Check file location:
```bash
ls -la config/.env
cat config/.env  # Verify content
```

### Variable Not Found

Ensure you're loading the right file:
```python
# Check if file exists
import os
if os.path.exists('config/.env'):
    load_dotenv('config/.env')
else:
    print("Config file not found!")
```

## 📚 Related Documentation

- [SDK Usage Guide](../docs/guides/SDK_USAGE.md) - SDK configuration
- [Docker Deployment](../docs/deployment/DOCKER_GATEWAY.md) - Docker configuration
- [Gateway Admin](../docs/guides/GATEWAY_ADMIN.md) - Gateway configuration

## 🔗 External Resources

- [python-dotenv](https://python-dotenv.readthedocs.io/) - Load env files
- [12 Factor App](https://12factor.net/) - Configuration best practices
- [Environment Variables](https://en.wikipedia.org/wiki/Environment_variable) - Overview

---

**Last Updated:** 2026-01-12
**Status:** Complete and ready to use

# AIConexus SDK - Production Deployment Guide

## Overview

This guide covers deploying the AIConexus SDK in production environments, from local development to cloud-based multi-agent systems.

---

## Prerequisites

- Python 3.10+
- Docker (for containerized deployment)
- PostgreSQL 13+ (for persistent registry)
- Redis (optional, for caching)
- At least one LLM endpoint (OpenAI, Anthropic, local)

---

## Phase 1: Local Development Deployment

### Step 1: Environment Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -e .  # Install SDK in development mode

# Create .env file
cat > .env << EOF
# LLM Configuration
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4

# SDK Configuration
AICONEXUS_LOG_LEVEL=INFO
AICONEXUS_MAX_ITERATIONS=10
AICONEXUS_TIMEOUT_MS=30000

# Database (optional)
DATABASE_URL=postgresql://user:password@localhost:5432/aiconexus

# Redis (optional)
REDIS_URL=redis://localhost:6379
EOF

# Load environment
export $(cat .env | xargs)
```

### Step 2: Verify Installation

```bash
# Run verification script
python -c "
from src.aiconexus.sdk import SDKAgent, ExpertiseArea
print('✅ SDK imported successfully')
print('✅ Ready for development')
"

# Run basic test
python examples/basic_agent.py
```

### Step 3: Local Testing

```bash
# Run unit tests
pytest tests/sdk/ -v --cov=src/aiconexus/sdk

# Expected output:
# ===================== 14 passed in 2.34s =====================

# Run integration tests
pytest tests/integration/ -v

# Run performance tests
pytest tests/performance/ -v
```

---

## Phase 2: Containerized Deployment

### Step 1: Create Dockerfile

```dockerfile
# Dockerfile
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Install SDK
RUN pip install -e .

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "from src.aiconexus.sdk import SDKAgent; print('OK')"

# Default command
CMD ["python", "-m", "uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Step 2: Create docker-compose.yml

```yaml
version: '3.9'

services:
  # Main SDK service
  sdk:
    build: .
    ports:
      - "8000:8000"
    environment:
      OPENAI_API_KEY: ${OPENAI_API_KEY}
      OPENAI_MODEL: gpt-4
      DATABASE_URL: postgresql://aiconexus:password@postgres:5432/aiconexus
      REDIS_URL: redis://redis:6379
      LOG_LEVEL: INFO
    depends_on:
      - postgres
      - redis
    networks:
      - aiconexus-net
    restart: on-failure
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  # PostgreSQL for persistent registry
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: aiconexus
      POSTGRES_USER: aiconexus
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./scripts/init_db.sql:/docker-entrypoint-initdb.d/init.sql
    networks:
      - aiconexus-net
    restart: unless-stopped

  # Redis for caching
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    networks:
      - aiconexus-net
    restart: unless-stopped

  # Monitoring (Prometheus)
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./config/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    networks:
      - aiconexus-net
    restart: unless-stopped

  # Visualization (Grafana)
  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      GF_SECURITY_ADMIN_PASSWORD: admin
    volumes:
      - grafana_data:/var/lib/grafana
    networks:
      - aiconexus-net
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
  prometheus_data:
  grafana_data:

networks:
  aiconexus-net:
    driver: bridge
```

### Step 3: Build and Run

```bash
# Build images
docker-compose build

# Start services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f sdk

# Stop services
docker-compose down

# Cleanup
docker-compose down -v  # Remove volumes too
```

---

## Phase 3: Cloud Deployment (AWS)

### Step 1: Prepare for AWS

```bash
# Create ECR repository
aws ecr create-repository --repository-name aiconexus-sdk --region us-east-1

# Login to ECR
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin \
  123456789.dkr.ecr.us-east-1.amazonaws.com

# Tag image
docker tag aiconexus-sdk:latest \
  123456789.dkr.ecr.us-east-1.amazonaws.com/aiconexus-sdk:latest

# Push to ECR
docker push 123456789.dkr.ecr.us-east-1.amazonaws.com/aiconexus-sdk:latest
```

### Step 2: Create CloudFormation Template

```yaml
# cloudformation/stack.yml
AWSTemplateFormatVersion: '2010-09-09'
Description: 'AIConexus SDK Stack'

Parameters:
  ImageUri:
    Type: String
    Description: ECR image URI
  
  DBPassword:
    Type: String
    NoEcho: true
    Description: RDS database password

Resources:
  # RDS PostgreSQL
  AiconexusDB:
    Type: AWS::RDS::DBInstance
    Properties:
      DBInstanceClass: db.t3.micro
      Engine: postgres
      MasterUsername: aiconexus
      MasterUserPassword: !Ref DBPassword
      AllocatedStorage: '20'
      StorageType: gp3
      VPCSecurityGroups:
        - !Ref DBSecurityGroup

  # ElastiCache Redis
  AiconexusCache:
    Type: AWS::ElastiCache::CacheCluster
    Properties:
      CacheNodeType: cache.t3.micro
      Engine: redis
      NumCacheNodes: 1
      VpcSecurityGroupIds:
        - !Ref CacheSecurityGroup

  # ECS Cluster
  AiconexusCluster:
    Type: AWS::ECS::Cluster
    Properties:
      ClusterName: aiconexus-cluster
      ClusterSettings:
        - Name: containerInsights
          Value: enabled

  # Task Definition
  AiconexusTask:
    Type: AWS::ECS::TaskDefinition
    Properties:
      Family: aiconexus-sdk
      NetworkMode: awsvpc
      RequiresCompatibilities:
        - FARGATE
      Cpu: '256'
      Memory: '512'
      ExecutionRoleArn: !GetAtt TaskExecutionRole.Arn
      TaskRoleArn: !GetAtt TaskRole.Arn
      ContainerDefinitions:
        - Name: sdk
          Image: !Ref ImageUri
          PortMappings:
            - ContainerPort: 8000
              Protocol: tcp
          Environment:
            - Name: DATABASE_URL
              Value: !Sub |
                postgresql://aiconexus:${DBPassword}@${AiconexusDB.Endpoint.Address}:5432/aiconexus
            - Name: REDIS_URL
              Value: !Sub |
                redis://${AiconexusCache.RedisEndpoint.Address}:6379
            - Name: LOG_LEVEL
              Value: INFO
          LogConfiguration:
            LogDriver: awslogs
            Options:
              awslogs-group: !Ref LogGroup
              awslogs-region: !Ref AWS::Region
              awslogs-stream-prefix: ecs

  # ECS Service
  AiconexusService:
    Type: AWS::ECS::Service
    DependsOn: LoadBalancerListener
    Properties:
      Cluster: !Ref AiconexusCluster
      TaskDefinition: !Ref AiconexusTask
      DesiredCount: 2
      LaunchType: FARGATE
      NetworkConfiguration:
        AwsvpcConfiguration:
          AssignPublicIp: ENABLED
          Subnets:
            - !Ref PublicSubnet1
            - !Ref PublicSubnet2
          SecurityGroups:
            - !Ref ContainerSecurityGroup
      LoadBalancers:
        - ContainerName: sdk
          ContainerPort: 8000
          TargetGroupArn: !Ref TargetGroup

  # CloudWatch Log Group
  LogGroup:
    Type: AWS::Logs::LogGroup
    Properties:
      LogGroupName: /ecs/aiconexus-sdk
      RetentionInDays: 7

Outputs:
  LoadBalancerURL:
    Description: Load balancer URL
    Value: !GetAtt LoadBalancer.DNSName
  
  DatabaseEndpoint:
    Description: RDS endpoint
    Value: !GetAtt AiconexusDB.Endpoint.Address
  
  RedisEndpoint:
    Description: Redis endpoint
    Value: !GetAtt AiconexusCache.RedisEndpoint.Address
```

### Step 3: Deploy to AWS

```bash
# Validate template
aws cloudformation validate-template \
  --template-body file://cloudformation/stack.yml

# Create stack
aws cloudformation create-stack \
  --stack-name aiconexus-prod \
  --template-body file://cloudformation/stack.yml \
  --parameters \
    ParameterKey=ImageUri,ParameterValue=123456789.dkr.ecr.us-east-1.amazonaws.com/aiconexus-sdk:latest \
    ParameterKey=DBPassword,ParameterValue=YourSecurePassword123! \
  --region us-east-1

# Monitor stack creation
aws cloudformation describe-stacks \
  --stack-name aiconexus-prod \
  --region us-east-1

# Get outputs
aws cloudformation describe-stacks \
  --stack-name aiconexus-prod \
  --query 'Stacks[0].Outputs' \
  --region us-east-1
```

---

## Phase 4: Production Configuration

### Step 1: Environment Variables

```bash
# Production .env
cat > .env.production << EOF
# LLM Configuration (Use production API keys!)
OPENAI_API_KEY=${PRODUCTION_OPENAI_KEY}
OPENAI_MODEL=gpt-4

# Database
DATABASE_URL=postgresql://user:pass@prod-db.example.com/aiconexus
DATABASE_POOL_SIZE=10
DATABASE_POOL_RECYCLE=3600

# Redis (for caching)
REDIS_URL=redis://prod-redis.example.com:6379
REDIS_DB=0
REDIS_PASSWORD=${REDIS_PASSWORD}

# SDK Configuration
AICONEXUS_LOG_LEVEL=WARNING  # Less verbose in production
AICONEXUS_MAX_ITERATIONS=10
AICONEXUS_TIMEOUT_MS=30000
AICONEXUS_REGISTRY_STRATEGY=semantic
AICONEXUS_ENABLE_CACHING=true

# Monitoring
SENTRY_DSN=https://examplePublicKey@o0.ingest.sentry.io/0
PROMETHEUS_ENABLED=true
JAEGER_ENABLED=true
JAEGER_AGENT_HOST=prod-jaeger.example.com
JAEGER_AGENT_PORT=6831

# Security
SSL_VERIFY=true
API_KEY_SECRET=${API_KEY_SECRET}
ENABLE_RATE_LIMITING=true
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_PERIOD=60

# Backup
BACKUP_ENABLED=true
BACKUP_SCHEDULE="0 2 * * *"  # 2 AM daily
BACKUP_RETENTION_DAYS=30
EOF
```

### Step 2: Database Migration

```bash
# Create initialization script
cat > scripts/init_db.sql << EOF
-- Initialize database
CREATE DATABASE aiconexus;

-- Connect to database
\c aiconexus

-- Create tables for persistent registry
CREATE TABLE agents (
    id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    endpoint VARCHAR(255) NOT NULL,
    status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE agent_expertise (
    agent_id UUID REFERENCES agents(id),
    domain VARCHAR(255),
    level VARCHAR(50),
    PRIMARY KEY (agent_id, domain)
);

-- Create indexes
CREATE INDEX idx_agents_status ON agents(status);
CREATE INDEX idx_expertise_domain ON agent_expertise(domain);

-- Create audit log
CREATE TABLE audit_log (
    id SERIAL PRIMARY KEY,
    agent_id UUID REFERENCES agents(id),
    action VARCHAR(255),
    details JSONB,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_audit_agent ON audit_log(agent_id);
CREATE INDEX idx_audit_timestamp ON audit_log(timestamp);
EOF

# Run migration
psql -U aiconexus -d aiconexus -f scripts/init_db.sql
```

### Step 3: Monitoring Setup

**Prometheus configuration:**
```yaml
# config/prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'aiconexus-sdk'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/metrics'
    scrape_interval: 5s
```

**Grafana dashboard:**
```json
{
  "dashboard": {
    "title": "AIConexus SDK Metrics",
    "panels": [
      {
        "title": "Request Latency",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, http_request_duration_seconds_bucket)"
          }
        ]
      },
      {
        "title": "Error Rate",
        "targets": [
          {
            "expr": "rate(http_requests_failed_total[5m])"
          }
        ]
      },
      {
        "title": "Tool Execution Time",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, tool_execution_duration_seconds_bucket)"
          }
        ]
      }
    ]
  }
}
```

---

## Phase 5: Security Hardening

### Step 1: API Key Management

```python
# config/security.py
import os
from cryptography.fernet import Fernet

class SecretManager:
    def __init__(self):
        self.cipher = Fernet(os.getenv('ENCRYPTION_KEY').encode())
    
    def encrypt_api_key(self, api_key: str) -> str:
        return self.cipher.encrypt(api_key.encode()).decode()
    
    def decrypt_api_key(self, encrypted_key: str) -> str:
        return self.cipher.decrypt(encrypted_key.encode()).decode()

# Usage
secret_mgr = SecretManager()
encrypted = secret_mgr.encrypt_api_key("sk-...")
decrypted = secret_mgr.decrypt_api_key(encrypted)
```

### Step 2: Rate Limiting

```python
# middleware/rate_limiting.py
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/agents/execute")
@limiter.limit("100/minute")
async def execute_agent(request):
    # Limit to 100 requests per minute per IP
    pass
```

### Step 3: HTTPS/TLS

```python
# In docker-compose or AWS CloudFormation
# Use SSL certificates from AWS Certificate Manager

# For local testing:
# openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365

# Run with SSL:
# python -m uvicorn api.main:app --ssl-keyfile=key.pem --ssl-certfile=cert.pem
```

### Step 4: Input Validation

```python
# middleware/validation.py
from pydantic import BaseModel, validator

class AgentExecuteRequest(BaseModel):
    task: str
    max_iterations: int = 10
    timeout_ms: int = 30000
    
    @validator('task')
    def task_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Task cannot be empty')
        return v
    
    @validator('max_iterations')
    def max_iterations_range(cls, v):
        if v < 1 or v > 100:
            raise ValueError('Max iterations must be 1-100')
        return v
```

---

## Phase 6: Monitoring & Alerts

### Step 1: Application Metrics

```python
# monitoring/metrics.py
from prometheus_client import Counter, Histogram, Gauge
import time

# Counters
requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

errors_total = Counter(
    'http_errors_total',
    'Total errors',
    ['type']
)

# Histograms
request_duration = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration',
    ['method', 'endpoint']
)

tool_duration = Histogram(
    'tool_execution_duration_seconds',
    'Tool execution duration',
    ['tool_name']
)

# Gauges
active_agents = Gauge(
    'active_agents',
    'Number of active agents'
)
```

### Step 2: Alerting Rules

```yaml
# config/alerts.yml
groups:
  - name: aiconexus
    interval: 30s
    rules:
      # High error rate
      - alert: HighErrorRate
        expr: rate(http_errors_total[5m]) > 0.1
        for: 5m
        annotations:
          summary: "High error rate detected"
      
      # High latency
      - alert: HighLatency
        expr: histogram_quantile(0.95, http_request_duration_seconds_bucket) > 10
        for: 5m
        annotations:
          summary: "P95 latency exceeds 10 seconds"
      
      # Database down
      - alert: DatabaseDown
        expr: up{job="postgresql"} == 0
        for: 1m
        annotations:
          summary: "PostgreSQL is down"
      
      # Redis down
      - alert: RedisDown
        expr: up{job="redis"} == 0
        for: 1m
        annotations:
          summary: "Redis is down"
```

---

## Phase 7: Maintenance & Scaling

### Step 1: Auto-Scaling

```yaml
# AWS ECS auto-scaling policy
AWSTemplateFormatVersion: '2010-09-09'

Resources:
  ServiceScalingTarget:
    Type: AWS::ApplicationAutoScaling::ScalableTarget
    Properties:
      MaxCapacity: 10
      MinCapacity: 2
      ResourceId: service/aiconexus-cluster/aiconexus-service
      RoleARN: !GetAtt AutoScalingRole.Arn
      ScalableDimension: ecs:service:DesiredCount
      ServiceNamespace: ecs

  CPUScalingPolicy:
    Type: AWS::ApplicationAutoScaling::ScalingPolicy
    Properties:
      PolicyName: cpu-scaling
      PolicyType: TargetTrackingScaling
      ScalingTargetId: !Ref ServiceScalingTarget
      TargetTrackingScalingPolicyConfiguration:
        TargetValue: 70.0
        PredefinedMetricSpecification:
          PredefinedMetricType: ECSServiceAverageCPUUtilization
```

### Step 2: Backup & Recovery

```bash
#!/bin/bash
# scripts/backup.sh

# Backup PostgreSQL
pg_dump -U aiconexus aiconexus | gzip > backups/db-$(date +%Y%m%d).sql.gz

# Backup Redis
redis-cli BGSAVE

# Upload to S3
aws s3 cp backups/ s3://aiconexus-backups/ --recursive

# Cleanup old backups (keep 30 days)
find backups/ -mtime +30 -delete
```

### Step 3: Health Checks

```python
# api/health.py
from fastapi import APIRouter
import asyncio

router = APIRouter()

@router.get("/health")
async def health_check():
    """Basic health check"""
    return {"status": "ok"}

@router.get("/health/detailed")
async def detailed_health_check():
    """Detailed health check with component status"""
    
    checks = {
        "database": await check_database(),
        "redis": await check_redis(),
        "llm": await check_llm(),
        "registry": await check_registry(),
    }
    
    overall = "healthy" if all(checks.values()) else "degraded"
    
    return {
        "status": overall,
        "checks": checks,
        "timestamp": datetime.now().isoformat()
    }

async def check_database():
    try:
        # Try to connect to database
        async with get_db() as db:
            await db.execute("SELECT 1")
        return True
    except:
        return False

async def check_redis():
    try:
        redis = await get_redis()
        await redis.ping()
        return True
    except:
        return False
```

---

## Troubleshooting

### Issue: High Memory Usage

```bash
# Check memory
docker stats

# Solution: Reduce cache size or enable Redis
# Update environment: REDIS_URL=redis://host:6379
```

### Issue: Database Connection Errors

```bash
# Check database
psql -U aiconexus -h db-host -c "SELECT 1"

# Increase connection pool
DATABASE_POOL_SIZE=20

# Check logs
docker logs aiconexus-sdk
```

### Issue: Slow Tool Execution

```bash
# Profile tool execution
python -m cProfile -s cumulative api/main.py

# Optimize tools or add caching
AICONEXUS_ENABLE_CACHING=true
REDIS_URL=redis://host:6379
```

---

## Deployment Checklist

- [ ] Code review completed
- [ ] All tests passing (>90% coverage)
- [ ] Performance benchmarks met
- [ ] Security audit completed
- [ ] Database migrations tested
- [ ] Environment variables configured
- [ ] Backups configured
- [ ] Monitoring/alerting setup
- [ ] Load balancer configured
- [ ] SSL certificates installed
- [ ] Rate limiting enabled
- [ ] Documentation updated
- [ ] Team trained on deployment

---

**Version**: 1.0  
**Last Updated**: January 2026  
**Status**: Production-Ready

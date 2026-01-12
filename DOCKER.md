# Docker Setup for AIConexus

This directory contains Docker configurations for running AIConexus in different environments.

## Files

- **Dockerfile**: Multi-stage Docker image with development, testing, and production targets
- **docker-compose.yml**: Orchestrates containers for different environments and optional monitoring
- **prometheus.yml**: Prometheus configuration for metrics collection
- **.dockerignore**: Excludes unnecessary files from Docker builds

## Quick Start

### Development

Run tests in a container with live code updates:

```bash
docker-compose -f docker-compose.yml --profile dev up dev
```

### Testing

Run the full test suite:

```bash
docker-compose -f docker-compose.yml --profile test up test
```

### Load Testing

Run load tests (100-500+ concurrent connections):

```bash
docker-compose -f docker-compose.yml --profile load-test up load-test
```

### Production

Run the application in production mode:

```bash
docker-compose -f docker-compose.yml --profile production up -d app
```

### With Monitoring

Start with Prometheus and Grafana:

```bash
docker-compose -f docker-compose.yml --profile production --profile monitoring up -d
```

Then access:
- **Grafana**: http://localhost:3000 (admin/admin)
- **Prometheus**: http://localhost:9090

## Build Targets

### Development
- Installs all dependencies including dev packages
- Mounts local code for live updates
- Runs pytest by default
- Useful for development and debugging

### Testing
- Installs test dependencies
- Runs complete test suite with coverage
- Useful for CI/CD pipelines

### Production
- Only production dependencies
- Non-root user for security
- Health checks enabled
- Minimal image size
- Optimized for deployment

## Environment Variables

- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)
- `HOST`: Server host (default: 0.0.0.0)
- `PORT`: Server port (default: 8000)
- `PYTHONUNBUFFERED`: Disable Python output buffering

## Health Checks

The production container includes health checks that verify:
- HTTP endpoint responsiveness
- Interval: 30 seconds
- Timeout: 3 seconds
- Retries: 3

## Network

All services use the `aiconexus-network` bridge network for communication.

## Volumes

- **prometheus_data**: Persistent storage for Prometheus metrics
- **grafana_data**: Persistent storage for Grafana configuration

## Building Images

Build a specific target:

```bash
docker build --target production -t aiconexus:prod .
docker build --target testing -t aiconexus:test .
docker build --target development -t aiconexus:dev .
```

## Cleanup

Remove all containers and volumes:

```bash
docker-compose down -v
```

Remove unused images:

```bash
docker image prune -a
```

## Performance Considerations

- Use `.dockerignore` to exclude unnecessary files
- Multi-stage builds reduce final image size
- Production image is optimized for minimal footprint
- Development image includes full debugging capabilities

## Security

- Production uses non-root user (UID 1000)
- No hardcoded credentials
- Use environment variables for configuration
- Consider using secrets management for production deployments

## Troubleshooting

### Container won't start
Check logs: `docker-compose logs [service-name]`

### Permission denied
Ensure Docker daemon is running and user has permissions:
```bash
sudo usermod -aG docker $USER
```

### Network issues
Verify network exists:
```bash
docker network ls | grep aiconexus
```

## Further Documentation

See main README.md for project information and setup instructions.

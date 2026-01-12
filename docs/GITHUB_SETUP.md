# GitHub Setup Documentation

Complete setup for GitHub Actions CI/CD and professional open-source infrastructure.

## What Has Been Set Up

### CI/CD Pipelines

#### 1. Tests Workflow (.github/workflows/tests.yml)
- Runs on every push to main/develop and pull requests
- Tests on Python 3.9 through 3.13
- Runs unit tests, integration tests, and load tests
- Generates code coverage reports
- Uploads to codecov.io

#### 2. Code Quality Workflow (.github/workflows/quality.yml)
- Code formatting check (black)
- Import sorting check (isort)
- Linting (flake8)
- Type checking (mypy)
- Security scanning (bandit)

#### 3. Release Workflow (.github/workflows/release.yml)
- Triggered on git tag (vX.Y.Z)
- Builds distribution packages
- Publishes to PyPI
- Creates GitHub Release

### Configuration Files

#### Code Quality Configuration
- `.pre-commit-config.yaml` - Pre-commit hooks configuration
- `setup.cfg` - Setuptools and tool configuration
- `.bandit` - Security scanning configuration
- Quality section in pyproject.toml

#### Issue and PR Templates
- `.github/ISSUE_TEMPLATE/bug_report.md` - Bug report template
- `.github/ISSUE_TEMPLATE/feature_request.md` - Feature request template
- `.github/PULL_REQUEST_TEMPLATE.md` - Pull request template

### Documentation

- `CHANGELOG.md` - Version history and changes
- `SECURITY.md` - Security policy and vulnerability reporting
- `CODE_OF_CONDUCT.md` - Community guidelines
- `DEVELOPMENT.md` - Developer setup and workflow
- `RELEASE.md` - Release process documentation

### Status Badges

Added to README.md:
- Python version badge
- License badge
- Code style badge
- Tests workflow badge
- Code quality badge
- Codecov coverage badge

## Next Steps to Enable

### 1. Connect to Codecov

```bash
# Codecov will auto-detect from GitHub Actions
# No setup needed - it reads codecov.yml
```

### 2. PyPI Setup

```bash
# Create account at https://pypi.org/
# Create API token
# Add to GitHub Secrets as PYPI_API_TOKEN
```

### 3. Test the Workflows

```bash
# Commit changes
git add .
git commit -m "ci: add github actions and open-source infrastructure"
git push origin main

# Watch workflows run at:
# https://github.com/aiconexus/aiconexus/actions
```

### 4. Enable Branch Protection Rules

In GitHub Settings:
1. Go to Settings > Branches
2. Add rule for main branch
3. Require status checks to pass before merging
4. Select: Tests, Code Quality workflows

### 5. Add Dependabot

In GitHub Settings:
1. Go to Security & analysis
2. Enable Dependabot
3. Set up automatic dependency updates

## Files Created/Modified

### New Files
```
.github/
  workflows/
    tests.yml          - Main test pipeline
    quality.yml        - Code quality checks
    release.yml        - Automated releases
  ISSUE_TEMPLATE/
    bug_report.md      - Bug report template
    feature_request.md - Feature request template
  PULL_REQUEST_TEMPLATE.md - PR template

Root Files:
  CHANGELOG.md         - Version history
  SECURITY.md          - Security policy
  CODE_OF_CONDUCT.md   - Community guidelines
  DEVELOPMENT.md       - Developer guide
  RELEASE.md           - Release process
  .pre-commit-config.yaml - Pre-commit hooks
  .bandit             - Security configuration
  setup.cfg           - Tool configuration
```

## Running Locally

### Pre-commit Hooks

```bash
# Install
pip install pre-commit
pre-commit install

# Run manually
pre-commit run --all-files
```

### Tests Locally

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run all tests
pytest tests/ -v --cov=src

# Run by category
pytest tests/unit/ -v
pytest tests/integration/ -v
```

### Code Quality Checks

```bash
# Format with black
black src tests

# Sort imports
isort src tests

# Lint with flake8
flake8 src tests

# Type check
mypy src

# Security scan
bandit -r src
```

## Continuous Integration

### What Runs on Every Commit

1. **Tests**: Full test suite on Python 3.9-3.13
2. **Quality**: Code formatting, style, types, security
3. **Coverage**: Test coverage reporting to codecov
4. **Status Checks**: Required to pass before merging

### What Runs on Release

1. **Build**: Creates distribution packages
2. **Check**: Validates packages with twine
3. **Publish**: Uploads to PyPI (if token provided)
4. **Release**: Creates GitHub Release page

## Monitoring

### GitHub Actions Dashboard

https://github.com/aiconexus/aiconexus/actions

### Coverage Reports

https://codecov.io/gh/aiconexus/aiconexus

### PyPI Package

https://pypi.org/project/aiconexus/

## Troubleshooting

### Workflow Failures

1. Check the action run output
2. Look for specific error messages
3. Review logs in Actions tab
4. Common issues:
   - Python version mismatch
   - Missing dependencies
   - Environment variables not set

### PyPI Publishing Fails

- Verify PYPI_API_TOKEN in GitHub Secrets
- Check token permissions and expiration
- Ensure version is not already published
- Look at twine output in workflow logs

### Tests Failing in CI

- May pass locally but fail in CI
- Check for:
  - OS-specific issues (use ubuntu-latest)
  - Python version incompatibilities
  - Async timing issues
  - Missing test fixtures

## Security

### Secrets Management

Never commit:
- PyPI tokens
- API credentials
- Private keys

Use GitHub Secrets:
1. Settings > Secrets and variables > Actions
2. Add new repository secret
3. Use in workflows: ${{ secrets.SECRET_NAME }}

### Bandit Security Scanning

Scans for:
- SQL injection
- Insecure cryptography
- Hardcoded passwords
- Unsafe eval usage

Review bandit-report.json in workflow artifacts.

## Next Advanced Features

Future enhancements:
- Docker image building
- Automated documentation deployment
- Performance benchmarking
- Dependency updates with Dependabot
- Code coverage badges
- Release automation with conventional commits

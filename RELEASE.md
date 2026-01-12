# Release Process

This document describes how to release a new version of AIConexus.

## Pre-Release Checklist

- [ ] All tests pass locally
- [ ] All GitHub Actions workflows pass
- [ ] Code coverage is maintained or improved
- [ ] Documentation is up-to-date
- [ ] CHANGELOG.md is updated
- [ ] Version number is decided (semantic versioning)

## Release Steps

### 1. Update Version Number

Update the version in the following files:

```bash
# In src/aiconexus/__init__.py
__version__ = "X.Y.Z"

# In setup.cfg
version = X.Y.Z

# In pyproject.toml (if using Poetry)
version = "X.Y.Z"
```

### 2. Update CHANGELOG

Add a new section in CHANGELOG.md with:

```markdown
## [X.Y.Z] - YYYY-MM-DD

### Added
- New feature descriptions

### Changed
- Changed feature descriptions

### Fixed
- Bug fix descriptions

### Deprecated
- Deprecated feature descriptions

### Removed
- Removed feature descriptions

### Security
- Security fix descriptions
```

### 3. Create a Release Commit

```bash
git add .
git commit -m "release: bump version to X.Y.Z"
```

### 4. Create a Git Tag

```bash
git tag -a vX.Y.Z -m "Release version X.Y.Z"
```

### 5. Push Changes and Tag

```bash
git push origin main
git push origin vX.Y.Z
```

### 6. Automatic Release Creation

GitHub Actions will automatically:
- Build distribution packages
- Create a GitHub Release
- Publish to PyPI

### 7. Verify Release

- Check the GitHub Release page
- Verify the package on PyPI: https://pypi.org/project/aiconexus/
- Test installation: `pip install aiconexus==X.Y.Z`

## Semantic Versioning

Follow Semantic Versioning (MAJOR.MINOR.PATCH):

- **MAJOR**: Incompatible API changes
- **MINOR**: New functionality that is backward compatible
- **PATCH**: Backward compatible bug fixes

Examples:
- `1.0.0` - Initial release
- `1.1.0` - New features added
- `1.1.1` - Bug fix
- `2.0.0` - Breaking changes

## Version Branches

- Main branch (`main`): Latest stable release
- Develop branch (`develop`): Development branch for next release
- Feature branches: `feature/*`
- Bug fix branches: `fix/*`
- Release branches: `release/X.Y.Z`

## Documentation Release

Update documentation site after release:

1. Build documentation locally
2. Deploy to documentation site
3. Update version dropdown in docs

## Post-Release

- Announce release in discussions/announcements
- Update version in development branch
- Close related issues
- Plan next release

## Emergency Patches

For critical security or stability issues:

1. Create a `hotfix/` branch from the release tag
2. Fix the issue
3. Update version to X.Y.(Z+1)
4. Follow normal release process
5. Merge back into main and develop

## Build Requirements

Ensure you have:

```bash
pip install build twine
```

## Manual Publishing (if needed)

```bash
# Build packages
python -m build

# Check packages
twine check dist/*

# Upload to PyPI
twine upload dist/* -r pypi
```

## Release Notes Template

Use this template for GitHub releases:

```markdown
# AIConexus X.Y.Z

## What's New

### Features
- Feature description

### Bug Fixes
- Bug fix description

### Breaking Changes
- Breaking change description (if any)

### Deprecations
- Deprecated features

## Contributors

- @username1
- @username2

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for full list of changes.

## Installation

```bash
pip install aiconexus==X.Y.Z
```

## Documentation

See [documentation](https://docs.aiconexus.dev) for usage guides.
```

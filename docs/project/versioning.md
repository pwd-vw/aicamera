# Semantic Versioning Strategy

## Overview

This document outlines the semantic versioning strategy for the AI Camera monorepo, following the **MAJOR.MINOR.PATCH** format as defined by [Semantic Versioning 2.0.0](https://semver.org/).

**Current Version**: `2.0.0` (Starting point for the monorepo)

## Version Format

```
MAJOR.MINOR.PATCH[-PRERELEASE][+BUILD]
```

### Version Components

- **MAJOR** (2): Incompatible API changes
- **MINOR** (0): New functionality in a backward-compatible manner
- **PATCH** (0): Backward-compatible bug fixes
- **PRERELEASE** (optional): Alpha, beta, rc versions
- **BUILD** (optional): Build metadata

## Versioning Rules

### MAJOR Version (X.0.0)

**Increment when:**
- Breaking changes to public APIs
- Major architectural changes
- Incompatible database schema changes
- Removal of deprecated features
- Changes that require user intervention

**Examples:**
- Changing API endpoints from `/api/v1/` to `/api/v2/`
- Modifying database table structures
- Removing support for older Python/Node.js versions
- Changing communication protocols

### MINOR Version (X.Y.0)

**Increment when:**
- New features added in backward-compatible manner
- New API endpoints added
- New database tables/columns added
- New configuration options
- Performance improvements
- New AI models added

**Examples:**
- Adding new detection algorithms
- New API endpoints for analytics
- Adding support for new camera types
- New WebSocket events
- Adding new database views

### PATCH Version (X.Y.Z)

**Increment when:**
- Bug fixes
- Security patches
- Documentation updates
- Minor performance improvements
- Dependency updates

**Examples:**
- Fixing memory leaks
- Correcting API response formats
- Updating documentation
- Security vulnerability patches
- Minor UI/UX improvements

## Component-Specific Versioning

### Edge Component (Python)
- **Location**: `edge/requirements.txt`
- **Version tracking**: Via commit hashes and requirements files
- **Updates**: When Python dependencies or edge logic changes

### Server Component (Node.js)
- **Location**: `server/package.json`
- **Version tracking**: Via npm package versions
- **Updates**: When Node.js dependencies or server logic changes

### Shared Components
- **Protocols**: `server/protocols/`
- **Database Schema**: `server/database/schema.sql`
- **Documentation**: `docs/`

## Pre-release Versions

### Alpha (2.0.0-alpha.1)
- Early development versions
- May contain incomplete features
- Not recommended for production

### Beta (2.0.0-beta.1)
- Feature-complete versions
- Undergoing testing
- May contain bugs

### Release Candidate (2.0.0-rc.1)
- Final testing before release
- Should be stable
- Last chance for critical fixes

## Release Process

### 1. Development Phase
```bash
# Current development version
2.0.0-dev.1
2.0.0-dev.2
...
```

### 2. Alpha Phase
```bash
# Alpha releases for testing
2.0.0-alpha.1
2.0.0-alpha.2
...
```

### 3. Beta Phase
```bash
# Beta releases for feature testing
2.0.0-beta.1
2.0.0-beta.2
...
```

### 4. Release Candidate
```bash
# Release candidates
2.0.0-rc.1
2.0.0-rc.2
...
```

### 5. Stable Release
```bash
# Final stable release
2.0.0
```

## Version Update Workflow

### Automatic Versioning (GitHub Actions)

1. **Commit Message Convention**:
   - `feat:` → MINOR version bump
   - `fix:` → PATCH version bump
   - `BREAKING CHANGE:` → MAJOR version bump

2. **Branch Strategy**:
   - `main` → Production releases
   - `develop` → Development versions
   - `feature/*` → Feature development
   - `hotfix/*` → Critical fixes

3. **Release Process**:
   - Create release branch from `main`
   - Update version numbers
   - Create GitHub release
   - Tag with semantic version

## Version Number Locations

### Root Level
- `package.json` (monorepo version)
- `README.md` (documentation)

### Edge Component
- `edge/requirements.txt` (dependency versions)
- `edge/src/__init__.py` (component version)

### Server Component
- `server/package.json` (component version)
- `server/src/index.js` (API version)

### Documentation
- `docs/project/versioning.md` (this file)
- `docs/project/CHANGELOG.md` (release notes)

## Examples

### Version 2.0.0 (Initial Release)
- Monorepo structure established
- Edge and server components separated
- Basic communication protocols defined

### Version 2.1.0 (Feature Release)
- New AI model support
- Enhanced analytics API
- Improved WebSocket events

### Version 2.1.1 (Patch Release)
- Bug fix in image processing
- Security update in dependencies
- Documentation corrections

### Version 3.0.0 (Major Release)
- Breaking API changes
- New database schema
- Major architectural improvements

## Migration Guide

### From v1.x to v2.0.0
- **Breaking Changes**: Complete restructure to monorepo
- **Migration Steps**: 
  1. Backup existing data
  2. Install new dependencies
  3. Update configuration files
  4. Test edge and server components

### Version Compatibility Matrix

| Edge Version | Server Version | Compatibility |
|--------------|----------------|---------------|
| 2.0.0        | 2.0.0          | ✅ Full       |
| 2.1.0        | 2.0.0          | ✅ Backward   |
| 2.0.0        | 2.1.0          | ✅ Backward   |
| 3.0.0        | 2.x.x          | ❌ Breaking   |

## Tools and Automation

### GitHub Actions
- **Automatic versioning** based on commit messages
- **Release creation** with changelog generation
- **Dependency scanning** for security updates
- **Automated testing** before releases

### Scripts
- `scripts/version.sh` - Version management script
- `scripts/release.sh` - Release automation
- `scripts/changelog.sh` - Changelog generation

### Dependencies
- `conventional-changelog` - Changelog generation
- `semantic-release` - Automated versioning
- `@semantic-release/github` - GitHub integration

## Best Practices

### 1. Commit Messages
```
feat: add new license plate detection algorithm
fix: resolve memory leak in image processing
docs: update API documentation
BREAKING CHANGE: modify database schema for analytics
```

### 2. Branch Naming
```
feature/add-mqtt-support
hotfix/fix-security-vulnerability
release/2.1.0
```

### 3. Tag Naming
```
v2.0.0
v2.1.0-alpha.1
v2.1.0-beta.1
v2.1.0-rc.1
```

### 4. Release Notes
- Clear description of changes
- Migration instructions for breaking changes
- Known issues and limitations
- Performance improvements
- Security updates

## Monitoring and Maintenance

### Version Tracking
- **GitHub Releases**: Official release tracking
- **Dependency Updates**: Automated security scanning
- **Performance Monitoring**: Version-specific metrics
- **User Feedback**: Version-specific issue tracking

### Deprecation Policy
- **Deprecation Notice**: 6 months advance notice
- **Migration Support**: Documentation and tools
- **Backward Compatibility**: Maintained for 12 months
- **Security Updates**: Continued for deprecated versions

---

**Last Updated**: 2024-08-21  
**Next Review**: 2024-12-21  
**Maintainer**: AI Camera Team

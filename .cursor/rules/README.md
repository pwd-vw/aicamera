# Cursor Rules Directory

This directory contains Cursor AI development rules and guidelines for the AI Camera monorepo.

## Files

### `aicamera-monorepo.mdc` (Active)
- **Status**: ✅ Active
- **Description**: Current development rules for the AI Camera monorepo
- **Scope**: Edge component, Server component, documentation, scripts, deployment
- **Always Apply**: Yes

## Usage

Cursor will automatically apply the rules from `aicamera-monorepo.mdc` to all development work in this repository.

## Rule Categories

The active rules cover:

1. **Project Overview** - Monorepo structure and architecture
2. **Repository Structure** - File organization and naming
3. **Development Environment** - Python, Node.js, database setup
4. **Versioning Strategy** - Semantic versioning (2.0.0+)
5. **Communication Protocols** - WebSocket, REST API, MQTT
6. **Code Organization** - Import conventions, dependency injection
7. **Documentation Organization** - All docs in `/docs/` directory
8. **Script Organization** - Component-specific script locations
9. **Testing Strategy** - Unit, integration, end-to-end testing
10. **Security Guidelines** - Authentication, encryption, validation
11. **Performance Optimization** - Database, caching, monitoring
12. **Deployment** - Systemd, nginx, CI/CD pipeline


The project has been restructured from a single-component system to a monorepo:
- **Structured**: Edge (Python) + Server (Node.js) components
- **Documentation**: Organized by component (`docs/edge/`, `docs/server/`, `docs/reference/`) with clear categories
- **Scripts**: Organized by component (`/edge/scripts/`, `/server/scripts/`)
- **Services**: Component-specific systemd services

## Adding New Rules

To add new rules:

1. Create a new `.mdc` file in this directory
2. Add proper frontmatter with `alwaysApply` and `description`
3. Update this README with the new rule file
4. Consider if the rule should be merged into the main file

## Rule Priority

1. **aicamera-monorepo.mdc** - Always applied (main rules)
2. **Future rule files** - Based on `alwaysApply` setting

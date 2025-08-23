# AI Camera Edge System - Documentation

**Version:** 1.3.4  
**Last Updated:** 2025-08-19  
**Author:** AI Camera Team  

## 📚 Documentation Structure

This documentation is organized into three main categories:

### 🖥️ **Edge Device Documentation** (`edge/`)
Documentation specific to edge device deployment and operation.

- **[RELEASE_v2.0.md](edge/RELEASE_v2.0.md)** - Release notes and changelog
- **[INSTALLATION.md](edge/INSTALLATION.md)** - Edge device installation guide
- **[DEPLOYMENT.md](edge/DEPLOYMENT.md)** - Production deployment guide
- **[TROUBLESHOOTING.md](edge/TROUBLESHOOTING.md)** - Edge device troubleshooting
- **[project-overview.md](edge/project-overview.md)** - Project overview and architecture
- **[api-reference.md](edge/api-reference.md)** - Edge device API reference
- **[picamera2-reference.md](edge/picamera2-reference.md)** - PiCamera2 configuration reference
- **[metadata-debugging.md](edge/metadata-debugging.md)** - Metadata debugging guide
- **[dashboard-improvements.md](edge/dashboard-improvements.md)** - Dashboard improvements guide

### 🖥️ **Server Documentation** (`server/`)
Documentation for server-side components and APIs.

- **[API_REFERENCE.md](server/API_REFERENCE.md)** - REST API documentation
- **[WEBSOCKET_API.md](server/WEBSOCKET_API.md)** - WebSocket API documentation
- **[DATABASE_SCHEMA.md](server/DATABASE_SCHEMA.md)** - Database schema documentation
- **[SERVER_DEPLOYMENT.md](server/SERVER_DEPLOYMENT.md)** - Server deployment guide

### 📖 **Guides** (`guides/`)
General guides and tutorials applicable to both edge and server components.

- **[CONFIGURATION_GUIDE.md](guides/CONFIGURATION_GUIDE.md)** - Complete configuration guide
- **[README_IMPORT_ISSUES.md](guides/README_IMPORT_ISSUES.md)** - Import and dependency troubleshooting
- **[PERFORMANCE_TUNING.md](guides/PERFORMANCE_TUNING.md)** - Performance optimization guide
- **[SECURITY_GUIDE.md](guides/SECURITY_GUIDE.md)** - Security best practices
- **[installation.md](guides/installation.md)** - General installation guide
- **[development.md](guides/development.md)** - Development setup guide
- **[tailscale-setup.md](guides/tailscale-setup.md)** - Tailscale VPN setup guide

## 🚀 Quick Start

### For Edge Device Setup
1. **[Configuration Guide](guides/CONFIGURATION_GUIDE.md)** - Start here for configuration
2. **[Installation Guide](edge/INSTALLATION.md)** - Follow installation steps
3. **[Deployment Guide](edge/DEPLOYMENT.md)** - Production deployment
4. **[Troubleshooting](edge/TROUBLESHOOTING.md)** - If you encounter issues

### For Server Setup
1. **[Server Deployment](server/SERVER_DEPLOYMENT.md)** - Server installation
2. **[API Reference](server/API_REFERENCE.md)** - API documentation
3. **[Database Schema](server/DATABASE_SCHEMA.md)** - Database setup

### For Developers
1. **[Configuration Guide](guides/CONFIGURATION_GUIDE.md)** - Environment setup
2. **[Performance Tuning](guides/PERFORMANCE_TUNING.md)** - Optimization
3. **[Security Guide](guides/SECURITY_GUIDE.md)** - Security practices

## 📋 Documentation Status

| Document | Status | Last Updated | Version |
|----------|--------|--------------|---------|
| Configuration Guide | ✅ Complete | 2025-08-19 | 1.3.4 |
| Release Notes | ✅ Complete | 2025-08-19 | 1.3.1 |
| Import Issues Guide | ✅ Complete | 2025-08-19 | 1.3.4 |
| Project Overview | ✅ Complete | 2025-08-19 | 1.3.4 |
| PiCamera2 Reference | ✅ Complete | 2025-08-19 | 1.3.4 |
| Installation Guide | 🔄 In Progress | 2025-08-19 | 1.3.4 |
| Deployment Guide | 🔄 In Progress | 2025-08-19 | 1.3.4 |
| API Reference | 🔄 In Progress | 2025-08-19 | 1.3.4 |
| Troubleshooting | 🔄 In Progress | 2025-08-19 | 1.3.4 |

## 🔍 Search Documentation

### By Topic
- **Installation**: [Installation Guide](edge/INSTALLATION.md), [Configuration Guide](guides/CONFIGURATION_GUIDE.md)
- **Configuration**: [Configuration Guide](guides/CONFIGURATION_GUIDE.md)
- **Deployment**: [Deployment Guide](edge/DEPLOYMENT.md), [Server Deployment](server/SERVER_DEPLOYMENT.md)
- **Troubleshooting**: [Troubleshooting](edge/TROUBLESHOOTING.md), [Import Issues](guides/README_IMPORT_ISSUES.md)
- **API**: [API Reference](server/API_REFERENCE.md), [WebSocket API](server/WEBSOCKET_API.md)
- **Performance**: [Performance Tuning](guides/PERFORMANCE_TUNING.md)
- **Security**: [Security Guide](guides/SECURITY_GUIDE.md)

### By Component
- **Edge Device**: All files in `edge/` directory
- **Server**: All files in `server/` directory
- **General**: All files in `guides/` directory

## 📝 Contributing to Documentation

### Adding New Documentation
1. Create the document in the appropriate directory:
   - `edge/` for edge device specific docs
   - `server/` for server specific docs
   - `guides/` for general guides
2. Update this index file
3. Follow the documentation template

### Documentation Template
```markdown
# Document Title

**Version:** X.X.X  
**Last Updated:** YYYY-MM-DD  
**Author:** Author Name  

## Overview
Brief description of the document's purpose.

## Table of Contents
- [Section 1](#section-1)
- [Section 2](#section-2)

## Section 1
Content...

## Section 2
Content...

## Related Documents
- [Link to related doc](path/to/doc.md)
```

## 🔗 External Resources

- **[Main README](../README.md)** - Project overview and quick start
- **[GitHub Repository](https://github.com/your-repo/aicamera)** - Source code
- **[Issue Tracker](https://github.com/your-repo/aicamera/issues)** - Bug reports and feature requests
- **[Wiki](https://github.com/your-repo/aicamera/wiki)** - Additional resources

## 📞 Support

For documentation issues or suggestions:
1. Check the [troubleshooting guide](edge/TROUBLESHOOTING.md)
2. Review [import issues guide](guides/README_IMPORT_ISSUES.md)
3. Create an issue in the GitHub repository
4. Contact the development team

---

**Note:** This documentation is continuously updated. For the latest version, check the repository or run `git pull` to update your local copy.

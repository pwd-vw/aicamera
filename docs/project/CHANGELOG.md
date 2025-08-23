# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Semantic versioning strategy and automation
- GitHub Actions for CI/CD pipeline
- Dependabot configuration for automated dependency updates
- Version management scripts

### Changed
- Updated project structure documentation
- Enhanced README with monorepo information

## [2.0.0] - 2024-08-21

### Added
- **Monorepo Structure**: Complete restructure from v1.x to monorepo architecture
- **Node.js Server Component**: New data ingestion server with Express.js
- **Multi-Protocol Communication**: WebSocket (primary), REST API (backup), MQTT (fallback)
- **Database Schema**: PostgreSQL schema for cameras, detections, analytics
- **API Specifications**: OpenAPI 3.0 specification for REST API
- **Socket.IO Events**: Real-time communication event specifications
- **Image Sync Service**: SFTP/rsync for secure image transfer
- **Health Monitoring**: Comprehensive health check endpoints
- **Security Middleware**: Helmet, CORS, rate limiting, compression
- **Logging System**: Winston-based structured logging
- **Validation**: Joi-based request and environment validation
- **Error Handling**: Comprehensive error handling and responses
- **Dependency Injection**: Modular architecture with dependency container
- **Testing Framework**: Jest for server, pytest for edge
- **Documentation**: Comprehensive documentation structure

### Changed
- **Architecture**: Separated edge (Python) and server (Node.js) components
- **Communication**: Implemented multi-layered communication strategy
- **Database**: New PostgreSQL schema with proper relationships
- **API Design**: RESTful API with proper versioning
- **Deployment**: Updated for monorepo structure
- **Configuration**: Environment-based configuration management

### Breaking Changes
- **Complete Restructure**: v1.x codebase restructured into monorepo
- **API Endpoints**: New API structure with versioning
- **Database Schema**: Incompatible with v1.x database
- **Configuration**: New environment variables and configuration files
- **Dependencies**: Updated dependency management for both components

### Migration Guide
1. **Backup Data**: Export existing data from v1.x
2. **Install Dependencies**: 
   ```bash
   cd server && npm install
   cd edge && pip install -r requirements.txt
   ```
3. **Update Configuration**: Copy and modify environment files
4. **Database Migration**: Create new PostgreSQL database and apply schema
5. **Test Components**: Verify edge and server functionality

### Technical Details
- **Edge Component**: Python 3.11+, Hailo AI Accelerator support
- **Server Component**: Node.js 18+, Express.js, Socket.IO
- **Database**: PostgreSQL 14+, Redis 6+
- **Communication**: WebSocket (primary), REST API, MQTT
- **Image Transfer**: SFTP/rsync with batch processing
- **Security**: JWT authentication, rate limiting, CORS
- **Monitoring**: Health checks, logging, metrics

### Known Issues
- Initial release - may contain minor bugs
- Limited AI model support in first release
- Basic analytics implementation
- Manual deployment process

### Performance
- Improved image processing pipeline
- Optimized database queries
- Reduced memory usage
- Faster startup times

### Security
- Updated dependencies with security patches
- Implemented proper authentication
- Added input validation
- Enhanced error handling

---

## [1.3.0] - 2024-07-15 (Legacy)

### Added
- Initial AI Camera implementation
- Hailo AI Accelerator integration
- License plate detection
- Web interface
- Basic API endpoints

### Changed
- Improved detection accuracy
- Enhanced user interface
- Better error handling

### Fixed
- Memory leak issues
- Camera initialization problems
- WebSocket connection stability

---

## [1.2.0] - 2024-06-20 (Legacy)

### Added
- Basic camera functionality
- Simple detection algorithms
- Web dashboard

### Changed
- Improved performance
- Better documentation

---

## [1.1.0] - 2024-05-10 (Legacy)

### Added
- Initial project setup
- Basic camera integration
- Simple web interface

### Fixed
- Installation issues
- Configuration problems

---

## [1.0.0] - 2024-04-01 (Legacy)

### Added
- Project initialization
- Basic structure
- Documentation

---

**Note**: Versions 1.x are legacy and no longer supported. Please migrate to v2.0.0+ for continued support and new features.

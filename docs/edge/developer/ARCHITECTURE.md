# AI Camera v2.0 - Architecture Documentation

**Version:** 2.0.0  
**Last Updated:** 2025-08-23  
**Author:** AI Camera Team  
**Category:** Architecture Documentation  
**Status:** Active

## Overview

AI Camera v2.0 เป็นระบบกล้องอัจฉริยะที่ใช้ Raspberry Pi 5 และ Hailo AI Accelerator สำหรับการตรวจจับป้ายทะเบียนรถ (LPR - License Plate Recognition) ระบบประกอบด้วย Edge Component และ Server Component ที่ทำงานร่วมกันผ่านการสื่อสารแบบ Multi-Protocol

## System Architecture

### Edge Component (Raspberry Pi 5 + Hailo-8)

```
┌─────────────────────────────────────────────────────────────┐
│                    Edge Component                           │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │   Camera    │  │ Detection   │  │    Web      │        │
│  │   Handler   │  │  Manager    │  │  Interface  │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
│         │                │                │               │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │   Camera    │  │ Detection   │  │   Health    │        │
│  │  Manager    │  │ Processor   │  │  Monitor    │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
│         │                │                │               │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │   Storage   │  │ WebSocket   │  │   Flask     │        │
│  │  Manager    │  │   Sender    │  │    App      │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
└─────────────────────────────────────────────────────────────┘
```

### Server Component (Node.js)

```
┌─────────────────────────────────────────────────────────────┐
│                   Server Component                          │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │   Data      │  │   API       │  │  Database   │        │
│  │ Ingestion   │  │  Gateway    │  │  Manager    │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
│         │                │                │               │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │ WebSocket   │  │   REST      │  │   MQTT      │        │
│  │   Server    │  │    API      │  │  Handler    │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
└─────────────────────────────────────────────────────────────┘
```

## Singleton Camera Access Architecture

**🚨 CRITICAL**: The camera system implements a singleton pattern to prevent multiple concurrent access to Picamera2, which does not support multiple processes accessing the camera simultaneously.

### Camera Access Pattern

#### Core Components:
- **CameraHandler**: Singleton low-level camera operations (Picamera2 interface)
- **CameraManager**: High-level camera service management (accesses CameraHandler)
- **Frame Buffer System**: Single capture thread provides frames and metadata to all consumers

#### Frame Buffer System:
```
┌─────────────────────────────────────────────────────────────┐
│                    Frame Buffer System                      │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────┐ │
│  │              Single Capture Thread                      │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │ │
│  │  │   Main      │  │   Lores     │  │  Metadata   │    │ │
│  │  │  Stream     │  │   Stream    │  │   Capture   │    │ │
│  │  └─────────────┘  └─────────────┘  └─────────────┘    │ │
│  └─────────────────────────────────────────────────────────┘ │
│                              │                              │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │              Thread-Safe Buffers                        │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │ │
│  │  │   Main      │  │   Lores     │  │  Metadata   │    │ │
│  │  │  Frame      │  │   Frame     │  │   Buffer    │    │ │
│  │  │  Buffer     │  │   Buffer    │  │             │    │ │
│  │  └─────────────┘  └─────────────┘  └─────────────┘    │ │
│  └─────────────────────────────────────────────────────────┘ │
│                              │                              │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │              Multiple Consumers                         │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │ │
│  │  │ Detection   │  │   Video     │  │   Health    │    │ │
│  │  │  Manager    │  │ Streaming   │  │  Monitor    │    │ │
│  │  └─────────────┘  └─────────────┘  └─────────────┘    │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### Component Access Rules

#### ✅ Allowed Access Patterns:
- **Detection Manager**: Uses `camera_manager.capture_frame()` for main stream
- **Video Streaming**: Uses `camera_manager.capture_lores_frame()` for web interface
- **Health Monitor**: Gets status from `camera_manager.get_status()`
- **Metadata Access**: Uses `camera_manager.get_status()` for camera metadata
- **Experimental Components**: Access metadata through standard API endpoints

#### ❌ Forbidden Access Patterns:
- **Direct Camera Access**: Never call `picam2.capture_request()` directly
- **Multiple Processes**: Never access CameraHandler from multiple processes
- **Bypass Manager**: Never access CameraHandler directly, always use CameraManager
- **Concurrent Capture**: Never have multiple components calling capture methods simultaneously

### Frame Buffer Methods

#### CameraHandler Frame Buffer Interface:
```python
# Thread-safe frame access
get_main_frame() -> np.ndarray
get_lores_frame() -> np.ndarray
get_cached_metadata() -> dict
is_frame_buffer_ready() -> bool

# Frame capture methods (use buffer)
capture_frame() -> np.ndarray  # Returns from main buffer
capture_lores_frame() -> np.ndarray  # Returns from lores buffer
```

#### CameraManager Interface:
```python
# High-level camera operations
capture_frame() -> np.ndarray  # For detection
capture_lores_frame() -> np.ndarray  # For video streaming
get_status() -> dict  # For health monitoring
get_config() -> dict  # For configuration
```

## Communication Protocols

### Primary: WebSocket
- **Real-time bidirectional communication**
- **Event-driven updates**
- **Automatic reconnection**
- **Status synchronization**

### Backup: REST API
- **Reliable HTTP communication**
- **Standard CRUD operations**
- **Error handling and retry logic**
- **JSON response format**

### Fallback: MQTT
- **Lightweight messaging**
- **Poor network conditions**
- **Battery-efficient communication**
- **QoS levels support**

### Image Transfer: SFTP/rsync
- **Secure file transfer**
- **Incremental synchronization**
- **Bandwidth optimization**
- **Resume capability**

## Component Architecture

### Camera Handler
- **Singleton pattern implementation**
- **Picamera2 interface management**
- **Frame buffer system**
- **Metadata capture and caching**
- **Thread-safe operations**

### Camera Manager
- **High-level camera operations**
- **Service lifecycle management**
- **Status monitoring and reporting**
- **Configuration management**
- **Auto-startup coordination**

### Detection Manager
- **AI detection workflow orchestration**
- **Frame processing pipeline**
- **Model management (Hailo-8)**
- **Result aggregation and storage**
- **Performance optimization**

### Health Monitor
- **System health monitoring**
- **Component status tracking**
- **Performance metrics collection**
- **Alert generation**
- **Auto-recovery mechanisms**

### Web Interface
- **Flask Blueprint architecture**
- **REST API endpoints**
- **WebSocket event handling**
- **Real-time dashboard updates**
- **Responsive UI design**

## Dependency Injection

### Service Container
```python
# Core services
camera_manager = get_service('camera_manager')
detection_manager = get_service('detection_manager')
health_monitor = get_service('health_monitor')
storage_manager = get_service('storage_manager')
websocket_sender = get_service('websocket_sender')
```

### Service Lifecycle
1. **Initialization**: Services are created and registered
2. **Configuration**: Services are configured with settings
3. **Startup**: Services are started in sequence
4. **Operation**: Services run and communicate
5. **Shutdown**: Services are stopped gracefully

## Auto-Startup Sequence

### Startup Flow
```
1. Camera Handler Initialization
   ├── Picamera2 setup
   ├── Frame buffer initialization
   └── Capture thread start

2. Camera Manager Startup
   ├── Service registration
   ├── Status monitoring
   └── Auto-startup coordination

3. Detection Manager Startup
   ├── Model loading (Hailo-8)
   ├── Processing pipeline setup
   └── Frame processing start

4. Health Monitor Startup
   ├── Component monitoring
   ├── Performance tracking
   └── Alert system activation

5. Web Interface Startup
   ├── Flask application
   ├── Blueprint registration
   └── WebSocket server

6. System Ready
   ├── All services operational
   ├── Real-time monitoring active
   └── API endpoints available
```

### Configuration
- **Startup delays**: Configurable delays between service starts
- **Retry logic**: Automatic retry for failed service starts
- **Dependency checking**: Ensure dependencies are available
- **Status reporting**: Real-time startup status updates

## WSGI Entry Point for AI Camera v2.0

### Application Structure
```python
# edge/src/app.py
from edge.src.web import create_app

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
```

### Blueprint Registration
```python
# Web interface blueprints
app.register_blueprint(main_bp)
app.register_blueprint(camera_bp, url_prefix='/camera')
app.register_blueprint(detection_bp, url_prefix='/detection')
app.register_blueprint(health_bp, url_prefix='/health')
app.register_blueprint(storage_bp, url_prefix='/storage')
app.register_blueprint(websocket_bp, url_prefix='/websocket')
```

### Service Integration
- **Dependency injection**: Services accessed through container
- **Error handling**: Graceful error handling and recovery
- **Logging**: Structured logging throughout application
- **Monitoring**: Health checks and performance metrics

## Security Considerations

### Authentication
- **Tailscale integration**: Automatic authentication
- **API security**: Input validation and sanitization
- **Access control**: Role-based access control
- **Audit logging**: Comprehensive audit trails

### Data Protection
- **Encryption**: TLS/SSL for all communications
- **Secure storage**: Encrypted data storage
- **Privacy compliance**: GDPR and privacy regulations
- **Data retention**: Configurable retention policies

## Performance Optimization

### Camera Operations
- **Frame buffer system**: Efficient frame sharing
- **Thread optimization**: Minimal thread contention
- **Memory management**: Efficient memory usage
- **Processing pipeline**: Optimized detection workflow

### Web Interface
- **Caching**: Browser and server-side caching
- **Compression**: Gzip compression for responses
- **CDN integration**: Content delivery optimization
- **Load balancing**: Horizontal scaling support

## Monitoring and Logging

### Health Monitoring
- **Component status**: Real-time component monitoring
- **Performance metrics**: CPU, memory, disk usage
- **Error tracking**: Comprehensive error logging
- **Alert system**: Automated alert generation

### Logging Strategy
- **Structured logging**: JSON format logs
- **Log levels**: DEBUG, INFO, WARNING, ERROR
- **Log rotation**: Automatic log file rotation
- **Centralized logging**: Log aggregation and analysis

## Deployment Architecture

### Edge Deployment
- **Systemd services**: Service management
- **Nginx reverse proxy**: Web server configuration
- **Gunicorn WSGI**: Python application server
- **Auto-startup**: Automatic service startup

### Server Deployment
- **Docker containers**: Containerized deployment
- **Load balancing**: Horizontal scaling
- **Database clustering**: High availability
- **Backup systems**: Automated backup and recovery

## Future Enhancements

### Planned Features
- **Multi-camera support**: Multiple camera integration
- **Advanced analytics**: Machine learning analytics
- **Mobile application**: Native mobile app
- **Cloud integration**: Cloud service integration

### Scalability Improvements
- **Microservices**: Service decomposition
- **Message queues**: Asynchronous processing
- **Distributed caching**: Redis cluster
- **Auto-scaling**: Dynamic resource allocation


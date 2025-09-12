# Database Manager Component Reference

## Overview

The `DatabaseManager` component is responsible for managing all database operations in the AI Camera system. It provides a centralized interface for storing detection results, system events, health checks, and configuration data using SQLite database.

## Database Configuration

- **Database Path**: `/home/camuser/aicamera/edge/db/lpr_data.db`
- **Database Type**: SQLite3
- **Connection**: Thread-safe with `check_same_thread=False`
- **Row Factory**: `sqlite3.Row` for column access by name

## Database Schema

The database schema evolves through migration scripts. The current schema includes columns added by migrations v2 and v3.

### 1. detection_results Table

Primary table for storing vehicle and license plate detection results.

**Base Schema (v1):**
```sql
CREATE TABLE IF NOT EXISTS detection_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    vehicles_count INTEGER DEFAULT 0,
    plates_count INTEGER DEFAULT 0,
    ocr_results TEXT,
    vehicle_detected_image_path TEXT,
    plate_image_path TEXT,
    cropped_plates_paths TEXT,
    vehicle_detections TEXT,
    plate_detections TEXT,
    processing_time_ms REAL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    sent_to_server BOOLEAN DEFAULT 0,
    sent_at DATETIME,
    server_response TEXT
)
```

**Enhanced Schema (v2 + v3):**
Additional columns added by migrations:
- `original_image_path TEXT` (v3) - Path to original captured image
- `hailo_ocr_results TEXT` (v2) - JSON array of Hailo OCR results
- `easyocr_results TEXT` (v2) - JSON array of EasyOCR results  
- `best_ocr_method TEXT` (v2) - Method that produced best OCR result
- `ocr_processing_time_ms REAL` (v2) - Total OCR processing time
- `parallel_ocr_success BOOLEAN` (v2) - Whether parallel OCR succeeded
- `hailo_ocr_confidence REAL` (v2) - Hailo OCR confidence score
- `easyocr_confidence REAL` (v2) - EasyOCR confidence score
- `hailo_processing_time_ms REAL` (v2) - Hailo OCR processing time
- `easyocr_processing_time_ms REAL` (v2) - EasyOCR processing time
- `hailo_ocr_error TEXT` (v2) - Hailo OCR error messages
- `easyocr_error TEXT` (v2) - EasyOCR error messages

**Key Fields:**
- `original_image_path`: Path to the original captured image (only image stored)
- `vehicle_detections`: JSON array of vehicle bounding boxes and metadata
- `plate_detections`: JSON array of license plate bounding boxes and metadata
- `ocr_results`: JSON array of OCR text recognition results
- `sent_to_server`: Boolean flag for WebSocket transmission status

### 2. system_events Table

Logs system events and application state changes.

```sql
CREATE TABLE IF NOT EXISTS system_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_type TEXT NOT NULL,
    event_data TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
```

### 3. configuration Table

Stores application configuration key-value pairs.

```sql
CREATE TABLE IF NOT EXISTS configuration (
    key TEXT PRIMARY KEY,
    value TEXT,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
)
```

### 4. health_checks Table

Stores system health monitoring results.

```sql
CREATE TABLE IF NOT EXISTS health_checks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    component TEXT NOT NULL,
    status TEXT NOT NULL,
    message TEXT,
    details TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    sent_to_server BOOLEAN DEFAULT 0,
    sent_at DATETIME,
    server_response TEXT
)
```

### 5. websocket_sender_logs Table

Logs WebSocket transmission activities and status.

```sql
CREATE TABLE IF NOT EXISTS websocket_sender_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    action TEXT NOT NULL,
    status TEXT NOT NULL,
    message TEXT,
    data_type TEXT,
    record_count INTEGER DEFAULT 0,
    server_response TEXT,
    aicamera_id TEXT,
    checkpoint_id TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
)
```

## Core Methods

### Initialization

#### `__init__(self, logger=None)`
- Initializes the DatabaseManager instance
- Sets up database path and connection variables
- Configures logging

#### `initialize(self) -> bool`
- Creates database directory if it doesn't exist
- Establishes SQLite connection with thread safety
- Creates all required tables
- Returns `True` on success, `False` on failure

### Detection Results Management

#### `insert_detection_result(self, detection_data: Dict[str, Any]) -> Optional[int]`
- Inserts a new detection result record
- Serializes JSON data for vehicle/plate detections and OCR results
- Returns the inserted record ID or `None` on failure

**Input Data Structure:**
```python
{
    'timestamp': str,
    'vehicles_count': int,
    'plates_count': int,
    'original_image_path': str,
    'vehicle_detections': List[Dict],
    'plate_detections': List[Dict],
    'ocr_results': List[Dict],
    'processing_time_ms': float
}
```

#### `get_recent_detections(self, limit: int = 50) -> List[Dict[str, Any]]`
- Retrieves the most recent detection results
- Deserializes JSON fields back to Python objects
- Returns list of detection result dictionaries

#### `get_detection_results_paginated(self, page: int = 1, per_page: int = 20, ...) -> Dict[str, Any]`
- Retrieves detection results with pagination
- Supports filtering by date range and vehicle count
- Returns paginated results with metadata

#### `get_detection_result_by_id(self, result_id: int) -> Optional[Dict[str, Any]]`
- Retrieves a specific detection result by ID
- Returns the detection result dictionary or `None` if not found

#### `get_detection_statistics(self) -> Dict[str, Any]`
- Calculates aggregate statistics from detection results
- Returns total counts, averages, and time-based metrics

### Health Monitoring

#### `insert_health_check_result(self, timestamp: str, component: str, status: str, message: str, details: str = None) -> Optional[int]`
- Inserts health check results for system components
- Returns the inserted record ID or `None` on failure

#### `get_latest_health_checks(self, limit: int = 10) -> List[Dict[str, Any]]`
- Retrieves the most recent health check results
- Returns list of health check dictionaries

### WebSocket Integration

#### `get_unsent_detection_results(self, limit: int = 50) -> List[Dict[str, Any]]`
- Retrieves detection results that haven't been sent to server
- Used by WebSocket sender for data transmission
- Returns list of unsent detection results

#### `get_unsent_health_checks(self, limit: int = 50) -> List[Dict[str, Any]]`
- Retrieves health checks that haven't been sent to server
- Used by WebSocket sender for health data transmission
- Returns list of unsent health checks

#### `mark_detection_result_sent(self, record_id: int, server_response: str = None) -> bool`
- Marks a detection result as sent to server
- Updates `sent_to_server` flag and `sent_at` timestamp
- Stores server response if provided

#### `mark_health_check_sent(self, record_id: int, server_response: str = None) -> bool`
- Marks a health check as sent to server
- Updates `sent_to_server` flag and `sent_at` timestamp
- Stores server response if provided

### WebSocket Logging

#### `log_websocket_action(self, action: str, status: str, message: str = None, ...) -> Optional[int]`
- Logs WebSocket transmission activities
- Records action type, status, message, and metadata
- Returns the inserted log record ID

#### `get_websocket_sender_logs(self, limit: int = 50) -> List[Dict[str, Any]]`
- Retrieves WebSocket sender log records
- Returns list of log entries with transmission details

### System Events

#### `log_system_event(self, event_type: str, event_data: Any = None)`
- Logs system events and state changes
- Serializes event data to JSON if provided
- Used for debugging and system monitoring

### Utility Methods

#### `execute_query(self, query: str, params: tuple = None) -> List[tuple]`
- Executes custom SQL queries
- Returns raw query results as list of tuples
- Used for custom database operations

#### `cleanup_old_records(self, days_to_keep: int = 30)`
- Removes old records from all tables
- Helps manage database size and performance
- Configurable retention period

#### `get_status(self) -> Dict[str, Any]`
- Returns database connection status and statistics
- Provides health information for monitoring

#### `cleanup(self)`
- Closes database connection
- Performs cleanup operations
- Called during application shutdown

## Data Storage Optimization

### Image Storage Strategy
- **Original Images Only**: Only `original_image_path` is stored in database
- **No Annotated Images**: Annotated images are generated dynamically for visualization
- **Bounding Box Metadata**: Vehicle and plate detections stored as JSON with coordinates
- **Disk Usage Reduction**: 66% reduction in images stored per detection

### JSON Serialization
- Vehicle detections: Bounding boxes, confidence scores, tracking IDs
- Plate detections: Bounding boxes, confidence scores, vehicle associations
- OCR results: Text, confidence, method used, processing metadata

## Error Handling

- All database operations include comprehensive error handling
- Failed operations return `None` or `False` with logged error messages
- Database connection issues are logged and handled gracefully
- JSON serialization errors are caught and logged

## Thread Safety

- Uses `check_same_thread=False` for SQLite connection
- Suitable for multi-threaded applications
- Row factory enables column access by name for better code readability

## Dependencies

- `sqlite3`: Built-in Python SQLite interface
- `json`: JSON serialization/deserialization
- `logging`: Application logging
- `datetime`: Timestamp handling
- `pathlib.Path`: File system operations

## Usage Example

```python
from edge.src.components.database_manager import DatabaseManager

# Initialize database manager
db_manager = DatabaseManager()
if not db_manager.initialize():
    print("Failed to initialize database")

# Insert detection result
detection_data = {
    'timestamp': '2025-01-27T10:30:00',
    'vehicles_count': 2,
    'plates_count': 1,
    'original_image_path': '/edge/captured_images/frame_001.jpg',
    'vehicle_detections': [{'bbox': [100, 200, 300, 400], 'score': 0.95}],
    'plate_detections': [{'bbox': [150, 250, 200, 280], 'score': 0.88}],
    'ocr_results': [{'text': 'ABC123', 'confidence': 0.92}],
    'processing_time_ms': 150.5
}

record_id = db_manager.insert_detection_result(detection_data)
if record_id:
    print(f"Detection result inserted with ID: {record_id}")

# Retrieve recent detections
recent_detections = db_manager.get_recent_detections(limit=10)
print(f"Retrieved {len(recent_detections)} recent detections")

# Cleanup
db_manager.cleanup()
```

## Database Migrations

The database schema is managed through migration scripts located in `/edge/src/database/`:

### Migration v2: Enhanced OCR Support
- **File**: `schema_migration_v2.py`
- **Purpose**: Adds support for parallel Hailo OCR and EasyOCR processing
- **New Columns**: OCR performance metrics, parallel processing metadata, confidence scores
- **Features**: Automatic backup, data migration, index creation

### Migration v3: Image Storage Optimization  
- **File**: `schema_migration_v3.py`
- **Purpose**: Adds `original_image_path` column for optimized image storage
- **New Columns**: `original_image_path` for storing only original images
- **Features**: Automatic backup, index creation for image path queries

### Migration Process
1. **Automatic Detection**: Migrations check if they're needed before running
2. **Backup Creation**: Database is backed up before any schema changes
3. **Schema Updates**: New columns are added with proper error handling
4. **Data Migration**: Existing data is migrated to new schema format
5. **Index Creation**: Performance indexes are created for new columns
6. **Version Tracking**: Schema version is recorded in `schema_version` table

### Running Migrations
```python
from edge.src.database.schema_migration_v2 import run_migration as run_v2
from edge.src.database.schema_migration_v3 import run_migration as run_v3

# Run migrations in order
run_v2()  # Add OCR enhancement columns
run_v3()  # Add original_image_path column
```

### Database Initialization
The database can be initialized using the provided script:
```bash
# Run database initialization script
python edge/scripts/init_database.py
```

This script:
- Creates the database if it doesn't exist
- Runs all necessary migrations
- Validates the schema
- Sets up initial configuration

## Schema Notes

The database schema is properly managed through migration scripts. The `insert_detection_result` method references columns that are added by migrations v2 and v3. The migration system ensures backward compatibility and handles schema evolution gracefully.

## Version Information

- **Component Version**: 1.3
- **Last Updated**: August 2025
- **Author**: AI Camera Team

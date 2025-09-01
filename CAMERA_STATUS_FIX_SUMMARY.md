# Camera Status Fix Summary

## Problem Description
The camera dashboard showed inconsistent status across different dashboards:
- **Edge Dashboard**: Showed "Online" when `status.streaming` was true
- **Health Dashboard**: Showed "Initialized and Streaming" when both `initialized` and `streaming` were true  
- **Camera Dashboard**: Showed "Offline" when `status.streaming` was false

## Root Cause
The camera dashboard JavaScript was not properly handling the API reference format which requires both `initialized` and `streaming` flags to determine the actual camera status.

## API Reference Format
According to the API reference (`docs/edge/api-reference.md`), the camera status should have this structure:

```json
{
  "success": true,
  "status": {
    "initialized": true,
    "streaming": true,
    "frame_count": 1234,
    "average_fps": 29.5,
    "uptime": 3600.5,
    "camera_handler": {
      "initialized": true,
      "streaming": true,
      "camera_properties": {
        "Model": "imx708"
      },
      "current_config": {
        "main": {
          "size": [1280, 720]
        },
        "controls": {
          "FrameDurationLimits": [33333, 33333]
        }
      }
    }
  }
}
```

## Fixes Applied

### 1. Updated Camera Status Logic (`edge/src/web/static/js/camera.js`)

**Before:**
```javascript
if (status.streaming) {
    statusClass = 'status-online';
    statusText = 'Online';
} else if (status.initialized) {
    statusClass = 'status-warning';
    statusText = 'Ready';
}
```

**After:**
```javascript
// Check status according to API reference: initialized and streaming flags
if (status.initialized && status.streaming) {
    statusClass = 'status-online';
    statusText = 'Online';
} else if (status.initialized && !status.streaming) {
    statusClass = 'status-warning';
    statusText = 'Ready';
} else if (!status.initialized) {
    statusClass = 'status-offline';
    statusText = 'Offline';
}
```

### 2. Updated Video Status Logic

**Before:**
```javascript
if (status.streaming) {
    this.updateVideoStatus('hidden', '');
} else if (status.initialized) {
    this.updateVideoStatus('offline', 'Camera ready but not streaming');
}
```

**After:**
```javascript
if (status.initialized && status.streaming) {
    this.updateVideoStatus('hidden', '');
} else if (status.initialized && !status.streaming) {
    this.updateVideoStatus('offline', 'Camera ready but not streaming');
} else {
    this.updateVideoStatus('offline', 'Camera not initialized');
}
```

### 3. Updated WebSocket Event Handler

**Before:**
```javascript
const isStreaming = data.status.streaming;
```

**After:**
```javascript
const isStreaming = data.status.initialized && data.status.streaming;
```

### 4. Updated Status Display Logic

**Before:**
```javascript
<strong class="text-${status.streaming ? 'success' : status.initialized ? 'warning' : 'danger'}">
    ${status.streaming ? 'Online' : status.initialized ? 'Ready' : 'Offline'}
</strong>
```

**After:**
```javascript
<strong class="text-${status.initialized && status.streaming ? 'success' : status.initialized ? 'warning' : 'danger'}">
    ${status.initialized && status.streaming ? 'Online' : status.initialized ? 'Ready' : 'Offline'}
</strong>
```

### 5. Enhanced Status Content Display

Updated `updateStatusContent` function to properly extract data from the API reference format:
- Resolution from `camera_handler.current_config.main.size`
- Sensor model from `camera_handler.camera_properties.Model`
- Framerate from `camera_handler.current_config.controls.FrameDurationLimits`
- Added frame count and average FPS display

## Status Mapping

| initialized | streaming | Dashboard Status | Description |
|-------------|-----------|------------------|-------------|
| false | false | Offline | Camera not initialized |
| true | false | Ready | Camera initialized but not streaming |
| true | true | Online | Camera initialized and streaming |

## Files Modified
- `edge/src/web/static/js/camera.js` - Updated status logic and display

## Files NOT Modified (as requested)
- `edge/src/components/camera_handler.py` - No changes to avoid affecting other modules
- `edge/src/services/camera_manager.py` - No changes to avoid affecting other modules
- `edge/src/web/blueprints/camera.py` - No changes needed, already follows API reference

## Result
The camera dashboard now properly displays status according to the API reference format, ensuring consistency across all dashboards:
- **Online**: Only when both `initialized=true` and `streaming=true`
- **Ready**: When `initialized=true` but `streaming=false`
- **Offline**: When `initialized=false`

This fix resolves the status inconsistency issue without affecting the core camera functionality or other modules.

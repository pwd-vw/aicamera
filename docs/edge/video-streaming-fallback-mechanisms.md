# Video Streaming Fallback Mechanisms

## Overview

The AI Camera system now includes comprehensive fallback mechanisms for video streaming to ensure reliable video feed delivery even when the primary camera system encounters issues.

## Architecture

### Multi-Layer Fallback System

The video streaming system implements a three-tier fallback architecture:

1. **Primary Source**: Camera Manager (lores frames)
2. **Secondary Source**: Cached Frames (last successful capture)
3. **Tertiary Source**: Fallback Frames (static placeholder)

### Components

- **VideoStreamingService**: Enhanced with fallback mechanisms
- **Camera Blueprint**: Multiple video feed endpoints with error handling
- **Fallback Frame Generator**: Static placeholder frames for error states
- **Health Monitoring**: Real-time health checks and status reporting

## Fallback Mechanisms

### 1. Frame Source Fallback

```python
def _get_frame_with_fallback(self) -> Tuple[Optional[np.ndarray], str]:
    """
    Get frame with comprehensive fallback mechanisms.
    
    Returns:
        Tuple[Optional[np.ndarray], str]: Frame data and source description
    """
    # Primary source: Camera manager
    if self.camera_manager:
        frame = self.camera_manager.capture_lores_frame()
        if frame is not None and self._validate_frame(frame):
            return frame, "camera_lores"
    
    # Secondary source: Last successful frame (cached)
    if self.last_successful_frame is not None:
        return self.last_successful_frame.copy(), "cached_frame"
    
    # Tertiary source: Fallback frame
    return self.fallback_frame, "fallback_frame"
```

### 2. Error Recovery

- **Error Counting**: Tracks consecutive errors
- **Recovery Time**: Automatic recovery after error timeout
- **Adaptive Delays**: Longer delays for repeated errors
- **Graceful Degradation**: Continues streaming with fallback frames

### 3. Health Monitoring

```python
def health_check(self) -> Dict[str, Any]:
    """Perform health check with fallback status."""
    status = {
        'healthy': True,
        'camera_health': camera_ratio > 0.5,  # At least 50% frames from camera
        'fallback_health': fallback_ratio < 0.3,  # Less than 30% fallback frames
        'error_rate_healthy': self.error_count < self.max_errors
    }
    return status
```

## Video Feed Endpoints

### 1. Main Video Feed (`/camera/video_feed`)

- **Primary**: Uses VideoStreamingService with fallback
- **Fallback**: Direct camera manager access
- **Error Handling**: Continuous error stream on failure

### 2. Lores Video Feed (`/camera/video_feed_lores`)

- **Primary**: Uses VideoStreamingService with fallback
- **Fallback**: Direct camera manager access
- **Optimized**: Lower quality for better performance

### 3. Video Test Endpoint (`/camera/video_test`)

Comprehensive end-to-end testing:

```json
{
  "success": true,
  "test_results": {
    "overall_status": "passed",
    "summary": {
      "passed": 5,
      "total": 5,
      "success_rate": 100.0
    },
    "tests": {
      "camera_manager": {"status": "passed", "message": "Camera manager available"},
      "camera_handler": {"status": "passed", "message": "Camera initialized and streaming"},
      "frame_capture": {"status": "passed", "message": "Frame captured successfully"},
      "video_streaming": {"status": "passed", "message": "Streaming service healthy"},
      "frame_buffer": {"status": "passed", "message": "Frame buffer ready"}
    }
  }
}
```

### 4. Status Endpoints

- **`/camera/video_streaming_status`**: Detailed streaming status with fallback metrics
- **`/camera/video_streaming_reset`**: Reset fallback mode and error counters

## Fallback Frame Generation

### Static Placeholder Frames

```python
def _initialize_fallback_frame(self):
    """Initialize fallback frame for error states."""
    fallback_img = np.zeros((self.height, self.width, 3), dtype=np.uint8)
    fallback_img[:] = (50, 50, 50)  # Dark gray background
    
    # Add informative text
    cv2.putText(fallback_img, "AI Camera", (self.width//2 - 100, self.height//2 - 50), 
               font, 1.5, (255, 255, 255), 2)
    cv2.putText(fallback_img, "Video Feed", (self.width//2 - 80, self.height//2), 
               font, 1.0, (200, 200, 200), 2)
    cv2.putText(fallback_img, "Initializing...", (self.width//2 - 70, self.height//2 + 50), 
               font, 0.8, (150, 150, 150), 1)
```

### Error Placeholder Frames

Dynamic error frames with specific error messages:

```python
def _generate_error_placeholder(message):
    """Generate error placeholder with message."""
    # Create gradient background
    # Add error icon and message
    # Include timestamp and retry indicator
```

## Performance Metrics

### Source Distribution Tracking

```python
source_distribution = {
    'camera': 85.2,    # Percentage of frames from camera
    'cached': 12.1,    # Percentage of frames from cache
    'fallback': 2.7    # Percentage of frames from fallback
}
```

### Health Metrics

- **Camera Health**: >50% frames from camera
- **Fallback Health**: <30% fallback frames
- **Error Rate**: <10 consecutive errors
- **FPS Health**: >50% of target FPS
- **Queue Health**: <80% queue capacity

## Error Handling

### Error Types and Responses

1. **Camera Hardware Error**: Fallback to cached/placeholder frames
2. **Memory Allocation Error**: Reduced quality, fallback frames
3. **Camera Timeout**: Retry with exponential backoff
4. **Frame Encoding Error**: Lower quality encoding
5. **Network Error**: Local fallback frames

### Recovery Mechanisms

- **Automatic Recovery**: Resume camera usage after error timeout
- **Manual Reset**: Reset fallback mode via API endpoint
- **Progressive Degradation**: Reduce quality before using fallback
- **Error Isolation**: Prevent single error from affecting entire system

## Testing

### End-to-End Testing

```bash
# Run comprehensive video streaming test
python edge/test_video_streaming.py
```

### Test Coverage

1. **Basic Functionality**: Video feed endpoints, status endpoints
2. **Fallback Mechanisms**: Error simulation, recovery testing
3. **Performance**: Frame rate, quality, queue management
4. **Error Handling**: Various error scenarios and responses
5. **Health Monitoring**: Health checks and metrics validation

### Test Results

```
============================================================
VIDEO STREAMING END-TO-END TEST
============================================================
✅ Video streaming status: Working
✅ Video test endpoint: All tests passed
✅ Camera status: Initialized and streaming
✅ Video feed endpoints: Responding correctly
✅ Fallback mode reset: Working

============================================================
FALLBACK MECHANISMS TEST
============================================================
✅ System in normal mode
✅ Good camera frame ratio (100%)
✅ Proper error handling
```

## Configuration

### Fallback Settings

```python
# VideoStreamingService configuration
self.max_errors = 10                    # Maximum consecutive errors
self.error_recovery_time = 5.0          # Error recovery timeout (seconds)
self.fallback_mode = False              # Current fallback state
self.last_successful_frame = None       # Cached frame
```

### Quality Settings

- **Camera Frames**: Full quality (80%)
- **Cached Frames**: Medium quality (70%)
- **Fallback Frames**: Lower quality (60%)

## Monitoring and Alerting

### Status Indicators

- **Green**: Normal operation (>50% camera frames)
- **Yellow**: Degraded operation (high fallback usage)
- **Red**: Error state (fallback mode active)

### Metrics Dashboard

- Real-time source distribution
- Error rate tracking
- Performance metrics
- Health status indicators

## Benefits

### Reliability

- **Continuous Operation**: Video feed never completely stops
- **Graceful Degradation**: Maintains functionality during issues
- **Automatic Recovery**: Self-healing without manual intervention

### Performance

- **Optimized Quality**: Adjusts quality based on source
- **Efficient Caching**: Reduces camera load with cached frames
- **Smart Fallback**: Minimal performance impact during normal operation

### User Experience

- **Seamless Transitions**: Users don't notice fallback activation
- **Informative Feedback**: Error messages and status indicators
- **Consistent Interface**: Same endpoints work in all states

## Future Enhancements

### Planned Improvements

1. **Advanced Caching**: Multiple cached frames for smoother transitions
2. **Predictive Fallback**: Proactive fallback based on health trends
3. **Quality Adaptation**: Dynamic quality adjustment based on conditions
4. **Multi-Camera Support**: Fallback between multiple camera sources
5. **Machine Learning**: Predictive error detection and prevention

### Integration Opportunities

- **Health Monitoring**: Integration with system health monitoring
- **Alerting System**: Automated alerts for fallback activation
- **Analytics**: Detailed usage analytics and performance insights
- **Configuration Management**: Dynamic configuration updates

## Conclusion

The video streaming fallback mechanisms provide a robust, reliable video feed system that ensures continuous operation even when the primary camera system encounters issues. The multi-layer approach with comprehensive error handling, health monitoring, and graceful degradation makes the system highly resilient and user-friendly.

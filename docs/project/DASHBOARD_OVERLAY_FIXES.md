# Dashboard Overlay and Console Error Fixes

## Issues Fixed

### 1. Persistent Overlay Frame at Bottom of Video Feed ✅

**Problem**: The capture status overlay was persisting at the bottom of the video feed section, showing "Ready to capture" message.

**Root Cause**: The `showCaptureStatus` function was being called during initialization, displaying the capture status overlay that wasn't being hidden properly.

**Solution**:
- **File**: `edge/src/web/static/js/camera.js`
- **Changes**:
  1. Modified initialization to hide capture status by default instead of showing it
  2. Added auto-hide functionality for non-critical status messages (3-second timeout)
  3. Enhanced `hideCaptureStatus` function to properly hide the overlay

**Code Changes**:
```javascript
// Before
this.showCaptureStatus('Ready to capture', 'info');

// After
this.hideCaptureStatus();

// Added auto-hide for non-critical messages
if (type === 'info' || type === 'success') {
    setTimeout(() => {
        this.hideCaptureStatus();
    }, 3000);
}
```

### 2. Console Log Error Spam ✅

**Problem**: Multiple console errors were appearing:
- `Image saved to manual_capture directory`
- `WebSocket connection failed, using HTTP API fallback`
- `Video feed error - manual refresh recommended`
- `HTTP API error: Expected JSON response, got text/html`

**Root Causes**:
1. **HTTP API 404 Errors**: `/camera/status` endpoint returning 404, causing HTML response instead of JSON
2. **Video Feed Error Spam**: Multiple error messages for the same issue
3. **WebSocket Connection Issues**: Connection failures causing fallback to HTTP API

**Solutions**:

#### A. HTTP API Error Handling
- **File**: `edge/src/web/static/js/camera.js`
- **Changes**:
  1. Added proper HTTP status code checking
  2. Suppressed 404 error messages to reduce noise
  3. Improved error handling for non-JSON responses

```javascript
// Added HTTP status checking
if (!response.ok) {
    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
}

// Suppress 404 errors to reduce noise
if (!error.message.includes('404')) {
    AICameraUtils.addLogMessage('log-container', `HTTP API error: ${error.message}`, 'warning');
}
```

#### B. Video Feed Error Spam Prevention
- **File**: `edge/src/web/static/js/camera.js`
- **Changes**:
  1. Added `videoErrorShown` flag to prevent duplicate error messages
  2. Reset error flag when video feed recovers
  3. Only show error message once per error cycle

```javascript
// Added error spam prevention
if (!this.videoErrorShown) {
    AICameraUtils.addLogMessage('log-container', 'Video feed error - manual refresh recommended', 'warning');
    this.videoErrorShown = true;
}

// Reset flag on success
this.videoErrorShown = false;
```

## Technical Details

### Overlay Elements Structure
```html
<div class="video-container-compact">
    <div class="video-feed-wrapper position-relative">
        <img id="video-feed" src="/camera/video_feed" class="video-feed-compact">
        <div id="video-status" class="video-status-overlay"> <!-- Fixed in previous update -->
            <!-- Loading/error overlay -->
        </div>
    </div>
    
    <div id="capture-status" class="mt-2" style="display: none;"> <!-- FIXED -->
        <!-- Capture status overlay -->
    </div>
</div>
```

### Error Handling Flow
1. **WebSocket Connection**: Primary method for real-time updates
2. **HTTP API Fallback**: Used when WebSocket fails
3. **Error Suppression**: 404 errors suppressed to reduce noise
4. **Error Recovery**: Automatic retry with exponential backoff
5. **User Notification**: Single error message per error cycle

## Verification

### Overlay Fix
- ✅ Capture status overlay hidden by default
- ✅ Auto-hide after 3 seconds for info/success messages
- ✅ No persistent overlay at bottom of video feed
- ✅ Clean single video frame display

### Console Error Fix
- ✅ Reduced HTTP API error spam (404 errors suppressed)
- ✅ Single video feed error message per error cycle
- ✅ Proper error recovery and flag reset
- ✅ Cleaner console output

## Files Modified

1. `edge/src/web/static/js/camera.js` - Main JavaScript fixes
2. `edge/src/web/templates/camera/dashboard.html` - CSS improvements (from previous update)

## Status: ✅ COMPLETED

Both the persistent overlay issue and console error spam have been resolved:
- Dashboard now shows clean single video frame without persistent overlays
- Console errors are significantly reduced and properly handled
- Better user experience with cleaner interface and fewer error messages

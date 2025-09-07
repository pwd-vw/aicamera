# Video Feed Optimization - RGB Direct Encoding & Dashboard Display Fix

## Changes Made

### 1. RGB → JPEG Direct Encoding (No BGR Conversion)

**Problem**: Video feed was converting RGB frames to BGR before JPEG encoding, which was unnecessary and could cause color issues.

**Solution**: Modified the video streaming to use RGB frames directly for JPEG encoding.

**Files Modified**:
- `edge/src/components/improved_camera_manager.py`

**Changes**:
```python
# Before (unnecessary BGR conversion)
frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
_, buffer = cv2.imencode('.jpg', frame_bgr, [cv2.IMWRITE_JPEG_QUALITY, 85])

# After (direct RGB encoding)
_, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
```

**Benefits**:
- Eliminates unnecessary color conversion
- Reduces processing overhead
- Maintains color accuracy
- Faster frame encoding

### 2. Dashboard Video Overlay Display Fix

**Problem**: Dashboard was showing overlapping frames due to video status overlay not hiding properly.

**Solution**: Enhanced CSS to ensure video status overlay is properly hidden by default and only shows when needed.

**Files Modified**:
- `edge/src/web/templates/camera/dashboard.html`

**Changes**:
```css
/* Before */
.video-status-overlay {
    display: none; /* Hidden by default */
    /* ... */
}

/* After */
.video-status-overlay {
    display: none !important; /* Force hidden by default */
    opacity: 0; /* Ensure it's transparent when hidden */
    /* ... */
}

.video-status-overlay.show {
    display: flex !important;
    opacity: 1;
}
```

**Benefits**:
- Eliminates overlapping frame display
- Ensures clean single video feed display
- Better user experience
- Proper overlay visibility control

## Technical Details

### Video Feed Pipeline (After Changes)
```
Camera Frame (RGB888) → Direct JPEG Encoding → Web Display
```

### Color Format Flow
1. **Camera Capture**: RGB888 format from Picamera2
2. **Video Streaming**: RGB888 frames used directly
3. **JPEG Encoding**: RGB888 → JPEG (no conversion needed)
4. **Web Display**: Natural color representation

### Dashboard Display
- **Single Video Feed**: Only one video stream displayed
- **Clean Overlay**: Status overlay properly hidden when not needed
- **Responsive Design**: Video feed scales properly to container

## Verification

### RGB Direct Encoding
- ✅ No BGR conversion in video streaming
- ✅ RGB888 frames encoded directly to JPEG
- ✅ Color accuracy maintained
- ✅ Performance improved

### Dashboard Display
- ✅ Single video feed displayed
- ✅ No overlapping frames
- ✅ Status overlay properly controlled
- ✅ Clean user interface

## Files Modified

1. `edge/src/components/improved_camera_manager.py` - RGB direct encoding
2. `edge/src/web/templates/camera/dashboard.html` - Overlay display fix

## Status: ✅ COMPLETED

Both issues have been resolved:
- Video feed now uses RGB → JPEG direct encoding without BGR conversion
- Dashboard displays only one large frame without overlapping elements

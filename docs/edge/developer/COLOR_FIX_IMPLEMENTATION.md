# Camera Color Fix Implementation

## Problem Description
The camera system was experiencing color inversion issues where:
- Red appeared as Blue
- Blue appeared as Red  
- Green remained Green

This was caused by inconsistent color format configuration between camera streams.

## Root Cause
The camera was configured with mixed color formats:
- **Main stream**: `RGB888` (correct for web display)
- **Lores stream**: `XBGR8888` (incorrect - caused color channel swapping)
- **Detection processor**: Expected BGR format but received mixed formats
- **Video feed manager**: Had to convert between formats

## Solution Implemented

### 1. Camera Configuration Update
**File**: `edge/src/components/camera_handler.py`

**Changes Made**:
```python
# Before (inconsistent formats)
main_config = {"size": MAIN_RESOLUTION, "format": "RGB888"}
lores_config = {"size": LORES_RESOLUTION, "format": "XBGR8888"}

# After (consistent formats)
main_config = {"size": MAIN_RESOLUTION, "format": "RGB888"}
lores_config = {"size": LORES_RESOLUTION, "format": "RGB888"}  # Fixed!
```

### 2. Detection Processor Update
**File**: `edge/src/components/detection_processor.py`

**Changes Made**:
```python
# Before (assumed BGR format)
elif frame.shape[2] == 3:  # Already BGR/RGB - assume BGR
    pass  # Keep as-is

# After (explicit RGB to BGR conversion)
elif frame.shape[2] == 3:  # RGB from camera - convert to BGR for OpenCV
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
```

### 3. Format Information Updates
**File**: `edge/src/components/camera_handler.py`

**Changes Made**:
- Updated `capture_lores_frame()` format from `XBGR8888` to `RGB888`
- Updated `capture_ml_frame()` lores_format from `XBGR8888` to `RGB888`

## Color Pipeline After Fix

### Camera Capture
```
Camera Sensor → RGB888 (Main Stream) → RGB888 (Lores Stream)
```

### Detection Processing
```
RGB888 Frame → cv2.cvtColor(RGB2BGR) → BGR for OpenCV Models
```

### Video Feed Display
```
RGB888 Frame → cv2.cvtColor(RGB2BGR) → JPEG Encoding → Web Display
```

## Benefits of This Fix

1. **Consistent Color Representation**: Both streams now use the same RGB888 format
2. **No More Color Inversion**: Red stays red, blue stays blue
3. **Simplified Processing**: Clear conversion path from RGB to BGR when needed
4. **Better Performance**: Eliminates unnecessary format conversions
5. **Maintainable Code**: Single source of truth for color format

## Testing the Fix

### 1. Visual Verification
- Check that red objects appear red in video feed
- Check that blue objects appear blue in video feed
- Verify colors in stored detection images

### 2. Detection Accuracy
- Vehicle detection should work with correct colors
- License plate detection should maintain color accuracy
- No more color-based false positives

### 3. Performance Monitoring
- Monitor frame processing times
- Check for any new errors in logs
- Verify camera stability

## Files Modified

1. `edge/src/components/camera_handler.py` - Camera configuration and format info
2. `edge/src/components/detection_processor.py` - Frame color conversion logic

## Notes

- The fix maintains backward compatibility
- No changes needed to web interface
- Detection models continue to work as expected
- Camera performance should improve slightly due to consistent formats

## Future Considerations

- Consider adding color format validation in camera initialization
- Monitor for any edge cases with different camera modules
- Document color format requirements for future development

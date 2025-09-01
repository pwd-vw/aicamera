# Video Feed and WebSocket Connection Fixes

## Issues Identified and Fixed

### 1. **Unnecessary Video Feed Refreshing**

**Root Cause:**
- The system was calling "Video feed refreshed" too frequently
- `updateVideoFeedStatus()` was being called every 5 seconds
- Video feed was being refreshed even when working properly

**Fixes Implemented:**
- Increased video feed status check interval from 5 seconds to 15 seconds
- Added logic to only refresh when absolutely necessary
- Reduced automatic retry attempts from max errors to just 2 attempts
- Added manual refresh button for user-initiated refreshes

**Files Modified:**
- `edge/src/web/static/js/camera.js` - Reduced refresh frequency and improved logic

### 2. **Aggressive Error Handling and Retry Mechanism**

**Root Cause:**
- Video feed errors were triggering too many automatic retries
- Error count was reaching max retries too quickly
- System was constantly trying to recover without user intervention

**Fixes Implemented:**
- Reduced automatic retry attempts from `maxVideoErrors` to just 2
- Added 30-second cooldown before re-enabling automatic retries
- Changed error messages from "max retries reached" to "manual refresh recommended"
- Added manual refresh function that resets error count

**Files Modified:**
- `edge/src/web/static/js/camera.js` - Improved error handling and retry logic

### 3. **WebSocket Connection Issues**

**Root Cause:**
- Multiple reconnection attempts that kept failing
- Short timeouts and aggressive reconnection settings
- HTTP API fallback was being called too frequently

**Fixes Implemented:**
- Increased WebSocket timeout from 5 seconds to 10 seconds
- Reduced reconnection attempts from 3 to 2
- Increased reconnection delay from 2 seconds to 5 seconds
- Added maximum reconnection delay limit of 10 seconds
- Increased WebSocket response timeout from 3 to 5 seconds

**Files Modified:**
- `edge/src/web/static/js/camera.js` - Improved WebSocket configuration

### 4. **HTTP API Error Handling**

**Root Cause:**
- "Unexpected token '<'" errors when receiving HTML instead of JSON
- No content-type checking before parsing responses
- Immediate fallback to HTTP API on WebSocket failures

**Fixes Implemented:**
- Added content-type checking before parsing JSON responses
- Better error messages for non-JSON responses
- Changed HTTP API errors from 'error' to 'warning' level
- Prevented immediate retries on HTTP API failures

**Files Modified:**
- `edge/src/web/static/js/camera.js` - Enhanced HTTP API error handling

### 5. **Video Feed Status Checking Logic**

**Root Cause:**
- Video feed status was being checked too aggressively
- Status updates were triggering unnecessary refresh attempts
- Cooldown periods were too short

**Fixes Implemented:**
- Doubled the cooldown period for video feed status checks
- Added error count threshold before attempting refresh
- Only refresh video feed when camera streaming status changes AND feed is broken
- Added manual refresh button for user control

**Files Modified:**
- `edge/src/web/static/js/camera.js` - Improved status checking logic
- `edge/src/web/templates/camera/dashboard.html` - Added manual refresh button

## Technical Details

### Video Feed Refresh Flow (Improved)
```
1. Check video feed status every 15 seconds (was 5 seconds)
2. Only refresh if:
   - Video feed is broken AND
   - Camera is streaming AND
   - Haven't refreshed recently (cooldown * 2) AND
   - Error count is low (< 2)
3. Manual refresh button always works (bypasses cooldown)
```

### WebSocket Connection Flow (Improved)
```
1. Connect with 10-second timeout
2. Maximum 2 reconnection attempts
3. 5-second delay between reconnection attempts
4. 10-second maximum delay limit
5. 5-second wait for WebSocket response before HTTP fallback
```

### Error Handling Flow (Improved)
```
1. First 2 errors: Automatic retry with exponential backoff
2. After 2 errors: Stop automatic retries, show manual refresh message
3. 30-second cooldown before re-enabling automatic retries
4. Manual refresh button resets error count immediately
```

## Expected Results

After these fixes:
1. **Video Feed Stability**: Video feed should be much more stable with fewer unnecessary refreshes
2. **Reduced Log Spam**: Fewer "Video feed refreshed" and "WebSocket connection failed" messages
3. **Better User Control**: Manual refresh button for when automatic recovery fails
4. **Improved Performance**: Less aggressive checking and retry mechanisms
5. **Better Error Messages**: Clear guidance when manual intervention is needed

## Files Modified Summary

| File | Purpose of Fix |
|------|----------------|
| `edge/src/web/static/js/camera.js` | Reduced refresh frequency, improved error handling, better WebSocket config |
| `edge/src/web/templates/camera/dashboard.html` | Added manual refresh button |

## Key Changes Made

### JavaScript Changes:
- **Video feed status check interval**: 5s → 15s
- **Automatic retry attempts**: max errors → 2
- **WebSocket timeout**: 5s → 10s
- **Reconnection attempts**: 3 → 2
- **Reconnection delay**: 2s → 5s
- **WebSocket response timeout**: 3s → 5s
- **Error cooldown**: Added 30s reset timer
- **Manual refresh function**: Added user-initiated refresh

### HTML Changes:
- **Manual refresh button**: Added above video container
- **User guidance**: Added explanatory text for manual refresh

## Next Steps

1. **Restart the application** to apply all the JavaScript changes
2. **Test the dashboard** to verify video feed stability
3. **Monitor the logs** for reduced refresh and connection messages
4. **Use manual refresh button** when automatic recovery fails

## Notes

- All fixes maintain backward compatibility
- Manual refresh button gives users control over video feed recovery
- Reduced automatic retries prevent system from getting stuck in retry loops
- Better error messages guide users on when manual intervention is needed
- WebSocket configuration is more conservative to prevent connection spam

/**
 * AI Camera v2.0 - Camera Dashboard JavaScript
 * 
 * Camera control and monitoring functionality - uses cached data only.
 * 
 * @author AI Camera Team
 * @version 2.0
 * @since 2025-08-23
 */

// Force cache refresh for development
console.log('AI Camera Dashboard JavaScript loaded - Cache busted at:', new Date().toISOString());



// Camera dashboard state management
const CameraManager = {
    socket: null,
    statusUpdateInterval: null,
    lastStatusUpdate: 0,
    statusUpdateThrottle: 30000, // Increased to 30 seconds between status updates (was 5 seconds)
    cachedStatus: null,
    cachedConfig: null,
    cachedMetadata: null, // New: Cache for metadata
    metadataLoaded: false, // New: Track if metadata has been loaded once
    
    // Video feed stability variables
    lastStreamingStatus: false,
    videoFeedRefreshTimeout: null,
    
    /**
     * Initialize Camera Manager
     */
    init: function() {
        console.log('Initializing Camera Manager (cached data mode)...');
        
        // Initialize cached data storage
        this.cachedStatus = null;
        this.cachedConfig = null;
        this.cachedMetadata = null; // Initialize new cache
        this.metadataLoaded = false; // Track if metadata has been loaded once
        
        // Initialize video feed independently first
        this.initVideoFeed();
        
        // Setup WebSocket connection for status monitoring only
        this.initializeWebSocket();
        
        // Setup event handlers
        this.setupEventHandlers();
        this.setupFormHandlers();
        
        // Load metadata once when dashboard loads
        this.loadMetadataOnce();
        
        // Debug: Show metadata section after a delay to ensure it's loaded
        setTimeout(() => {
            this.toggleMetadataSection(true);
        }, 3000);
        
        console.log('Camera Manager initialized successfully (cached data mode)');
    },

    /**
     * Initialize video feed independently from WebSocket
     */
    initVideoFeed: function() {
        console.log('Initializing video feed independently...');
        
        // Setup video feed event handlers
        this.setupVideoFeedHandlers();
        
        // Start independent video feed status monitoring
        this.startVideoFeedMonitoring();
        
        console.log('Video feed initialized independently');
    },

    /**
     * Start independent video feed monitoring
     */
    startVideoFeedMonitoring: function() {
        // Start periodic status checks (independent of WebSocket)
        this.videoFeedRefreshTimeout = setTimeout(() => {
            this.updateVideoFeedStatus();
        }, 15000); // Check every 15 seconds
        
        console.log('Independent video feed monitoring started');
    },

    /**
     * Initialize WebSocket connection for camera namespace
     */
    initializeWebSocket: function() {
        if (typeof io === 'undefined') {
            console.log('Socket.IO not available, using HTTP API only');
            AICameraUtils.addLogMessage('log-container', 'Socket.IO not available, using HTTP API only', 'info');
            // Load status from HTTP API as fallback
            this.loadStatusFromAPI();
            return;
        }

        try {
            this.socket = io('/camera', {
                timeout: 10000, // Increased timeout
                reconnection: true,
                reconnectionAttempts: 2, // Reduced from 3 to 2
                reconnectionDelay: 5000, // Increased from 2000 to 5000
                maxReconnectionAttempts: 2, // Limit total reconnection attempts
                reconnectionDelayMax: 10000 // Maximum delay between attempts
            });
            this.setupSocketHandlers();
            console.log('WebSocket connection initialized');
        } catch (error) {
            console.error('Error initializing WebSocket:', error);
            AICameraUtils.addLogMessage('log-container', `WebSocket error: ${error.message}`, 'warning');
            // Load status from HTTP API as fallback
            this.loadStatusFromAPI();
        }
    },

    /**
     * Load camera status from HTTP API (fallback)
     */
    loadStatusFromAPI: function() {
        console.log('Loading camera status from HTTP API...');
        fetch('/camera/status')
            .then(response => {
                // Check if response is JSON
                const contentType = response.headers.get('content-type');
                if (!contentType || !contentType.includes('application/json')) {
                    throw new Error(`Expected JSON response, got ${contentType || 'unknown content type'}`);
                }
                return response.json();
            })
            .then(data => {
                if (data && data.success && data.status) {
                    console.log('✅ Status loaded from HTTP API:', data.status);
                    this.cachedStatus = data.status;
                    this.updateCameraStatus(data.status);
                } else {
                    console.error('❌ Invalid status data from HTTP API:', data);
                    AICameraUtils.addLogMessage('log-container', 'Invalid status data from HTTP API', 'warning');
                }
            })
            .catch(error => {
                console.error('❌ Error loading status from HTTP API:', error);
                AICameraUtils.addLogMessage('log-container', `HTTP API error: ${error.message}`, 'warning');
                
                // Don't retry immediately on HTTP API errors
                // The WebSocket will attempt reconnection instead
            });
    },

    /**
     * Setup WebSocket event handlers
     */
    setupSocketHandlers: function() {
        if (!this.socket) return;

        this.socket.on('connect', () => {
            console.log('✅ Connected to camera service');
            AICameraUtils.addLogMessage('log-container', 'Connected to camera service', 'success');
            // Request initial status
            this.socket.emit('camera_status_request');
            
            // Set a timeout to fallback to HTTP API if no response received
            setTimeout(() => {
                if (!this.cachedStatus) {
                    console.log('No status received from WebSocket, falling back to HTTP API...');
                    this.loadStatusFromAPI();
                }
            }, 5000); // Increased from 3 to 5 seconds for WebSocket response
        });

        this.socket.on('disconnect', () => {
            console.log('❌ Disconnected from camera service');
            AICameraUtils.addLogMessage('log-container', 'Disconnected from camera service, using HTTP API fallback', 'warning');
            // Load status from HTTP API as fallback
            this.loadStatusFromAPI();
        });

        this.socket.on('connect_error', (error) => {
            console.log('WebSocket connection error:', error.message);
            AICameraUtils.addLogMessage('log-container', 'WebSocket connection failed, using HTTP API fallback', 'warning');
            // Load status from HTTP API as fallback
            this.loadStatusFromAPI();
        });

        this.socket.on('camera_status_update', (data) => {
            console.log('📡 Received camera_status_update:', data);
            if (data && data.success && data.status) {
                console.log('✅ Status data received:', data.status);
                this.cachedStatus = data.status; // Cache status
                this.updateCameraStatus(data.status);
                if (data.config) {
                    console.log('✅ Config data received:', data.config);
                    this.cachedConfig = data.config; // Cache config
                    this.updateConfigForm(data.config);
                }
                
                // CRITICAL: Video feed is completely independent - no status-based control
                // WebSocket status updates should NEVER affect video feed operation
                console.log('🎯 Video feed status: Completely independent from WebSocket status updates');
                console.log('🎯 Video feed continues operating regardless of status changes');
                
                // Explicitly prevent any video feed actions based on status
                if (data.status.streaming_status) {
                    console.log(`🎯 Streaming status: ${data.status.streaming_status} - Video feed unaffected`);
                }
                if (data.status.camera_status) {
                    console.log(`🎯 Camera status: ${data.status.camera_status} - Video feed unaffected`);
                }
            } else {
                console.error('❌ Invalid status data received:', data);
                AICameraUtils.addLogMessage('log-container', 'Invalid status data received', 'error');
            }
        });

        this.socket.on('camera_control_response', (response) => {
            console.log('📡 Received camera_control_response:', response);
            this.handleControlResponse(response);
        });

        this.socket.on('camera_config_response', (response) => {
            console.log('📡 Received camera_config_response:', response);
            this.handleConfigResponse(response);
        });
    },

    /**
     * Setup event handlers for control buttons
     */
    setupEventHandlers: function() {
        // Control buttons
        const startBtn = document.getElementById('start-btn');
        const stopBtn = document.getElementById('stop-btn');
        const restartBtn = document.getElementById('restart-btn');
        const captureBtn = document.getElementById('capture-btn');

        if (startBtn) startBtn.addEventListener('click', () => this.sendCommand('start'));
        if (stopBtn) stopBtn.addEventListener('click', () => this.sendCommand('stop'));
        if (restartBtn) restartBtn.addEventListener('click', () => this.sendCommand('restart'));
        if (captureBtn) captureBtn.addEventListener('click', () => this.sendCommand('capture'));

        // Refresh video button
        const refreshVideoBtn = document.getElementById('refresh-video-btn');
        if (refreshVideoBtn) {
            refreshVideoBtn.addEventListener('click', () => this.refreshVideoFeed());
        }

        // Test video button
        const testVideoBtn = document.getElementById('test-video-btn');
        if (testVideoBtn) {
            testVideoBtn.addEventListener('click', () => this.testVideoFeed());
        }

        // Video feed error handling
        this.setupVideoFeedHandlers();
    },

    /**
     * Setup form handlers for configuration
     */
    setupFormHandlers: function() {
        // Configuration form
        const configForm = document.getElementById('config-form');
        if (configForm) {
            configForm.addEventListener('submit', (e) => this.handleConfigSubmit(e));
        }

        // Range sliders
        this.setupRangeSliders();
    },

    /**
     * Setup range sliders with live updates
     */
    setupRangeSliders: function() {
        const sliders = [
            { slider: 'framerate', display: 'framerate-value' },
            { slider: 'brightness', display: 'brightness-value' },
            { slider: 'contrast', display: 'contrast-value' },
            { slider: 'saturation', display: 'saturation-value' }
        ];

        sliders.forEach(({ slider, display }) => {
            const sliderElement = document.getElementById(slider);
            const displayElement = document.getElementById(display);
            
            if (sliderElement && displayElement) {
                sliderElement.addEventListener('input', () => {
                    displayElement.textContent = sliderElement.value;
                });
            }
        });
    },

    /**
     * Send camera command
     */
    sendCommand: function(command) {
        if (!this.socket || !this.socket.connected) {
            AICameraUtils.showToast('Not connected to camera service', 'warning');
            return;
        }

        this.socket.emit('camera_control', { command: command });
        AICameraUtils.addLogMessage('log-container', `Sending ${command} command...`, 'info');
    },

    /**
     * Handle control response
     */
    handleControlResponse: function(response) {
        const message = response.success ? 
            (response.message || 'Command executed successfully') :
            (response.error || response.message || 'Command failed');
        
        AICameraUtils.addLogMessage('log-container', `Camera control: ${message}`, 
            response.success ? 'success' : 'error');
        
        if (response.success) {
            AICameraUtils.showToast(message, 'success');
        } else {
            AICameraUtils.showToast(message, 'error');
        }
    },

    /**
     * Handle configuration response
     */
    handleConfigResponse: function(response) {
        const message = response.success ? 
            (response.message || 'Configuration updated successfully') :
            (response.error || 'Configuration update failed');
        
        AICameraUtils.addLogMessage('log-container', `Configuration: ${message}`, 
            response.success ? 'success' : 'error');
        
        AICameraUtils.showToast(message, response.success ? 'success' : 'error');
    },

    /**
     * Update camera status display
     */
    updateCameraStatus: function(status) {
        console.log('Updating camera status:', status);

        // Update status indicator based on API reference format
        let statusClass = 'status-offline';
        let statusText = 'Offline';

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

        const statusIndicator = document.getElementById('camera-status-main');
        const statusTextElement = document.getElementById('camera-status-text-main');
        
        if (statusIndicator) {
            statusIndicator.className = `status-indicator ${statusClass}`;
            console.log('Status indicator updated:', statusClass);
        } else {
            console.warn('Status indicator element not found: camera-status-main');
        }
        
        if (statusTextElement) {
            statusTextElement.textContent = statusText;
            console.log('Status text updated:', statusText);
        } else {
            console.warn('Status text element not found: camera-status-text-main');
        }

        // Update video status based on camera status
        if (status.initialized && status.streaming) {
            this.updateVideoStatus('hidden', '');
            // Force refresh video feed when camera starts streaming
            this.refreshVideoFeed();
        } else if (status.initialized && !status.streaming) {
            this.updateVideoStatus('offline', 'Camera ready but not streaming');
        } else {
            this.updateVideoStatus('offline', 'Camera not initialized');
        }

        // Update detailed status content
        this.updateStatusContent(status);
    },

    /**
     * Update detailed status content according to API reference
     */
    updateStatusContent: function(status) {
        const statusContent = document.getElementById('status-content');
        if (!statusContent) {
            console.warn('Status content element not found');
            return;
        }

        // Extract data according to API reference format
        const cameraHandler = status.camera_handler || {};
        const cameraProps = cameraHandler.camera_properties || {};
        const currentConfig = cameraHandler.current_config || {};
        const mainConfig = currentConfig.main || {};
        const controls = currentConfig.controls || {};
        
        console.log('Status update variables:', {
            cameraHandler: cameraHandler,
            cameraProps: cameraProps,
            currentConfig: currentConfig,
            mainConfig: mainConfig,
            controls: controls
        });
        
        // Get resolution from main config according to API reference
        let resolution = 'Unknown';
        if (mainConfig.size && Array.isArray(mainConfig.size)) {
            resolution = `${mainConfig.size[0]}x${mainConfig.size[1]}`;
        }
        
        // Get sensor model from camera properties according to API reference
        let sensorModel = 'Unknown';
        if (cameraProps && cameraProps.Model) {
            sensorModel = `${cameraProps.Model}`;
        }
        
        // Get framerate from metadata
        let framerate = 'Unknown';
        if (currentConfig.controls && currentConfig.controls.FrameDurationLimits) {
            const frameDuration = currentConfig.controls.FrameDurationLimits[0];
            framerate = `${Math.round(1000000 / frameDuration)} FPS`; // ✅ "30 FPS"
        } else if (status.config && status.config.framerate) {
            framerate = `${status.config.framerate} FPS`;
        }

        console.log('Calculated values:', {
            resolution: resolution,
            sensorModel: sensorModel,
            framerate: framerate,
            uptime: status.uptime
        });

        // Compact status display
        const statusHtml = `
            <div class="row g-1">
                <div class="col-6">
                    <small class="text-muted">Status:</small><br>
                    <strong class="text-${status.initialized && status.streaming ? 'success' : status.initialized ? 'warning' : 'danger'}">
                        ${status.initialized && status.streaming ? 'Online' : status.initialized ? 'Ready' : 'Offline'}
                    </strong>
                </div>
                <div class="col-6">
                    <small class="text-muted">Resolution:</small><br>
                    <strong>${resolution}</strong>
                </div>
            </div>
            <div class="row g-1 mt-1">
                <div class="col-6">
                    <small class="text-muted">Frame Rate:</small><br>
                    <strong>${framerate}</strong>
                </div>
                <div class="col-6">
                    <small class="text-muted">Sensor:</small><br>
                    <strong>${sensorModel}</strong>
                </div>
            </div>
            ${status.frame_count ? `
                <div class="row g-1 mt-1">
                    <div class="col-6">
                        <small class="text-muted">Frame Count:</small><br>
                        <strong>${status.frame_count.toLocaleString()}</strong>
                    </div>
                    <div class="col-6">
                        <small class="text-muted">Avg FPS:</small><br>
                        <strong>${status.average_fps ? status.average_fps.toFixed(1) : '0.0'}</strong>
                    </div>
                </div>
            ` : ''}
            ${status.uptime ? `
                <div class="row g-1 mt-1">
                    <div class="col-12">
                        <small class="text-muted">Uptime:</small><br>
                        <strong>${AICameraUtils.formatDuration(status.uptime)}</strong>
                    </div>
                </div>
            ` : ''}
        `;
        
        statusContent.innerHTML = statusHtml;
        console.log('Status content updated successfully');
    },

    /**
     * Update configuration form with current values
     */
    updateConfigForm: function(config) {
        // Handle resolution from main configuration
        if (config.main && config.main.size) {
            const resolutionSelect = document.getElementById('resolution');
            if (resolutionSelect) {
                resolutionSelect.value = `(${config.main.size[0]}, ${config.main.size[1]})`;
            }
        } else if (config.resolution) {
            const resolutionSelect = document.getElementById('resolution');
            if (resolutionSelect) {
                resolutionSelect.value = `(${config.resolution[0]}, ${config.resolution[1]})`;
            }
        }

        // Handle controls from configuration
        const controls = config.controls || {};
        
        // Calculate framerate from FrameDurationLimits
        let framerate = 30; // Default
        if (controls.FrameDurationLimits && Array.isArray(controls.FrameDurationLimits)) {
            const frameDuration = controls.FrameDurationLimits[0];
            framerate = Math.round(1000000 / frameDuration);
        }
        
        // Update framerate slider and display
        const framerateSlider = document.getElementById('framerate');
        const framerateDisplay = document.getElementById('framerate-value');
        if (framerateSlider) framerateSlider.value = framerate;
        if (framerateDisplay) framerateDisplay.textContent = framerate;
        
        // Handle other controls
        const configMappings = [
            { key: 'brightness', elementId: 'brightness', displayId: 'brightness-value' },
            { key: 'contrast', elementId: 'contrast', displayId: 'contrast-value' },
            { key: 'saturation', elementId: 'saturation', displayId: 'saturation-value' },
            { key: 'awb_mode', elementId: 'awb_mode' }
        ];

        configMappings.forEach(({ key, elementId, displayId }) => {
            // Check both config and controls for values
            let value = config[key];
            if (value === undefined && controls[key] !== undefined) {
                value = controls[key];
            }
            
            if (value !== undefined) {
                const element = document.getElementById(elementId);
                if (element) {
                    element.value = value;
                    
                    if (displayId) {
                        const displayElement = document.getElementById(displayId);
                        if (displayElement) {
                            displayElement.textContent = value;
                        }
                    }
                }
            }
        });
    },

    /**
     * Handle configuration form submission
     */
    handleConfigSubmit: function(e) {
        e.preventDefault();
        
        if (!this.socket || !this.socket.connected) {
            AICameraUtils.showToast('Not connected to camera service', 'warning');
            return;
        }

        const formData = new FormData(e.target);
        const config = {};
        
        for (let [key, value] of formData.entries()) {
            if (key === 'resolution') {
                // Parse resolution string
                const match = value.match(/\((\d+),\s*(\d+)\)/);
                if (match) {
                    config.resolution = [parseInt(match[1]), parseInt(match[2])];
                }
            } else if (['framerate', 'brightness', 'contrast', 'saturation'].includes(key)) {
                config[key] = parseFloat(value);
            } else {
                config[key] = value;
            }
        }
        
        this.socket.emit('camera_config_update', { config: config });
        AICameraUtils.addLogMessage('log-container', 'Updating camera configuration...', 'info');
    },

    /**
     * Refresh video feed independently from WebSocket
     */
    refreshVideoFeed: function() {
        const now = Date.now();
        const cooldown = 2000; // 2 second cooldown
        
        // Check cooldown to prevent rapid refreshes
        if (now - this.lastVideoRefresh < cooldown) {
            console.log(`Video feed refresh cooldown active (${cooldown - (now - this.lastVideoRefresh)}ms remaining)`);
            return;
        }
        
        console.log('🔄 Refreshing video feed independently...');
        this.lastVideoRefresh = now;
        
        // Reset error state
        this.videoErrorState = false;
        this.videoErrorCount = 0;
        
        // Don't show loading state for refresh - video should continue showing
        // Only show brief status update in console
        console.log('Video feed refresh in progress...');
        
        // Get video feed element
        const videoFeed = document.getElementById('video-feed');
        if (!videoFeed) {
            console.error('Video feed element not found');
            return;
        }
        
        // Force refresh by changing src with timestamp
        const timestamp = Date.now();
        const newSrc = `/camera/video_feed?t=${timestamp}`;
        
        console.log(`Setting video feed source: ${newSrc}`);
        videoFeed.src = newSrc;
        
        // Set timeout to check if video loaded successfully
        setTimeout(() => {
            this.updateVideoFeedStatus();
        }, 3000);
    },

    /**
     * Update video feed status independently
     */
    updateVideoFeedStatus: function() {
        const videoFeed = document.getElementById('video-feed');
        if (!videoFeed) return;
        
        // Check if video is actually displaying content
        const isVideoWorking = videoFeed.complete && 
                              videoFeed.naturalWidth > 0 && 
                              videoFeed.naturalHeight > 0 &&
                              !this.videoErrorState;
        
        if (isVideoWorking) {
            console.log('✅ Video feed is working properly');
            // Hide status overlay when video is working
            this.updateVideoStatus('hidden', '');
            this.videoErrorCount = 0;
            this.videoErrorState = false;
        } else {
            console.log('⚠️ Video feed may have issues');
            // Only show warning status if there are actual issues
            if (this.videoErrorState || this.videoErrorCount > 0) {
                this.updateVideoStatus('warning', 'Video feed may need refresh');
            } else {
                // Hide status overlay if no issues detected
                this.updateVideoStatus('hidden', '');
            }
        }
        
        // Schedule next status check (independent of WebSocket)
        this.videoFeedRefreshTimeout = setTimeout(() => {
            this.updateVideoFeedStatus();
        }, 15000); // Check every 15 seconds
    },

    /**
     * Handle video feed errors with intelligent fallback and better chunked encoding support
     */
    handleVideoFeedError: function(e) {
        console.log('Video feed error detected:', e);
        this.videoErrorCount++;
        this.videoErrorState = true;
        
        // Check for specific error types
        const isChunkedError = e.message && e.message.includes('ERR_INCOMPLETE_CHUNKED_ENCODING');
        const isNetworkError = e.message && (e.message.includes('ERR_') || e.message.includes('Failed to fetch'));
        const isTimeoutError = e.message && e.message.includes('timeout');
        const isLoadError = e.type === 'error' && e.target && e.target.tagName === 'IMG';
        
        // Log specific error type
        if (isChunkedError) {
            console.warn('Chunked encoding error detected - this usually means the video stream is incomplete');
            AICameraUtils.addLogMessage('log-container', 'Video stream incomplete - server may be having issues', 'warning');
            
            // For chunked encoding errors, try to recover with a fresh connection
            this.attemptChunkedEncodingRecovery();
            
        } else if (isNetworkError) {
            console.warn('Network error detected - connection issues with video feed');
            AICameraUtils.addLogMessage('log-container', 'Network error with video feed - check connection', 'warning');
            
        } else if (isTimeoutError) {
            console.warn('Timeout error detected - video feed taking too long to respond');
            AICameraUtils.addLogMessage('log-container', 'Video feed timeout - server may be overloaded', 'warning');
            
        } else if (isLoadError) {
            console.warn('Image load error detected - video feed element failed to load');
            AICameraUtils.addLogMessage('log-container', 'Video feed image load failed - attempting recovery', 'warning');
            
        } else {
            console.warn('Unknown video feed error:', e.message || e.type);
            AICameraUtils.addLogMessage('log-container', 'Unknown video feed error - check console for details', 'warning');
        }
        
        // Update status based on error type
        if (isChunkedError) {
            this.updateVideoStatus('error', 'Video stream incomplete - attempting recovery...');
        } else if (isNetworkError) {
            this.updateVideoStatus('error', 'Network error - check connection');
        } else if (isTimeoutError) {
            this.updateVideoStatus('error', 'Video feed timeout - server busy');
        } else if (isLoadError) {
            this.updateVideoStatus('error', 'Video feed load error - attempting recovery...');
        } else {
            this.updateVideoStatus('error', 'Video feed error - use refresh button');
        }
        
        // Only retry for certain error types
        if (this.videoErrorCount <= 2 && (isNetworkError || isTimeoutError)) {
            const backoff = Math.min(this.videoErrorBackoff * Math.pow(2, this.videoErrorCount - 1), this.maxVideoErrorBackoff);
            console.log(`Video feed error ${this.videoErrorCount}/2, retrying in ${backoff}ms`);
            
            setTimeout(() => {
                this.refreshVideoFeed();
            }, backoff);
        } else {
            console.error('Video feed error limit reached, stopping automatic retries');
            AICameraUtils.addLogMessage('log-container', 'Video feed error limit reached - manual refresh recommended', 'error');
            
            // Show user-friendly message
            this.showVideoFeedErrorHelp();
            
            // Reset error count after a longer delay to allow manual intervention
            setTimeout(() => {
                this.videoErrorCount = 0;
                console.log('Video feed error count reset, automatic retries re-enabled');
            }, 30000); // 30 seconds
        }
    },
    
    /**
     * Attempt recovery from chunked encoding errors
     */
    attemptChunkedEncodingRecovery: function() {
        console.log('🔄 Attempting chunked encoding error recovery...');
        
        // Wait a bit before attempting recovery
        setTimeout(() => {
            // Try to refresh video feed with a new timestamp
            const videoFeed = document.getElementById('video-feed');
            if (videoFeed) {
                const timestamp = Date.now();
                const newSrc = `/camera/video_feed?t=${timestamp}&recovery=1`;
                
                console.log(`Attempting recovery with new source: ${newSrc}`);
                
                // Set new source
                videoFeed.src = newSrc;
                
                // Monitor recovery attempt
                setTimeout(() => {
                    this.updateVideoFeedStatus();
                }, 5000); // Check after 5 seconds
            }
        }, 2000); // Wait 2 seconds before recovery attempt
    },
    
    /**
     * Show helpful information for video feed errors
     */
    showVideoFeedErrorHelp: function() {
        const helpMessage = `
            <div class="alert alert-warning" role="alert">
                <h6><i class="fas fa-exclamation-triangle"></i> Video Feed Issue Detected</h6>
                <p class="mb-2">The video feed is experiencing issues. Here are some things to try:</p>
                <ul class="mb-2">
                    <li>Click the <strong>Refresh Video</strong> button above</li>
                    <li>Check if the camera is properly connected</li>
                    <li>Refresh the browser page</li>
                    <li>Check the server logs for errors</li>
                </ul>
                <button class="btn btn-sm btn-warning" onclick="CameraManager.manualRefreshVideo()">
                    <i class="fas fa-sync-alt"></i> Refresh Video Feed
                </button>
            </div>
        `;
        
        // Add to log container
        AICameraUtils.addLogMessage('log-container', helpMessage, 'warning', true);
    },

    /**
     * Handle successful video feed load
     */
    handleVideoFeedSuccess: function() {
        console.log('Video feed loaded successfully');
        this.videoErrorCount = 0;
        this.videoErrorState = false;
        this.updateVideoStatus('hidden', '');
        AICameraUtils.addLogMessage('log-container', 'Video feed loaded successfully', 'success');
    },

    /**
     * Attempt video feed recovery
     */
    attemptVideoFeedRecovery: function() {
        if (this.videoErrorState) {
            console.log('Attempting video feed recovery...');
            AICameraUtils.addLogMessage('log-container', 'Attempting video feed recovery...', 'info');
            this.videoErrorCount = 0;
            this.videoErrorState = false;
            this.refreshVideoFeed();
        }
    },

    /**
     * Manual video refresh function (user-initiated)
     */
    manualRefreshVideo: function() {
        console.log('Manual video feed refresh requested by user');
        AICameraUtils.addLogMessage('log-container', 'Manual video feed refresh requested', 'info');
        
        // Reset error states
        this.videoErrorCount = 0;
        this.videoErrorState = false;
        this.lastVideoRefresh = 0; // Force refresh regardless of cooldown
        
        // Perform refresh
        this.refreshVideoFeed();
    },
    

    /**
     * Verify video feed independence from WebSocket
     */
    verifyVideoFeedIndependence: function() {
        console.log('🔍 Verifying video feed independence from WebSocket...');
        
        // Check if video feed is operating independently
        const videoFeed = document.getElementById('video-feed');
        if (!videoFeed) {
            console.warn('⚠️ Video feed element not found');
            return false;
        }
        
        // Check video feed source
        const currentSrc = videoFeed.src;
        if (currentSrc && currentSrc.includes('/camera/video_feed')) {
            console.log('✅ Video feed source is correct and independent');
        } else {
            console.warn('⚠️ Video feed source may not be independent');
        }
        
        // Check if video feed has error state
        if (this.videoErrorState) {
            console.log('⚠️ Video feed has error state, but this is independent of WebSocket');
        } else {
            console.log('✅ Video feed is in normal state');
        }
        
        // Check WebSocket connection status
        if (this.socket && this.socket.connected) {
            console.log('✅ WebSocket is connected, but video feed operates independently');
        } else {
            console.log('⚠️ WebSocket is disconnected, but video feed continues independently');
        }
        
        console.log('🎯 Video feed independence verification complete');
        return true;
    },

    /**
     * Test video feed functionality
     */
    testVideoFeed: function() {
        console.log('Testing video feed...');
        AICameraUtils.addLogMessage('log-container', 'Testing video feed...', 'info');
        
        AICameraUtils.apiRequest('/camera/video_test')
            .then(data => {
                console.log('Video test response:', data);
                if (data && data.success) {
                    const results = data.video_test_results;
                    const message = `Video Test Results:
                        Camera Initialized: ${results.camera_initialized}
                        Camera Streaming: ${results.camera_streaming}
                        Frame Capture: ${results.frame_capture_success}
                        Frame Shape: ${results.frame_shape || 'N/A'}
                        Frame Error: ${results.frame_error || 'None'}`;
                    
                    AICameraUtils.addLogMessage('log-container', message, 'success');
                    AICameraUtils.showToast('Video test completed - check logs', 'success');
                } else {
                    AICameraUtils.addLogMessage('log-container', 'Video test failed', 'error');
                    AICameraUtils.showToast('Video test failed', 'error');
                }
            })
            .catch(error => {
                console.error('Video test error:', error);
                AICameraUtils.addLogMessage('log-container', `Video test error: ${error.message}`, 'error');
                AICameraUtils.showToast('Video test error', 'error');
            });
    },
    
    /**
     * Update video status overlay - only show when necessary
     */
    updateVideoStatus: function(status, message) {
        const videoStatus = document.getElementById('video-status');
        if (!videoStatus) return;
        
        const statusContent = videoStatus.querySelector('.video-status-content');
        if (!statusContent) return;
        
        const icon = statusContent.querySelector('i');
        const text = statusContent.querySelector('span');
        
        // Only show status overlay for critical states
        if (status === 'hidden' || status === 'success') {
            videoStatus.classList.remove('show');
            return;
        }
        
        // Show status overlay only for important states
        videoStatus.classList.add('show');
        
        if (status === 'loading') {
            // Only show loading for initial load, not for refresh
            if (message === 'Loading video feed...') {
                icon.className = 'fas fa-spinner fa-spin';
                text.textContent = message;
            } else {
                // For refresh operations, show briefly then hide
                icon.className = 'fas fa-sync-alt fa-spin';
                text.textContent = message;
                
                // Auto-hide refresh status after 2 seconds
                setTimeout(() => {
                    if (videoStatus.classList.contains('show')) {
                        this.updateVideoStatus('hidden', '');
                    }
                }, 2000);
            }
        } else if (status === 'error') {
            icon.className = 'fas fa-exclamation-triangle';
            text.textContent = message || 'Video feed error';
        } else if (status === 'warning') {
            icon.className = 'fas fa-exclamation-circle';
            text.textContent = message || 'Video feed warning';
        } else if (status === 'offline') {
            icon.className = 'fas fa-video-slash';
            text.textContent = message || 'Camera offline';
        }
    },
    


    /**
     * Update from cached data (no API calls)
     */
    updateFromCachedData: function() {
        if (this.cachedStatus) {
            this.updateCameraStatus(this.cachedStatus);
        }
        if (this.cachedConfig) {
            this.updateConfigForm(this.cachedConfig);
        }
        
        // Update video feed status
        this.updateVideoFeedStatus();
    },

    /**
     * Load metadata once when dashboard loads (no periodic fetching)
     */
    loadMetadataOnce: function() {
        if (this.metadataLoaded) {
            console.log('Metadata already loaded, skipping...');
            return;
        }
        
        console.log('Loading camera metadata once...');
        AICameraUtils.addLogMessage('log-container', 'Loading camera metadata...', 'info');
        
        // Load metadata from debug endpoint
        AICameraUtils.apiRequest('/camera/debug_metadata')
            .then(data => {
                console.log('Raw metadata response:', data);
                
                if (data && data.success && data.debug_info) {
                    console.log('Metadata loaded successfully:', data);
                    this.cachedMetadata = data;
                    this.metadataLoaded = true;
                    
                    // Update metadata display
                    this.updateMetadataDisplay(data);
                    
                    AICameraUtils.addLogMessage('log-container', 'Camera metadata loaded successfully', 'success');
                } else {
                    console.error('Failed to load metadata - invalid response structure:', data);
                    AICameraUtils.addLogMessage('log-container', 'Failed to load metadata - invalid response structure', 'error');
                }
            })
            .catch(error => {
                console.error('Metadata load error:', error);
                AICameraUtils.addLogMessage('log-container', `Metadata load error: ${error.message}`, 'error');
            });
    },

    /**
     * Show or hide metadata section
     */
    toggleMetadataSection: function(show = true) {
        const metadataSection = document.getElementById('metadata-section');
        if (metadataSection) {
            metadataSection.style.display = show ? 'block' : 'none';
            console.log(`Metadata section ${show ? 'shown' : 'hidden'}`);
        }
    },

    /**
     * Toggle metadata section visibility (called from HTML onclick)
     */
    toggleMetadata: function() {
        const metadataSection = document.getElementById('metadata-section');
        const metadataContent = document.getElementById('metadata-content');
        const toggleIcon = document.getElementById('metadata-toggle-icon');
        
        if (metadataSection && metadataContent) {
            const isVisible = metadataContent.style.display !== 'none';
            
            if (isVisible) {
                metadataContent.style.display = 'none';
                if (toggleIcon) toggleIcon.className = 'fas fa-chevron-right';
            } else {
                metadataContent.style.display = 'block';
                if (toggleIcon) toggleIcon.className = 'fas fa-chevron-down';
            }
            
            console.log(`Metadata content ${isVisible ? 'hidden' : 'shown'}`);
        }
    },

    /**
     * Refresh metadata (called from HTML onclick)
     */
    refreshMetadata: function() {
        console.log('Refreshing metadata...');
        AICameraUtils.addLogMessage('log-container', 'Refreshing camera metadata...', 'info');
        
        // Reset metadata loaded flag to force reload
        this.metadataLoaded = false;
        this.loadMetadataOnce();
    },

    /**
     * Export metadata (called from HTML onclick)
     */
    exportMetadata: function() {
        if (this.cachedMetadata) {
            const dataStr = JSON.stringify(this.cachedMetadata, null, 2);
            const dataBlob = new Blob([dataStr], {type: 'application/json'});
            const url = URL.createObjectURL(dataBlob);
            const link = document.createElement('a');
            link.href = url;
            link.download = `camera_metadata_${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}.json`;
            link.click();
            URL.revokeObjectURL(url);
            
            console.log('Metadata exported successfully');
            AICameraUtils.addLogMessage('log-container', 'Metadata exported successfully', 'success');
        } else {
            console.log('No metadata available to export');
            AICameraUtils.addLogMessage('log-container', 'No metadata available to export', 'warning');
        }
    },

    /**
     * Update metadata display with comprehensive table view and Thai descriptions
     */
    updateMetadataDisplay: function(metadata) {
        try {
            // Validate metadata object
            if (!metadata) {
                console.error('Metadata object is null or undefined');
                AICameraUtils.addLogMessage('log-container', 'Error: Metadata object is null or undefined', 'error');
                return;
            }
            
            // Update metadata section if it exists
            const metadataSection = document.getElementById('metadata-section');
            if (metadataSection) {
                // Show the metadata section
                metadataSection.style.display = 'block';
                
                const metadataContent = document.getElementById('metadata-content');
                if (metadataContent) {
                    // Format and display metadata in table format
                    let html = '<div class="metadata-table-container">';
                    
                    // Metadata descriptions in Thai
                    const thaiDescriptions = {
                    // Camera Properties
                        'Model': 'รุ่นของกล้อง',
                        'Location': 'ตำแหน่งของกล้อง',
                        'Revision': 'เวอร์ชันของฮาร์ดแวร์',
                        'SerialNumber': 'หมายเลขซีเรียล',
                        'LensModel': 'รุ่นของเลนส์',
                        'LensLocation': 'ตำแหน่งของเลนส์',
                        
                        // Configuration
                        'size': 'ขนาดภาพ (ความกว้าง x ความสูง)',
                        'format': 'รูปแบบสีของภาพ',
                        'framerate': 'อัตราเฟรมต่อวินาที',
                        'brightness': 'ความสว่าง (-1 ถึง 1)',
                        'contrast': 'ความคมชัด (0 ถึง 2)',
                        'saturation': 'ความอิ่มตัวของสี (0 ถึง 2)',
                        'sharpness': 'ความคมชัดของภาพ (0 ถึง 2)',
                        'exposure_time': 'เวลาการเปิดรับแสง (ไมโครวินาที)',
                        'analogue_gain': 'การขยายสัญญาณแอนะล็อก',
                        'digital_gain': 'การขยายสัญญาณดิจิทัล',
                        'awb_mode': 'โหมดสมดุลแสงขาว',
                        'ae_enabled': 'เปิดใช้งานการเปิดรับแสงอัตโนมัติ',
                        'awb_enabled': 'เปิดใช้งานสมดุลแสงขาวอัตโนมัติ',
                        'af_enabled': 'เปิดใช้งานการโฟกัสอัตโนมัติ',
                        
                        // Status
                        'initialized': 'สถานะการเริ่มต้นกล้อง',
                        'streaming': 'สถานะการสตรีมวิดีโอ',
                        'frame_count': 'จำนวนเฟรมที่ถ่ายได้',
                        'uptime': 'เวลาทำงานของกล้อง',
                        'temperature': 'อุณหภูมิของกล้อง',
                        'error_count': 'จำนวนข้อผิดพลาด',
                        'last_error': 'ข้อผิดพลาดล่าสุด',
                        
                        // Manager Status
                        'auto_start_enabled': 'เปิดใช้งานการเริ่มต้นอัตโนมัติ',
                        'auto_start_uptime': 'เวลาทำงานตั้งแต่เริ่มต้นอัตโนมัติ',
                        'last_capture_time': 'เวลาถ่ายภาพล่าสุด',
                        'total_captures': 'จำนวนภาพที่ถ่ายทั้งหมด',
                        'memory_usage': 'การใช้หน่วยความจำ',
                        'cpu_usage': 'การใช้ CPU',
                        
                        // Camera Metadata (from actual API response)
                        'ExposureTime': 'เวลาการเปิดรับแสง (ไมโครวินาที)',
                        'AnalogueGain': 'การขยายสัญญาณแอนะล็อก',
                        'DigitalGain': 'การขยายสัญญาณดิจิทัล',
                        'FocusFoM': 'คุณภาพการโฟกัส (Figure of Merit)',
                        'LensPosition': 'ตำแหน่งเลนส์',
                        'SensorTemperature': 'อุณหภูมิเซ็นเซอร์',
                        'ColourTemperature': 'อุณหภูมิสี (เคลวิน)',
                        'Lux': 'ความสว่าง (ลักซ์)',
                        'ColourGains': 'การขยายสี',
                        'FrameDuration': 'ระยะเวลาเฟรม (ไมโครวินาที)',
                        'FrameWallClock': 'เวลาผนังเฟรม',
                        'SensorTimestamp': 'เวลาสแตมป์เซ็นเซอร์',
                        'AeState': 'สถานะการเปิดรับแสงอัตโนมัติ',
                        'AfState': 'สถานะการโฟกัสอัตโนมัติ',
                        'AfPauseState': 'สถานะการหยุดการโฟกัสอัตโนมัติ',
                        'ScalerCrop': 'การครอบตัดสเกล',
                        'ScalerCrops': 'การครอบตัดสเกลหลายรายการ',
                        'SensorBlackLevels': 'ระดับสีดำของเซ็นเซอร์',
                        'ColourCorrectionMatrix': 'เมทริกซ์การแก้ไขสี',
                        'total_gain': 'การขยายรวม',
                        'frame_timestamp': 'เวลาสแตมป์เฟรม',
                        'request_timestamp': 'เวลาสแตมป์คำขอ',
                        'awb_gains': 'การขยายสมดุลแสงขาวอัตโนมัติ',
                        'af_state': 'สถานะการโฟกัสอัตโนมัติ'
                    };
                    
                    // Helper function to format value
                    const formatValue = (value) => {
                        if (value === null || value === undefined) return 'ไม่ระบุ';
                        if (typeof value === 'boolean') return value ? 'เปิดใช้งาน' : 'ปิดใช้งาน';
                        if (typeof value === 'number') {
                            if (value > 1000000) return value.toLocaleString();
                            if (value > 1000) return value.toFixed(2);
                            return value.toString();
                        }
                        if (typeof value === 'object') return JSON.stringify(value, null, 2);
                        return value.toString();
                    };
                    
                    // Helper function to get Thai description
                    const getThaiDescription = (key) => {
                        return thaiDescriptions[key] || 'ไม่มีการอธิบาย';
                    };
                    
                    // Debug Information Section
                    if (metadata.debug_info) {
                        html += `
                            <div class="metadata-category">
                                <h5 class="category-title">
                                    <i class="fas fa-bug"></i> ข้อมูลการแก้ไขปัญหา (Debug Information)
                                </h5>
                                <div class="table-responsive">
                                    <table class="table table-sm table-striped metadata-table">
                                        <thead class="table-light">
                                            <tr>
                                                <th width="25%">คีย์ (Key)</th>
                                                <th width="35%">ค่า (Value)</th>
                                                <th width="40%">คำอธิบาย (Description)</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                        `;
                        
                        // Debug status
                        const debugStatus = [
                            { key: 'camera_initialized', value: metadata.debug_info.camera_initialized, desc: 'กล้องเริ่มต้นแล้ว' },
                            { key: 'camera_streaming', value: metadata.debug_info.camera_streaming, desc: 'กล้องกำลังสตรีม' },
                            { key: 'picam2_exists', value: metadata.debug_info.picam2_exists, desc: 'Picam2 มีอยู่' },
                            { key: 'picam2_started', value: metadata.debug_info.picam2_started, desc: 'Picam2 เริ่มต้นแล้ว' },
                            { key: 'success', value: metadata.debug_info.success, desc: 'การดำเนินการสำเร็จ' }
                        ];
                        
                        debugStatus.forEach(item => {
                            const statusClass = item.value ? 'text-success' : 'text-danger';
                            html += `
                                <tr>
                                    <td><code class="text-primary">${item.key}</code></td>
                                    <td><span class="${statusClass}">${formatValue(item.value)}</span></td>
                                    <td><small class="text-muted">${item.desc}</small></td>
                                </tr>
                            `;
                        });
                        
                        html += `
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                        `;
                    }
                    
                    // Extracted Metadata Section
                    if (metadata.debug_info && metadata.debug_info.extracted_metadata) {
                        const extracted = metadata.debug_info.extracted_metadata;
                        html += `
                            <div class="metadata-category">
                                <h5 class="category-title">
                                    <i class="fas fa-camera"></i> ข้อมูลเมทาดาต้าที่สกัด (Extracted Metadata)
                                </h5>
                                <div class="table-responsive">
                                    <table class="table table-sm table-striped metadata-table">
                                        <thead class="table-light">
                                            <tr>
                                                <th width="25%">คีย์ (Key)</th>
                                                <th width="35%">ค่า (Value)</th>
                                                <th width="40%">คำอธิบาย (Description)</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                        `;
                        
                        Object.entries(extracted).forEach(([key, value]) => {
                            html += `
                                <tr>
                                    <td><code class="text-primary">${key}</code></td>
                                    <td><span class="text-success">${formatValue(value)}</span></td>
                                    <td><small class="text-muted">${getThaiDescription(key)}</small></td>
                                </tr>
                            `;
                        });
                        
                        html += `
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                        `;
                    }
                    
                    // Complete Metadata Section
                    if (metadata.debug_info && metadata.debug_info.extracted_metadata && metadata.debug_info.extracted_metadata.complete_metadata) {
                        const complete = metadata.debug_info.extracted_metadata.complete_metadata;
                        html += `
                            <div class="metadata-category">
                                <h5 class="category-title">
                                    <i class="fas fa-database"></i> ข้อมูลเมทาดาต้าแบบสมบูรณ์ (Complete Metadata)
                                </h5>
                                <div class="table-responsive">
                                    <table class="table table-sm table-striped metadata-table">
                                        <thead class="table-light">
                                            <tr>
                                                <th width="25%">คีย์ (Key)</th>
                                                <th width="35%">ค่า (Value)</th>
                                                <th width="40%">คำอธิบาย (Description)</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                        `;
                        
                        Object.entries(complete).forEach(([key, value]) => {
                            html += `
                                <tr>
                                    <td><code class="text-primary">${key}</code></td>
                                    <td><span class="text-success">${formatValue(value)}</span></td>
                                    <td><small class="text-muted">${getThaiDescription(key)}</small></td>
                                </tr>
                            `;
                        });
                        
                        html += `
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                        `;
                    }
                    
                    // Debug Steps Section
                    if (metadata.debug_info && metadata.debug_info.steps) {
                        const steps = metadata.debug_info.steps;
                        html += `
                            <div class="metadata-category">
                                <h5 class="category-title">
                                    <i class="fas fa-list-ol"></i> ขั้นตอนการแก้ไขปัญหา (Debug Steps)
                                </h5>
                                <div class="table-responsive">
                                    <table class="table table-sm table-striped metadata-table">
                                        <thead class="table-light">
                                            <tr>
                                                <th width="25%">คีย์ (Key)</th>
                                                <th width="35%">ค่า (Value)</th>
                                                <th width="40%">คำอธิบาย (Description)</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                        `;
                        
                        const stepDescriptions = {
                            'step1_camera_ready': 'ขั้นตอนที่ 1: กล้องพร้อม',
                            'step2_picam2_started': 'ขั้นตอนที่ 2: Picam2 เริ่มต้นแล้ว',
                            'step3_capture_request': 'ขั้นตอนที่ 3: คำขอการจับภาพ',
                            'step4_get_metadata': 'ขั้นตอนที่ 4: รับเมทาดาต้า',
                            'step5_extract_metadata': 'ขั้นตอนที่ 5: สกัดเมทาดาต้า',
                            'step6_release_request': 'ขั้นตอนที่ 6: ปล่อยคำขอ'
                        };
                        
                        Object.entries(steps).forEach(([key, value]) => {
                            if (typeof value === 'boolean') {
                                const statusClass = value ? 'text-success' : 'text-danger';
                                html += `
                                    <tr>
                                        <td><code class="text-primary">${key}</code></td>
                                        <td><span class="${statusClass}">${formatValue(value)}</span></td>
                                        <td><small class="text-muted">${stepDescriptions[key] || 'ไม่มีการอธิบาย'}</small></td>
                                    </tr>
                                `;
                            }
                        });
                        
                        html += `
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                        `;
                    }
                    
                    // Timestamp
                    html += `
                        <div class="text-center mt-3">
                            <small class="text-muted">
                                <i class="fas fa-clock"></i> อัปเดตล่าสุด: ${new Date().toLocaleString('th-TH')}
                            </small>
                        </div>
                    `;
                    
                    html += '</div>';
                    metadataContent.innerHTML = html;
                }
            }
        } catch (error) {
            console.error('Error updating metadata display:', error);
        }
    },

    /**
     * Setup video feed event handlers with independence from WebSocket
     */
    setupVideoFeedHandlers: function() {
        console.log('Setting up video feed event handlers with independence from WebSocket');
        
        const videoFeed = document.getElementById('video-feed');
        if (!videoFeed) {
            console.error('Video feed element not found');
            return;
        }

        // Video feed load success
        videoFeed.addEventListener('load', () => {
            console.log('Video feed loaded successfully');
            this.handleVideoFeedSuccess();
        });

        // Video feed error handling
        videoFeed.addEventListener('error', (e) => {
            console.log('Video feed error event:', e);
            this.handleVideoFeedError(e);
        });

        // Video feed load start
        videoFeed.addEventListener('loadstart', () => {
            console.log('Video feed loading started');
            this.updateVideoStatus('loading', 'Loading video feed...');
        });

        // Video feed load end
        videoFeed.addEventListener('loadend', () => {
            console.log('Video feed loading completed');
            // Status will be updated by load or error event
        });

        // Initial video feed status check (independent of WebSocket)
        setTimeout(() => {
            this.updateVideoFeedStatus();
        }, 2000); // Check after 2 seconds
    },

    /**
     * Handle video feed errors with intelligent fallback
     */
    handleVideoFeedError: function(e) {
        console.log('Video feed error detected:', e);
        this.videoErrorCount++;
        
        // Check if it's a chunked encoding error
        const isChunkedError = e.message && e.message.includes('ERR_INCOMPLETE_CHUNKED_ENCODING');
        const isNetworkError = e.message && (e.message.includes('ERR_') || e.message.includes('Failed to fetch'));
        
        if (isChunkedError || isNetworkError) {
            console.warn('Network/streaming error detected, will attempt recovery');
            AICameraUtils.addLogMessage('log-container', 'Video stream error detected - attempting recovery', 'warning');
        }
        
        // Only retry if error count is low and we haven't recently tried
        if (this.videoErrorCount <= 2 && this.videoErrorCount <= this.maxVideoErrors) {
            const backoff = Math.min(this.videoErrorBackoff * Math.pow(2, this.videoErrorCount - 1), this.maxVideoErrorBackoff);
            console.log(`Video feed error ${this.videoErrorCount}/2, retrying in ${backoff}ms`);
            
            setTimeout(() => {
                this.refreshVideoFeed();
            }, backoff);
        } else {
            console.error('Video feed error limit reached, stopping automatic retries');
            this.updateVideoStatus('error', 'Video feed error - manual refresh recommended');
            AICameraUtils.addLogMessage('log-container', 'Video feed error - manual refresh recommended', 'warning');
            
            // Reset error count after a longer delay to allow manual intervention
            setTimeout(() => {
                this.videoErrorCount = 0;
                console.log('Video feed error count reset, automatic retries re-enabled');
            }, 30000); // 30 seconds
        }
    },

    /**
     * Handle successful video feed load
     */
    handleVideoFeedSuccess: function() {
        console.log('Video feed loaded successfully');
        this.videoErrorCount = 0;
        this.videoErrorState = false;
        this.updateVideoStatus('hidden', '');
        AICameraUtils.addLogMessage('log-container', 'Video feed loaded successfully', 'success');
    },

    /**
     * Attempt video feed recovery
     */
    attemptVideoFeedRecovery: function() {
        if (this.videoErrorState) {
            console.log('Attempting video feed recovery...');
            AICameraUtils.addLogMessage('log-container', 'Attempting video feed recovery...', 'info');
            this.videoErrorCount = 0;
            this.videoErrorState = false;
            this.refreshVideoFeed();
        }
    },

    /**
     * Manual video feed refresh (user-initiated)
     */
    manualRefreshVideo: function() {
        console.log('Manual video feed refresh requested by user');
        AICameraUtils.addLogMessage('log-container', 'Manual video feed refresh requested', 'info');
        
        // Reset error count for manual refresh
        this.videoErrorCount = 0;
        this.videoErrorState = false;
        
        // Force refresh regardless of cooldown
        this.lastVideoRefresh = 0;
        this.refreshVideoFeed();
    },
};

// Initialize camera manager when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded, initializing Camera Manager...');
    
    // Initial log message
    AICameraUtils.addLogMessage('log-container', 'Camera dashboard loaded', 'info');
    
    // Initialize camera manager
    CameraManager.init();
    
    console.log('Camera Dashboard JavaScript loaded');
});

// Add beforeunload handler to properly cleanup resources
window.addEventListener('beforeunload', function() {
    console.log('Browser closing/refreshing - cleaning up video feed and WebSocket');
    
    // Cleanup WebSocket connection
    if (CameraManager.socket) {
        CameraManager.socket.disconnect();
        CameraManager.socket = null;
    }
    
    // Stop video feed status checks
    if (CameraManager.videoFeedRefreshTimeout) {
        clearTimeout(CameraManager.videoFeedRefreshTimeout);
        CameraManager.videoFeedRefreshTimeout = null;
    }
    
    // Reset error states
    CameraManager.videoErrorCount = 0;
    CameraManager.videoErrorState = false;
    
    // Clear any pending timeouts
    if (CameraManager.statusUpdateInterval) {
        clearInterval(CameraManager.statusUpdateInterval);
        CameraManager.statusUpdateInterval = null;
    }
    
    console.log('Camera Manager cleanup completed');
});

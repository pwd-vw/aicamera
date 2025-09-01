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
        
        // Setup WebSocket connection
        this.initializeWebSocket();
        
        // Setup event handlers
        this.setupEventHandlers();
        this.setupVideoFeedHandlers();
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
     * Initialize WebSocket connection for camera namespace
     */
    initializeWebSocket: function() {
        if (typeof io === 'undefined') {
            console.log('Socket.IO not available, using HTTP API only');
            AICameraUtils.addLogMessage('log-container', 'Socket.IO not available, using HTTP API', 'info');
            return;
        }

        try {
            this.socket = io('/camera', {
                timeout: 5000,
                reconnection: true,
                reconnectionAttempts: 3,
                reconnectionDelay: 2000
            });
            this.setupSocketHandlers();
            console.log('WebSocket connection initialized');
        } catch (error) {
            console.error('Error initializing WebSocket:', error);
            AICameraUtils.addLogMessage('log-container', `WebSocket error: ${error.message}`, 'warning');
        }
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
        });

        this.socket.on('disconnect', () => {
            console.log('❌ Disconnected from camera service');
            AICameraUtils.addLogMessage('log-container', 'Disconnected from camera service', 'warning');
        });

        this.socket.on('connect_error', (error) => {
            console.log('WebSocket connection error:', error.message);
            AICameraUtils.addLogMessage('log-container', 'WebSocket connection failed, using cached data', 'warning');
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
                
                // Only refresh video feed if camera streaming status changed AND video feed is broken
                const wasStreaming = this.lastStreamingStatus;
                const isStreaming = data.status.initialized && data.status.streaming;
                this.lastStreamingStatus = isStreaming;
                
                if (wasStreaming !== isStreaming && isStreaming) {
                    console.log('Camera streaming started, checking video feed status...');
                    // Check if video feed needs refresh (only if it's broken)
                    setTimeout(() => {
                        this.updateVideoFeedStatus(); // This will only refresh if needed
                    }, 2000); // Give video feed time to start naturally
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
     * Refresh video feed (simplified to avoid conflicts)
     */
    refreshVideoFeed: function() {
        const videoFeed = document.getElementById('video-feed');
        if (!videoFeed) return;
        
        console.log('Refreshing video feed...');
        
        // Simple refresh without cache buster to avoid conflicts
        const currentSrc = videoFeed.src;
        videoFeed.src = '';
        setTimeout(() => {
            videoFeed.src = currentSrc;
        }, 100);
        
        AICameraUtils.addLogMessage('log-container', 'Video feed refreshed', 'info');
    },

    /**
     * Check video feed status (simplified)
     */
    checkVideoFeedStatus: function() {
        const videoFeed = document.getElementById('video-feed');
        if (!videoFeed) return;
        
        console.log('Checking video feed status...');
        console.log('Video feed src:', videoFeed.src);
        console.log('Video feed naturalWidth:', videoFeed.naturalWidth);
        console.log('Video feed naturalHeight:', videoFeed.naturalHeight);
        
        if (videoFeed.complete && videoFeed.naturalWidth > 0) {
            console.log('Video feed appears to be working');
            this.updateVideoStatus('online', 'Video feed active');
        } else {
            console.log('Video feed not working properly');
            this.updateVideoStatus('offline', 'Video feed not available');
        }
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
     * Update video status overlay
     */
    updateVideoStatus: function(status, message) {
        const videoStatus = document.getElementById('video-status');
        if (!videoStatus) return;
        
        const statusContent = videoStatus.querySelector('.video-status-content');
        if (!statusContent) return;
        
        const icon = statusContent.querySelector('i');
        const text = statusContent.querySelector('span');
        
        if (status === 'hidden') {
            videoStatus.classList.add('hidden');
        } else {
            videoStatus.classList.remove('hidden');
            
            if (status === 'loading') {
                icon.className = 'fas fa-spinner fa-spin';
                text.textContent = message || 'Loading video feed...';
            } else if (status === 'error') {
                icon.className = 'fas fa-exclamation-triangle';
                text.textContent = message || 'Video feed error';
            } else if (status === 'offline') {
                icon.className = 'fas fa-video-slash';
                text.textContent = message || 'Camera offline';
            }
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
     * Update video feed status and implement fallback mechanism
     */
    updateVideoFeedStatus: function() {
        const videoFeed = document.getElementById('video-feed');
        if (!videoFeed) return;
        
        // Check if video feed is working properly
        const isVideoWorking = videoFeed.complete && videoFeed.naturalWidth > 0;
        
        if (isVideoWorking) {
            this.updateVideoStatus('hidden', '');
            // Video is working, no need to refresh
            return;
        }
        
        // Video feed is not working - check if camera should be streaming
        if (this.cachedStatus && this.cachedStatus.streaming) {
            // Camera is streaming but video feed is broken - this is a fallback case
            console.log('Camera is streaming but video feed is broken - initiating fallback refresh');
            AICameraUtils.addLogMessage('log-container', 'Video feed broken while camera streaming - initiating fallback', 'warning');
            this.updateVideoStatus('error', 'Video feed broken - attempting recovery');
            
            // Only refresh if we haven't recently tried
            const now = Date.now();
            if (now - this.lastVideoRefresh > this.videoRefreshCooldown) {
                this.refreshVideoFeed();
            }
        } else {
            // Camera is not streaming, so video feed should be offline
            this.updateVideoStatus('offline', 'Camera not streaming');
        }
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
     * Setup video feed event handlers with improved stability
     */
    setupVideoFeedHandlers: function() {
        const videoFeed = document.getElementById('video-feed');
        const videoStatus = document.getElementById('video-status');
        
        if (videoFeed) {
            console.log('Setting up video feed event handlers with improved stability');
            
            // Enhanced error handling with exponential backoff
            this.videoErrorCount = 0;
            this.maxVideoErrors = 3;
            this.videoErrorBackoff = 2000; // Start with 2 seconds
            this.maxVideoErrorBackoff = 30000; // Max 30 seconds
            this.videoErrorState = false;
            this.lastVideoRefresh = 0;
            this.videoRefreshCooldown = 15000; // Increased to 15 seconds between refreshes (was 5 seconds)
            
            videoFeed.addEventListener('error', (e) => {
                this.handleVideoFeedError(e);
            });

            videoFeed.addEventListener('load', () => {
                this.handleVideoFeedSuccess();
            });
            
            videoFeed.addEventListener('loadstart', () => {
                console.log('Video feed loading started');
                this.updateVideoStatus('loading', 'Loading video feed...');
            });
            
            videoFeed.addEventListener('abort', () => {
                console.warn('Video feed loading aborted');
                AICameraUtils.addLogMessage('log-container', 'Video feed loading aborted', 'warning');
            });
            
            videoFeed.addEventListener('stalled', () => {
                console.warn('Video feed stalled');
                AICameraUtils.addLogMessage('log-container', 'Video feed stalled', 'warning');
                // Don't immediately retry on stall, let the error handler manage it
            });
            
            // Check if video feed is working after a delay
            setTimeout(() => {
                this.updateVideoFeedStatus();
            }, 5000);
        } else {
            console.error('Video feed element not found');
        }
    },

    /**
     * Handle video feed errors with intelligent fallback
     */
    handleVideoFeedError: function(e) {
        this.videoErrorCount++;
        console.warn(`Video feed error #${this.videoErrorCount}:`, e);
        
        // Check if camera should be streaming
        if (this.cachedStatus && this.cachedStatus.streaming) {
            // Camera is streaming but video feed failed - this is a real error
            if (this.videoErrorCount <= this.maxVideoErrors) {
                AICameraUtils.addLogMessage('log-container', `Video feed error #${this.videoErrorCount} - retrying...`, 'warning');
                this.updateVideoStatus('error', `Video feed error #${this.videoErrorCount} - retrying...`);
                
                // Exponential backoff
                const backoffDelay = Math.min(this.videoErrorBackoff * Math.pow(2, this.videoErrorCount - 1), this.maxVideoErrorBackoff);
                
                setTimeout(() => {
                    this.refreshVideoFeed();
                }, backoffDelay);
            } else {
                console.error('Video feed error limit reached, camera may be offline');
                AICameraUtils.addLogMessage('log-container', 'Video feed error limit reached - camera may be offline', 'error');
                this.updateVideoStatus('error', 'Camera may be offline');
                this.videoErrorState = true;
                
                // Try to recover after a longer delay
                setTimeout(() => {
                    this.attemptVideoFeedRecovery();
                }, 30000); // 30 seconds
            }
        } else {
            // Camera is not streaming, so video feed errors are expected
            console.log('Video feed error while camera not streaming - expected behavior');
            this.updateVideoStatus('offline', 'Camera not streaming');
            // Don't retry if camera is not supposed to be streaming
        }
    },

    /**
     * Handle successful video feed load
     */
    handleVideoFeedSuccess: function() {
        console.log('Video feed loaded successfully');
        this.videoErrorCount = 0; // Reset error count
        this.videoErrorState = false; // Clear error state
        this.videoErrorBackoff = 2000; // Reset backoff
        AICameraUtils.addLogMessage('log-container', 'Video feed loaded successfully', 'success');
        this.updateVideoStatus('hidden', '');
        
        // Verify the video feed is actually working
        setTimeout(() => {
            this.updateVideoFeedStatus();
        }, 1000);
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
     * Refresh video feed with cooldown protection
     */
    refreshVideoFeed: function() {
        const now = Date.now();
        if (now - this.lastVideoRefresh < this.videoRefreshCooldown) {
            console.log('Video feed refresh skipped - cooldown active');
            return;
        }
        
        this.lastVideoRefresh = now;
        console.log('Refreshing video feed...');
        AICameraUtils.addLogMessage('log-container', 'Video feed refreshed', 'info');
        
        const videoFeed = document.getElementById('video-feed');
        if (videoFeed) {
            // Add cache-busting parameter
            const currentSrc = videoFeed.src;
            const separator = currentSrc.includes('?') ? '&' : '?';
            videoFeed.src = currentSrc + separator + 't=' + now;
        }
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

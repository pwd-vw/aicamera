/**
 * AI Camera v2.0.0 - Camera Dashboard JavaScript
 * Camera control and monitoring functionality
 */

// Camera dashboard state management
const CameraManager = {
    socket: null,
    
    /**
     * Initialize camera dashboard
     */
    init: function() {
        console.log('Initializing Camera Manager...');
        
        try {
            this.initializeWebSocket();
            this.setupEventHandlers();
            this.setupFormHandlers();
            console.log('Camera Manager initialized successfully');
        } catch (error) {
            console.error('Error initializing Camera Manager:', error);
            AICameraUtils.addLogMessage('log-container', `Initialization error: ${error.message}`, 'error');
        }
    },

    /**
     * Initialize WebSocket connection for camera namespace
     */
    initializeWebSocket: function() {
        if (typeof io === 'undefined') {
            console.warn('Socket.IO not available, falling back to HTTP API');
            AICameraUtils.addLogMessage('log-container', 'Socket.IO not available, using HTTP API', 'warning');
            return;
        }

        try {
            this.socket = io('/camera');
            this.setupSocketHandlers();
            console.log('WebSocket connection initialized');
        } catch (error) {
            console.error('Error initializing WebSocket:', error);
            AICameraUtils.addLogMessage('log-container', `WebSocket error: ${error.message}`, 'error');
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
            this.socket.emit('camera_status_request');
        });

        this.socket.on('disconnect', () => {
            console.log('❌ Disconnected from camera service');
            AICameraUtils.addLogMessage('log-container', 'Disconnected from camera service', 'error');
        });

        this.socket.on('camera_status_update', (data) => {
            console.log('📡 Received camera_status_update:', data);
            if (data && data.success && data.status) {
                console.log('✅ Status data received:', data.status);
                this.updateCameraStatus(data.status);
                if (data.config) {
                    console.log('✅ Config data received:', data.config);
                    this.updateConfigForm(data.config);
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
        const videoFeed = document.getElementById('video-feed');
        const videoStatus = document.getElementById('video-status');
        
        if (videoFeed) {
            console.log('Setting up video feed event handlers');
            
            // Improved error handling with timeout
            let errorCount = 0;
            const maxErrors = 3;
            
            videoFeed.addEventListener('error', (e) => {
                errorCount++;
                console.warn(`Video feed error #${errorCount}:`, e);
                
                if (errorCount <= maxErrors) {
                    AICameraUtils.addLogMessage('log-container', `Video feed error #${errorCount} - retrying...`, 'warning');
                    this.updateVideoStatus('error', `Video feed error #${errorCount} - retrying...`);
                    
                    // Retry after a delay
                    setTimeout(() => {
                        this.refreshVideoFeed();
                    }, 2000);
                } else {
                    console.error('Video feed error limit reached, camera may be offline');
                    AICameraUtils.addLogMessage('log-container', 'Video feed error limit reached - camera may be offline', 'error');
                    this.updateVideoStatus('error', 'Camera may be offline');
                }
            });

            videoFeed.addEventListener('load', () => {
                console.log('Video feed loaded successfully');
                errorCount = 0; // Reset error count on successful load
                AICameraUtils.addLogMessage('log-container', 'Video feed loaded successfully', 'success');
                this.updateVideoStatus('hidden', '');
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
                AICameraUtils.addLogMessage('log-container', 'Video feed stalled - retrying...', 'warning');
                setTimeout(() => {
                    this.refreshVideoFeed();
                }, 1000);
            });
            
            // Check if video feed is working after a delay
            setTimeout(() => {
                this.checkVideoFeedStatus();
            }, 5000); // Increased delay to 5 seconds
        } else {
            console.error('Video feed element not found');
        }
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

        // Update status indicator
        let statusClass = 'status-offline';
        let statusText = 'Offline';

        if (status.streaming) {
            statusClass = 'status-online';
            statusText = 'Online';
        } else if (status.initialized) {
            statusClass = 'status-warning';
            statusText = 'Ready';
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
        if (status.streaming) {
            this.updateVideoStatus('hidden', '');
            // Force refresh video feed when camera starts streaming
            this.refreshVideoFeed();
        } else if (status.initialized) {
            this.updateVideoStatus('offline', 'Camera ready but not streaming');
        } else {
            this.updateVideoStatus('offline', 'Camera not initialized');
        }

        // Update detailed status content
        this.updateStatusContent(status);
    },

    /**
     * Update detailed status content
     */
    updateStatusContent: function(status) {
        const statusContent = document.getElementById('status-content');
        if (!statusContent) {
            console.warn('Status content element not found');
            return;
        }

        // Extract metadata information
        const metadata = status.metadata || {};
        const cameraProps = status.camera_handler?.camera_properties || {};
        const currentConfig = status.config || {};
        const mainConfig = currentConfig.main || {};
        
        console.log('Status update variables:', {
            metadata: metadata,
            cameraProps: cameraProps,
            currentConfig: currentConfig,
            mainConfig: mainConfig
        });
        
        // Get resolution from metadata
        let resolution = 'Unknown';
        if (mainConfig.size && Array.isArray(mainConfig.size)) {
            resolution = `${mainConfig.size[0]}x${mainConfig.size[1]}`;
        } else if (currentConfig.main && currentConfig.main.size) {
            resolution = `${currentConfig.main.size[0]}x${currentConfig.main.size[1]}`;
        } else if (status.config && status.config.resolution) {
            resolution = `${status.config.resolution[0]}x${status.config.resolution[1]}`;
        }
        
        // Get sensor model from metadata
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
                    <strong class="text-${status.streaming ? 'success' : status.initialized ? 'warning' : 'danger'}">
                        ${status.streaming ? 'Online' : status.initialized ? 'Ready' : 'Offline'}
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
     * Request status update
     */
    requestStatusUpdate: function() {
        if (this.socket && this.socket.connected) {
            this.socket.emit('camera_status_request');
        } else {
            // Fallback to HTTP API if WebSocket not available
            this.requestStatusViaHTTP();
        }
    },

    /**
     * Refresh video feed
     */
    refreshVideoFeed: function() {
        const videoFeed = document.getElementById('video-feed');
        if (videoFeed) {
            console.log('Refreshing video feed...');
            this.updateVideoStatus('loading', 'Refreshing video feed...');
            AICameraUtils.addLogMessage('log-container', 'Refreshing video feed...', 'info');
            
            // Store current src
            const currentSrc = videoFeed.src;
            
            // Clear current src
            videoFeed.src = '';
            
            // Wait a moment then set new src with cache buster
            setTimeout(() => {
                const newSrc = currentSrc.split('?')[0] + '?t=' + Date.now();
                videoFeed.src = newSrc;
                console.log('Video feed src updated:', newSrc);
                
                // Set a timeout to check if video loads successfully
                const loadTimeout = setTimeout(() => {
                    if (videoFeed.naturalWidth === 0 || videoFeed.naturalHeight === 0) {
                        console.warn('Video feed refresh timeout - may still be loading');
                        AICameraUtils.addLogMessage('log-container', 'Video feed refresh timeout - may still be loading', 'warning');
                    }
                }, 10000); // 10 second timeout
                
                // Clear timeout when video loads successfully
                videoFeed.addEventListener('load', () => {
                    clearTimeout(loadTimeout);
                }, { once: true });
                
            }, 100);
        } else {
            console.error('Video feed element not found');
        }
    },
    
    /**
     * Check video feed status
     */
    checkVideoFeedStatus: function() {
        const videoFeed = document.getElementById('video-feed');
        if (!videoFeed) return;
        
        console.log('Checking video feed status...');
        console.log('Video feed src:', videoFeed.src);
        console.log('Video feed naturalWidth:', videoFeed.naturalWidth);
        console.log('Video feed naturalHeight:', videoFeed.naturalHeight);
        console.log('Video feed readyState:', videoFeed.readyState);
        console.log('Video feed networkState:', videoFeed.networkState);
        
        if (videoFeed.naturalWidth === 0 || videoFeed.naturalHeight === 0) {
            console.warn('Video feed appears to be empty or not loading');
            AICameraUtils.addLogMessage('log-container', 'Video feed appears to be empty - camera may not be streaming', 'warning');
            
            // Try to refresh if video is not loading
            setTimeout(() => {
                if (videoFeed.naturalWidth === 0 || videoFeed.naturalHeight === 0) {
                    console.log('Video feed still empty, attempting refresh...');
                    this.refreshVideoFeed();
                }
            }, 3000);
        } else {
            console.log('Video feed appears to be working');
            AICameraUtils.addLogMessage('log-container', 'Video feed status check: OK', 'success');
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
     * Request status via HTTP API (fallback)
     */
    requestStatusViaHTTP: function() {
        AICameraUtils.apiRequest('/camera/status')
            .then(data => {
                if (data && data.success) {
                    this.updateCameraStatus(data.status);
                    if (data.status.config) {
                        this.updateConfigForm(data.status.config);
                    }
                }
            })
            .catch(error => {
                console.warn('Camera status not available:', error.message);
                AICameraUtils.addLogMessage('log-container', 'Camera service not available', 'warning');
                // Set default offline status
                this.updateCameraStatus({streaming: false, initialized: false});
            });
    },
    
    /**
     * Start periodic video feed health check
     */
    startVideoHealthCheck: function() {
        // Check video feed health every 30 seconds
        setInterval(() => {
            const videoFeed = document.getElementById('video-feed');
            if (videoFeed && videoFeed.src) {
                // Only check if video feed has a source
                this.checkVideoFeedStatus();
            }
        }, 30000); // 30 seconds
        
        console.log('Video feed health check started (30s interval)');
    }
};

// Initialize camera manager when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded, initializing Camera Manager...');
    
    // Initial log message
    AICameraUtils.addLogMessage('log-container', 'Camera dashboard loaded', 'info');
    
    // Initialize camera manager
    CameraManager.init();
    
    // Request initial status immediately
    CameraManager.requestStatusUpdate();
    
    // Start periodic health check
    CameraManager.startVideoHealthCheck();
    
    console.log('Camera Dashboard JavaScript loaded');
});

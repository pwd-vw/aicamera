/**
 * AI Camera v2.0 - Camera Dashboard JavaScript
 * 
 * Camera control and monitoring functionality - uses cached data only.
 * 
 * @author AI Camera Team
 * @version 2.0
 * @since 2025-08-23
 */

// Camera dashboard state management
const CameraManager = {
    socket: null,
    statusUpdateInterval: null,
    lastStatusUpdate: 0,
    statusUpdateThrottle: 5000, // Minimum 5 seconds between status updates
    cachedStatus: null,
    cachedConfig: null,
    cachedMetadata: null, // New: Cache for metadata
    metadataLoaded: false, // New: Track if metadata has been loaded once
    
    /**
     * Initialize Camera Manager
     */
    init: function() {
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
    },

    /**
     * Initialize WebSocket connection for camera namespace
     */
    initializeWebSocket: function() {
        if (typeof io === 'undefined') {
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
        } catch (error) {
            // Silent error handling
        }
    },

    /**
     * Setup WebSocket event handlers
     */
    setupSocketHandlers: function() {
        if (!this.socket) return;

        this.socket.on('connect', () => {
            // Request initial status
            this.socket.emit('camera_status_request');
        });

        this.socket.on('disconnect', () => {
            // Silent disconnect handling
        });

        this.socket.on('connect_error', (error) => {
            // Silent error handling
        });

        this.socket.on('camera_status_update', (data) => {
            if (data && data.success && data.status) {
                this.cachedStatus = data.status; // Cache status
                this.updateCameraStatus(data.status);
                if (data.config) {
                    this.cachedConfig = data.config; // Cache config
                    this.updateConfigForm(data.config);
                }
            } else {
                // Silent error handling
            }
        });

        this.socket.on('camera_control_response', (response) => {
            this.handleControlResponse(response);
        });

        this.socket.on('camera_config_response', (response) => {
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
            return;
        }

        this.socket.emit('camera_control', { command: command });
    },

    /**
     * Handle control response
     */
    handleControlResponse: function(response) {
        const message = response.success ? 
            (response.message || 'Command executed successfully') :
            (response.error || response.message || 'Command failed');
        
        // Silent error handling
    },

    /**
     * Handle configuration response
     */
    handleConfigResponse: function(response) {
        const message = response.success ? 
            (response.message || 'Configuration updated successfully') :
            (response.error || 'Configuration update failed');
        
        // Silent error handling
    },

    /**
     * Update camera status display
     */
    updateCameraStatus: function(status) {
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
        } else {
            // Silent warning
        }
        
        if (statusTextElement) {
            statusTextElement.textContent = statusText;
        } else {
            // Silent warning
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
            // Silent warning
            return;
        }

        // Extract metadata information
        const metadata = status.metadata || {};
        const cameraProps = status.camera_handler?.camera_properties || {};
        const currentConfig = status.config || {};
        const mainConfig = currentConfig.main || {};
        
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
    },

    /**
     * Refresh video feed (simplified to avoid conflicts)
     */
    refreshVideoFeed: function() {
        const videoFeed = document.getElementById('video-feed');
        if (!videoFeed) return;
        
        // Simple refresh without cache buster to avoid conflicts
        const currentSrc = videoFeed.src;
        videoFeed.src = '';
        setTimeout(() => {
            videoFeed.src = currentSrc;
        }, 100);
    },

    /**
     * Check video feed status (simplified)
     */
    checkVideoFeedStatus: function() {
        const videoFeed = document.getElementById('video-feed');
        if (!videoFeed) return;
        
        // Check if video feed is loading properly
        if (videoFeed.complete && videoFeed.naturalWidth > 0) {
            this.updateVideoStatus('online', 'Video feed active');
        } else {
            this.updateVideoStatus('offline', 'Video feed not available');
        }
    },
    

    /**
     * Test video feed functionality
     */
    testVideoFeed: function() {
        AICameraUtils.apiRequest('/camera/video_test')
            .then(data => {
                if (data && data.success) {
                    const results = data.video_test_results;
                    const message = `Video Test Results:
                        Camera Initialized: ${results.camera_initialized}
                        Camera Streaming: ${results.camera_streaming}
                        Frame Capture: ${results.frame_capture_success}
                        Frame Shape: ${results.frame_shape || 'N/A'}
                        Frame Error: ${results.frame_error || 'None'}`;
                    
                } else {
                }
            })
            .catch(error => {
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
     * Update video feed status without API calls
     */
    updateVideoFeedStatus: function() {
        const videoFeed = document.getElementById('video-feed');
        if (!videoFeed) return;
        
        // Check if video feed is loading properly
        if (videoFeed.complete && videoFeed.naturalWidth > 0) {
            this.updateVideoStatus('online', 'Video feed active');
        } else {
            this.updateVideoStatus('offline', 'Video feed not available');
        }
    },

    /**
     * Load metadata once when dashboard loads (no periodic fetching)
     */
    loadMetadataOnce: function() {
        if (this.metadataLoaded) {
            return;
        }
        
        // Load metadata from debug endpoint
        AICameraUtils.apiRequest('/camera/debug_metadata')
            .then(data => {
                if (data && data.success) {
                    this.cachedMetadata = data.metadata;
                    this.metadataLoaded = true;
                    
                    // Update metadata display
                    this.updateMetadataDisplay(data.metadata);
                    
                } else {
                    // Silent error handling
                }
            })
            .catch(error => {
                // Silent error handling
            });
    },

    /**
     * Update metadata display with loaded data
     */
    updateMetadataDisplay: function(metadata) {
        try {
            // Update metadata section if it exists
            const metadataSection = document.getElementById('metadata-section');
            if (metadataSection) {
                const metadataContent = document.getElementById('metadata-content');
                if (metadataContent) {
                    // Format and display metadata
                    let html = '<div class="metadata-grid">';
                    
                    // Camera Properties
                    if (metadata.camera_properties) {
                        html += '<div class="metadata-group">';
                        html += '<h6 class="metadata-title">Camera Properties</h6>';
                        for (const [key, value] of Object.entries(metadata.camera_properties)) {
                            html += `<div class="metadata-item"><span class="metadata-label">${key}:</span><span class="metadata-value">${value}</span></div>`;
                        }
                        html += '</div>';
                    }
                    
                    // Current Configuration
                    if (metadata.current_config) {
                        html += '<div class="metadata-group">';
                        html += '<h6 class="metadata-title">Current Configuration</h6>';
                        for (const [key, value] of Object.entries(metadata.current_config)) {
                            html += `<div class="metadata-item"><span class="metadata-label">${key}:</span><span class="metadata-value">${JSON.stringify(value)}</span></div>`;
                        }
                        html += '</div>';
                    }
                    
                    // Camera Status
                    if (metadata.camera_status) {
                        html += '<div class="metadata-group">';
                        html += '<h6 class="metadata-title">Camera Status</h6>';
                        for (const [key, value] of Object.entries(metadata.camera_status)) {
                            html += `<div class="metadata-item"><span class="metadata-label">${key}:</span><span class="metadata-value">${value}</span></div>`;
                        }
                        html += '</div>';
                    }
                    
                    // Manager Status
                    if (metadata.manager_status) {
                        html += '<div class="metadata-group">';
                        html += '<h6 class="metadata-title">Manager Status</h6>';
                        for (const [key, value] of Object.entries(metadata.manager_status)) {
                            html += `<div class="metadata-item"><span class="metadata-label">${key}:</span><span class="metadata-value">${value}</span></div>`;
                        }
                        html += '</div>';
                    }
                    
                    html += '</div>';
                    metadataContent.innerHTML = html;
                }
            }
        } catch (error) {
            // Silent error handling
        }
    },

    /**
     * Setup video feed event handlers
     */
    setupVideoFeedHandlers: function() {
        const videoFeed = document.getElementById('video-feed');
        const videoStatus = document.getElementById('video-status');
        
        if (videoFeed) {
            // Improved error handling with timeout
            let errorCount = 0;
            const maxErrors = 3;
            
            videoFeed.addEventListener('error', (e) => {
                errorCount++;
                
                if (errorCount <= maxErrors) {
                    this.updateVideoStatus('error', `Video feed error #${errorCount} - retrying...`);
                    
                    // Retry after a delay
                    setTimeout(() => {
                        this.refreshVideoFeed();
                    }, 2000);
                } else {
                    // Silent error handling
                }
            });

            videoFeed.addEventListener('load', () => {
                errorCount = 0; // Reset error count on successful load
                this.updateVideoStatus('hidden', '');
            });
            
            videoFeed.addEventListener('loadstart', () => {
                this.updateVideoStatus('loading', 'Loading video feed...');
            });
            
            videoFeed.addEventListener('abort', () => {
                // Silent warning
            });
            
            videoFeed.addEventListener('stalled', () => {
                // Silent warning
                setTimeout(() => {
                    this.refreshVideoFeed();
                }, 1000);
            });
            
            // Check if video feed is working after a delay
            setTimeout(() => {
                this.updateVideoFeedStatus(); // Use cached status
            }, 5000); // Increased delay to 5 seconds
        } else {
            // Silent error handling
        }
    },
};

// Initialize camera manager when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    
    // Initialize camera manager
    CameraManager.init();
    
});

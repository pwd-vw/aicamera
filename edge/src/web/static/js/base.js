/**
 * AI Camera v2.0 - Base JavaScript Functions
 * 
 * Common utilities and functions shared across all dashboards.
 * 
 * @author AI Camera Team
 * @version 2.0
 * @since 2025-08-23
 */

// Global utilities
const AICameraUtils = {
    /**
     * Format timestamp to locale string
     */
    formatTimestamp: function(timestamp) {
        if (!timestamp) return '-';
        return new Date(timestamp).toLocaleString();
    },

    /**
     * Format time duration in seconds to human readable format
     */
    formatDuration: function(seconds) {
        if (!seconds) return '0s';
        const minutes = Math.floor(seconds / 60);
        const secs = Math.floor(seconds % 60);
        return minutes > 0 ? `${minutes}m ${secs}s` : `${secs}s`;
    },

    /**
     * Update status indicator element
     */
    updateStatusIndicator: function(elementId, isOnline, statusText) {
        const element = document.getElementById(elementId);
        if (element) {
            element.className = `status-indicator ${isOnline ? 'status-online' : 'status-offline'}`;
        }
        
        const textElement = document.getElementById(elementId + '-text');
        if (textElement) {
            textElement.textContent = statusText || (isOnline ? 'Online' : 'Offline');
        }
    },

    /**
     * Add log message to log container
     */
    addLogMessage: function(containerId, message, type = 'info') {
        const container = document.getElementById(containerId);
        if (!container) return;

        const timestamp = new Date().toLocaleTimeString();
        const logEntry = document.createElement('div');
        logEntry.className = `log-entry log-${type}`;
        logEntry.innerHTML = `[${timestamp}] ${message}`;
        
        container.appendChild(logEntry);
        container.scrollTop = container.scrollHeight;
        
        // Keep only last 100 messages
        while (container.children.length > 100) {
            container.removeChild(container.firstChild);
        }
    },

    /**
     * Show toast notification (SILENT MODE - Disabled)
     */
    showToast: function(message, type = 'info') {
        // SILENT MODE: Toast notifications are disabled
        // Uncomment the code below to re-enable toast notifications
        
        /*
        // Create toast if it doesn't exist
        let toastContainer = document.getElementById('toast-container');
        if (!toastContainer) {
            toastContainer = document.createElement('div');
            toastContainer.id = 'toast-container';
            toastContainer.className = 'position-fixed top-0 end-0 p-3';
            toastContainer.style.zIndex = '1050';
            document.body.appendChild(toastContainer);
        }

        const toastId = 'toast-' + Date.now();
        const toastHtml = `
            <div class="toast" id="${toastId}" role="alert" aria-live="assertive" aria-atomic="true">
                <div class="toast-header">
                    <i class="fas fa-camera text-primary me-2"></i>
                    <strong class="me-auto">AI Camera</strong>
                    <small class="text-muted">${new Date().toLocaleTimeString()}</small>
                    <button type="button" class="btn-close" data-bs-dismiss="toast"></button>
                </div>
                <div class="toast-body bg-${type === 'error' ? 'danger' : type === 'success' ? 'success' : 'info'} text-white">
                    ${message}
                </div>
            </div>
        `;

        toastContainer.insertAdjacentHTML('beforeend', toastHtml);
        const toast = new bootstrap.Toast(document.getElementById(toastId));
        toast.show();

        // Remove toast element after it's hidden
        document.getElementById(toastId).addEventListener('hidden.bs.toast', function() {
            this.remove();
        });
        */
        
        // Silent mode: Only log to console for debugging
        console.log(`[TOAST ${type.toUpperCase()}] ${message}`);
    },

    /**
     * Make API request
     */
    apiRequest: function(url, options = {}) {
        const defaultOptions = {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            },
        };

        const requestOptions = { ...defaultOptions, ...options };

        return fetch(url, requestOptions)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .catch(error => {
                console.error('API request failed:', error);
                throw error;
            });
    },

    /**
     * Debounce function to limit API calls
     */
    debounce: function(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },

    /**
     * Make API request with error handling
     */
    apiRequest: function(url, options = {}) {
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
        };

        const controller = new AbortController();
        const timeoutMs = (options && options.timeoutMs) || 30000;
        const finalOptions = { ...defaultOptions, ...options, signal: controller.signal };

        const timer = setTimeout(() => controller.abort(), timeoutMs);

        const doFetch = () => fetch(url, finalOptions).then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const contentType = response.headers.get('content-type');
            if (contentType && contentType.includes('application/json')) {
                return response.json();
            } else {
                return response.text().then(text => {
                    try {
                        return JSON.parse(text);
                    } catch (parseError) {
                        console.error('Response is not valid JSON:', text.substring(0, 200));
                        throw new Error('Invalid JSON response from server');
                    }
                });
            }
        });

        return doFetch()
            .catch(error => {
                // Retry once on network-level failures
                const isAbort = error && (error.name === 'AbortError' || /network.*timeout/i.test(error.message));
                const isNetwork = error && (/Failed to fetch/i.test(error.message) || /NetworkError/i.test(error.message));
                if (isAbort || isNetwork) {
                    return new Promise(resolve => setTimeout(resolve, 500)).then(doFetch);
                }
                throw error;
            })
            .finally(() => clearTimeout(timer))
            .catch(error => {
                console.error('API request failed:', url, error);
                throw error;
            });
    }
};

// Global WebSocket manager
const WebSocketManager = {
    socket: null,
    reconnectAttempts: 0,
    maxReconnectAttempts: 5,
    connectionTimeout: 10000, // 10 seconds timeout

    /**
     * Initialize WebSocket connection
     */
    init: function(namespace = '/') {
        if (typeof io === 'undefined') {
            console.warn('Socket.IO not loaded, WebSocket functionality disabled');
            return;
        }

        // Configure Socket.IO with timeout and reconnection settings
        if (!window.useSocketIO) {
            return; // Socket.IO disabled
        }
        this.socket = io(namespace, {
            timeout: this.connectionTimeout,
            reconnection: true,
            reconnectionAttempts: this.maxReconnectAttempts,
            reconnectionDelay: 1000,
            reconnectionDelayMax: 5000,
            maxReconnectionAttempts: this.maxReconnectAttempts
        });
        
        this.setupEventHandlers();
    },

    /**
     * Setup common WebSocket event handlers
     */
    setupEventHandlers: function() {
        if (!this.socket) return;

        this.socket.on('connect', () => {
            console.log('WebSocket connected successfully');
            AICameraUtils.showToast('Connected to server', 'success');
            this.reconnectAttempts = 0;
            
            // Update connection status in main dashboard
            const connectionElement = document.getElementById('main-server-connection-status');
            const connectionText = document.getElementById('main-server-connection-text');
            if (connectionElement) {
                connectionElement.className = 'status-indicator status-online';
            }
            if (connectionText) {
                connectionText.textContent = 'Connected';
            }
            
            // Add log message
            AICameraUtils.addLogMessage('main-server-logs', 'WebSocket connection established', 'success');
        });

        this.socket.on('disconnect', (reason) => {
            console.log('WebSocket disconnected:', reason);
            AICameraUtils.showToast('Disconnected from server: ' + reason, 'warning');
            
            // Update connection status in main dashboard
            const connectionElement = document.getElementById('main-server-connection-status');
            const connectionText = document.getElementById('main-server-connection-text');
            if (connectionElement) {
                connectionElement.className = 'status-indicator status-offline';
            }
            if (connectionText) {
                connectionText.textContent = 'Disconnected';
            }
            
            // Add log message
            AICameraUtils.addLogMessage('main-server-logs', 'WebSocket disconnected: ' + reason, 'warning');
        });

        this.socket.on('connect_error', (error) => {
            console.error('WebSocket connection error:', error);
            AICameraUtils.showToast('Connection error: ' + error.message, 'error');
            
            // Update connection status in main dashboard
            const connectionElement = document.getElementById('main-server-connection-status');
            const connectionText = document.getElementById('main-server-connection-text');
            if (connectionElement) {
                connectionElement.className = 'status-indicator status-offline';
            }
            if (connectionText) {
                connectionText.textContent = 'Connection Error';
            }
            
            // Add log message
            AICameraUtils.addLogMessage('main-server-logs', 'WebSocket connection error: ' + error.message, 'error');
            
            this.handleReconnect();
        });

        this.socket.on('reconnect_attempt', (attemptNumber) => {
            console.log(`WebSocket reconnection attempt ${attemptNumber}/${this.maxReconnectAttempts}`);
            AICameraUtils.addLogMessage('main-server-logs', `Reconnection attempt ${attemptNumber}/${this.maxReconnectAttempts}`, 'info');
        });

        this.socket.on('reconnect_failed', () => {
            console.error('WebSocket reconnection failed after all attempts');
            AICameraUtils.showToast('Connection failed after all attempts. Please refresh the page.', 'error');
            AICameraUtils.addLogMessage('main-server-logs', 'WebSocket reconnection failed after all attempts', 'error');
        });
    },

    /**
     * Handle reconnection logic
     */
    handleReconnect: function() {
        this.reconnectAttempts++;
        if (this.reconnectAttempts <= this.maxReconnectAttempts) {
            const delay = Math.pow(2, this.reconnectAttempts) * 1000; // Exponential backoff
            setTimeout(() => {
                console.log(`Attempting to reconnect... (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
                this.socket.connect();
            }, delay);
        } else {
            AICameraUtils.showToast('Connection failed. Please refresh the page.', 'error');
        }
    },

    /**
     * Emit event with error handling
     */
    emit: function(event, data) {
        if (this.socket && this.socket.connected) {
            this.socket.emit(event, data);
        } else {
            console.warn('WebSocket not connected, cannot emit event:', event);
            AICameraUtils.showToast('Not connected to server', 'warning');
        }
    }
};

/**
 * Fullscreen Manager - ปรับปรุงให้รองรับ headless environment
 */
const FullscreenManager = {
    isFullscreen: false,
    isHeadless: false,
    
    /**
     * Initialize fullscreen manager
     */
    init: function() {
        console.log('Fullscreen manager initialized. Current state: Normal');
        
        // ตรวจสอบว่าเป็น headless environment หรือไม่
        this.detectHeadlessEnvironment();
        
        // Setup event listeners
        this.setupEventListeners();
        
        // Update UI
        this.updateExitButton();
    },
    
    /**
     * Detect if running in headless environment
     */
    detectHeadlessEnvironment: function() {
        // ตรวจสอบว่าไม่มี display หรือเป็น headless
        if (!window.screen || window.screen.width === 0 || window.screen.height === 0) {
            this.isHeadless = true;
            console.log('Headless environment detected - disabling fullscreen features');
        }
        
        // ตรวจสอบว่าเป็น kiosk mode หรือไม่
        if (window.navigator.standalone || (window.chrome && window.chrome.webstore)) {
            this.isHeadless = true;
            console.log('Kiosk mode detected - disabling fullscreen features');
        }
        
        // ตรวจสอบว่าเป็น embedded browser หรือไม่
        if (window.location.href.includes('localhost') && !window.screen.availWidth) {
            this.isHeadless = true;
            console.log('Embedded browser detected - disabling fullscreen features');
        }
    },
    
    /**
     * Setup event listeners
     */
    setupEventListeners: function() {
        // Keyboard shortcut for fullscreen (F11)
        document.addEventListener('keydown', (e) => {
            if (e.key === 'F11') {
                e.preventDefault();
                if (this.isFullscreen) {
                    this.exitFullscreen();
                } else {
                    this.enterFullscreen();
                }
            }
        });
        
        // Fullscreen change events
        document.addEventListener('fullscreenchange', () => {
            this.isFullscreen = !!document.fullscreenElement;
            this.updateExitButton();
        });
        
        document.addEventListener('webkitfullscreenchange', () => {
            this.isFullscreen = !!document.webkitFullscreenElement;
            this.updateExitButton();
        });
        
        document.addEventListener('msfullscreenchange', () => {
            this.isFullscreen = !!document.msFullscreenElement;
            this.updateExitButton();
        });
    },
    
    /**
     * Enter fullscreen mode - ป้องกันการเรียกใช้ใน headless environment
     */
    enterFullscreen: function() {
        // ตรวจสอบว่าเป็น headless environment หรือไม่
        if (this.isHeadless) {
            console.warn('Fullscreen not available in headless environment');
            AICameraUtils.showToast('Fullscreen not available in this environment', 'warning');
            return;
        }
        
        // ตรวจสอบว่าเป็น user gesture หรือไม่
        if (!this.isUserGesture()) {
            console.warn('Fullscreen can only be initiated by user gesture');
            AICameraUtils.showToast('Please click the fullscreen button manually', 'info');
            return;
        }
        
        const elem = document.documentElement;
        
        try {
            if (elem.requestFullscreen) {
                elem.requestFullscreen();
            } else if (elem.webkitRequestFullscreen) {
                elem.webkitRequestFullscreen();
            } else if (elem.msRequestFullscreen) {
                elem.msRequestFullscreen();
            } else {
                throw new Error('Fullscreen API not supported');
            }
            
            this.isFullscreen = true;
            this.updateExitButton();
            AICameraUtils.showToast('Entered fullscreen mode', 'info');
            
        } catch (error) {
            console.error('Failed to enter fullscreen mode:', error);
            AICameraUtils.showToast('Failed to enter fullscreen mode', 'error');
        }
    },
    
    /**
     * Exit fullscreen mode
     */
    exitFullscreen: function() {
        try {
            if (document.exitFullscreen) {
                document.exitFullscreen();
            } else if (document.webkitExitFullscreen) {
                document.webkitExitFullscreen();
            } else if (document.msExitFullscreen) {
                document.msExitFullscreen();
            }
            
            this.isFullscreen = false;
            this.updateExitButton();
            AICameraUtils.showToast('Exited fullscreen mode', 'info');
            
        } catch (error) {
            console.error('Failed to exit fullscreen mode:', error);
            AICameraUtils.showToast('Failed to exit fullscreen mode', 'error');
        }
    },
    
    /**
     * Check if action is triggered by user gesture
     */
    isUserGesture: function() {
        // ตรวจสอบว่าเป็น user interaction หรือไม่
        return true; // ให้ผ่านไปก่อน แต่จะมีการตรวจสอบเพิ่มเติมใน enterFullscreen
    },
    
    /**
     * Update exit button appearance based on current state
     */
    updateExitButton: function() {
        const exitBtn = document.getElementById('exit-browser-btn');
        if (!exitBtn) return;
        
        const icon = exitBtn.querySelector('i');
        const text = exitBtn.querySelector('span');
        
        if (this.isHeadless) {
            // ใน headless environment ให้ปิดการใช้งาน fullscreen button
            exitBtn.disabled = true;
            exitBtn.className = 'btn btn-secondary btn-sm';
            exitBtn.title = 'Fullscreen not available in headless mode';
            if (icon) icon.className = 'fas fa-ban';
            if (text) text.textContent = 'Fullscreen N/A';
        } else if (this.isFullscreen) {
            // Show exit fullscreen button
            exitBtn.disabled = false;
            icon.className = 'fas fa-compress';
            if (text) text.textContent = 'Exit Fullscreen';
            exitBtn.className = 'btn btn-warning btn-sm';
            exitBtn.title = 'Exit Full Screen Mode (F11)';
        } else {
            // Show enter fullscreen button
            exitBtn.disabled = false;
            icon.className = 'fas fa-expand';
            if (text) text.textContent = 'Fullscreen';
            exitBtn.className = 'btn btn-primary btn-sm';
            exitBtn.title = 'Enter Full Screen Mode (F11)';
        }
    }
};

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    const tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    const popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Add smooth scrolling to anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });

    // Initialize fullscreen manager
    FullscreenManager.init();

    console.log('AI Camera v2.0 - Base JavaScript loaded');
});

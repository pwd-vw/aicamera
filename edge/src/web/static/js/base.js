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
     * Add log message to log container (silent version)
     */
    addLogMessage: function(containerId, message, type = 'info') {
        // Silent - no logging
        return;
    },

    /**
     * Show toast notification (silent version)
     */
    showToast: function(message, type = 'info') {
        // Silent - no notifications
        return;
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
                // Silent error handling
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

        const finalOptions = { ...defaultOptions, ...options };
        
        return fetch(url, finalOptions)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                
                // Check if response is JSON
                const contentType = response.headers.get('content-type');
                if (contentType && contentType.includes('application/json')) {
                    return response.json();
                } else {
                    // If not JSON, get text and try to parse as JSON
                    return response.text().then(text => {
                        try {
                            return JSON.parse(text);
                        } catch (parseError) {
                            // Silent error handling
                            throw new Error('Invalid JSON response from server');
                        }
                    });
                }
            })
            .catch(error => {
                // Silent error handling
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
            return;
        }

        // Configure Socket.IO with timeout and reconnection settings
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
        });

        this.socket.on('disconnect', (reason) => {
            // Update connection status in main dashboard
            const connectionElement = document.getElementById('main-server-connection-status');
            const connectionText = document.getElementById('main-server-connection-text');
            if (connectionElement) {
                connectionElement.className = 'status-indicator status-offline';
            }
            if (connectionText) {
                connectionText.textContent = 'Disconnected';
            }
        });

        this.socket.on('connect_error', (error) => {
            // Update connection status in main dashboard
            const connectionElement = document.getElementById('main-server-connection-status');
            const connectionText = document.getElementById('main-server-connection-text');
            if (connectionElement) {
                connectionElement.className = 'status-indicator status-offline';
            }
            if (connectionText) {
                connectionText.textContent = 'Connection Error';
            }
            
            this.handleReconnect();
        });

        this.socket.on('reconnect_attempt', (attemptNumber) => {
            // Add log message
        });

        this.socket.on('reconnect_failed', () => {
            // Show toast notification
            // Add log message
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
                this.socket.connect();
            }, delay);
        } else {
        }
    },

    /**
     * Emit event with error handling
     */
    emit: function(event, data) {
        if (this.socket && this.socket.connected) {
            this.socket.emit(event, data);
        } else {
            // Silent warning
        }
    }
};

// Fullscreen management
const FullscreenManager = {
    isFullscreen: true, // Default to fullscreen in kiosk mode
    
    /**
     * Initialize fullscreen functionality
     */
    init: function() {
        // Check if we're in kiosk mode
        this.isFullscreen = window.navigator.standalone || 
                           document.webkitIsFullScreen || 
                           document.fullscreenElement !== null;
        
        // Setup exit button functionality
        this.setupExitButton();
        
        // Setup keyboard shortcuts
        this.setupKeyboardShortcuts();
        
        // Auto-enter fullscreen on page load (for kiosk mode)
        this.autoEnterFullscreen();
        
    },
    
    /**
     * Auto-enter fullscreen on page load
     */
    autoEnterFullscreen: function() {
        // Wait a bit for the page to load completely
        setTimeout(() => {
            if (!this.isFullscreen) {
                this.enterFullscreen();
            }
        }, 2000);
    },
    
    /**
     * Setup exit button functionality
     */
    setupExitButton: function() {
        const exitBtn = document.getElementById('exit-browser-btn');
        if (!exitBtn) return;
        
        // Update button text and icon based on current state
        this.updateExitButton();
        
        // Add click event listener
        exitBtn.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            this.toggleFullscreen();
        });
        
        // Prevent right-click context menu on the button
        exitBtn.addEventListener('contextmenu', (e) => {
            e.preventDefault();
            e.stopPropagation();
        });
    },
    
    /**
     * Setup keyboard shortcuts
     */
    setupKeyboardShortcuts: function() {
        document.addEventListener('keydown', (e) => {
            // F11 to toggle fullscreen
            if (e.key === 'F11') {
                e.preventDefault();
                this.toggleFullscreen();
            }
            
            // Escape to exit fullscreen (only if in fullscreen)
            if (e.key === 'Escape' && this.isFullscreen) {
                e.preventDefault();
                this.exitFullscreen();
            }
        });
        
        // Listen for fullscreen change events
        document.addEventListener('fullscreenchange', () => {
            this.isFullscreen = document.fullscreenElement !== null;
            this.updateExitButton();
        });
        
        document.addEventListener('webkitfullscreenchange', () => {
            this.isFullscreen = document.webkitFullscreenElement !== null;
            this.updateExitButton();
        });
        
        document.addEventListener('mozfullscreenchange', () => {
            this.isFullscreen = document.mozFullScreenElement !== null;
            this.updateExitButton();
        });
    },
    
    /**
     * Toggle between fullscreen and normal mode
     */
    toggleFullscreen: function() {
        if (this.isFullscreen) {
            this.exitFullscreen();
        } else {
            this.enterFullscreen();
        }
    },
    
    /**
     * Enter fullscreen mode
     */
    enterFullscreen: function() {
        const elem = document.documentElement;
        
        if (elem.requestFullscreen) {
            elem.requestFullscreen();
        } else if (elem.webkitRequestFullscreen) {
            elem.webkitRequestFullscreen();
        } else if (elem.msRequestFullscreen) {
            elem.msRequestFullscreen();
        }
        
        this.isFullscreen = true;
        this.updateExitButton();
    },
    
    /**
     * Exit fullscreen mode
     */
    exitFullscreen: function() {
        // Check if we're in a kiosk-like environment
        if (window.navigator.standalone || window.chrome && window.chrome.webstore) {
            // In kiosk mode, show a confirmation dialog instead of exiting
            if (confirm('Are you sure you want to exit fullscreen mode? This will show the browser interface.')) {
                if (document.exitFullscreen) {
                    document.exitFullscreen();
                } else if (document.webkitExitFullscreen) {
                    document.webkitExitFullscreen();
                } else if (document.msExitFullscreen) {
                    document.msExitFullscreen();
                }
                
                this.isFullscreen = false;
                this.updateExitButton();
            }
        } else {
            // Normal browser mode
            if (document.exitFullscreen) {
                document.exitFullscreen();
            } else if (document.webkitExitFullscreen) {
                document.webkitExitFullscreen();
            } else if (document.msExitFullscreen) {
                document.msExitFullscreen();
            }
            
            this.isFullscreen = false;
            this.updateExitButton();
        }
    },
    
    /**
     * Update exit button appearance based on current state
     */
    updateExitButton: function() {
        const exitBtn = document.getElementById('exit-browser-btn');
        if (!exitBtn) return;
        
        const icon = exitBtn.querySelector('i');
        const text = exitBtn.querySelector('span');
        
        if (this.isFullscreen) {
            // Show exit fullscreen button
            icon.className = 'fas fa-compress';
            if (text) text.textContent = 'Exit Fullscreen';
            exitBtn.className = 'btn btn-warning btn-sm';
            exitBtn.title = 'Exit Full Screen Mode (F11)';
        } else {
            // Show enter fullscreen button
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

});

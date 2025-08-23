/**
 * AI Camera v2.0 - Storage Management JavaScript
 * 
 * Handles storage monitoring, cleanup, and configuration management.
 * 
 * @author AI Camera Team
 * @version 2.0
 * @since 2025-08-23
 */

// Storage Manager state management
const StorageManager = {
    socket: null,
    statusUpdateInterval: null,
    currentStatus: null,
    isMonitoring: false,
    
    /**
     * Initialize storage manager
     */
    init: function() {
        this.initializeWebSocket();
        this.setupEventHandlers();
        this.loadInitialStatus();
    },

    /**
     * Initialize WebSocket connection
     */
    initializeWebSocket: function() {
        if (typeof io === 'undefined') {
            return;
        }
        
        this.socket = io();  // Use main namespace instead of /storage
        this.setupSocketHandlers();
        
        // Test connection
        this.socket.on('connect', () => {
        });
        
        this.socket.on('disconnect', () => {
        });
        
        this.socket.on('connect_error', (error) => {
        });
    },

    /**
     * Setup WebSocket event handlers
     */
    setupSocketHandlers: function() {
        if (!this.socket) return;

        this.socket.on('connect', () => {
        });

        this.socket.on('storage_status_response', (data) => {
            this.updateStorageStatus(data);
        });

        this.socket.on('storage_analytics_response', (data) => {
            this.updateAnalytics(data);
        });

        this.socket.on('storage_cleanup_response', (data) => {
            this.handleCleanupResponse(data);
        });

        this.socket.on('storage_config_response', (data) => {
            this.handleConfigResponse(data);
        });

        this.socket.on('storage_monitor_response', (data) => {
            this.handleMonitorResponse(data);
        });

        this.socket.on('storage_alerts_response', (data) => {
            this.updateAlerts(data);
        });

        this.socket.on('storage_room_joined', (data) => {
        });

        this.socket.on('storage_room_left', (data) => {
        });
    },

    /**
     * Setup event handlers for UI elements
     */
    setupEventHandlers: function() {
        // Toggle monitoring button
        const toggleBtn = document.getElementById('toggle-monitoring-btn');
        if (toggleBtn) {
            toggleBtn.addEventListener('click', () => {
                this.toggleMonitoring();
            });
        }

        // Manual cleanup button
        const cleanupBtn = document.getElementById('manual-cleanup-btn');
        if (cleanupBtn) {
            cleanupBtn.addEventListener('click', () => {
                this.performManualCleanup();
            });
        }

        // Refresh status button
        const refreshBtn = document.getElementById('refresh-status-btn');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => {
                this.refreshStatus();
            });
        }

        // Get analytics button
        const analyticsBtn = document.getElementById('get-analytics-btn');
        if (analyticsBtn) {
            analyticsBtn.addEventListener('click', () => {
                this.getAnalytics();
            });
        }

        // Clear alerts button
        const clearAlertsBtn = document.getElementById('clear-alerts-btn');
        if (clearAlertsBtn) {
            clearAlertsBtn.addEventListener('click', () => {
                this.clearAlerts();
            });
        }

        // Configuration form
        const configForm = document.getElementById('storage-config-form');
        if (configForm) {
            configForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.updateConfiguration();
            });
        }
    },

    /**
     * Load initial storage status
     */
    loadInitialStatus: function() {
        
        // Add loading indicators
        this.showLoadingIndicators();
        
        // Request status with retry mechanism
        this.requestStorageStatusWithRetry();
        this.requestAlerts();
    },

    /**
     * Show loading indicators
     */
    showLoadingIndicators: function() {
        const elements = [
            'disk-usage-text',
            'free-space-gb', 
            'total-files',
            'folder-size-text',
            'sent-files-count',
            'unsent-files-count',
            'files-deleted-count',
            'space-freed-gb'
        ];
        
        elements.forEach(id => {
            const element = document.getElementById(id);
            if (element) {
                element.textContent = 'Loading...';
            }
        });
    },

    /**
     * Request storage status with retry mechanism
     */
    requestStorageStatusWithRetry: function(retryCount = 0) {
        const maxRetries = 3;
        
        this.requestStorageStatus()
            .catch(error => {
                
                if (retryCount < maxRetries) {
                    setTimeout(() => {
                        this.requestStorageStatusWithRetry(retryCount + 1);
                    }, 2000);
                } else {
                    this.showErrorState();
                }
            });
    },

    /**
     * Show error state
     */
    showErrorState: function() {
        const elements = [
            'disk-usage-text',
            'free-space-gb', 
            'total-files',
            'folder-size-text',
            'sent-files-count',
            'unsent-files-count',
            'files-deleted-count',
            'space-freed-gb'
        ];
        
        elements.forEach(id => {
            const element = document.getElementById(id);
            if (element) {
                element.textContent = 'Error';
                element.className = element.className + ' text-danger';
            }
        });
        
    },

    /**
     * Request storage status via WebSocket
     */
    requestStorageStatus: function() {
        return new Promise((resolve, reject) => {
            if (this.socket) {
                this.socket.emit('storage_status_request');
                
                // Set up one-time listener for response
                const responseHandler = (data) => {
                    this.socket.off('storage_status_response', responseHandler);
                    if (data && data.success) {
                        resolve(data);
                    } else {
                        reject(new Error(data?.error || 'Storage status request failed'));
                    }
                };
                
                this.socket.on('storage_status_response', responseHandler);
                
                // Timeout after 10 seconds
                setTimeout(() => {
                    this.socket.off('storage_status_response', responseHandler);
                    reject(new Error('Storage status request timeout'));
                }, 10000);
                
            } else {
                // Fallback to HTTP API
                this.loadStatusFromAPI()
                    .then(resolve)
                    .catch(reject);
            }
        });
    },

    /**
     * Load status from HTTP API
     */
    loadStatusFromAPI: function() {
        return AICameraUtils.apiRequest('/storage/status')
            .then(data => {
                this.updateStorageStatus(data);
                return data;
            })
            .catch(error => {
                throw error;
            });
    },

    /**
     * Update storage status display
     */
    updateStorageStatus: function(data) {
        
        if (!data || !data.success) {
            return;
        }

        this.currentStatus = data.data;
        const status = data.data;
        

        // Update disk usage
        this.updateDiskUsage(status.disk_usage);
        
        // Update file counts
        this.updateFileCounts(status.file_counts);
        
        // Update folder stats
        this.updateFolderStats(status.folder_stats);
        
        // Update cleanup stats
        this.updateCleanupStats(status.cleanup_stats);
        
        // Update configuration form
        this.updateConfigurationForm(status.configuration);
        
        // Update monitoring status
        this.updateMonitoringStatus(status.status);
        
        // Update recommendations
        this.updateRecommendations(status);
    },

    /**
     * Update disk usage display
     */
    updateDiskUsage: function(diskUsage) {
        
        if (!diskUsage) {
            return;
        }

        const progressBar = document.getElementById('disk-usage-progress');
        const usageText = document.getElementById('disk-usage-text');
        const freeSpaceElement = document.getElementById('free-space-gb');
        
        if (!progressBar || !usageText || !freeSpaceElement) {
            return;
        }

        if (progressBar) {
            const usagePercent = diskUsage.usage_percentage || 0;
            progressBar.style.width = usagePercent + '%';
            progressBar.textContent = usagePercent.toFixed(1) + '%';
            
            // Set color based on usage
            if (usagePercent > 90) {
                progressBar.className = 'progress-bar bg-danger';
            } else if (usagePercent > 75) {
                progressBar.className = 'progress-bar bg-warning';
            } else {
                progressBar.className = 'progress-bar bg-success';
            }
        }

        if (usageText) {
            usageText.textContent = `${diskUsage.used_gb?.toFixed(1) || 0} GB used of ${diskUsage.total_gb?.toFixed(1) || 0} GB`;
        }

        if (freeSpaceElement) {
            freeSpaceElement.textContent = (diskUsage.free_gb || 0).toFixed(1);
        }
    },

    /**
     * Update file counts display
     */
    updateFileCounts: function(fileCounts) {
        
        if (!fileCounts) {
            return;
        }

        const sentFilesElement = document.getElementById('sent-files-count');
        const unsentFilesElement = document.getElementById('unsent-files-count');
        const totalFilesElement = document.getElementById('total-files');
        
        if (!sentFilesElement || !unsentFilesElement || !totalFilesElement) {
            return;
        }

        if (sentFilesElement) {
            sentFilesElement.textContent = fileCounts.sent_files || 0;
        }

        if (unsentFilesElement) {
            unsentFilesElement.textContent = fileCounts.unsent_files || 0;
        }

        if (totalFilesElement) {
            totalFilesElement.textContent = fileCounts.total_files || 0;
        }
    },

    /**
     * Update folder stats display
     */
    updateFolderStats: function(folderStats) {
        if (!folderStats) return;

        const folderSizeText = document.getElementById('folder-size-text');
        if (folderSizeText) {
            folderSizeText.textContent = `${(folderStats.total_size_mb || 0).toFixed(1)} MB`;
        }
    },

    /**
     * Update cleanup stats display
     */
    updateCleanupStats: function(cleanupStats) {
        if (!cleanupStats) return;

        const filesDeletedElement = document.getElementById('files-deleted-count');
        const spaceFreedElement = document.getElementById('space-freed-gb');

        if (filesDeletedElement) {
            filesDeletedElement.textContent = cleanupStats.total_files_deleted || 0;
        }

        if (spaceFreedElement) {
            spaceFreedElement.textContent = (cleanupStats.disk_space_freed_gb || 0).toFixed(2);
        }
    },

    /**
     * Update configuration form
     */
    updateConfigurationForm: function(config) {
        if (!config) return;

        const minFreeSpaceInput = document.getElementById('min-free-space');
        const retentionDaysInput = document.getElementById('retention-days');
        const batchSizeInput = document.getElementById('batch-size');
        const monitorIntervalInput = document.getElementById('monitor-interval');

        if (minFreeSpaceInput) {
            minFreeSpaceInput.value = config.min_free_space_gb || 10;
        }

        if (retentionDaysInput) {
            retentionDaysInput.value = config.retention_days || 7;
        }

        if (batchSizeInput) {
            batchSizeInput.value = config.batch_size || 100;
        }

        if (monitorIntervalInput) {
            monitorIntervalInput.value = config.monitor_interval || 300;
        }
    },

    /**
     * Update monitoring status display
     */
    updateMonitoringStatus: function(status) {
        
        if (!status) {
            return;
        }

        const monitoringStatus = document.getElementById('monitoring-status');
        const monitoringText = document.getElementById('monitoring-text');
        const toggleBtn = document.getElementById('toggle-monitoring-btn');

        this.isMonitoring = status.running || false;

        if (monitoringStatus) {
            const statusDot = monitoringStatus.querySelector('.status-dot');
            if (statusDot) {
                statusDot.className = this.isMonitoring ? 'status-dot status-online' : 'status-dot status-offline';
            }
        }

        if (monitoringText) {
            monitoringText.textContent = this.isMonitoring ? 'Running' : 'Stopped';
        }

        if (toggleBtn) {
            toggleBtn.textContent = this.isMonitoring ? 'Stop Monitoring' : 'Start Monitoring';
            toggleBtn.className = this.isMonitoring ? 'btn btn-sm btn-outline-danger mt-2' : 'btn btn-sm btn-outline-primary mt-2';
        }
    },

    /**
     * Update recommendations display
     */
    updateRecommendations: function(status) {
        const recommendationsContainer = document.getElementById('recommendations-container');
        if (!recommendationsContainer) return;

        const diskUsage = status.disk_usage;
        const recommendations = [];

        if (diskUsage && diskUsage.free_gb < 5.0) {
            recommendations.push({
                level: 'danger',
                text: `CRITICAL: Very low disk space (${diskUsage.free_gb.toFixed(1)} GB free). Consider immediate cleanup.`
            });
        } else if (diskUsage && diskUsage.free_gb < 10.0) {
            recommendations.push({
                level: 'warning',
                text: `WARNING: Low disk space (${diskUsage.free_gb.toFixed(1)} GB free). Schedule cleanup soon.`
            });
        }

        const folderStats = status.folder_stats;
        if (folderStats && folderStats.total_size_mb > 1000) {
            recommendations.push({
                level: 'info',
                text: 'Consider reducing retention period to save disk space.'
            });
        }

        const fileCounts = status.file_counts;
        if (fileCounts && fileCounts.unsent_files > 100) {
            recommendations.push({
                level: 'warning',
                text: 'High number of unsent files. Check network connectivity.'
            });
        }

        if (recommendations.length === 0) {
            recommendations.push({
                level: 'success',
                text: 'Storage system is healthy. No immediate action required.'
            });
        }

        // Render recommendations
        recommendationsContainer.innerHTML = recommendations.map(rec => `
            <div class="alert alert-${rec.level} alert-dismissible fade show" role="alert">
                <i class="fas fa-lightbulb"></i> ${rec.text}
                <button type="button" class="close" data-dismiss="alert">
                    <span>&times;</span>
                </button>
            </div>
        `).join('');
    },

    /**
     * Toggle monitoring on/off
     */
    toggleMonitoring: function() {
        if (this.isMonitoring) {
            this.stopMonitoring();
        } else {
            this.startMonitoring();
        }
    },

    /**
     * Start monitoring
     */
    startMonitoring: function() {
        if (this.socket) {
            this.socket.emit('storage_monitor_start', { interval: 300 });
        } else {
            AICameraUtils.apiRequest('/storage/monitor/start', {
                method: 'POST',
                body: JSON.stringify({ interval: 300 })
            })
            .then(data => {
                this.handleMonitorResponse(data);
            })
            .catch(error => {
            });
        }
    },

    /**
     * Stop monitoring
     */
    stopMonitoring: function() {
        if (this.socket) {
            this.socket.emit('storage_monitor_stop');
        } else {
            AICameraUtils.apiRequest('/storage/monitor/stop', {
                method: 'POST'
            })
            .then(data => {
                this.handleMonitorResponse(data);
            })
            .catch(error => {
            });
        }
    },

    /**
     * Perform manual cleanup
     */
    performManualCleanup: function() {
        const cleanupBtn = document.getElementById('manual-cleanup-btn');
        if (cleanupBtn) {
            cleanupBtn.disabled = true;
            cleanupBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Cleaning...';
        }

        if (this.socket) {
            this.socket.emit('storage_cleanup_request');
        } else {
            AICameraUtils.apiRequest('/storage/cleanup', {
                method: 'POST'
            })
            .then(data => {
                this.handleCleanupResponse(data);
            })
            .catch(error => {
                this.resetCleanupButton();
            });
        }
    },

    /**
     * Reset cleanup button
     */
    resetCleanupButton: function() {
        const cleanupBtn = document.getElementById('manual-cleanup-btn');
        if (cleanupBtn) {
            cleanupBtn.disabled = false;
            cleanupBtn.innerHTML = '<i class="fas fa-broom"></i> Manual Cleanup';
        }
    },

    /**
     * Refresh status
     */
    refreshStatus: function() {
        this.requestStorageStatus();
    },

    /**
     * Get analytics
     */
    getAnalytics: function() {
        if (this.socket) {
            this.socket.emit('storage_analytics_request', { days: 7 });
        } else {
            AICameraUtils.apiRequest('/storage/analytics?days=7')
                .then(data => {
                    this.updateAnalytics(data);
                })
                .catch(error => {
                });
        }
    },

    /**
     * Update analytics display
     */
    updateAnalytics: function(data) {
        if (!data || !data.success) {
            return;
        }

        // Update analytics display
        const analytics = data.data;
        
        // You can add more analytics display logic here
    },

    /**
     * Update configuration
     */
    updateConfiguration: function() {
        const config = {
            min_free_space_gb: parseFloat(document.getElementById('min-free-space').value),
            retention_days: parseInt(document.getElementById('retention-days').value),
            batch_size: parseInt(document.getElementById('batch-size').value),
            monitor_interval: parseInt(document.getElementById('monitor-interval').value)
        };

        if (this.socket) {
            this.socket.emit('storage_config_update', { config: config });
        } else {
            AICameraUtils.apiRequest('/storage/config', {
                method: 'POST',
                body: JSON.stringify(config)
            })
            .then(data => {
                this.handleConfigResponse(data);
            })
            .catch(error => {
            });
        }
    },

    /**
     * Request alerts
     */
    requestAlerts: function() {
        if (this.socket) {
            this.socket.emit('storage_alerts_request');
        } else {
            AICameraUtils.apiRequest('/storage/alerts')
                .then(data => {
                    this.updateAlerts(data);
                })
                .catch(error => {
                });
        }
    },

    /**
     * Update alerts display
     */
    updateAlerts: function(data) {
        if (!data || !data.success) {
            return;
        }

        const alertsContainer = document.getElementById('alerts-container');
        if (!alertsContainer) return;

        const alerts = data.data.alerts || [];
        
        if (alerts.length === 0) {
            alertsContainer.innerHTML = `
                <div class="text-center text-muted">
                    <i class="fas fa-info-circle"></i> No alerts at the moment
                </div>
            `;
            return;
        }

        alertsContainer.innerHTML = alerts.map(alert => `
            <div class="alert alert-${alert.level === 'CRITICAL' ? 'danger' : 'warning'} alert-dismissible fade show" role="alert">
                <strong>${alert.level}:</strong> ${alert.message}
                <br><small class="text-muted">${new Date(alert.timestamp).toLocaleString()}</small>
                <button type="button" class="close" data-dismiss="alert">
                    <span>&times;</span>
                </button>
            </div>
        `).join('');
    },

    /**
     * Clear alerts
     */
    clearAlerts: function() {
        if (this.socket) {
            this.socket.emit('storage_alerts_clear');
        } else {
            AICameraUtils.apiRequest('/storage/alerts/clear', {
                method: 'POST'
            })
            .then(data => {
                this.updateAlerts(data);
            })
            .catch(error => {
            });
        }
    },

    /**
     * Handle cleanup response
     */
    handleCleanupResponse: function(data) {
        this.resetCleanupButton();
        
        if (data && data.success) {
            this.requestStorageStatus(); // Refresh status
        } else {
        }
    },

    /**
     * Handle configuration response
     */
    handleConfigResponse: function(data) {
        if (data && data.success) {
        } else {
        }
    },

    /**
     * Handle monitoring response
     */
    handleMonitorResponse: function(data) {
        if (data && data.success) {
            this.requestStorageStatus(); // Refresh status
        } else {
        }
    },

    /**
     * Cleanup when leaving page
     */
    cleanup: function() {
        if (this.statusUpdateInterval) {
            clearInterval(this.statusUpdateInterval);
        }
        
        if (this.socket) {
            this.socket.emit('leave_storage_room');
        }
    }
};

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    StorageManager.init();
    
    window.addEventListener('beforeunload', function() {
        StorageManager.cleanup();
    });
    
});

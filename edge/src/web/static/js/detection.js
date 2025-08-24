/**
 * AI Camera v2.0 - Unified Detection Dashboard JavaScript
 * 
 * Combined detection control, monitoring, and results functionality.
 * 
 * @author AI Camera Team
 * @version 2.0
 * @since 2025-08-23
 */

// Unified Detection Manager
const DetectionManager = {
    socket: null,
    statusUpdateInterval: null,
    detectionRunning: false,
    lastStatusUpdate: null,
    
    // Detection Results Manager properties
    currentPage: 1,
    perPage: 20,
    totalPages: 0,
    currentSort: { by: 'created_at', order: 'desc' },
    currentFilters: {
        search: '',
        dateFrom: '',
        dateTo: '',
        hasVehicles: '',
        hasPlates: ''
    },
    isLoading: false,
    
    /**
     * Initialize unified detection dashboard
     */
    init: function() {
        this.initializeWebSocket();
        this.setupEventHandlers();
        this.setupFormHandlers();
        this.setupResultsEventHandlers();
        this.setupComprehensiveOutputToggle();
        this.startPeriodicUpdates();
        this.loadResults();
        this.loadStatistics();
        this.loadConfiguration();
        console.log('Unified Detection Manager initialized');
    },

    /**
     * Initialize WebSocket connection
     */
    initializeWebSocket: function() {
        if (typeof io === 'undefined') {
            console.warn('Socket.IO not available');
            return;
        }

        this.socket = io();
        this.setupSocketHandlers();
    },

    /**
     * Setup WebSocket event handlers
     */
    setupSocketHandlers: function() {
        if (!this.socket) return;

        this.socket.on('connect', () => {
            console.log('Connected to server');
            this.addLogMessage('Connected to server', 'info');
            this.socket.emit('join_detection_room');
            this.requestStatusUpdate();
        });

        this.socket.on('disconnect', () => {
            console.log('Disconnected from server');
            this.addLogMessage('Disconnected from server', 'warning');
        });

        this.socket.on('detection_status_update', (data) => {
            if (data && data.success && data.detection_status) {
                this.updateDetectionStatus(data.detection_status);
            } else {
                console.error('Invalid detection status update:', data);
            }
        });

        this.socket.on('detection_control_response', (response) => {
            this.handleControlResponse(response);
        });

        this.socket.on('detection_statistics_update', (stats) => {
            this.updateStatistics(stats);
        });

        this.socket.on('detection_status_error', (error) => {
            this.addLogMessage('Status error: ' + error.error, 'error');
        });
    },

    /**
     * Setup event handlers for detection control
     */
    setupEventHandlers: function() {
        // Control buttons
        const startBtn = document.getElementById('start-detection');
        const stopBtn = document.getElementById('stop-detection');
        const processBtn = document.getElementById('process-frame');

        if (startBtn) startBtn.addEventListener('click', () => this.controlDetection('start'));
        if (stopBtn) stopBtn.addEventListener('click', () => this.controlDetection('stop'));
        if (processBtn) processBtn.addEventListener('click', () => this.processFrame());
    },

    /**
     * Setup event handlers for detection results
     */
    setupResultsEventHandlers: function() {
        // Setup modal event handlers
        this.setupModalEventHandlers();
        // Refresh button
        const refreshBtn = document.getElementById('refresh-results-btn');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => {
                this.loadResults();
                this.addLogMessage('Refreshing detection results...', 'info');
            });
        }

        // Export button
        const exportBtn = document.getElementById('export-results-btn');
        if (exportBtn) {
            exportBtn.addEventListener('click', () => {
                this.showExportModal();
            });
        }

        // Clear filters button
        const clearFiltersBtn = document.getElementById('clear-filters-btn');
        if (clearFiltersBtn) {
            clearFiltersBtn.addEventListener('click', () => {
                this.clearFilters();
            });
        }

        // Search input with debounce
        const searchInput = document.getElementById('search-input');
        if (searchInput) {
            let searchTimeout;
            searchInput.addEventListener('input', (e) => {
                clearTimeout(searchTimeout);
                searchTimeout = setTimeout(() => {
                    this.currentFilters.search = e.target.value;
                    this.currentPage = 1;
                    this.loadResults();
                }, 500);
            });
        }

        // Date filters
        const dateFrom = document.getElementById('date-from');
        if (dateFrom) {
            dateFrom.addEventListener('change', (e) => {
                this.currentFilters.dateFrom = e.target.value;
                this.currentPage = 1;
                this.loadResults();
            });
        }

        const dateTo = document.getElementById('date-to');
        if (dateTo) {
            dateTo.addEventListener('change', (e) => {
                this.currentFilters.dateTo = e.target.value;
                this.currentPage = 1;
                this.loadResults();
            });
        }

        // Vehicle filter
        const hasVehicles = document.getElementById('has-vehicles');
        if (hasVehicles) {
            hasVehicles.addEventListener('change', (e) => {
                this.currentFilters.hasVehicles = e.target.value;
                this.currentPage = 1;
                this.loadResults();
            });
        }

        // Plates filter
        const hasPlates = document.getElementById('has-plates');
        if (hasPlates) {
            hasPlates.addEventListener('change', (e) => {
                this.currentFilters.hasPlates = e.target.value;
                this.currentPage = 1;
                this.loadResults();
            });
        }

        // Per page selector
        const perPageSelect = document.getElementById('per-page-select');
        if (perPageSelect) {
            perPageSelect.addEventListener('change', (e) => {
                this.perPage = parseInt(e.target.value);
                this.currentPage = 1;
                this.loadResults();
            });
        }

        // Export confirmation
        const confirmExportBtn = document.getElementById('confirm-export-btn');
        if (confirmExportBtn) {
            confirmExportBtn.addEventListener('click', () => {
                this.exportResults();
            });
        }

        // Sortable table headers
        document.querySelectorAll('.sortable').forEach(header => {
            header.addEventListener('click', (e) => {
                const sortBy = e.currentTarget.dataset.sort;
                this.handleSort(sortBy);
            });
        });
    },

    /**
     * Setup modal event handlers
     */
    setupModalEventHandlers: function() {
        const detailModal = document.getElementById('detail-modal');
        if (detailModal) {
            // Handle modal hidden event
            detailModal.addEventListener('hidden.bs.modal', () => {
                // Clear modal content
                const modalBody = document.getElementById('detail-modal-body');
                if (modalBody) {
                    modalBody.innerHTML = '';
                }
                
                // Clear modal instance
                this.currentDetailModal = null;
                
                // Ensure dashboard remains active
                console.log('Detail modal closed, dashboard remains active');
            });
            
            // Handle modal shown event
            detailModal.addEventListener('shown.bs.modal', () => {
                console.log('Detail modal opened');
            });
        }
    },

    /**
     * Setup form handlers
     */
    setupFormHandlers: function() {
        const configForm = document.getElementById('detection-config-form');
        if (configForm) {
            configForm.addEventListener('submit', (e) => this.handleConfigSubmit(e));
        }
    },

    /**
     * Start periodic status updates - OPTIMIZED for reduced resource usage
     */
    startPeriodicUpdates: function() {
        // Update immediately
        this.requestStatusUpdate();
        
        // Setup periodic updates every 30 seconds (increased from 5 seconds for reduced resource usage)
        this.statusUpdateInterval = setInterval(() => {
            this.requestStatusUpdate();
        }, 30000);
        
        // Load recent results after 2 seconds (increased from 1 second)
        setTimeout(() => this.loadRecentResults(), 2000);
        
        // Add initial log message
        this.addLogMessage('Detection dashboard initialized (optimized)', 'info');
        this.addLogMessage('Connecting to detection service...', 'info');
    },

    /**
     * Control detection service
     */
    controlDetection: function(command) {
        const button = document.getElementById(command === 'start' ? 'start-detection' : 'stop-detection');
        if (button) button.disabled = true;
        
        if (!this.socket || !this.socket.connected) {
            AICameraUtils.showToast('Not connected to server', 'warning');
            if (button) button.disabled = false;
            return;
        }
        
        this.socket.emit('detection_control', { command: command });
        this.addLogMessage(`Sending ${command} command...`, 'info');
    },

    /**
     * Process single frame
     */
    processFrame: function() {
        const button = document.getElementById('process-frame');
        if (button) {
            button.disabled = true;
            button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';
        }
        
        if (!this.socket || !this.socket.connected) {
            AICameraUtils.showToast('Not connected to server', 'warning');
            this.resetProcessButton();
            return;
        }
        
        this.socket.emit('detection_control', { command: 'process_frame' });
        this.addLogMessage('Processing single frame...', 'info');
        
        setTimeout(() => this.resetProcessButton(), 3000);
    },

    /**
     * Reset process frame button
     */
    resetProcessButton: function() {
        const button = document.getElementById('process-frame');
        if (button) {
            button.disabled = false;
            button.innerHTML = '<i class="fas fa-camera"></i> Process Frame';
        }
    },

    /**
     * Handle control response
     */
    handleControlResponse: function(response) {
        const { command, success, message, error } = response;
        
        if (success) {
            this.addLogMessage(`${command} successful: ${message}`, 'success');
            AICameraUtils.showToast(`${command} successful`, 'success');
        } else {
            this.addLogMessage(`${command} failed: ${error || message}`, 'error');
            AICameraUtils.showToast(`${command} failed: ${error || message}`, 'error');
        }
        
        // Re-enable buttons
        const startBtn = document.getElementById('start-detection');
        const stopBtn = document.getElementById('stop-detection');
        if (startBtn) startBtn.disabled = false;
        if (stopBtn) stopBtn.disabled = false;
        
        // Request updated status
        this.requestStatusUpdate();
    },

    /**
     * Request status update
     */
    requestStatusUpdate: function() {
        if (this.socket && this.socket.connected) {
            this.socket.emit('detection_status_request');
            this.socket.emit('detection_statistics_request');
        } else {
            // Fallback to HTTP API if WebSocket not available
            this.requestStatusViaHTTP();
        }
    },

    /**
     * Request status via HTTP API (fallback)
     */
    requestStatusViaHTTP: function() {
        AICameraUtils.apiRequest('/detection/status')
            .then(data => {
                if (data && data.success && data.detection_status) {
                    this.updateDetectionStatus(data.detection_status);
                } else {
                    console.error('Invalid status response:', data);
                }
            })
            .catch(error => {
                console.warn('Detection status not available:', error.message);
                        // Set default status according to variable_management.md standards
        this.updateDetectionStatus({
            service_running: false,
            detection_processor_status: {
                models_loaded: false,
                vehicle_model_available: false,
                lp_detection_model_available: false,
                lp_ocr_model_available: false,
                easyocr_available: false
            },
            detection_interval: 0.1,
            confidence_threshold: 0.5
        });
            });

        AICameraUtils.apiRequest('/detection/statistics')
            .then(data => {
                if (data && data.success && data.statistics) {
                    this.updateStatistics(data.statistics);
                } else {
                    console.error('Invalid statistics response:', data);
                }
            })
            .catch(error => {
                console.warn('Detection statistics not available:', error.message);
                // Set default statistics
                this.updateStatistics({
                    total_frames_processed: 0,
                    total_vehicles_detected: 0,
                    total_plates_detected: 0,
                    successful_ocr: 0,
                    detection_rate_percent: 0,
                    avg_processing_time_ms: 0
                });
            });
    },

    /**
     * Update detection status display
     */
    updateDetectionStatus: function(status) {
        this.lastStatusUpdate = status;
        
        // Update service status
        const serviceRunning = status.service_running || false;
        this.detectionRunning = serviceRunning;
        
        const serviceStatusElement = document.getElementById('service-status');
        if (serviceStatusElement) {
            serviceStatusElement.textContent = serviceRunning ? 'Running' : 'Stopped';
            serviceStatusElement.className = `badge ${serviceRunning ? 'bg-success' : 'bg-secondary'}`;
        }
        
        // Update service status card
        const statusCard = document.getElementById('service-status-card');
        if (statusCard) {
            statusCard.className = `card status-card ${serviceRunning ? 'active' : ''}`;
        }
        
        // Update models status
        const processorStatus = status.detection_processor_status || {};
        const modelsLoaded = processorStatus.models_loaded || false;
        
        const modelsStatusElement = document.getElementById('models-status');
        if (modelsStatusElement) {
            modelsStatusElement.textContent = modelsLoaded ? 'Loaded' : 'Not Loaded';
            modelsStatusElement.className = `badge ${modelsLoaded ? 'bg-success' : 'bg-danger'}`;
        }
        
        // Update detection interval with fallback
        const interval = status.detection_interval || 0.1;
        const intervalElement = document.getElementById('detection-interval');
        const intervalSetting = document.getElementById('detection-interval');
        if (intervalElement) intervalElement.textContent = `${interval}s`;
        if (intervalSetting) intervalSetting.value = interval;
        
        // Update model status indicators
        this.updateModelStatus('vehicle-model-status', processorStatus.vehicle_model_available);
        this.updateModelStatus('lp-detection-model-status', processorStatus.lp_detection_model_available);
        this.updateModelStatus('lp-ocr-model-status', processorStatus.lp_ocr_model_available);
        this.updateModelStatus('easyocr-status', processorStatus.easyocr_available);
        
        // Update detection configuration display with fallbacks
        const resolution = processorStatus.detection_resolution || [640, 640];
        const resolutionElement = document.getElementById('detection-resolution');
        if (resolutionElement) resolutionElement.textContent = `${resolution[0]}x${resolution[1]}`;
        
        const vehicleConfElement = document.getElementById('vehicle-confidence');
        if (vehicleConfElement) vehicleConfElement.textContent = processorStatus.confidence_threshold || 0.5;
        
        const plateConfElement = document.getElementById('plate-confidence');
        if (plateConfElement) plateConfElement.textContent = processorStatus.plate_confidence_threshold || 0.3;
        
        // Update button states
        this.updateButtonStates(serviceRunning, modelsLoaded);
    },

    /**
     * Update model status indicator
     */
    updateModelStatus: function(elementId, isLoaded) {
        const element = document.getElementById(elementId);
        if (element) {
            element.className = `model-status ${isLoaded ? 'loaded' : 'not-loaded'}`;
        }
    },

    /**
     * Update button states
     */
    updateButtonStates: function(serviceRunning, modelsLoaded) {
        const startBtn = document.getElementById('start-detection');
        const stopBtn = document.getElementById('stop-detection');
        const processBtn = document.getElementById('process-frame');
        
        if (startBtn) startBtn.disabled = serviceRunning || !modelsLoaded;
        if (stopBtn) stopBtn.disabled = !serviceRunning;
        if (processBtn) processBtn.disabled = !modelsLoaded;
    },

    /**
     * Update statistics display
     */
    updateStatistics: function(stats) {
        // Update main statistics cards
        const statMappings = [
            { key: 'total_detections', elementId: 'total-detections', default: 0 },
            { key: 'total_vehicles', elementId: 'total-vehicles', default: 0 },
            { key: 'total_plates', elementId: 'total-plates', default: 0 },
            { key: 'avg_processing_time_ms', elementId: 'avg-processing-time', default: 0, suffix: 'ms', format: (val) => `${val.toFixed(1)}ms` },
            { key: 'current_fps', elementId: 'current-fps', default: 0, format: (val) => val.toFixed(1) },
            { key: 'detection_errors', elementId: 'detection-errors', default: 0 }
        ];

        statMappings.forEach(({ key, elementId, default: defaultValue, suffix = '', format }) => {
            const element = document.getElementById(elementId);
            if (element) {
                const value = stats[key] || defaultValue;
                if (format) {
                    element.textContent = format(value);
                } else {
                    element.textContent = `${value}${suffix}`;
                }
            }
        });
        
        // Update last detection timestamp
        const lastDetectionElement = document.getElementById('last-detection');
        if (lastDetectionElement) {
            if (stats.last_detection) {
                const date = new Date(stats.last_detection);
                lastDetectionElement.textContent = date.toLocaleString();
            } else {
                lastDetectionElement.textContent = 'None';
            }
        }
    },

    /**
     * Add log message
     */
    addLogMessage: function(message, type = 'info') {
        AICameraUtils.addLogMessage('detection-log', message, type);
    },

    /**
     * Load recent detection results
     */
    loadRecentResults: function() {
        console.log('Loading recent detection results...');
        AICameraUtils.apiRequest('/detection/results')
            .then(data => {
                console.log('Recent results response:', data);
                if (data.success) {
                    // Take only the first 10 results for recent display
                    const recentResults = data.results.slice(0, 10);
                    this.displayRecentResults(recentResults);
                } else {
                    throw new Error(data.error || 'Failed to load results');
                }
            })
            .catch(error => {
                console.error('Error loading recent results:', error);
                this.addLogMessage('Failed to load recent results: ' + error.message, 'error');
            });
    },

    /**
     * Load detection results with pagination and filters
     */
    loadResults: function() {
        if (this.isLoading) return;
        
        this.isLoading = true;
        this.showLoadingState();
        
        const params = new URLSearchParams({
            page: this.currentPage,
            per_page: this.perPage,
            sort_by: this.currentSort.by,
            sort_order: this.currentSort.order
        });
        
        // Add filters
        if (this.currentFilters.search) params.append('search', this.currentFilters.search);
        if (this.currentFilters.dateFrom) params.append('date_from', this.currentFilters.dateFrom);
        if (this.currentFilters.dateTo) params.append('date_to', this.currentFilters.dateTo);
        if (this.currentFilters.hasVehicles) params.append('has_vehicles', this.currentFilters.hasVehicles);
        if (this.currentFilters.hasPlates) params.append('has_plates', this.currentFilters.hasPlates);
        
        console.log('Loading detection results...');
        AICameraUtils.apiRequest('/detection/results')
            .then(data => {
                console.log('Results response:', data);
                if (data.success) {
                    // Apply client-side filtering and pagination
                    const filteredResults = this.filterResults(data.results);
                    const paginatedResults = this.paginateResults(filteredResults);
                    this.displayResults({
                        results: paginatedResults,
                        count: filteredResults.length
                    });
                } else {
                    throw new Error(data.error || 'Failed to load results');
                }
            })
            .catch(error => {
                console.error('Error loading results:', error);
                this.showErrorState(error.message);
            })
            .finally(() => {
                this.isLoading = false;
            });
    },

    /**
     * Load statistics
     */
    loadStatistics: function() {
        AICameraUtils.apiRequest('/detection/statistics')
            .then(data => {
                if (data.success) {
                    this.updateStatisticsDisplay(data.statistics);
                }
            })
            .catch(error => {
                console.error('Failed to load statistics:', error);
            });
    },

    /**
     * Display detection results
     */
    displayResults: function(data) {
        const { results, count } = data;
        
        this.updateResultsCount(count || results.length);
        this.renderResultsTable(results);
        this.renderPagination();
        
        if (!results || results.length === 0) {
            this.showEmptyState();
        } else {
            this.hideEmptyState();
        }
        
        this.hideLoadingState();
        this.hideErrorState();
    },

    /**
     * Render results table
     */
    renderResultsTable: function(results) {
        const tbody = document.getElementById('results-table-body');
        if (!tbody) return;
        
        tbody.innerHTML = '';
        
        results.forEach(result => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${result.id || 'N/A'}</td>
                <td>${AICameraUtils.formatTimestamp(result.timestamp || result.created_at)}</td>
                <td>${result.vehicles_detected || result.vehicles_count || 0}</td>
                <td>${result.plates_detected || result.plates_count || 0}</td>
                <td>${this.formatOcrResults(result.ocr_results)}</td>
                <td>${result.processing_time_ms || 0}ms</td>
                <td>
                    <button class="btn btn-sm btn-outline-primary" onclick="DetectionManager.showDetail(${result.id || 0})">
                        <i class="fas fa-eye"></i> View
                    </button>
                </td>
            `;
            tbody.appendChild(row);
        });
    },

    /**
     * Format OCR results for display
     */
    formatOcrResults: function(ocrResults) {
        if (!ocrResults || ocrResults.length === 0) {
            return '<span class="text-muted">No OCR results</span>';
        }
        
        return ocrResults.map(ocr => 
            `<span class="badge bg-success me-1">${ocr.text}</span>`
        ).join('');
    },





    /**
     * Handle sorting
     */
    handleSort: function(sortBy) {
        if (this.currentSort.by === sortBy) {
            this.currentSort.order = this.currentSort.order === 'asc' ? 'desc' : 'asc';
        } else {
            this.currentSort.by = sortBy;
            this.currentSort.order = 'desc';
        }
        
        this.updateSortIcons();
        this.loadResults();
    },

    /**
     * Update sort icons
     */
    updateSortIcons: function() {
        document.querySelectorAll('.sortable').forEach(header => {
            const icon = header.querySelector('.sort-icon');
            const sortBy = header.dataset.sort;
            
            if (sortBy === this.currentSort.by) {
                icon.className = `fas fa-sort-${this.currentSort.order === 'asc' ? 'up' : 'down'} sort-icon`;
            } else {
                icon.className = 'fas fa-sort sort-icon';
            }
        });
    },

    /**
     * Clear filters
     */
    clearFilters: function() {
        this.currentFilters = {
            search: '',
            dateFrom: '',
            dateTo: '',
            hasVehicles: '',
            hasPlates: ''
        };
        
        // Reset form inputs
        const searchInput = document.getElementById('search-input');
        if (searchInput) searchInput.value = '';
        
        const dateFrom = document.getElementById('date-from');
        if (dateFrom) dateFrom.value = '';
        
        const dateTo = document.getElementById('date-to');
        if (dateTo) dateTo.value = '';
        
        const hasVehicles = document.getElementById('has-vehicles');
        if (hasVehicles) hasVehicles.value = '';
        
        const hasPlates = document.getElementById('has-plates');
        if (hasPlates) hasPlates.value = '';
        
        this.currentPage = 1;
        this.loadResults();
    },

    /**
     * Show export modal
     */
    showExportModal: function() {
        const modal = new bootstrap.Modal(document.getElementById('export-modal'));
        modal.show();
    },

    /**
     * Export results
     */
    exportResults: function() {
        const format = document.getElementById('export-format').value;
        
        const params = new URLSearchParams({
            format: format,
            sort_by: this.currentSort.by,
            sort_order: this.currentSort.order
        });
        
        // Add filters
        if (this.currentFilters.search) params.append('search', this.currentFilters.search);
        if (this.currentFilters.dateFrom) params.append('date_from', this.currentFilters.dateFrom);
        if (this.currentFilters.dateTo) params.append('date_to', this.currentFilters.dateTo);
        if (this.currentFilters.hasVehicles) params.append('has_vehicles', this.currentFilters.hasVehicles);
        if (this.currentFilters.hasPlates) params.append('has_plates', this.currentFilters.hasPlates);
        
        const url = `/detection_results/api/export?${params.toString()}`;
        
        // Create download link
        const link = document.createElement('a');
        link.href = url;
        link.download = `detection_results_${new Date().toISOString().split('T')[0]}.${format}`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        // Close modal
        const modal = bootstrap.Modal.getInstance(document.getElementById('export-modal'));
        modal.hide();
        
        AICameraUtils.showToast('Export started', 'success');
    },

    /**
     * Update statistics display
     */
    updateStatisticsDisplay: function(stats) {
        // Update main statistics cards
        const elements = {
            'total-detections': stats.total_detections || 0,
            'total-vehicles': stats.total_vehicles || 0,
            'total-plates': stats.total_plates || 0,
            'avg-processing-time': `${(stats.avg_processing_time_ms || 0).toFixed(1)}ms`,
            'current-fps': (stats.current_fps || 0).toFixed(1),
            'detection-errors': stats.detection_errors || 0
        };
        
        Object.entries(elements).forEach(([id, value]) => {
            const element = document.getElementById(id);
            if (element) element.textContent = value;
        });
        
        // Update last detection timestamp
        const lastDetectionElement = document.getElementById('last-detection');
        if (lastDetectionElement) {
            if (stats.last_detection) {
                const date = new Date(stats.last_detection);
                lastDetectionElement.textContent = date.toLocaleString();
            } else {
                lastDetectionElement.textContent = 'None';
            }
        }
    },

    /**
     * Show loading state
     */
    showLoadingState: function() {
        const loadingSpinner = document.getElementById('loading-spinner');
        const resultsTable = document.getElementById('results-table-container');
        const emptyState = document.getElementById('empty-state');
        const errorState = document.getElementById('error-state');
        
        if (loadingSpinner) loadingSpinner.style.display = 'block';
        if (resultsTable) resultsTable.style.display = 'none';
        if (emptyState) emptyState.style.display = 'none';
        if (errorState) errorState.style.display = 'none';
    },

    /**
     * Hide loading state
     */
    hideLoadingState: function() {
        const loadingSpinner = document.getElementById('loading-spinner');
        const resultsTable = document.getElementById('results-table-container');
        
        if (loadingSpinner) loadingSpinner.style.display = 'none';
        if (resultsTable) resultsTable.style.display = 'block';
    },

    /**
     * Show empty state
     */
    showEmptyState: function() {
        const emptyState = document.getElementById('empty-state');
        const resultsTable = document.getElementById('results-table-container');
        
        if (emptyState) emptyState.style.display = 'block';
        if (resultsTable) resultsTable.style.display = 'none';
    },

    /**
     * Hide empty state
     */
    hideEmptyState: function() {
        const emptyState = document.getElementById('empty-state');
        if (emptyState) emptyState.style.display = 'none';
    },

    /**
     * Show error state
     */
    showErrorState: function(message) {
        const errorState = document.getElementById('error-state');
        const errorMessage = document.getElementById('error-message');
        const loadingSpinner = document.getElementById('loading-spinner');
        
        if (errorState) errorState.style.display = 'block';
        if (errorMessage) errorMessage.textContent = message;
        if (loadingSpinner) loadingSpinner.style.display = 'none';
    },

    /**
     * Hide error state
     */
    hideErrorState: function() {
        const errorState = document.getElementById('error-state');
        if (errorState) errorState.style.display = 'none';
    },

    /**
     * Update results count
     */
    updateResultsCount: function(total) {
        const countElement = document.getElementById('results-count');
        if (countElement) {
            countElement.textContent = `${total} results`;
        }
    },

    /**
     * Update pagination info
     */
    updatePaginationInfo: function(pagination) {
        const infoElement = document.getElementById('pagination-info');
        if (infoElement) {
            const start = (pagination.page - 1) * pagination.per_page + 1;
            const end = Math.min(start + pagination.per_page - 1, pagination.total);
            infoElement.textContent = `Showing ${start}-${end} of ${pagination.total} results`;
        }
    },

    /**
     * Render pagination
     */
    renderPagination: function() {
        const nav = document.getElementById('pagination-nav');
        const container = document.getElementById('pagination-container');
        
        if (!nav || !container) return;
        
        // Always show pagination container for info display
        container.style.display = 'block';
        nav.innerHTML = '';
        
        // Only show navigation buttons if there are multiple pages
        if (this.totalPages <= 1) {
            return;
        }
        
        // Previous button
        const prevLi = document.createElement('li');
        prevLi.className = `page-item ${this.currentPage === 1 ? 'disabled' : ''}`;
        prevLi.innerHTML = `
            <button class="page-link" onclick="DetectionManager.goToPage(${this.currentPage - 1})" ${this.currentPage === 1 ? 'disabled' : ''}>
                <i class="fas fa-chevron-left"></i>
            </button>
        `;
        nav.appendChild(prevLi);
        
        // Page numbers
        const startPage = Math.max(1, this.currentPage - 2);
        const endPage = Math.min(this.totalPages, this.currentPage + 2);
        
        for (let i = startPage; i <= endPage; i++) {
            const li = document.createElement('li');
            li.className = `page-item ${i === this.currentPage ? 'active' : ''}`;
            li.innerHTML = `
                <button class="page-link" onclick="DetectionManager.goToPage(${i})">${i}</button>
            `;
            nav.appendChild(li);
        }
        
        // Next button
        const nextLi = document.createElement('li');
        nextLi.className = `page-item ${this.currentPage === this.totalPages ? 'disabled' : ''}`;
        nextLi.innerHTML = `
            <button class="page-link" onclick="DetectionManager.goToPage(${this.currentPage + 1})" ${this.currentPage === this.totalPages ? 'disabled' : ''}>
                <i class="fas fa-chevron-right"></i>
            </button>
        `;
        nav.appendChild(nextLi);
    },

    /**
     * Go to specific page
     */
    goToPage: function(page) {
        if (page >= 1 && page <= this.totalPages && page !== this.currentPage) {
            this.currentPage = page;
            this.loadResults();
        }
    },

    /**
     * Filter results based on current filters
     */
    filterResults: function(results) {
        let filtered = results;
        
        // Search filter
        if (this.currentFilters.search) {
            const searchTerm = this.currentFilters.search.toLowerCase();
            filtered = filtered.filter(result => {
                const ocrText = result.ocr_text || '';
                const timestamp = result.timestamp || '';
                return ocrText.toLowerCase().includes(searchTerm) || 
                       timestamp.toLowerCase().includes(searchTerm);
            });
        }
        
        // Date filters
        if (this.currentFilters.dateFrom) {
            filtered = filtered.filter(result => {
                const resultDate = new Date(result.timestamp || result.created_at);
                const fromDate = new Date(this.currentFilters.dateFrom);
                return resultDate >= fromDate;
            });
        }
        
        if (this.currentFilters.dateTo) {
            filtered = filtered.filter(result => {
                const resultDate = new Date(result.timestamp || result.created_at);
                const toDate = new Date(this.currentFilters.dateTo);
                toDate.setHours(23, 59, 59); // End of day
                return resultDate <= toDate;
            });
        }
        
        // Vehicle filter
        if (this.currentFilters.hasVehicles) {
            const hasVehicles = this.currentFilters.hasVehicles === 'true';
            filtered = filtered.filter(result => {
                const hasVehiclesResult = (result.vehicles_count || 0) > 0;
                return hasVehiclesResult === hasVehicles;
            });
        }
        
        // Plates filter
        if (this.currentFilters.hasPlates) {
            const hasPlates = this.currentFilters.hasPlates === 'true';
            filtered = filtered.filter(result => {
                const hasPlatesResult = (result.plates_count || 0) > 0;
                return hasPlatesResult === hasPlates;
            });
        }
        
        return filtered;
    },

    /**
     * Paginate results
     */
    paginateResults: function(results) {
        const startIndex = (this.currentPage - 1) * this.perPage;
        const endIndex = startIndex + this.perPage;
        this.totalPages = Math.ceil(results.length / this.perPage);
        return results.slice(startIndex, endIndex);
    },

    /**
     * Display recent detection results
     */
    displayRecentResults: function(results) {
        const container = document.getElementById('recent-results');
        if (!container) return;
        
        if (!results || results.length === 0) {
            container.innerHTML = '<p class="text-muted text-center">No detection results available</p>';
            return;
        }
        
        container.innerHTML = '';
        
        results.slice(0, 10).forEach(result => {
            const resultDiv = document.createElement('div');
            const hasDetections = (result.vehicles_count || 0) > 0;
            resultDiv.className = `detection-result ${hasDetections ? 'success' : 'no-detection'}`;
            
            resultDiv.innerHTML = `
                <div class="d-flex justify-content-between align-items-center mb-2">
                    <small class="text-muted">${AICameraUtils.formatTimestamp(result.timestamp || result.created_at)}</small>
                    <div class="badge bg-${hasDetections ? 'success' : 'warning'}">
                        ${result.vehicles_count || 0} vehicles, ${result.plates_count || 0} plates
                    </div>
                </div>
                ${result.ocr_results && result.ocr_results.length > 0 ? 
                    `<div class="small"><strong>License Plates:</strong> ${result.ocr_results.map(ocr => ocr.text).join(', ')}</div>` : 
                    '<div class="small text-muted">No license plates detected</div>'
                }
            `;
            
            container.appendChild(resultDiv);
        });
    },

    /**
     * Load detection configuration from API
     */
    loadConfiguration: function() {
        AICameraUtils.apiRequest('/detection/config')
            .then(data => {
                if (data && data.success && data.config) {
                    this.updateConfigForm(data.config);
                } else {
                    console.error('Invalid config response:', data);
                }
            })
            .catch(error => {
                console.error('Failed to load configuration:', error);
                this.addLogMessage('Failed to load configuration: ' + error.message, 'error');
            });
    },

    /**
     * Update configuration form with data from API
     */
    updateConfigForm: function(config) {
        const intervalElement = document.getElementById('detection-interval');
        const vehicleConfElement = document.getElementById('vehicle-confidence');
        const plateConfElement = document.getElementById('plate-confidence');
        const autoStartElement = document.getElementById('auto-start-setting');
        
        if (intervalElement) intervalElement.value = config.detection_interval || 0.1;
        if (vehicleConfElement) vehicleConfElement.value = config.vehicle_confidence || 0.5;
        if (plateConfElement) plateConfElement.value = config.plate_confidence || 0.3;
        if (autoStartElement) autoStartElement.checked = config.auto_start || false;
    },

    /**
     * Handle configuration form submission
     */
    handleConfigSubmit: function(e) {
        e.preventDefault();
        
        const interval = parseFloat(document.getElementById('detection-interval').value);
        const autoStart = document.getElementById('auto-start-setting').checked;
        
        AICameraUtils.apiRequest('/detection/config', {
            method: 'POST',
            body: JSON.stringify({
                detection_interval: interval,
                auto_start: autoStart
            })
        })
        .then(data => {
            if (data.success) {
                this.addLogMessage('Configuration updated successfully', 'success');
                AICameraUtils.showToast('Configuration updated', 'success');
                this.requestStatusUpdate();
            } else {
                throw new Error(data.error || 'Configuration update failed');
            }
        })
        .catch(error => {
            this.addLogMessage('Failed to update configuration: ' + error.message, 'error');
        });
    },

    /**
     * Clear all filters
     */
    clearFilters: function() {
        this.currentFilters = {};
        this.currentPage = 1;
        
        // Clear form inputs
        const searchInput = document.getElementById('search-input');
        const dateFrom = document.getElementById('date-from');
        const dateTo = document.getElementById('date-to');
        const hasVehicles = document.getElementById('has-vehicles');
        const hasPlates = document.getElementById('has-plates');
        
        if (searchInput) searchInput.value = '';
        if (dateFrom) dateFrom.value = '';
        if (dateTo) dateTo.value = '';
        if (hasVehicles) hasVehicles.value = '';
        if (hasPlates) hasPlates.value = '';
        
        this.loadResults();
        this.addLogMessage('Filters cleared', 'info');
    },

    /**
     * Show export modal
     */
    showExportModal: function() {
        const modal = new bootstrap.Modal(document.getElementById('export-modal'));
        modal.show();
    },

    /**
     * Export results
     */
    exportResults: function() {
        const format = document.getElementById('export-format').value;
        this.addLogMessage(`Exporting results as ${format.toUpperCase()}...`, 'info');
        
        // For now, just show a message
        AICameraUtils.showToast(`Export functionality will be implemented soon`, 'info');
        
        // Close modal
        const modal = bootstrap.Modal.getInstance(document.getElementById('export-modal'));
        if (modal) modal.hide();
    },

    /**
     * Handle sorting
     */
    handleSort: function(sortBy) {
        if (this.currentSort.by === sortBy) {
            this.currentSort.order = this.currentSort.order === 'asc' ? 'desc' : 'asc';
        } else {
            this.currentSort.by = sortBy;
            this.currentSort.order = 'asc';
        }
        
        this.loadResults();
    },

    /**
     * Cleanup when leaving page
     */
    cleanup: function() {
        if (this.statusUpdateInterval) {
            clearInterval(this.statusUpdateInterval);
        }
    },

        /**
     * Show detail modal for a specific result
     */
    showDetail: function(resultId) {
        // Store current modal instance
        this.currentDetailModal = new bootstrap.Modal(document.getElementById('detail-modal'));
        const modalBody = document.getElementById('detail-modal-body');
        
        // Show loading in modal
        modalBody.innerHTML = `
            <div class="text-center py-5">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
                <div class="mt-2">Loading detection details...</div>
            </div>
        `;
        
        // Show modal
        this.currentDetailModal.show();

        // Load detailed data from specific detection endpoint
        AICameraUtils.apiRequest(`/detection/results/${resultId}`)
            .then(data => {
                if (data && data.success) {
                    this.displayDetailModal(data.result);
                } else {
                    modalBody.innerHTML = `
                        <div class="alert alert-danger">
                            <i class="fas fa-exclamation-triangle me-2"></i>
                            Error loading details: ${data?.error || 'Unknown error'}
                        </div>
                    `;
                }
            })
            .catch(error => {
                console.error('Error loading detail:', error);
                modalBody.innerHTML = `
                    <div class="alert alert-danger">
                        <i class="fas fa-exclamation-triangle me-2"></i>
                        Network error occurred while loading details.
                    </div>
                `;
            });
    },

/**
 * Display detail modal content
 */
displayDetailModal: function(result) {
    const modalBody = document.getElementById('detail-modal-body');
    
    modalBody.innerHTML = `
        <!-- OCR Results Section - Emphasized -->
        <div class="row mb-4">
            <div class="col-12">
                <div class="card border-primary">
                    <div class="card-header bg-primary text-white">
                        <h5 class="mb-0"><i class="fas fa-id-card me-2"></i>License Plate Recognition (LPR) Results</h5>
                    </div>
                    <div class="card-body">
                        ${this.formatOcrResultsForDetail(result.ocr_results)}
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Image Preview Section - Emphasized -->
        <div class="row mb-4">
            <div class="col-12">
                <div class="card border-success">
                    <div class="card-header bg-success text-white">
                        <h5 class="mb-0"><i class="fas fa-image me-2"></i>Detection Image Preview</h5>
                    </div>
                    <div class="card-body">
                        ${this.formatImagePreview(result)}
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Metadata Section - Normal -->
        <div class="row">
            <div class="col-12">
                <div class="card">
                    <div class="card-header">
                        <h6 class="mb-0"><i class="fas fa-info-circle me-2"></i>Detection Metadata</h6>
                    </div>
                    <div class="card-body">
                        <div class="row">
                            <div class="col-md-6">
                                <table class="table table-sm table-borderless">
                                    <tr><td><strong>Detection ID:</strong></td><td>#${result.id}</td></tr>
                                    <tr><td><strong>Timestamp:</strong></td><td>${AICameraUtils.formatTimestamp(result.timestamp || result.created_at)}</td></tr>
                                    <tr><td><strong>Processing Time:</strong></td><td>${result.processing_time_ms || 0}ms</td></tr>
                                </table>
                            </div>
                            <div class="col-md-6">
                                <table class="table table-sm table-borderless">
                                    <tr><td><strong>Vehicles Detected:</strong></td><td><span class="badge bg-info">${result.vehicles_count || 0}</span></td></tr>
                                    <tr><td><strong>License Plates:</strong></td><td><span class="badge bg-warning">${result.plates_count || 0}</span></td></tr>
                                    <tr><td><strong>OCR Confidence:</strong></td><td><span class="badge bg-success">${this.calculateAverageConfidence(result.ocr_results)}%</span></td></tr>
                                </table>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
},

/**
 * Format OCR results for detail view - Enhanced
 */
formatOcrResultsForDetail: function(ocrResults) {
    if (!ocrResults || ocrResults.length === 0) {
        return `
            <div class="text-center py-4">
                <i class="fas fa-exclamation-triangle fa-3x text-muted mb-3"></i>
                <h6 class="text-muted">No License Plates Detected</h6>
                <p class="text-muted">No OCR results available for this detection.</p>
            </div>
        `;
    }
    
    return `
        <div class="row">
            ${ocrResults.map((ocr, index) => `
                <div class="col-md-6 mb-3">
                    <div class="card h-100 border-${this.getConfidenceColor(ocr.confidence)}">
                        <div class="card-header bg-${this.getConfidenceColor(ocr.confidence)} text-white">
                            <div class="d-flex justify-content-between align-items-center">
                                <h6 class="mb-0">Plate #${index + 1}</h6>
                                <span class="badge bg-light text-dark">${(ocr.confidence * 100).toFixed(1)}%</span>
                            </div>
                        </div>
                        <div class="card-body text-center">
                            <div class="ocr-text-display mb-3">
                                <h4 class="text-primary font-weight-bold">${ocr.text}</h4>
                            </div>
                            <div class="ocr-details">
                                <small class="text-muted">
                                    <i class="fas fa-language me-1"></i>Language: ${ocr.language === 'th' ? 'Thai' : 'English'}
                                </small>
                                <br>
                                <small class="text-muted">
                                    <i class="fas fa-chart-line me-1"></i>Confidence: ${(ocr.confidence * 100).toFixed(1)}%
                                </small>
                            </div>
                        </div>
                    </div>
                </div>
            `).join('')}
        </div>
    `;
},

/**
 * Format image preview for detail modal
 */
formatImagePreview: function(result) {
    const images = [];
    
    // Add original image if available
    if (result.original_image_path && result.original_image_path !== 'None') {
        images.push({
            type: 'original',
            path: result.original_image_path,
            title: 'Original Captured Image',
            icon: 'fas fa-camera',
            color: 'info'
        });
    }
    
    // Add vehicle detection image if available
    if (result.vehicle_detected_image_path && result.vehicle_detected_image_path !== 'None') {
        images.push({
            type: 'vehicle',
            path: result.vehicle_detected_image_path,
            title: 'Vehicle Detection Image',
            icon: 'fas fa-car',
            color: 'primary'
        });
    }
    
    // Add plate detection image if available
    if (result.plate_image_path && result.plate_image_path !== 'None') {
        images.push({
            type: 'plate',
            path: result.plate_image_path,
            title: 'License Plate Detection Image',
            icon: 'fas fa-id-card',
            color: 'success'
        });
    }
    
    // Add cropped plates if available
    if (result.cropped_plates_paths && result.cropped_plates_paths.length > 0) {
        result.cropped_plates_paths.forEach((platePath, index) => {
            if (platePath && platePath !== 'None') {
                images.push({
                    type: 'cropped',
                    path: platePath,
                    title: `Cropped Plate ${index + 1}`,
                    icon: 'fas fa-crop',
                    color: 'warning'
                });
            }
        });
    }
    
    if (images.length === 0) {
        return `
            <div class="alert alert-info">
                <i class="fas fa-info-circle me-2"></i>
                <strong>No Images Available</strong><br>
                <small class="text-muted">
                    Original: ${result.original_image_path || 'Not available'}<br>
                    Vehicle Detection: ${result.vehicle_detected_image_path || 'Not available'}<br>
                    Plate Detection: ${result.plate_image_path || 'Not available'}<br>
                    Cropped Plates: ${result.cropped_plates_paths?.length || 0} available
                </small>
            </div>
        `;
    }
    
    // Create responsive grid layout
    let imageGrid = '';
    images.forEach((image, index) => {
        const colClass = images.length === 1 ? 'col-12' : 
                       images.length === 2 ? 'col-md-6' : 
                       images.length === 3 ? 'col-md-4' : 'col-md-6 col-lg-3';
        
        imageGrid += `
            <div class="${colClass} mb-3">
                <div class="card h-100 border-${image.color}">
                    <div class="card-header bg-${image.color} text-white">
                        <h6 class="mb-0">
                            <i class="${image.icon} me-2"></i>${image.title}
                        </h6>
                    </div>
                    <div class="card-body text-center p-2">
                        <img src="/images/${image.path}" 
                             class="img-fluid rounded" 
                             style="max-height: 200px; object-fit: contain;"
                             alt="${image.title}"
                             onerror="this.parentElement.innerHTML='<div class=\\'text-muted\\'><i class=\\'fas fa-image fa-2x mb-2\\'></i><br>Image not found</div>'">
                    </div>
                    <div class="card-footer text-center">
                        <small class="text-muted">${image.path}</small>
                    </div>
                </div>
            </div>
        `;
    });
    
    return `
        <div class="row">
            ${imageGrid}
        </div>
        <div class="mt-3">
            <small class="text-muted">
                <i class="fas fa-info-circle me-1"></i>
                Showing ${images.length} of ${this.getTotalImageCount(result)} available images
            </small>
        </div>
    `;
},
    
    /**
     * Get total image count for a result
     */
    getTotalImageCount: function(result) {
        let count = 0;
        if (result.original_image_path && result.original_image_path !== 'None') count++;
        if (result.vehicle_detected_image_path && result.vehicle_detected_image_path !== 'None') count++;
        if (result.plate_image_path && result.plate_image_path !== 'None') count++;
        if (result.cropped_plates_paths && result.cropped_plates_paths.length > 0) {
            count += result.cropped_plates_paths.filter(path => path && path !== 'None').length;
        }
        return count;
    },

/**
 * Get confidence color based on confidence level
 */
getConfidenceColor: function(confidence) {
    if (confidence >= 0.9) return 'success';
    if (confidence >= 0.7) return 'warning';
    return 'danger';
},

/**
 * Calculate average confidence from OCR results
 */
calculateAverageConfidence: function(ocrResults) {
    if (!ocrResults || ocrResults.length === 0) return 0;
    const total = ocrResults.reduce((sum, ocr) => sum + ocr.confidence, 0);
    return (total / ocrResults.length * 100).toFixed(1);
},

/**
 * Setup comprehensive output display toggle
 */
setupComprehensiveOutputToggle: function() {
    const toggle = document.getElementById('output-display-toggle');
    const content = document.getElementById('comprehensive-output-content');
    
    if (toggle && content) {
        toggle.addEventListener('change', (e) => {
            if (e.target.checked) {
                content.style.display = 'block';                this.refreshComprehensiveData();
            } else {
                content.style.display = 'none';
            }
        });
    }
},

/**
 * Refresh comprehensive data
 */
refreshComprehensiveData: function() {
    this.updateRealTimeMetrics();
    this.updatePerformanceAnalytics();
    this.updateQualityMetrics();
    this.updateOperationalInsights();
    this.updateImageAnalysis();
},

/**
 * Update real-time detection metrics
 */
updateRealTimeMetrics: function() {
    const stats = this.lastStatusUpdate || {};
    
    // Calculate rates
    const totalFrames = stats.total_frames_processed || 0;
    const totalVehicles = stats.total_vehicles_detected || 0;
    const totalPlates = stats.total_plates_detected || 0;
    const successfulOcr = stats.successful_ocr || 0;
    
    const vehicleRate = totalFrames > 0 ? ((totalVehicles / totalFrames) * 100).toFixed(1) : '0';
    const plateRate = totalVehicles > 0 ? ((totalPlates / totalVehicles) * 100).toFixed(1) : '0';
    const ocrRate = totalPlates > 0 ? ((successfulOcr / totalPlates) * 100).toFixed(1) : '0';
    const avgProcessing = stats.avg_processing_time_ms || 0;
    
    // Update display
    this.updateElement('vehicle-detection-rate', vehicleRate + '%');
    this.updateElement('plate-detection-rate', plateRate + '%');
    this.updateElement('ocr-success-rate', ocrRate + '%');
    this.updateElement('processing-efficiency', avgProcessing + 'ms');
},

/**
 * Update performance analytics
 */
updatePerformanceAnalytics: function() {
    const stats = this.lastStatusUpdate || {};
    
    // Detection throughput
    const fps = stats.current_fps || 0;
    const totalFrames = stats.total_frames_processed || 0;
    const errors = stats.detection_errors || 0;
    
    // OCR method comparison
    const hailoSuccess = stats.hailo_ocr_success_rate || 0;
    const easyocrSuccess = stats.easyocr_success_rate || 0;
    const bestMethod = hailoSuccess > easyocrSuccess ? 'Hailo' : 'EasyOCR';
    
    this.updateElement('detection-throughput', fps + ' FPS');
    this.updateElement('total-frames-processed', totalFrames);
    this.updateElement('detection-errors-count', errors);
    this.updateElement('hailo-ocr-success', hailoSuccess + '%');
    this.updateElement('easyocr-success', easyocrSuccess + '%');
    this.updateElement('best-ocr-method', bestMethod);
},

/**
 * Update quality metrics
 */
updateQualityMetrics: function() {
    const stats = this.lastStatusUpdate || {};
    
    // Detection accuracy based on confidence
    const detectionAccuracy = stats.detection_accuracy || 0;
    const ocrAccuracy = stats.ocr_accuracy || 0;
    const systemReliability = stats.system_reliability || 0;
    
    // Update progress bars
    this.updateProgressBar('detection-accuracy-bar', detectionAccuracy);
    this.updateProgressBar('ocr-accuracy-bar', ocrAccuracy);
    this.updateProgressBar('system-reliability-bar', systemReliability);
},

/**
 * Update operational insights
 */
updateOperationalInsights: function() {
    const stats = this.lastStatusUpdate || {};
    
    // Peak detection times
    const peakTimes = stats.peak_detection_times || [];
    const peakTimesElement = document.getElementById('peak-detection-times');
    if (peakTimesElement) {
        if (peakTimes.length > 0) {
            peakTimesElement.innerHTML = peakTimes.map(time => 
                `<div class="badge bg-primary me-1">${time}</div>`
            ).join('');
        } else {
            peakTimesElement.innerHTML = '<p class="text-muted">No peak detection data available</p>';
        }
    }
    
    // Resource utilization
    this.updateElement('cpu-usage', stats.cpu_usage || 'N/A');
    this.updateElement('memory-usage', stats.memory_usage || 'N/A');
    this.updateElement('storage-used', stats.storage_used || 'N/A');
},

/**
 * Update image analysis
 */
updateImageAnalysis: function() {
    // Count images from recent results
    this.loadRecentResults().then(results => {
        let originalCount = 0;
        let vehicleDetectionCount = 0;
        let plateDetectionCount = 0;
        let croppedCount = 0;
        
        results.forEach(result => {
            if (result.original_image_path) originalCount++;
            if (result.vehicle_detected_image_path) vehicleDetectionCount++;
            if (result.plate_image_path) plateDetectionCount++;
            if (result.cropped_plates_paths && result.cropped_plates_paths.length > 0) {
                croppedCount += result.cropped_plates_paths.length;
            }
        });
        
        this.updateElement('original-images-count', originalCount);
        this.updateElement('vehicle-detection-count', vehicleDetectionCount);
        this.updateElement('plate-detection-count', plateDetectionCount);
        this.updateElement('cropped-plates-count', croppedCount);
    });
},

/**
 * Update element by ID
 */
updateElement: function(elementId, value) {
    const element = document.getElementById(elementId);
    if (element) {
        element.textContent = value;
    }
},

/**
 * Update progress bar
 */
updateProgressBar: function(elementId, percentage) {
    const element = document.getElementById(elementId);
    if (element) {
        element.style.width = percentage + '%';
        element.setAttribute('aria-valuenow', percentage);
    }
},

/**
 * Export comprehensive report
 */
exportComprehensiveReport: function() {
    const report = {
        timestamp: new Date().toISOString(),
        realTimeMetrics: {
            vehicleDetectionRate: document.getElementById('vehicle-detection-rate')?.textContent,
            plateDetectionRate: document.getElementById('plate-detection-rate')?.textContent,
            ocrSuccessRate: document.getElementById('ocr-success-rate')?.textContent,
            processingEfficiency: document.getElementById('processing-efficiency')?.textContent
        },
        performanceAnalytics: {
            detectionThroughput: document.getElementById('detection-throughput')?.textContent,
            totalFramesProcessed: document.getElementById('total-frames-processed')?.textContent,
            detectionErrors: document.getElementById('detection-errors-count')?.textContent
        },
        imageAnalysis: {
            annotatedImages: document.getElementById('annotated-images-count')?.textContent,
            originalImages: document.getElementById('original-images-count')?.textContent,
            croppedPlates: document.getElementById('cropped-plates-count')?.textContent
        }
    };
    
    // Create download link
    const dataStr = JSON.stringify(report, null, 2);
    const dataBlob = new Blob([dataStr], {type: 'application/json'});
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `detection_comprehensive_report_${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(link);
    link.click();
}  
};

// Initialize detection manager when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    DetectionManager.init();
    
    // Cleanup on page unload
    window.addEventListener('beforeunload', function() {
        DetectionManager.cleanup();
    });
    
    console.log('Detection Dashboard JavaScript loaded');
});

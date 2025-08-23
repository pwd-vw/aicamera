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
        this.startPeriodicUpdates();
        this.loadResults();
        this.loadStatistics();
    },

    /**
     * Initialize WebSocket connection
     */
    initializeWebSocket: function() {
        if (typeof io === 'undefined') {
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
            // Request initial status
            this.socket.emit('detection_status_request');
        });

        this.socket.on('disconnect', () => {
            // Silent disconnect handling
        });

        this.socket.on('connect_error', (error) => {
            // Silent error handling
        });

        this.socket.on('detection_status_update', (data) => {
            if (data && data.success && data.status) {
                this.updateDetectionStatus(data.status);
            } else {
                // Silent error handling
            }
        });

        this.socket.on('detection_control_response', (response) => {
            this.handleControlResponse(response);
        });

        this.socket.on('detection_config_response', (response) => {
            this.handleConfigResponse(response);
        });

        this.socket.on('detection_statistics_update', (stats) => {
            this.updateStatistics(stats);
        });

        this.socket.on('detection_status_error', (error) => {
            // Silent error handling
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

        // Clear filters button
        const clearFiltersBtn = document.getElementById('clear-filters-btn');
        if (clearFiltersBtn) {
            clearFiltersBtn.addEventListener('click', () => {
                this.clearFilters();
            });
        }

        // Refresh button
        const refreshResultsBtn = document.getElementById('refresh-results-btn');
        if (refreshResultsBtn) {
            refreshResultsBtn.addEventListener('click', () => {
                this.loadResults();
                this.loadStatistics();
            });
        }

        // Export button
        const exportResultsBtn = document.getElementById('export-results-btn');
        if (exportResultsBtn) {
            exportResultsBtn.addEventListener('click', () => {
                this.showExportModal();
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
     * Setup form handlers
     */
    setupFormHandlers: function() {
        const configForm = document.getElementById('detection-config-form');
        if (configForm) {
            configForm.addEventListener('submit', (e) => this.handleConfigSubmit(e));
        }
    },

    /**
     * Start periodic status updates
     */
    startPeriodicUpdates: function() {
        // Update immediately
        this.requestStatusUpdate();
        
        // Setup periodic updates every 5 seconds
        this.statusUpdateInterval = setInterval(() => {
            this.requestStatusUpdate();
        }, 5000);
        
        // Load recent results after 1 second
        setTimeout(() => this.loadRecentResults(), 1000);
        
        // Add initial log message
    },

    /**
     * Control detection service
     */
    controlDetection: function(command) {
        const button = document.getElementById(command === 'start' ? 'start-detection' : 'stop-detection');
        if (button) button.disabled = true;
        
        if (!this.socket || !this.socket.connected) {
            if (button) button.disabled = false;
            return;
        }
        
        this.socket.emit('detection_control', { command: command });
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
            this.resetProcessButton();
            return;
        }
        
        this.socket.emit('detection_control', { command: 'process_frame' });
        
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
        } else {
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
                if (data && data.success) {
                    this.updateDetectionStatus(data.status);
                }
            })
            .catch(error => {
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
                if (data && data.success) {
                    this.updateStatistics(data.statistics);
                }
            })
            .catch(error => {
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
        const intervalSetting = document.getElementById('interval-setting');
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
     * Load recent detection results
     */
    loadRecentResults: function() {
        AICameraUtils.apiRequest('/detection/results/recent')
            .then(data => {
                if (data.success) {
                    this.displayRecentResults(data.results);
                } else {
                    throw new Error(data.error || 'Failed to load results');
                }
            })
            .catch(error => {
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
        
        AICameraUtils.apiRequest(`/detection_results/api/results?${params.toString()}`)
            .then(data => {
                if (data.success) {
                    this.displayResults(data);
                } else {
                    throw new Error(data.error || 'Failed to load results');
                }
            })
            .catch(error => {
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
        AICameraUtils.apiRequest('/detection_results/api/statistics')
            .then(data => {
                if (data.success) {
                    this.updateStatisticsDisplay(data.statistics);
                }
            })
            .catch(error => {
            });
    },

    /**
     * Display detection results
     */
    displayResults: function(data) {
        const { results, pagination } = data;
        
        this.totalPages = pagination.total_pages;
        this.updateResultsCount(pagination.total);
        this.updatePaginationInfo(pagination);
        this.renderResultsTable(results);
        this.renderPagination();
        
        if (results.length === 0) {
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
                <td>${result.id}</td>
                <td>${AICameraUtils.formatTimestamp(result.created_at)}</td>
                <td>${result.vehicles_count}</td>
                <td>${result.plates_count}</td>
                <td>${this.formatOcrResults(result.ocr_results)}</td>
                <td>${result.processing_time_ms}ms</td>
                <td>
                    <button class="btn btn-sm btn-outline-primary" onclick="DetectionManager.showDetail(${result.id})">
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
     * Show detail modal
     */
    showDetail: function(resultId) {
        AICameraUtils.apiRequest(`/detection_results/api/results/${resultId}`)
            .then(data => {
                if (data.success) {
                    this.displayDetailModal(data.result);
                } else {
                    throw new Error(data.error || 'Failed to load detail');
                }
            })
            .catch(error => {
            });
    },

    /**
     * Display detail modal
     */
    displayDetailModal: function(result) {
        const modalBody = document.getElementById('detail-modal-body');
        if (!modalBody) return;
        
        modalBody.innerHTML = `
            <!-- OCR Results Section - Emphasized -->
            <div class="row mb-4">
                <div class="col-12">
                    <div class="card border-primary">
                        <div class="card-header bg-primary text-white">
                            <h5 class="mb-0"><i class="fas fa-id-card me-2"></i>License Plate Recognition (LPR) Results</h5>
                        </div>
                        <div class="card-body">
                            ${this.formatOcrResultsDetail(result.ocr_results)}
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
                                        <tr><td><strong>Timestamp:</strong></td><td>${AICameraUtils.formatTimestamp(result.created_at)}</td></tr>
                                        <tr><td><strong>Processing Time:</strong></td><td>${result.processing_time_ms}ms</td></tr>
                                    </table>
                                </div>
                                <div class="col-md-6">
                                    <table class="table table-sm table-borderless">
                                        <tr><td><strong>Vehicles Detected:</strong></td><td><span class="badge bg-info">${result.vehicles_count}</span></td></tr>
                                        <tr><td><strong>License Plates:</strong></td><td><span class="badge bg-warning">${result.plates_count}</span></td></tr>
                                        <tr><td><strong>OCR Confidence:</strong></td><td><span class="badge bg-success">${this.calculateAverageConfidence(result.ocr_results)}%</span></td></tr>
                                    </table>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        const modal = new bootstrap.Modal(document.getElementById('detail-modal'));
        modal.show();
    },

    /**
     * Format OCR results for detail view - Enhanced
     */
    formatOcrResultsDetail: function(ocrResults) {
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
     * Format image preview
     */
    formatImagePreview: function(result) {
        if (!result.annotated_image_path) {
            return `
                <div class="text-center py-4">
                    <i class="fas fa-image fa-3x text-muted mb-3"></i>
                    <h6 class="text-muted">No Image Available</h6>
                    <p class="text-muted">Detection image not available for this record.</p>
                </div>
            `;
        }
        
        // Extract filename from path
        const annotatedFilename = result.annotated_image_path.split('/').pop();
        
        return `
            <div class="row">
                <div class="col-md-8">
                    <div class="main-image-container">
                        <img src="/detection_results/images/${annotatedFilename}" class="img-fluid rounded shadow" alt="Detection Result" 
                             style="max-height: 400px; width: 100%; object-fit: contain;">
                    </div>
                </div>
                <div class="col-md-4">
                    <h6 class="mb-3">Cropped License Plates</h6>
                    ${this.formatCroppedPlates(result.cropped_plates_paths)}
                </div>
            </div>
        `;
    },

    /**
     * Format cropped plates
     */
    formatCroppedPlates: function(croppedPlatesPaths) {
        if (!croppedPlatesPaths || croppedPlatesPaths.length === 0) {
            return '<p class="text-muted">No cropped plates available</p>';
        }
        
        return `
            <div class="cropped-plates-container">
                ${croppedPlatesPaths.map((path, index) => {
                    // Extract filename from path
                    const filename = path.split('/').pop();
                    return `
                        <div class="cropped-plate-item mb-2">
                            <img src="/detection_results/images/${filename}" class="img-fluid rounded border" alt="Cropped Plate ${index + 1}"
                                 style="max-height: 80px; width: 100%; object-fit: contain;">
                            <small class="text-muted d-block text-center">Plate ${index + 1}</small>
                        </div>
                    `;
                }).join('')}
            </div>
        `;
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
            const hasDetections = result.vehicles_count > 0;
            resultDiv.className = `detection-result ${hasDetections ? 'success' : 'no-detection'}`;
            
            resultDiv.innerHTML = `
                <div class="d-flex justify-content-between align-items-center mb-2">
                    <small class="text-muted">${AICameraUtils.formatTimestamp(result.timestamp)}</small>
                    <div class="badge bg-${hasDetections ? 'success' : 'warning'}">
                        ${result.vehicles_count} vehicles, ${result.plates_count} plates
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
     * Handle configuration form submission
     */
    handleConfigSubmit: function(e) {
        e.preventDefault();
        
        const interval = parseFloat(document.getElementById('interval-setting').value);
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
                this.requestStatusUpdate();
            } else {
                throw new Error(data.error || 'Configuration update failed');
            }
        })
        .catch(error => {
        });
    },

    /**
     * Handle configuration response
     */
    handleConfigResponse: function(response) {
        const { success, message, error } = response;
        if (success) {
            this.requestStatusUpdate();
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
    }
};

// Initialize detection manager when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    DetectionManager.init();
    
    // Cleanup on page unload
    window.addEventListener('beforeunload', function() {
        DetectionManager.cleanup();
    });
    
});

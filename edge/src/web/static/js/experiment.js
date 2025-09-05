// src/web/static/js/experiment.js
class ExperimentDashboard {
    constructor() {
        this.socket = io();
        this.currentExperiment = null;
        this.experimentStartTime = null;
        this.progressInterval = null;
        
        this.initializeSocket();
        this.loadInitialData();
    }
    
    initializeSocket() {
        // เชื่อมต่อ WebSocket
        this.socket.on('connect', () => {
            console.log('Connected to experiment server');
            this.socket.emit('join_experiment_room');
        });
        
        // รับอัปเดตสถานะการทดลอง
        this.socket.on('experiment_status_update', (status) => {
            this.updateExperimentStatus(status);
        });
        
        // รับความคืบหน้าการทดลอง
        this.socket.on('experiment_progress', (progress) => {
            this.updateExperimentProgress(progress);
        });
        
        // รับผลลัพธ์การทดลอง
        this.socket.on('experiment_result', (result) => {
            this.addExperimentResult(result);
        });
        
        // การทดลองเสร็จสิ้น
        this.socket.on('experiment_complete', (summary) => {
            this.showExperimentComplete(summary);
        });
    }
    
    loadInitialData() {
        // โหลดข้อมูลเริ่มต้น
        this.loadActiveExperiments();
        this.loadRecentResults();
        this.loadStillImages();
    }
    
    // Single Detection Experiment
    showSingleDetectionForm() {
        try {
            if (typeof bootstrap !== 'undefined' && bootstrap.Modal) {
                const modal = new bootstrap.Modal(document.getElementById('singleDetectionModal'));
                modal.show();
            } else {
                console.error('[EXPERIMENT] Bootstrap Modal not available');
                alert('Bootstrap Modal ไม่พร้อมใช้งาน');
            }
        } catch (error) {
            console.error('[EXPERIMENT] Error showing modal:', error);
            alert('เกิดข้อผิดพลาดในการแสดงฟอร์ม: ' + error.message);
        }
    }
    
    async startSingleDetectionExperiment() {
        const form = document.getElementById('singleDetectionForm');
        const formData = new FormData(form);
        
        const experimentConfig = {
            experiment_type: 'single_detection',
            image_source: formData.get('image_source'),
            still_image: formData.get('still_image'),
            camera_config: formData.get('camera_config'),
            custom_config: this.getCustomConfig(formData)
        };
        
        try {
            const response = await fetch('/experiments/create', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(experimentConfig)
            });
            
            if (response.ok) {
                const result = await response.json();
                this.startExperiment(result.experiment_id);
                bootstrap.Modal.getInstance(document.getElementById('singleDetectionModal')).hide();
            } else {
                throw new Error('Failed to create experiment');
            }
        } catch (error) {
            this.showError('เกิดข้อผิดพลาดในการสร้างการทดลอง: ' + error.message);
        }
    }
    
    // Length Detection Experiment
    showLengthDetectionForm() {
        try {
            if (typeof bootstrap !== 'undefined' && bootstrap.Modal) {
                const modal = new bootstrap.Modal(document.getElementById('lengthDetectionModal'));
                modal.show();
            } else {
                console.error('[EXPERIMENT] Bootstrap Modal not available');
                alert('Bootstrap Modal ไม่พร้อมใช้งาน');
            }
        } catch (error) {
            console.error('[EXPERIMENT] Error showing modal:', error);
            alert('เกิดข้อผิดพลาดในการแสดงฟอร์ม: ' + error.message);
        }
    }
    
    async startLengthDetectionExperiment() {
        const form = document.getElementById('lengthDetectionForm');
        const formData = new FormData(form);
        
        const experimentConfig = {
            experiment_type: 'length_detection',
            start_length: parseFloat(formData.get('start_length')),
            max_length: parseFloat(formData.get('max_length')),
            step: parseFloat(formData.get('step')),
            enable_auto_focus: formData.get('enable_auto_focus') === 'on',
            camera_config: formData.get('camera_config')
        };
        
        try {
            const response = await fetch('/experiments/create', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(experimentConfig)
            });
            
            if (response.ok) {
                const result = await response.json();
                this.startExperiment(result.experiment_id);
                bootstrap.Modal.getInstance(document.getElementById('lengthDetectionModal')).hide();
            } else {
                throw new Error('Failed to create experiment');
            }
        } catch (error) {
            this.showError('เกิดข้อผิดพลาดในการสร้างการทดลอง: ' + error.message);
        }
    }
    
    startExperiment(experimentId) {
        this.currentExperiment = experimentId;
        this.experimentStartTime = Date.now();
        
        // แสดง progress modal
        const progressModal = new bootstrap.Modal(document.getElementById('experimentProgressModal'));
        progressModal.show();
        
        // เริ่มการทดลอง
        this.socket.emit('start_experiment', experimentId);
        
        // เริ่ม progress timer
        this.startProgressTimer();
    }
    
    startProgressTimer() {
        this.progressInterval = setInterval(() => {
            if (this.experimentStartTime) {
                const elapsed = Date.now() - this.experimentStartTime;
                const minutes = Math.floor(elapsed / 60000);
                const seconds = Math.floor((elapsed % 60000) / 1000);
                document.getElementById('elapsedTime').textContent = 
                    `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
            }
        }, 1000);
    }
    
    updateExperimentProgress(progress) {
        const progressBar = document.getElementById('experimentProgressBar');
        const progressText = document.getElementById('experimentProgressText');
        
        if (progressBar && progressText) {
            progressBar.style.width = `${progress.progress_percent}%`;
            progressText.textContent = `${progress.progress_percent.toFixed(1)}%`;
        }
        
        // อัปเดตรายละเอียด
        if (progress.status) {
            document.getElementById('experimentStatus').textContent = progress.status;
        }
        
        if (progress.details) {
            document.getElementById('experimentDetails').textContent = progress.details;
        }
        
        if (progress.files_processed !== undefined) {
            document.getElementById('processedFiles').textContent = progress.files_processed;
        }
    }
    
    showExperimentComplete(summary) {
        // หยุด progress timer
        if (this.progressInterval) {
            clearInterval(this.progressInterval);
            this.progressInterval = null;
        }
        
        // ซ่อน progress modal
        const progressModal = bootstrap.Modal.getInstance(document.getElementById('experimentProgressModal'));
        if (progressModal) {
            progressModal.hide();
        }
        
        // แสดงผลลัพธ์
        this.showSuccess(`การทดลองเสร็จสิ้น! ลบไฟล์: ${summary.files_deleted}, พื้นที่ที่ได้: ${summary.space_freed_gb.toFixed(2)} GB`);
        
        // อัปเดตข้อมูล
        this.loadActiveExperiments();
        this.loadRecentResults();
        
        this.currentExperiment = null;
        this.experimentStartTime = null;
    }
    
    async stopExperiment() {
        if (this.currentExperiment) {
            try {
                const response = await fetch(`/experiments/stop/${this.currentExperiment}`, {
                    method: 'POST'
                });
                
                if (response.ok) {
                    this.showInfo('การทดลองถูกหยุดแล้ว');
                } else {
                    throw new Error('Failed to stop experiment');
                }
            } catch (error) {
                this.showError('เกิดข้อผิดพลาดในการหยุดการทดลอง: ' + error.message);
            }
        }
    }
    
    // Utility functions
    getCustomConfig(formData) {
        const customConfig = {};
        
        if (formData.get('camera_config') === 'custom') {
            if (formData.get('exposure_time')) {
                customConfig.exposure_time = parseInt(formData.get('exposure_time'));
            }
            if (formData.get('analog_gain')) {
                customConfig.analog_gain = parseFloat(formData.get('analog_gain'));
            }
        }
        
        return Object.keys(customConfig).length > 0 ? customConfig : null;
    }
    
    async loadActiveExperiments() {
        try {
            const response = await fetch('/experiments/active');
            if (response.ok) {
                const experiments = await response.json();
                this.displayActiveExperiments(experiments);
            }
        } catch (error) {
            console.error('Failed to load active experiments:', error);
        }
    }
    
    async loadRecentResults() {
        try {
            const response = await fetch('/experiments/results/recent?limit=10');
            if (response.ok) {
                const results = await response.json();
                this.displayRecentResults(results);
            }
        } catch (error) {
            console.error('Failed to load recent results:', error);
        }
    }
    
    async loadStillImages() {
        try {
            const response = await fetch('/experiments/still-images');
            if (response.ok) {
                const images = await response.json();
                this.populateStillImageOptions(images);
            }
        } catch (error) {
            console.error('Failed to load still images:', error);
        }
    }
    
    displayActiveExperiments(experiments) {
        const container = document.getElementById('active-experiments-list');
        
        if (experiments.length === 0) {
            container.innerHTML = '<p class="text-muted">ไม่มีการทดลองที่กำลังดำเนินการ</p>';
            return;
        }
        
        const html = experiments.map(exp => `
            <div class="card mb-2">
                <div class="card-body">
                    <div class="row align-items-center">
                        <div class="col-md-3">
                            <h6 class="mb-0">${exp.experiment_type}</h6>
                            <small class="text-muted">ID: ${exp.experiment_id}</small>
                        </div>
                        <div class="col-md-3">
                            <span class="badge bg-primary">${exp.status}</span>
                        </div>
                        <div class="col-md-3">
                            <small class="text-muted">เริ่มต้น: ${new Date(exp.start_time).toLocaleString('th-TH')}</small>
                        </div>
                        <div class="col-md-3">
                            <button class="btn btn-sm btn-danger" onclick="stopExperiment('${exp.experiment_id}')">
                                หยุด
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `).join('');
        
        container.innerHTML = html;
    }
    
    displayRecentResults(results) {
        const container = document.getElementById('recent-results');
        
        if (results.length === 0) {
            container.innerHTML = '<p class="text-muted">ไม่มีผลการทดลอง</p>';
            return;
        }
        
        const html = results.map(result => `
            <div class="card mb-2">
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-2">
                            <h6 class="mb-0">${result.experiment_type}</h6>
                            <small class="text-muted">${new Date(result.timestamp).toLocaleString('th-TH')}</small>
                        </div>
                        <div class="col-md-2">
                            <strong>Vehicles:</strong> ${result.vehicles_detected}<br>
                            <strong>Plates:</strong> ${result.plates_detected}
                        </div>
                        <div class="col-md-2">
                            <strong>OCR Success:</strong> ${result.ocr_success ? 'Yes' : 'No'}<br>
                            <strong>Confidence:</strong> ${(result.ocr_confidence * 100).toFixed(1)}%
                        </div>
                        <div class="col-md-2">
                            <strong>Processing:</strong> ${result.processing_time.toFixed(1)}ms<br>
                            <strong>Quality:</strong> ${result.image_quality}
                        </div>
                        <div class="col-md-2">
                            <button class="btn btn-sm btn-outline-primary" onclick="viewExperimentDetails('${result.experiment_id}')">
                                ดูรายละเอียด
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `).join('');
        
        container.innerHTML = html;
    }
    
    populateStillImageOptions(images) {
        const select = document.querySelector('select[name="still_image"]');
        if (!select) return;
        
        const options = images.map(img => 
            `<option value="${img.path}">${img.filename}</option>`
        ).join('');
        
        select.innerHTML = '<option value="">เลือกภาพ...</option>' + options;
    }
    
    // Event handlers
    handleImageSourceChange() {
        const imageSource = document.querySelector('select[name="image_source"]').value;
        const stillImageSection = document.getElementById('stillImageSection');
        
        if (imageSource === 'still') {
            stillImageSection.style.display = 'block';
        } else {
            stillImageSection.style.display = 'none';
        }
    }
    
    handleCameraConfigChange() {
        const cameraConfig = document.querySelector('select[name="camera_config"]').value;
        const customConfigSection = document.getElementById('customConfigSection');
        
        if (cameraConfig === 'custom') {
            customConfigSection.style.display = 'block';
        } else {
            customConfigSection.style.display = 'none';
        }
    }
    
    // Notification functions
    showSuccess(message) {
        this.showNotification(message, 'success');
    }
    
    showError(message) {
        this.showNotification(message, 'danger');
    }
    
    showInfo(message) {
        this.showNotification(message, 'info');
    }
    
    showNotification(message, type) {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        const container = document.querySelector('.container-fluid');
        container.insertBefore(alertDiv, container.firstChild);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 5000);
    }
}

// Initialize dashboard when page loads
document.addEventListener('DOMContentLoaded', () => {
    console.log('[EXPERIMENT] Initializing Experiment Dashboard...');
    try {
        window.experimentDashboard = new ExperimentDashboard();
        console.log('[EXPERIMENT] Dashboard initialized successfully');
        
        // Add event listeners with better error handling
        const imageSourceSelect = document.querySelector('select[name="image_source"]');
        const cameraConfigSelect = document.querySelector('select[name="camera_config"]');
        
        if (imageSourceSelect) {
            imageSourceSelect.addEventListener('change', () => {
                if (window.experimentDashboard) {
                    window.experimentDashboard.handleImageSourceChange();
                }
            });
            console.log('[EXPERIMENT] Image source event listener added');
        } else {
            console.warn('[EXPERIMENT] Image source select not found');
        }
        
        if (cameraConfigSelect) {
            cameraConfigSelect.addEventListener('change', () => {
                if (window.experimentDashboard) {
                    window.experimentDashboard.handleCameraConfigChange();
                }
            });
            console.log('[EXPERIMENT] Camera config event listener added');
        } else {
            console.warn('[EXPERIMENT] Camera config select not found');
        }
        
        console.log('[EXPERIMENT] Event listeners added successfully');
        
    } catch (error) {
        console.error('[EXPERIMENT] Error initializing Dashboard:', error);
    }
});

window.showSingleDetectionForm = function() {
    console.log('[EXPERIMENT] showSingleDetectionForm called');
    if (window.experimentDashboard) {
        try {
            window.experimentDashboard.showSingleDetectionForm();
        } catch (error) {
            console.error('[EXPERIMENT] Error showing single detection form:', error);
            alert('เกิดข้อผิดพลาดในการแสดงฟอร์ม: ' + error.message);
        }
    } else {
        console.error('[EXPERIMENT] Experiment dashboard not initialized');
        alert('Experiment dashboard ยังไม่พร้อม กรุณารอสักครู่');
    }
};

window.showLengthDetectionForm = function() {
    console.log('[EXPERIMENT] showLengthDetectionForm called');
    if (window.experimentDashboard) {
        try {
            window.experimentDashboard.showLengthDetectionForm();
        } catch (error) {
            console.error('[EXPERIMENT] Error showing length detection form:', error);
            alert('เกิดข้อผิดพลาดในการแสดงฟอร์ม: ' + error.message);
        }
    } else {
        console.error('[EXPERIMENT] Experiment dashboard not initialized');
        alert('Experiment dashboard ยังไม่พร้อม กรุณารอสักครู่');
    }
};

window.showFlexibleConfigForm = function() {
    console.log('[EXPERIMENT] showFlexibleConfigForm called');
    if (window.experimentDashboard) {
        // TODO: Implement flexible config form
        console.log('[EXPERIMENT] Flexible config form not implemented yet');
        alert('Flexible config form กำลังพัฒนา');
    } else {
        console.error('[EXPERIMENT] Experiment dashboard not initialized');
        alert('Experiment dashboard ยังไม่พร้อม กรุณารอสักครู่');
    }
};

window.startSingleDetectionExperiment = function() {
    console.log('[EXPERIMENT] startSingleDetectionExperiment called');
    if (window.experimentDashboard) {
        try {
            window.experimentDashboard.startSingleDetectionExperiment();
        } catch (error) {
            console.error('[EXPERIMENT] Error starting single detection experiment:', error);
            alert('เกิดข้อผิดพลาดในการเริ่มการทดลอง: ' + error.message);
        }
    } else {
        console.error('[EXPERIMENT] Experiment dashboard not initialized');
        alert('Experiment dashboard ยังไม่พร้อม กรุณารอสักครู่');
    }
};

window.startLengthDetectionExperiment = function() {
    console.log('[EXPERIMENT] startLengthDetectionExperiment called');
    if (window.experimentDashboard) {
        try {
            window.experimentDashboard.startLengthDetectionExperiment();
        } catch (error) {
            console.error('[EXPERIMENT] Error starting length detection experiment:', error);
            alert('เกิดข้อผิดพลาดในการเริ่มการทดลอง: ' + error.message);
        }
    } else {
        console.error('[EXPERIMENT] Experiment dashboard not initialized');
        alert('Experiment dashboard ยังไม่พร้อม กรุณารอสักครู่');
    }
};

window.stopExperiment = function(experimentId) {
    console.log('[EXPERIMENT] stopExperiment called with ID:', experimentId);
    if (window.experimentDashboard) {
        try {
            if (experimentId) {
                // Stop specific experiment
                window.experimentDashboard.stopExperiment(experimentId);
            } else {
                // Stop current experiment
                window.experimentDashboard.stopExperiment();
            }
        } catch (error) {
            console.error('[EXPERIMENT] Error stopping experiment:', error);
            alert('เกิดข้อผิดพลาดในการหยุดการทดลอง: ' + error.message);
        }
    } else {
        console.error('[EXPERIMENT] Experiment dashboard not initialized');
        alert('Experiment dashboard ยังไม่พร้อม กรุณารอสักครู่');
    }
};

window.viewExperimentDetails = function(experimentId) {
    console.log('[EXPERIMENT] viewExperimentDetails called with ID:', experimentId);
    // Navigate to experiment details page
    window.location.href = `/experiments/details/${experimentId}`;
};

window.refreshStatus = function() {
    console.log('[EXPERIMENT] refreshStatus called');
    if (window.experimentDashboard) {
        try {
            window.experimentDashboard.loadInitialData();
        } catch (error) {
            console.error('[EXPERIMENT] Error refreshing status:', error);
            alert('เกิดข้อผิดพลาดในการอัปเดตสถานะ: ' + error.message);
        }
    } else {
        console.error('[EXPERIMENT] Experiment dashboard not initialized');
        alert('Experiment dashboard ยังไม่พร้อม กรุณารอสักครู่');
    }
};

window.checkExperimentFunctions = function() {
    const functions = [
        'showSingleDetectionForm',
        'showLengthDetectionForm',
        'showFlexibleConfigForm',
        'startSingleDetectionExperiment',
        'startLengthDetectionExperiment',
        'stopExperiment',
        'viewExperimentDetails',
        'refreshStatus'
    ];
    
    const results = {};
    functions.forEach(funcName => {
        results[funcName] = typeof window[funcName] === 'function';
    });
    
    console.log('[EXPERIMENT] Function availability check:', results);
    return results;
};

// Auto-check when page loads
setTimeout(() => {
    window.checkExperimentFunctions();
}, 1000);

// Debug: Log all global functions immediately
console.log('[EXPERIMENT] Global functions defined:', {
    showSingleDetectionForm: typeof window.showSingleDetectionForm,
    showLengthDetectionForm: typeof window.showLengthDetectionForm,
    showFlexibleConfigForm: typeof window.showFlexibleConfigForm,
    startSingleDetectionExperiment: typeof window.startSingleDetectionExperiment,
    startLengthDetectionExperiment: typeof window.startLengthDetectionExperiment,
    stopExperiment: typeof window.stopExperiment,
    viewExperimentDetails: typeof window.viewExperimentDetails,
    refreshStatus: typeof window.refreshStatus
});

// Auto-check when page loads
setTimeout(() => {
    window.checkExperimentFunctions();
}, 1000);
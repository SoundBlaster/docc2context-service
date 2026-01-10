// DocC2Context Service - Frontend Upload JavaScript

class FileUploader {
    constructor() {
        this.dropZone = document.getElementById('dropZone');
        this.fileInput = document.getElementById('fileInput');
        this.uploadButton = document.getElementById('uploadButton');
        this.fileInfo = document.getElementById('fileInfo');
        this.fileName = document.getElementById('fileName');
        this.fileSize = document.getElementById('fileSize');
        this.progressContainer = document.getElementById('progressContainer');
        this.progressFill = document.getElementById('progressFill');
        this.statusMessage = document.getElementById('statusMessage');
        
        this.selectedFile = null;
        this.isUploading = false;
        
        this.initializeEventListeners();
    }
    
    initializeEventListeners() {
        // Drag and drop events
        this.dropZone.addEventListener('dragover', this.handleDragOver.bind(this));
        this.dropZone.addEventListener('drop', this.handleDrop.bind(this));
        this.dropZone.addEventListener('dragleave', this.handleDragLeave.bind(this));
        
        // File input events
        this.fileInput.addEventListener('change', this.handleFileSelect.bind(this));
        
        // Upload button events
        this.uploadButton.addEventListener('click', this.handleUploadClick.bind(this));
        
        // Prevent default drag behavior on page
        document.addEventListener('dragover', (e) => {
            e.preventDefault();
        });
        
        document.addEventListener('drop', (e) => {
            e.preventDefault();
        });
    }
    
    handleDragOver(e) {
        e.preventDefault();
        e.stopPropagation();
        this.dropZone.classList.add('drag-over');
    }
    
    handleDragLeave(e) {
        e.preventDefault();
        e.stopPropagation();
        this.dropZone.classList.remove('drag-over');
    }
    
    handleDrop(e) {
        e.preventDefault();
        e.stopPropagation();
        this.dropZone.classList.remove('drag-over');
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            this.selectFile(files[0]);
        }
    }
    
    handleFileSelect(e) {
        const files = e.target.files;
        if (files.length > 0) {
            this.selectFile(files[0]);
        }
    }
    
    selectFile(file) {
        // Validate file type
        if (!this.isValidFileType(file)) {
            this.showStatus('Please select a valid DocC archive (.zip or .doccarchive)', 'error');
            return;
        }
        
        // Validate file size (100MB limit)
        const maxSize = 100 * 1024 * 1024; // 100MB in bytes
        if (file.size > maxSize) {
            this.showStatus(`File size (${this.formatFileSize(file.size)}) exceeds 100MB limit`, 'error');
            return;
        }
        
        this.selectedFile = file;
        this.updateFileInfo();
        this.uploadButton.disabled = false;
        this.dropZone.classList.add('has-file');
        
        this.showStatus(`Selected: ${file.name}`, 'info');
    }
    
    isValidFileType(file) {
        const validTypes = ['.zip', '.doccarchive'];
        const fileName = file.name.toLowerCase();
        return validTypes.some(type => fileName.endsWith(type));
    }
    
    updateFileInfo() {
        if (this.selectedFile) {
            this.fileName.textContent = this.selectedFile.name;
            this.fileSize.textContent = this.formatFileSize(this.selectedFile.size);
            this.fileInfo.style.display = 'block';
        } else {
            this.fileInfo.style.display = 'none';
        }
    }
    
    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        const formattedSize = parseFloat((bytes / Math.pow(k, i)).toFixed(2));
        return formattedSize + ' ' + sizes[i];
    }
    
    async handleUploadClick() {
        if (!this.selectedFile || this.isUploading) {
            return;
        }
        
        this.isUploading = true;
        this.uploadButton.disabled = true;
        this.uploadButton.textContent = 'Converting...';
        this.showProgress();
        this.hideStatus();
        
        try {
            await this.uploadFile(this.selectedFile);
            this.showStatus('Conversion completed! Download should start automatically.', 'success');
        } catch (error) {
            this.showStatus(`Conversion failed: ${error.message}`, 'error');
        } finally {
            this.isUploading = false;
            this.uploadButton.disabled = false;
            this.uploadButton.textContent = 'Convert to Markdown';
            this.hideProgress();
        }
    }
    
    async uploadFile(file) {
        const formData = new FormData();
        formData.append('file', file);
        
        // Simulate progress (since we can't track real progress with fetch)
        this.simulateProgress();
        
        const response = await fetch('/api/v1/convert', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`HTTP ${response.status}: ${errorText}`);
        }
        
        // Check if response is a file download (ZIP) or error
        const contentType = response.headers.get('content-type');
        if (contentType && contentType.includes('application/zip')) {
            // Download the converted file
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = file.name.replace(/\.[^/.]+$/, '_converted.zip');
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
        } else {
            // Handle JSON error response
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Unknown error occurred');
        }
    }
    
    simulateProgress() {
        let progress = 0;
        const interval = setInterval(() => {
            progress += Math.random() * 15; // Random progress simulation
            if (progress > 90) {
                progress = 90;
                clearInterval(interval);
            }
            this.updateProgress(progress);
        }, 200);
        
        // Clear interval after 3 seconds max
        setTimeout(() => {
            clearInterval(interval);
        }, 3000);
    }
    
    showProgress() {
        this.progressContainer.style.display = 'block';
        this.updateProgress(0);
    }
    
    hideProgress() {
        this.progressContainer.style.display = 'none';
    }
    
    updateProgress(percent) {
        this.progressFill.style.width = `${percent}%`;
    }
    
    showStatus(message, type = 'info') {
        this.statusMessage.textContent = message;
        this.statusMessage.style.display = 'block';
        this.statusMessage.className = `status-message status-${type}`;
    }
    
    hideStatus() {
        this.statusMessage.style.display = 'none';
        this.statusMessage.className = 'status-message';
    }
}

// Initialize the uploader when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new FileUploader();
    console.log('FileUploader initialized successfully');
});

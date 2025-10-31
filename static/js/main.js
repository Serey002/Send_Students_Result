class StudentResultSystem {
    constructor() {
        this.currentFile = null;
        this.initializeEventListeners();
    }

    initializeEventListeners() {
        // File input change
        document.getElementById('fileInput').addEventListener('change', (e) => {
            this.handleFileSelect(e);
        });

        // Drag and drop
        const uploadArea = document.getElementById('uploadArea');
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('border-primary-400', 'bg-primary-50');
        });

        uploadArea.addEventListener('dragleave', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('border-primary-400', 'bg-primary-50');
        });

        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('border-primary-400', 'bg-primary-50');
            
            if (e.dataTransfer.files.length) {
                document.getElementById('fileInput').files = e.dataTransfer.files;
                this.handleFileSelect(e);
            }
        });
    }

    handleFileSelect(event) {
        const file = event.target.files[0];
        if (!file) return;

        // Validate file type
        const allowedTypes = ['.csv', '.xlsx', '.xls'];
        const fileExtension = '.' + file.name.split('.').pop().toLowerCase();
        
        if (!allowedTypes.includes(fileExtension)) {
            showNotification('error', 'Invalid File', 'Please upload a CSV or Excel file.');
            return;
        }

        this.currentFile = file;
        this.displayFileInfo(file);
        document.getElementById('uploadBtn').disabled = false;
    }

    displayFileInfo(file) {
        const fileInfo = document.getElementById('fileInfo');
        const fileName = document.getElementById('fileName');
        const fileSize = document.getElementById('fileSize');

        fileName.textContent = file.name;
        fileSize.textContent = this.formatFileSize(file.size);
        fileInfo.classList.remove('hidden');
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    async uploadFile() {
        if (!this.currentFile) {
            showNotification('error', 'No File', 'Please select a file first.');
            return;
        }

        const formData = new FormData();
        formData.append('file', this.currentFile);

        showLoading('Processing your file...');

        try {
            const response = await fetch('/api/upload', {
                method: 'POST',
                body: formData
            });

            const result = await response.json();

            if (response.ok && result.success) {
                showNotification('success', 'Upload Successful', result.message);
                this.displayPreview(result.data, result.stats);
            } else {
                showNotification('error', 'Upload Failed', result.error);
            }
        } catch (error) {
            showNotification('error', 'Upload Error', 'Failed to upload file. Please try again.');
            console.error('Upload error:', error);
        } finally {
            hideLoading();
        }
    }

    displayPreview(students, stats) {
        // Show preview section
        document.getElementById('previewSection').classList.remove('hidden');

        // Display statistics
        this.displayStats(stats);

        // Display table data
        const tableBody = document.getElementById('previewTableBody');
        tableBody.innerHTML = '';

        students.forEach((student, index) => {
            const row = document.createElement('tr');
            row.className = index % 2 === 0 ? 'bg-white' : 'bg-gray-50';
            row.innerHTML = `
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">${student.name}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${student.email}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${student.score}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${student.subject || 'General'}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium ${this.getGradeColor(student.score)}">${this.calculateGrade(student.score)}</td>
            `;
            tableBody.appendChild(row);
        });
    }

    displayStats(stats) {
        const statsContainer = document.getElementById('uploadStats');
        statsContainer.innerHTML = `
            <div class="bg-blue-50 p-4 rounded-lg">
                <div class="text-blue-900 font-bold text-2xl">${stats.total_students}</div>
                <div class="text-blue-700 text-sm">Total Students</div>
            </div>
            <div class="bg-green-50 p-4 rounded-lg">
                <div class="text-green-900 font-bold text-2xl">${stats.average_score.toFixed(1)}</div>
                <div class="text-green-700 text-sm">Average Score</div>
            </div>
            <div class="bg-purple-50 p-4 rounded-lg">
                <div class="text-purple-900 font-bold text-2xl">${stats.highest_score}</div>
                <div class="text-purple-700 text-sm">Highest Score</div>
            </div>
            <div class="bg-yellow-50 p-4 rounded-lg">
                <div class="text-yellow-900 font-bold text-2xl">${stats.subject_count}</div>
                <div class="text-yellow-700 text-sm">Subjects</div>
            </div>
        `;
    }

    calculateGrade(score) {
        if (score >= 90) return 'A';
        if (score >= 80) return 'B';
        if (score >= 70) return 'C';
        if (score >= 60) return 'D';
        return 'F';
    }

    getGradeColor(score) {
        if (score >= 90) return 'text-green-600';
        if (score >= 80) return 'text-blue-600';
        if (score >= 70) return 'text-yellow-600';
        if (score >= 60) return 'text-orange-600';
        return 'text-red-600';
    }

    async sendEmails() {
        if (!confirm('Are you sure you want to send emails to all students? This action cannot be undone.')) {
            return;
        }

        showLoading('Sending emails... This may take a few minutes.');

        try {
            const response = await fetch('/api/send-emails', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ batch_size: 50 })
            });

            const result = await response.json();

            if (response.ok && result.success) {
                showNotification('success', 'Emails Sent', result.message);
                
                if (result.errors && result.errors.length > 0) {
                    console.warn('Some emails failed:', result.errors);
                    // You could show a detailed error modal here
                }
            } else {
                showNotification('error', 'Sending Failed', result.error);
            }
        } catch (error) {
            showNotification('error', 'Network Error', 'Failed to send emails. Please check your connection.');
            console.error('Email sending error:', error);
        } finally {
            hideLoading();
        }
    }

    clearFile() {
        this.currentFile = null;
        document.getElementById('fileInput').value = '';
        document.getElementById('fileInfo').classList.add('hidden');
        document.getElementById('uploadBtn').disabled = true;
    }

    clearAllData() {
        if (confirm('Are you sure you want to clear all data? This will remove the current preview.')) {
            this.clearFile();
            document.getElementById('previewSection').classList.add('hidden');
            showNotification('info', 'Data Cleared', 'All student data has been cleared.');
        }
    }
}

// Initialize the application
let studentSystem;

document.addEventListener('DOMContentLoaded', () => {
    studentSystem = new StudentResultSystem();
});

// Global functions for HTML onclick handlers
function uploadFile() {
    studentSystem.uploadFile();
}

function sendEmails() {
    studentSystem.sendEmails();
}

function clearFile() {
    studentSystem.clearFile();
}

function clearAllData() {
    studentSystem.clearAllData();
}
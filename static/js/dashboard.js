class Dashboard {
    constructor() {
        this.stats = {};
        this.init();
    }

    async init() {
        await this.loadDashboardData();
        this.setupAutoRefresh();
    }

    async loadDashboardData() {
        try {
            showLoading('Loading dashboard data...');
            
            const response = await fetch('/api/dashboard-stats');
            const result = await response.json();

            if (response.ok && result.success) {
                this.stats = result;
                this.updateDashboard();
            } else {
                showNotification('error', 'Load Failed', result.error);
            }
        } catch (error) {
            showNotification('error', 'Load Error', 'Failed to load dashboard data.');
            console.error('Dashboard load error:', error);
        } finally {
            hideLoading();
        }
    }

    updateDashboard() {
        this.updateStatsCards();
        this.updateRecentActivity();
        this.updateSubjectStats();
        this.updateCharts();
    }

    updateStatsCards() {
        const { stats } = this.stats;
        
        document.getElementById('totalStudents').textContent = stats.total_students.toLocaleString();
        document.getElementById('sentEmails').textContent = stats.sent_emails.toLocaleString();
        document.getElementById('unsentEmails').textContent = stats.unsent_emails.toLocaleString();
        document.getElementById('completionRate').textContent = stats.completion_rate.toFixed(1) + '%';
    }

    updateRecentActivity() {
        const container = document.getElementById('recentActivity');
        
        if (!this.stats.recent_activity || this.stats.recent_activity.length === 0) {
            container.innerHTML = '<p class="text-gray-500 text-center">No recent activity</p>';
            return;
        }

        container.innerHTML = this.stats.recent_activity.map(activity => `
            <div class="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div class="flex items-center space-x-3">
                    <div class="flex-shrink-0">
                        <i class="fas ${activity.status === 'sent' ? 'fa-check-circle text-green-500' : 'fa-exclamation-circle text-red-500'}"></i>
                    </div>
                    <div>
                        <p class="text-sm font-medium text-gray-900">${activity.student_name}</p>
                        <p class="text-sm text-gray-500">${activity.student_email}</p>
                    </div>
                </div>
                <div class="text-right">
                    <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${activity.status === 'sent' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}">
                        ${activity.status}
                    </span>
                    <p class="text-xs text-gray-500 mt-1">${formatDate(activity.sent_at)}</p>
                </div>
            </div>
        `).join('');
    }

    updateSubjectStats() {
        const container = document.getElementById('subjectStats');
        
        if (!this.stats.subject_stats || this.stats.subject_stats.length === 0) {
            container.innerHTML = '<p class="text-gray-500 text-center">No subject data available</p>';
            return;
        }

        container.innerHTML = this.stats.subject_stats.map(subject => `
            <div class="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div>
                    <p class="text-sm font-medium text-gray-900">${subject.subject}</p>
                    <p class="text-sm text-gray-500">${subject.count} students</p>
                </div>
                <div class="text-right">
                    <p class="text-sm font-medium text-gray-900">${parseFloat(subject.avg_score).toFixed(1)}</p>
                    <p class="text-xs text-gray-500">Average</p>
                </div>
            </div>
        `).join('');
    }

    updateCharts() {
        // This will be implemented in charts.js
        if (window.updateCharts) {
            window.updateCharts(this.stats);
        }
    }

    setupAutoRefresh() {
        // Refresh dashboard every 30 seconds
        setInterval(() => {
            this.loadDashboardData();
        }, 30000);
    }
}

// Initialize dashboard when DOM is loaded
let dashboard;

document.addEventListener('DOMContentLoaded', () => {
    dashboard = new Dashboard();
});
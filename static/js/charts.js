class ChartManager {
    constructor() {
        this.gradeChart = null;
        this.emailHistoryChart = null;
    }

    updateCharts(stats) {
        this.createGradeChart(stats);
        this.createEmailHistoryChart(stats);
    }

    createGradeChart(stats) {
        const ctx = document.getElementById('gradeChart').getContext('2d');
        
        // Destroy existing chart if it exists
        if (this.gradeChart) {
            this.gradeChart.destroy();
        }

        const gradeDistribution = stats.stats?.grade_distribution || { A: 0, B: 0, C: 0, D: 0, F: 0 };

        this.gradeChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['A (90-100)', 'B (80-89)', 'C (70-79)', 'D (60-69)', 'F (0-59)'],
                datasets: [{
                    data: [
                        gradeDistribution.A || 0,
                        gradeDistribution.B || 0,
                        gradeDistribution.C || 0,
                        gradeDistribution.D || 0,
                        gradeDistribution.F || 0
                    ],
                    backgroundColor: [
                        '#10B981', // green
                        '#3B82F6', // blue
                        '#F59E0B', // yellow
                        '#F97316', // orange
                        '#EF4444'  // red
                    ],
                    borderWidth: 2,
                    borderColor: '#FFFFFF'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 20,
                            usePointStyle: true
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const label = context.label || '';
                                const value = context.raw || 0;
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = total > 0 ? ((value / total) * 100).toFixed(1) : 0;
                                return `${label}: ${value} (${percentage}%)`;
                            }
                        }
                    }
                }
            }
        });
    }

    createEmailHistoryChart(stats) {
        const ctx = document.getElementById('emailHistoryChart').getContext('2d');
        
        // Destroy existing chart if it exists
        if (this.emailHistoryChart) {
            this.emailHistoryChart.destroy();
        }

        const dailyStats = stats.daily_stats || [];
        const dates = dailyStats.map(stat => {
            const date = new Date(stat.date);
            return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
        });
        const counts = dailyStats.map(stat => stat.count);

        this.emailHistoryChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: dates,
                datasets: [{
                    label: 'Emails Sent',
                    data: counts,
                    borderColor: '#8B5CF6',
                    backgroundColor: 'rgba(139, 92, 246, 0.1)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4,
                    pointBackgroundColor: '#8B5CF6',
                    pointBorderColor: '#FFFFFF',
                    pointBorderWidth: 2,
                    pointRadius: 5,
                    pointHoverRadius: 7
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        mode: 'index',
                        intersect: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            stepSize: 1
                        },
                        grid: {
                            drawBorder: false
                        }
                    },
                    x: {
                        grid: {
                            display: false
                        }
                    }
                }
            }
        });
    }
}

// Initialize chart manager
const chartManager = new ChartManager();

// Global function to update charts
function updateCharts(stats) {
    chartManager.updateCharts(stats);
}
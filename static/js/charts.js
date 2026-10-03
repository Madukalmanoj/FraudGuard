/**
 * Chart.js wrapper functions for light theme dashboard
 */

// Common options for light theme charts
const lightThemeOptions = {
    responsive: true,
    maintainAspectRatio: false,
    color: '#475569',
    plugins: {
        legend: {
            position: 'bottom',
            labels: {
                color: '#334155',
                font: {
                    family: "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
                    size: 12,
                    weight: '500'
                },
                padding: 16,
                usePointStyle: true,
                pointStyle: 'circle'
            }
        },
        tooltip: {
            backgroundColor: '#0f172a',
            titleColor: '#ffffff',
            bodyColor: '#ffffff',
            cornerRadius: 8,
            padding: 10
        }
    },
    scales: {
        x: {
            ticks: { color: '#64748b' },
            grid: { color: '#f1f5f9' }
        },
        y: {
            ticks: { color: '#64748b' },
            grid: { color: '#f1f5f9' }
        }
    }
};

const pieThemeOptions = {
    responsive: true,
    maintainAspectRatio: false,
    color: '#475569',
    plugins: {
        legend: {
            position: 'bottom',
            labels: {
                color: '#334155',
                font: {
                    family: "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
                    size: 12,
                    weight: '500'
                },
                padding: 16,
                usePointStyle: true,
                pointStyle: 'circle'
            }
        },
        tooltip: {
            backgroundColor: '#0f172a',
            titleColor: '#ffffff',
            bodyColor: '#ffffff',
            cornerRadius: 8,
            padding: 10
        }
    }
};

function renderPieChart(canvasId, labels, data, colors) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    new Chart(ctx, {
        type: 'pie',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: colors || ['#ef4444', '#10b981'],
                borderWidth: 2,
                borderColor: '#ffffff'
            }]
        },
        options: pieThemeOptions
    });
}

function renderDoughnutChart(canvasId, labels, data, colors) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: colors || ['#ef4444', '#f59e0b', '#10b981'],
                borderWidth: 2,
                borderColor: '#ffffff'
            }]
        },
        options: {
            ...pieThemeOptions,
            cutout: '72%'
        }
    });
}

function renderBarChart(canvasId, labels, datasets, title) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: datasets
        },
        options: {
            ...lightThemeOptions,
            plugins: {
                ...lightThemeOptions.plugins,
                title: {
                    display: !!title,
                    text: title,
                    color: '#0f172a',
                    font: { size: 14, weight: '600' }
                }
            }
        }
    });
}

function renderLineChart(canvasId, labels, data, title) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: title,
                data: data,
                borderColor: '#10b981',
                backgroundColor: 'rgba(16, 185, 129, 0.1)',
                borderWidth: 2,
                fill: true,
                tension: 0.3
            }]
        },
        options: lightThemeOptions
    });
}

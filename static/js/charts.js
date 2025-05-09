// Chart creation and management

// Initialize charts
function initCharts() {
    fetchStatistics()
        .then(data => {
            createDisasterTypeChart(data.disasters_by_type);
            createDisasterStateChart(data.disasters_by_state);
            createDisasterMonthChart(data.disasters_by_month);
            createRiskLevelChart(data.risk_levels);
        })
        .catch(error => {
            console.error('Error initializing charts:', error);
            showAlert('Failed to load chart data. Please refresh the page.', 'danger');
        });
}

// Fetch statistics data from API
async function fetchStatistics() {
    try {
        const response = await fetch('/api/statistics');
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error('Fetch error:', error);
        throw error;
    }
}

// Create chart for disasters by type
function createDisasterTypeChart(data) {
    const ctx = document.getElementById('disasters-by-type-chart');
    if (!ctx) return;

    // Extract labels and data
    const labels = Object.keys(data);
    const values = Object.values(data);
    
    // Define colors for different disaster types
    const colors = [
        'rgba(54, 162, 235, 0.7)',  // Blue for Flood
        'rgba(255, 99, 132, 0.7)',  // Red for Earthquake
        'rgba(75, 192, 192, 0.7)',  // Teal for Tsunami
        'rgba(255, 159, 64, 0.7)'   // Orange for Forest Fire
    ];
    
    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: values,
                backgroundColor: colors.slice(0, labels.length),
                borderColor: colors.map(color => color.replace('0.7', '1')),
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'right',
                    labels: {
                        color: '#fff'
                    }
                },
                title: {
                    display: true,
                    text: 'Disasters by Type',
                    color: '#fff',
                    font: {
                        size: 16
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const label = context.label || '';
                            const value = context.raw || 0;
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = Math.round((value / total) * 100);
                            return `${label}: ${value} (${percentage}%)`;
                        }
                    }
                }
            }
        }
    });
}

// Create chart for disasters by state
function createDisasterStateChart(data) {
    const ctx = document.getElementById('disasters-by-state-chart');
    if (!ctx) return;

    // Sort states by number of disasters (descending)
    const sortedStates = Object.entries(data)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 10); // Show only top 10 states
    
    const labels = sortedStates.map(entry => entry[0]);
    const values = sortedStates.map(entry => entry[1]);
    
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Number of Disasters',
                data: values,
                backgroundColor: 'rgba(54, 162, 235, 0.7)',
                borderColor: 'rgba(54, 162, 235, 1)',
                borderWidth: 1
            }]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                title: {
                    display: true,
                    text: 'Disasters by State (Top 10)',
                    color: '#fff',
                    font: {
                        size: 16
                    }
                }
            },
            scales: {
                x: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    },
                    ticks: {
                        color: '#fff'
                    }
                },
                y: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        color: '#fff'
                    }
                }
            }
        }
    });
}

// Create chart for disasters by month
function createDisasterMonthChart(data) {
    const ctx = document.getElementById('disasters-by-month-chart');
    if (!ctx) return;

    // Ensure all months are present and in order
    const monthOrder = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                         'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    
    const orderedData = {};
    monthOrder.forEach(month => {
        orderedData[month] = data[month] || 0;
    });
    
    const labels = Object.keys(orderedData);
    const values = Object.values(orderedData);
    
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Number of Disasters',
                data: values,
                backgroundColor: 'rgba(75, 192, 192, 0.2)',
                borderColor: 'rgba(75, 192, 192, 1)',
                borderWidth: 2,
                tension: 0.1,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                title: {
                    display: true,
                    text: 'Disasters by Month (Current Year)',
                    color: '#fff',
                    font: {
                        size: 16
                    }
                }
            },
            scales: {
                x: {
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    },
                    ticks: {
                        color: '#fff'
                    }
                },
                y: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    },
                    ticks: {
                        color: '#fff'
                    }
                }
            }
        }
    });
}

// Create chart for risk levels
function createRiskLevelChart(data) {
    const ctx = document.getElementById('risk-level-chart');
    if (!ctx) return;

    // Extract labels and data
    const labels = Object.keys(data);
    const values = Object.values(data);
    
    // Colors for risk levels (green to black)
    const colors = [
        'rgba(40, 167, 69, 0.7)',   // Level 1 - Green
        'rgba(92, 184, 92, 0.7)',    // Level 2 - Light Green
        'rgba(255, 193, 7, 0.7)',    // Level 3 - Yellow
        'rgba(220, 53, 69, 0.7)',    // Level 4 - Red
        'rgba(0, 0, 0, 0.7)'         // Level 5 - Black
    ];
    
    new Chart(ctx, {
        type: 'polarArea',
        data: {
            labels: labels,
            datasets: [{
                data: values,
                backgroundColor: colors,
                borderColor: colors.map(color => color.replace('0.7', '1')),
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'right',
                    labels: {
                        color: '#fff'
                    }
                },
                title: {
                    display: true,
                    text: 'Risk Level Distribution',
                    color: '#fff',
                    font: {
                        size: 16
                    }
                }
            },
            scales: {
                r: {
                    ticks: {
                        display: false
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    },
                    angleLines: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    }
                }
            }
        }
    });
}

// Show alert message
function showAlert(message, type = 'info') {
    const alertPlaceholder = document.getElementById('alert-placeholder');
    
    if (alertPlaceholder) {
        const wrapper = document.createElement('div');
        wrapper.innerHTML = `
            <div class="alert alert-${type} alert-dismissible fade show" role="alert">
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            </div>
        `;
        
        alertPlaceholder.append(wrapper);
        
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            const alert = wrapper.querySelector('.alert');
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    }
}

// Initialize charts when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    // Check if any chart containers exist on the page
    if (document.querySelector('.chart-container')) {
        initCharts();
    }
});

// Smart Parking Management System - Frontend JavaScript

// Global variables
let socket = null;
let occupancyChart = null;
let trendChart = null;
let detectionActive = false;
let historyData = [];

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

// Initialize application
function initializeApp() {
    console.log('Initializing Smart Parking System...');
    
    // Setup Socket.IO connection
    setupSocketIO();
    
    // Setup event listeners
    setupEventListeners();
    
    // Initialize charts
    initializeCharts();
    
    // Load initial data
    loadParkingStatus();
    
    // Setup theme
    initializeTheme();
    
    console.log('Initialization complete');
}

// Setup Socket.IO for real-time updates
function setupSocketIO() {
    socket = io();
    
    socket.on('connect', function() {
        console.log('Connected to server');
        updateConnectionStatus(true);
        showNotification('Connected to server', 'success');
    });
    
    socket.on('disconnect', function() {
        console.log('Disconnected from server');
        updateConnectionStatus(false);
        showNotification('Disconnected from server', 'warning');
    });
    
    socket.on('parking_update', function(data) {
        console.log('Received parking update:', data);
        updateDashboard(data);
    });
    
    socket.on('connection_response', function(data) {
        console.log('Connection response:', data);
    });
}

// Setup event listeners
function setupEventListeners() {
    // Start detection button
    document.getElementById('startBtn').addEventListener('click', startDetection);
    
    // Stop detection button
    document.getElementById('stopBtn').addEventListener('click', stopDetection);
    
    // Refresh button
    document.getElementById('refreshBtn').addEventListener('click', loadParkingStatus);
    
    // Export button
    document.getElementById('exportBtn').addEventListener('click', exportData);
    
    // Fullscreen button
    document.getElementById('fullscreenBtn').addEventListener('click', toggleFullscreen);
    
    // Theme toggle
    document.getElementById('themeToggle').addEventListener('click', toggleTheme);
    
    // Request updates every 5 seconds when detection is active
    setInterval(function() {
        if (detectionActive && socket && socket.connected) {
            socket.emit('request_update');
        }
    }, 5000);
}

// Initialize charts
function initializeCharts() {
    // Occupancy Pie Chart
    const occupancyCtx = document.getElementById('occupancyChart').getContext('2d');
    occupancyChart = new Chart(occupancyCtx, {
        type: 'doughnut',
        data: {
            labels: ['Available', 'Occupied'],
            datasets: [{
                data: [0, 0],
                backgroundColor: ['#198754', '#dc3545'],
                borderWidth: 2,
                borderColor: '#fff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    position: 'bottom'
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const label = context.label || '';
                            const value = context.parsed || 0;
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = total > 0 ? ((value / total) * 100).toFixed(1) : 0;
                            return `${label}: ${value} (${percentage}%)`;
                        }
                    }
                }
            }
        }
    });
    
    // Trend Line Chart
    const trendCtx = document.getElementById('trendChart').getContext('2d');
    trendChart = new Chart(trendCtx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [
                {
                    label: 'Available',
                    data: [],
                    borderColor: '#198754',
                    backgroundColor: 'rgba(25, 135, 84, 0.1)',
                    tension: 0.4,
                    fill: true
                },
                {
                    label: 'Occupied',
                    data: [],
                    borderColor: '#dc3545',
                    backgroundColor: 'rgba(220, 53, 69, 0.1)',
                    tension: 0.4,
                    fill: true
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1
                    }
                }
            }
        }
    });
}

// Start detection
async function startDetection() {
    try {
        // Get selected video source
        const videoSourceSelect = document.getElementById('videoSourceSelect');
        const videoSource = videoSourceSelect ? videoSourceSelect.value : 'carPark.mp4';
        
        const response = await fetch('/api/detection/start', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                video_source: videoSource
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            detectionActive = true;
            document.getElementById('startBtn').disabled = true;
            document.getElementById('stopBtn').disabled = false;
            if (videoSourceSelect) {
                videoSourceSelect.disabled = true;
            }
            document.getElementById('videoOverlay').classList.add('hidden');
            document.getElementById('videoFeed').src = '/api/video/feed';
            updateStatusMessage(`Detection active - monitoring ${data.total_spaces || 0} parking spaces`, 'success');
            showNotification(`Detection started: ${videoSource}`, 'success');
        } else {
            showNotification('Failed to start detection: ' + data.error, 'danger');
        }
    } catch (error) {
        console.error('Error starting detection:', error);
        showNotification('Error starting detection', 'danger');
    }
}

// Stop detection
async function stopDetection() {
    try {
        const response = await fetch('/api/detection/stop', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            detectionActive = false;
            document.getElementById('startBtn').disabled = false;
            document.getElementById('stopBtn').disabled = true;
            const videoSourceSelect = document.getElementById('videoSourceSelect');
            if (videoSourceSelect) {
                videoSourceSelect.disabled = false;
            }
            document.getElementById('videoOverlay').classList.remove('hidden');
            document.getElementById('videoFeed').src = '';
            updateStatusMessage('Detection stopped - system ready', 'info');
            showNotification('Detection stopped successfully', 'info');
        } else {
            showNotification('Failed to stop detection: ' + data.error, 'danger');
        }
    } catch (error) {
        console.error('Error stopping detection:', error);
        showNotification('Error stopping detection', 'danger');
    }
}

// Load parking status
async function loadParkingStatus() {
    try {
        const response = await fetch('/api/parking/status');
        const data = await response.json();
        
        if (data.success) {
            updateDashboard(data);
            updateParkingMap(data.spaces);
        } else {
            showNotification('Failed to load parking status', 'warning');
        }
    } catch (error) {
        console.error('Error loading parking status:', error);
        showNotification('Error loading parking status', 'danger');
    }
    
    // Load history
    loadParkingHistory();
}

// Update dashboard with new data
function updateDashboard(data) {
    // Update statistics
    document.getElementById('totalSpaces').textContent = data.total_spaces || data.total || 0;
    document.getElementById('freeSpaces').textContent = data.free_spaces || data.free || 0;
    document.getElementById('occupiedSpaces').textContent = data.occupied_spaces || data.occupied || 0;
    
    const occupancyRate = data.occupancy_rate || 
        (data.occupied_spaces && data.total_spaces ? 
         (data.occupied_spaces / data.total_spaces * 100) : 0);
    document.getElementById('occupancyRate').textContent = occupancyRate.toFixed(1) + '%';
    
    // Update progress bars
    const freePercentage = data.total_spaces > 0 ? 
        ((data.free_spaces || data.free || 0) / (data.total_spaces || data.total || 1)) * 100 : 0;
    const occupiedPercentage = 100 - freePercentage;
    
    const availableProgress = document.getElementById('availableProgress');
    const occupiedProgress = document.getElementById('occupiedProgress');
    
    availableProgress.style.width = freePercentage + '%';
    availableProgress.textContent = `Available: ${data.free_spaces || data.free || 0}`;
    
    occupiedProgress.style.width = occupiedPercentage + '%';
    occupiedProgress.textContent = `Occupied: ${data.occupied_spaces || data.occupied || 0}`;
    
    // Update occupancy chart
    occupancyChart.data.datasets[0].data = [
        data.free_spaces || data.free || 0,
        data.occupied_spaces || data.occupied || 0
    ];
    occupancyChart.update();
    
    // Update last update time
    const now = new Date();
    document.getElementById('lastUpdate').textContent = now.toLocaleTimeString();
}

// Update parking map visualization
function updateParkingMap(spaces) {
    const parkingMap = document.getElementById('parkingMap');
    parkingMap.innerHTML = '';
    
    if (!spaces || spaces.length === 0) {
        parkingMap.innerHTML = '<p class="text-white text-center">No parking spaces configured</p>';
        return;
    }
    
    spaces.forEach((space, index) => {
        const spaceDiv = document.createElement('div');
        spaceDiv.className = `parking-space ${space.occupied ? 'occupied' : 'free'}`;
        spaceDiv.innerHTML = `
            <div class="parking-space-icon">
                <i class="fas fa-${space.occupied ? 'car' : 'square'}"></i>
            </div>
            <div class="parking-space-id">${space.id || index + 1}</div>
        `;
        
        spaceDiv.addEventListener('click', function() {
            showSpaceDetails(space);
        });
        
        parkingMap.appendChild(spaceDiv);
    });
}

// Load parking history
async function loadParkingHistory() {
    try {
        const response = await fetch('/api/parking/history');
        const data = await response.json();
        
        if (data.success && data.history) {
            historyData = data.history;
            updateTrendChart();
        }
    } catch (error) {
        console.error('Error loading parking history:', error);
    }
}

// Update trend chart with history data
function updateTrendChart() {
    if (historyData.length === 0) return;
    
    // Get last 20 data points
    const recentData = historyData.slice(-20);
    
    const labels = recentData.map(entry => {
        const date = new Date(entry.timestamp);
        return date.toLocaleTimeString();
    });
    
    const freeData = recentData.map(entry => entry.free);
    const occupiedData = recentData.map(entry => entry.occupied);
    
    trendChart.data.labels = labels;
    trendChart.data.datasets[0].data = freeData;
    trendChart.data.datasets[1].data = occupiedData;
    trendChart.update();
}

// Show space details
function showSpaceDetails(space) {
    const status = space.occupied ? 'Occupied' : 'Available';
    const statusClass = space.occupied ? 'danger' : 'success';
    
    showNotification(
        `Space ${space.id}: ${status} (Section ${space.section})`,
        statusClass
    );
}

// Export data
function exportData() {
    try {
        // Create CSV content
        let csvContent = 'Timestamp,Total Spaces,Available,Occupied,Occupancy Rate\n';
        
        historyData.forEach(entry => {
            csvContent += `${entry.timestamp},${entry.total},${entry.free},${entry.occupied},${entry.occupancy_rate.toFixed(2)}%\n`;
        });
        
        // Create blob and download
        const blob = new Blob([csvContent], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `parking_report_${new Date().toISOString()}.csv`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
        
        showNotification('Report exported successfully', 'success');
    } catch (error) {
        console.error('Error exporting data:', error);
        showNotification('Error exporting report', 'danger');
    }
}

// Toggle fullscreen video
function toggleFullscreen() {
    const videoFeed = document.getElementById('videoFeed');
    
    if (!document.fullscreenElement) {
        if (videoFeed.requestFullscreen) {
            videoFeed.requestFullscreen();
        } else if (videoFeed.webkitRequestFullscreen) {
            videoFeed.webkitRequestFullscreen();
        } else if (videoFeed.msRequestFullscreen) {
            videoFeed.msRequestFullscreen();
        }
        document.getElementById('fullscreenBtn').innerHTML = '<i class="fas fa-compress me-1"></i>Exit Fullscreen';
    } else {
        if (document.exitFullscreen) {
            document.exitFullscreen();
        }
        document.getElementById('fullscreenBtn').innerHTML = '<i class="fas fa-expand me-1"></i>Fullscreen Video';
    }
}

// Update connection status
function updateConnectionStatus(connected) {
    const statusBadge = document.getElementById('connectionStatus');
    if (connected) {
        statusBadge.className = 'badge bg-success ms-auto';
        statusBadge.innerHTML = '<i class="fas fa-circle pulse"></i> Connected';
    } else {
        statusBadge.className = 'badge bg-danger ms-auto';
        statusBadge.innerHTML = '<i class="fas fa-circle"></i> Disconnected';
    }
}

// Update status message
function updateStatusMessage(message, type = 'info') {
    const statusMessage = document.getElementById('statusMessage');
    const alertBox = statusMessage.closest('.alert');
    
    statusMessage.textContent = message;
    alertBox.className = `alert alert-${type} d-flex align-items-center`;
}

// Show notification
function showNotification(message, type = 'info') {
    // Create toast element
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type} border-0 fade show`;
    toast.setAttribute('role', 'alert');
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">${message}</div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    
    // Add to document
    document.body.appendChild(toast);
    
    // Auto remove after 3 seconds
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => {
            document.body.removeChild(toast);
        }, 300);
    }, 3000);
}

// Theme management
function initializeTheme() {
    const savedTheme = localStorage.getItem('theme') || 'light';
    document.body.setAttribute('data-theme', savedTheme);
    updateThemeIcon(savedTheme);
}

function toggleTheme() {
    const currentTheme = document.body.getAttribute('data-theme');
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';
    
    document.body.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    updateThemeIcon(newTheme);
    
    showNotification(`Switched to ${newTheme} theme`, 'info');
}

function updateThemeIcon(theme) {
    const icon = document.getElementById('themeIcon');
    if (theme === 'dark') {
        icon.className = 'fas fa-sun';
    } else {
        icon.className = 'fas fa-moon';
    }
}

// Periodic updates
setInterval(function() {
    if (detectionActive) {
        loadParkingHistory();
    }
}, 10000); // Update history every 10 seconds

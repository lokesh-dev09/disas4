// Map initialization and interaction handling
let map;
let disasterMarkers = L.layerGroup();
let riskZones = L.layerGroup();

// Risk level colors
const riskColors = {
    1: "#28a745", // Green (Very Low)
    2: "#5cb85c", // Light Green (Low)
    3: "#ffc107", // Yellow (Moderate)
    4: "#dc3545", // Red (High)
    5: "#000000"  // Black (Life-threatening)
};

// Risk level descriptions
const riskDescriptions = {
    1: "Very Low Risk",
    2: "Low Risk",
    3: "Moderate Risk",
    4: "High Risk",
    5: "Life-Threatening"
};

// Disaster type icons
const disasterIcons = {
    "Flood": "water",
    "Earthquake": "vibration",
    "Tsunami": "waves",
    "Forest Fire": "flame"
};

// Initialize map
function initMap() {
    // Create map centered on Malaysia
    map = L.map('map-container').setView([4.2105, 108.9758], 6);
    
    // Add tile layer (using OpenStreetMap)
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
        maxZoom: 18
    }).addTo(map);
    
    // Add layer groups to map
    disasterMarkers.addTo(map);
    riskZones.addTo(map);
    
    // Add legend
    addLegend();
    
    // Load initial data
    loadDisasters();
    loadRiskZones();
    
    // Set up event listeners
    setupEventListeners();
}

// Add map legend
function addLegend() {
    const legend = L.control({ position: 'bottomright' });
    
    legend.onAdd = function(map) {
        const div = L.DomUtil.create('div', 'map-legend');
        div.innerHTML = '<h6 class="mb-2">Risk Levels</h6>';
        
        for (let i = 1; i <= 5; i++) {
            div.innerHTML += `
                <div class="legend-item">
                    <div class="legend-color" style="background-color: ${riskColors[i]}"></div>
                    <div>${riskDescriptions[i]}</div>
                </div>
            `;
        }
        
        div.innerHTML += '<h6 class="mt-3 mb-2">Disaster Types</h6>';
        
        for (const [type, icon] of Object.entries(disasterIcons)) {
            div.innerHTML += `
                <div class="legend-item">
                    <i class="feather-${icon} me-2"></i>
                    <div>${type}</div>
                </div>
            `;
        }
        
        return div;
    };
    
    legend.addTo(map);
}

// Load disaster data from API
function loadDisasters() {
    // Get filter values
    const disasterType = document.getElementById('disaster-type-filter')?.value || '';
    const state = document.getElementById('state-filter')?.value || '';
    const activeOnly = document.getElementById('active-only-filter')?.checked || false;
    
    // Show loading indicator
    document.getElementById('map-loading').classList.remove('d-none');
    
    // Build query parameters
    let params = new URLSearchParams();
    if (disasterType) params.append('disaster_type', disasterType);
    if (state) params.append('state', state);
    if (activeOnly) params.append('active_only', 'true');
    
    // Fetch disaster data
    fetch(`/api/disasters?${params.toString()}`)
        .then(response => response.json())
        .then(data => {
            // Clear existing markers
            disasterMarkers.clearLayers();
            
            // Add new markers
            data.forEach(disaster => {
                const marker = createDisasterMarker(disaster);
                disasterMarkers.addLayer(marker);
            });
            
            // Hide loading indicator
            document.getElementById('map-loading').classList.add('d-none');
        })
        .catch(error => {
            console.error('Error loading disaster data:', error);
            // Hide loading indicator
            document.getElementById('map-loading').classList.add('d-none');
            // Show error message
            showAlert('Error loading disaster data. Please try again.', 'danger');
        });
}

// Create marker for a disaster
function createDisasterMarker(disaster) {
    // Determine icon based on disaster type
    const iconName = disasterIcons[disaster.type] || 'alert-triangle';
    
    // Create marker with popup
    const marker = L.marker([disaster.latitude, disaster.longitude], {
        title: disaster.title,
        icon: L.divIcon({
            html: `<i class="feather-${iconName}" style="color: ${riskColors[disaster.severity]}; font-size: 24px;"></i>`,
            className: 'disaster-marker',
            iconSize: [30, 30],
            iconAnchor: [15, 15]
        })
    });
    
    // Add popup with disaster information
    marker.bindPopup(`
        <div class="disaster-popup">
            <h5>${disaster.title}</h5>
            <p class="mb-1"><strong>Type:</strong> ${disaster.type}</p>
            <p class="mb-1"><strong>Location:</strong> ${disaster.state}</p>
            <p class="mb-1"><strong>Start Date:</strong> ${disaster.start_date}</p>
            <p class="mb-1"><strong>Status:</strong> ${disaster.is_active ? 'Active' : 'Inactive'}</p>
            <p class="mb-1"><strong>Severity:</strong> 
                <span class="badge risk-${disaster.severity}">${riskDescriptions[disaster.severity]}</span>
            </p>
            ${disaster.description ? `<p class="mt-2">${disaster.description}</p>` : ''}
        </div>
    `);
    
    return marker;
}

// Load risk assessment zones
function loadRiskZones() {
    // Get filter values
    const disasterType = document.getElementById('disaster-type-filter')?.value || '';
    const state = document.getElementById('state-filter')?.value || '';
    const minRiskLevel = document.getElementById('min-risk-filter')?.value || 1;
    
    // Build query parameters
    let params = new URLSearchParams();
    if (disasterType) params.append('disaster_type', disasterType);
    if (state) params.append('state', state);
    if (minRiskLevel > 1) params.append('min_risk_level', minRiskLevel);
    
    // Fetch risk assessment data
    fetch(`/api/risk_assessments?${params.toString()}`)
        .then(response => response.json())
        .then(data => {
            // Clear existing zones
            riskZones.clearLayers();
            
            // Add new zones
            data.forEach(assessment => {
                const circle = createRiskZone(assessment);
                riskZones.addLayer(circle);
            });
        })
        .catch(error => {
            console.error('Error loading risk zones:', error);
            showAlert('Error loading risk zone data. Please try again.', 'danger');
        });
}

// Create circle for a risk zone
function createRiskZone(assessment) {
    // Create circle with radius based on risk level
    const radius = 5000 + (assessment.risk_level * 5000); // Higher risk = larger circle
    
    const circle = L.circle([assessment.latitude, assessment.longitude], {
        color: riskColors[assessment.risk_level],
        fillColor: riskColors[assessment.risk_level],
        fillOpacity: 0.2,
        weight: 1,
        radius: radius
    });
    
    // Add popup with risk information
    circle.bindPopup(`
        <div class="risk-popup">
            <h5>${assessment.location_name}</h5>
            <p class="mb-1"><strong>State:</strong> ${assessment.state}</p>
            <p class="mb-1"><strong>Disaster Type:</strong> ${assessment.disaster_type}</p>
            <p class="mb-1"><strong>Risk Level:</strong> 
                <span class="badge risk-${assessment.risk_level}">${riskDescriptions[assessment.risk_level]}</span>
            </p>
            <p class="mb-1"><strong>Last Assessed:</strong> ${assessment.last_assessed}</p>
            ${assessment.details ? `<p class="mt-2">${assessment.details}</p>` : ''}
        </div>
    `);
    
    return circle;
}

// Set up event listeners for map controls
function setupEventListeners() {
    // Filter change handlers
    document.querySelectorAll('.map-filter').forEach(filter => {
        filter.addEventListener('change', () => {
            loadDisasters();
            loadRiskZones();
        });
    });
    
    // Layer toggle handlers
    document.getElementById('toggle-disasters')?.addEventListener('change', function() {
        if (this.checked) {
            map.addLayer(disasterMarkers);
        } else {
            map.removeLayer(disasterMarkers);
        }
    });
    
    document.getElementById('toggle-risk-zones')?.addEventListener('change', function() {
        if (this.checked) {
            map.addLayer(riskZones);
        } else {
            map.removeLayer(riskZones);
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

// Initialize map when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    if (document.getElementById('map-container')) {
        initMap();
    }
});

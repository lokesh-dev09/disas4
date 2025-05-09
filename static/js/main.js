// Main JavaScript file for general functionality

// Initialize Feather icons
function initFeatherIcons() {
    if (typeof feather !== 'undefined') {
        feather.replace();
    }
}

// Initialize tooltips and popovers
function initBootstrapComponents() {
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
}

// Handle alert filters
function setupAlertFilters() {
    const filterForm = document.getElementById('alert-filter-form');
    if (filterForm) {
        filterForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const disasterType = document.getElementById('disaster-type-filter').value;
            const state = document.getElementById('state-filter').value;
            const activeOnly = document.getElementById('active-only-filter').checked;
            
            // Build the URL with query parameters
            const url = new URL(window.location.href);
            url.searchParams.set('disaster_type', disasterType || '');
            url.searchParams.set('state', state || '');
            url.searchParams.set('active_only', activeOnly);
            
            // Navigate to the filtered page
            window.location.href = url.toString();
        });
    }
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

// Format date to a readable format
function formatDate(dateString) {
    if (!dateString) return 'N/A';
    
    const date = new Date(dateString);
    return date.toLocaleDateString('en-MY', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

// Toggle theme between light and dark
function toggleTheme() {
    const html = document.documentElement;
    const currentTheme = html.getAttribute('data-bs-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    
    html.setAttribute('data-bs-theme', newTheme);
    localStorage.setItem('preferred-theme', newTheme);
}

// Apply stored theme preference
function applyStoredTheme() {
    const storedTheme = localStorage.getItem('preferred-theme');
    if (storedTheme) {
        document.documentElement.setAttribute('data-bs-theme', storedTheme);
    }
}

// Handle refresh data button
function setupRefreshButton() {
    const refreshBtn = document.getElementById('refresh-data-btn');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', function() {
            // Show loading indicator
            this.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Refreshing...';
            this.disabled = true;
            
            // Reload the current page
            setTimeout(() => {
                window.location.reload();
            }, 1000);
        });
    }
}

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    // Apply stored theme
    applyStoredTheme();
    
    // Initialize components
    initFeatherIcons();
    initBootstrapComponents();
    
    // Setup event handlers
    setupAlertFilters();
    setupRefreshButton();
    
    // Setup theme toggle button
    const themeToggleBtn = document.getElementById('theme-toggle');
    if (themeToggleBtn) {
        themeToggleBtn.addEventListener('click', toggleTheme);
    }
});

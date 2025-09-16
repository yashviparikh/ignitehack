// App.js - Common functionality across all pages
// Food Rescue Matchmaker Application

// Global app configuration
const APP_CONFIG = {
    name: 'Food Rescue Matchmaker',
    version: '1.0.0',
    apiBaseUrl: '/api', // This would be backend URL in production
    roles: {
        donor: { name: 'Donor', icon: '🍞', dashboard: 'html/donor-dashboard.html' },
        ngo: { name: 'NGO', icon: '🏢', dashboard: 'html/ngo-dashboard.html' },
        admin: { name: 'Admin', icon: '⚙️', dashboard: 'html/admin-dashboard.html' }
    }
};

// Common utility functions
const Utils = {
    // Format date
    formatDate: function(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
    },
    
    // Format time ago
    timeAgo: function(dateString) {
        const now = new Date();
        const date = new Date(dateString);
        const diffInMinutes = Math.floor((now - date) / (1000 * 60));
        
        if (diffInMinutes < 1) return 'Just now';
        if (diffInMinutes < 60) return `${diffInMinutes} min ago`;
        
        const diffInHours = Math.floor(diffInMinutes / 60);
        if (diffInHours < 24) return `${diffInHours} hour${diffInHours > 1 ? 's' : ''} ago`;
        
        const diffInDays = Math.floor(diffInHours / 24);
        return `${diffInDays} day${diffInDays > 1 ? 's' : ''} ago`;
    },
    
    // Show notification
    showNotification: function(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <span>${message}</span>
            <button onclick="this.parentElement.remove()">&times;</button>
        `;
        
        // Add to page
        document.body.appendChild(notification);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, 5000);
    },
    
    // Validate email
    isValidEmail: function(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    },
    
    // Generate unique ID
    generateId: function() {
        return Date.now().toString(36) + Math.random().toString(36).substr(2);
    }
};

// User authentication management
const Auth = {
    // Get current user
    getCurrentUser: function() {
        const userData = localStorage.getItem('foodRescueUser');
        if (userData) {
            try {
                return JSON.parse(userData);
            } catch (e) {
                console.error('Error parsing user data:', e);
                this.logout();
                return null;
            }
        }
        return null;
    },
    
    // Check if user is authenticated
    isAuthenticated: function() {
        const user = this.getCurrentUser();
        return user && user.isAuthenticated;
    },
    
    // Get user role
    getUserRole: function() {
        const user = this.getCurrentUser();
        return user ? user.role : null;
    },
    
    // Login user
    login: function(email, role) {
        const userData = {
            email: email,
            role: role,
            isAuthenticated: true,
            loginTime: new Date().toISOString(),
            userId: Utils.generateId()
        };
        localStorage.setItem('foodRescueUser', JSON.stringify(userData));
        return userData;
    },
    
    // Logout user
    logout: function() {
        localStorage.removeItem('foodRescueUser');
        localStorage.removeItem('appData'); // Clear any app data
        window.location.href = '/index.html';
    },
    
    // Redirect to appropriate dashboard
    redirectToDashboard: function() {
        const user = this.getCurrentUser();
        if (user && user.role) {
            const roleConfig = APP_CONFIG.roles[user.role];
            if (roleConfig) {
                window.location.href = roleConfig.dashboard;
            }
        }
    }
};

// Local storage management
const Storage = {
    // Save data
    save: function(key, data) {
        try {
            localStorage.setItem(key, JSON.stringify(data));
            return true;
        } catch (e) {
            console.error('Error saving to localStorage:', e);
            return false;
        }
    },
    
    // Load data
    load: function(key) {
        try {
            const data = localStorage.getItem(key);
            return data ? JSON.parse(data) : null;
        } catch (e) {
            console.error('Error loading from localStorage:', e);
            return null;
        }
    },
    
    // Remove data
    remove: function(key) {
        localStorage.removeItem(key);
    },
    
    // Clear all app data
    clear: function() {
        const keysToKeep = ['foodRescueUser']; // Keep user session
        const keysToRemove = [];
        
        for (let i = 0; i < localStorage.length; i++) {
            const key = localStorage.key(i);
            if (!keysToKeep.includes(key)) {
                keysToRemove.push(key);
            }
        }
        
        keysToRemove.forEach(key => localStorage.removeItem(key));
    }
};

// Navigation management
const Navigation = {
    // Go to page
    goTo: function(url) {
        window.location.href = url;
    },
    
    // Go back
    goBack: function() {
        window.history.back();
    },
    
    // Reload current page
    reload: function() {
        window.location.reload();
    }
};

// Common page initialization
document.addEventListener('DOMContentLoaded', function() {
    console.log(`${APP_CONFIG.name} v${APP_CONFIG.version} - Page loaded`);
    
    // Add common event listeners
    addCommonEventListeners();
    
    // Check authentication status for protected pages
    checkPageAccess();
});

// Add common event listeners
function addCommonEventListeners() {
    // Add logout functionality to logout buttons
    const logoutButtons = document.querySelectorAll('.logout, [onclick*="logout"]');
    logoutButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            if (confirm('Are you sure you want to logout?')) {
                Auth.logout();
            }
        });
    });
    
    // Add form validation
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!validateForm(this)) {
                e.preventDefault();
            }
        });
    });
}

// Basic form validation
function validateForm(form) {
    const requiredFields = form.querySelectorAll('[required]');
    let isValid = true;
    
    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            field.classList.add('error');
            isValid = false;
        } else {
            field.classList.remove('error');
        }
        
        // Email validation
        if (field.type === 'email' && field.value && !Utils.isValidEmail(field.value)) {
            field.classList.add('error');
            Utils.showNotification('Please enter a valid email address', 'error');
            isValid = false;
        }
    });
    
    return isValid;
}

// Check if user has access to current page
function checkPageAccess() {
    const currentPage = window.location.pathname;
    const protectedPages = ['donor-dashboard.html', 'ngo-dashboard.html', 'admin-dashboard.html'];
    
    // Check if current page is a protected dashboard
    const isProtectedPage = protectedPages.some(page => currentPage.includes(page));
    
    if (isProtectedPage && !Auth.isAuthenticated()) {
        console.log('Access denied - redirecting to login');
        Utils.showNotification('Please login to access this page', 'error');
        setTimeout(() => {
            window.location.href = '/index.html';
        }, 2000);
        return false;
    }
    
    return true;
}

// Initialize app when page loads
window.addEventListener('load', function() {
    console.log('App fully loaded and ready');
});

// Handle page visibility changes
document.addEventListener('visibilitychange', function() {
    if (document.visibilityState === 'visible') {
        // Page became visible - could refresh data here
        console.log('Page became visible');
    }
});

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        APP_CONFIG,
        Utils,
        Auth,
        Storage,
        Navigation
    };
}
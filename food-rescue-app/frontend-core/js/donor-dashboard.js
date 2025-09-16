// Donor Dashboard Specific JavaScript
// Extends dashboard-common.js with donor-specific functionality

console.log('🍎 Donor Dashboard Script Loaded');

// Donor-specific functions and event handlers
class DonorDashboard {
    constructor() {
        this.donations = [];
        this.matches = [];
        
        // Initialize when dashboard manager is ready
        if (window.dashboardManager && window.dashboardManager.isInitialized) {
            this.init();
        } else {
            // Wait for dashboard manager to initialize
            document.addEventListener('DOMContentLoaded', () => {
                setTimeout(() => this.init(), 1000);
            });
        }
    }

    init() {
        console.log('🍎 Initializing Donor Dashboard...');
        
        // Load donor-specific data
        this.loadDonations();
        this.loadMatches();
        
        // Setup donor-specific event listeners
        this.setupEventListeners();
        
        console.log('✅ Donor Dashboard initialized');
    }

    loadDonations() {
        // Load donations from localStorage
        const storedDonations = localStorage.getItem(`donations_${window.dashboardManager.currentUser.email}`);
        this.donations = storedDonations ? JSON.parse(storedDonations) : [];
        
        // Add sample donations if none exist
        if (this.donations.length === 0) {
            this.donations = this.generateSampleDonations();
            this.saveDonations();
        }
    }

    loadMatches() {
        // Load matches from localStorage
        const storedMatches = localStorage.getItem(`matches_${window.dashboardManager.currentUser.email}`);
        this.matches = storedMatches ? JSON.parse(storedMatches) : [];
        
        // Add sample matches if none exist
        if (this.matches.length === 0) {
            this.matches = this.generateSampleMatches();
            this.saveMatches();
        }
    }

    generateSampleDonations() {
        return [
            {
                id: 1,
                title: 'Fresh Vegetables',
                description: 'Mixed vegetables from restaurant prep',
                quantity: '15kg',
                category: 'Vegetables',
                expiryDate: new Date(Date.now() + 2 * 24 * 60 * 60 * 1000).toISOString(),
                status: 'Active',
                location: 'Downtown Restaurant',
                createdAt: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString()
            },
            {
                id: 2,
                title: 'Baked Goods',
                description: 'Unsold bread and pastries',
                quantity: '8kg',
                category: 'Bakery',
                expiryDate: new Date(Date.now() + 1 * 24 * 60 * 60 * 1000).toISOString(),
                status: 'Matched',
                location: 'Local Bakery',
                createdAt: new Date(Date.now() - 6 * 60 * 60 * 1000).toISOString()
            }
        ];
    }

    generateSampleMatches() {
        return [
            {
                id: 1,
                donationId: 1,
                ngoName: 'Hope Kitchen',
                ngoContact: 'contact@hopekitchen.org',
                status: 'Confirmed',
                pickupTime: new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString(),
                matchedAt: new Date(Date.now() - 30 * 60 * 1000).toISOString()
            },
            {
                id: 2,
                donationId: 2,
                ngoName: 'Community Care Center',
                ngoContact: 'info@communitycare.org',
                status: 'Pickup Scheduled',
                pickupTime: new Date(Date.now() + 6 * 60 * 60 * 1000).toISOString(),
                matchedAt: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString()
            }
        ];
    }

    saveDonations() {
        localStorage.setItem(`donations_${window.dashboardManager.currentUser.email}`, JSON.stringify(this.donations));
    }

    saveMatches() {
        localStorage.setItem(`matches_${window.dashboardManager.currentUser.email}`, JSON.stringify(this.matches));
    }

    setupEventListeners() {
        // Add any donor-specific event listeners here
        console.log('🎧 Donor event listeners setup');
    }

    // Donor-specific methods that can be called from dashboard-common.js
    showAddDonationForm() {
        console.log('🍎 Showing Add Donation Form');
        // Implementation will be added in Phase 2
        alert('Add Donation form coming in Phase 2!');
    }

    showDonationsList() {
        console.log('📋 Showing Donations List');
        // Implementation will be added in Phase 2
        alert('Donations list coming in Phase 2!');
    }

    showMatchesList() {
        console.log('🤝 Showing Matches List');
        // Implementation will be added in Phase 2
        alert('Matches list coming in Phase 2!');
    }

    showImpactReport() {
        console.log('📈 Showing Impact Report');
        // Implementation will be added in Phase 2
        alert('Impact report coming in Phase 2!');
    }
}

// Initialize donor dashboard
const donorDashboard = new DonorDashboard();

// Export for global access
window.donorDashboard = donorDashboard;
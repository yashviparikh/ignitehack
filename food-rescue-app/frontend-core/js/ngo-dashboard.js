// NGO Dashboard Specific JavaScript
// Extends dashboard-common.js with NGO-specific functionality

console.log('🤝 NGO Dashboard Script Loaded');

// NGO-specific functions and event handlers
class NGODashboard {
    constructor() {
        this.collections = [];
        this.deliveries = [];
        this.beneficiaries = [];
        
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
        console.log('🤝 Initializing NGO Dashboard...');
        
        // Load NGO-specific data
        this.loadCollections();
        this.loadDeliveries();
        this.loadBeneficiaries();
        
        // Setup NGO-specific event listeners
        this.setupEventListeners();
        
        console.log('✅ NGO Dashboard initialized');
    }

    loadCollections() {
        // Load collections from localStorage
        const storedCollections = localStorage.getItem(`collections_${window.dashboardManager.currentUser.email}`);
        this.collections = storedCollections ? JSON.parse(storedCollections) : [];
        
        // Add sample collections if none exist
        if (this.collections.length === 0) {
            this.collections = this.generateSampleCollections();
            this.saveCollections();
        }
    }

    loadDeliveries() {
        // Load deliveries from localStorage
        const storedDeliveries = localStorage.getItem(`deliveries_${window.dashboardManager.currentUser.email}`);
        this.deliveries = storedDeliveries ? JSON.parse(storedDeliveries) : [];
        
        // Add sample deliveries if none exist
        if (this.deliveries.length === 0) {
            this.deliveries = this.generateSampleDeliveries();
            this.saveDeliveries();
        }
    }

    loadBeneficiaries() {
        // Load beneficiaries from localStorage
        const storedBeneficiaries = localStorage.getItem(`beneficiaries_${window.dashboardManager.currentUser.email}`);
        this.beneficiaries = storedBeneficiaries ? JSON.parse(storedBeneficiaries) : [];
        
        // Add sample beneficiaries if none exist
        if (this.beneficiaries.length === 0) {
            this.beneficiaries = this.generateSampleBeneficiaries();
            this.saveBeneficiaries();
        }
    }

    generateSampleCollections() {
        return [
            {
                id: 1,
                donorName: 'Green Valley Restaurant',
                foodType: 'Mixed Vegetables',
                quantity: '15kg',
                status: 'Scheduled',
                pickupTime: new Date(Date.now() + 4 * 60 * 60 * 1000).toISOString(),
                location: 'Downtown Area',
                expiryDate: new Date(Date.now() + 2 * 24 * 60 * 60 * 1000).toISOString()
            },
            {
                id: 2,
                donorName: 'City Bakery',
                foodType: 'Bread & Pastries',
                quantity: '8kg',
                status: 'Collected',
                pickupTime: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
                location: 'Main Street',
                expiryDate: new Date(Date.now() + 1 * 24 * 60 * 60 * 1000).toISOString()
            },
            {
                id: 3,
                donorName: 'Fresh Market',
                foodType: 'Fruits',
                quantity: '12kg',
                status: 'Available',
                pickupTime: null,
                location: 'Market District',
                expiryDate: new Date(Date.now() + 3 * 24 * 60 * 60 * 1000).toISOString()
            }
        ];
    }

    generateSampleDeliveries() {
        return [
            {
                id: 1,
                collectionId: 2,
                deliveryLocation: 'Community Center A',
                beneficiariesCount: 45,
                status: 'In Progress',
                scheduledTime: new Date(Date.now() + 2 * 60 * 60 * 1000).toISOString(),
                foodItems: ['Bread', 'Pastries']
            },
            {
                id: 2,
                collectionId: 1,
                deliveryLocation: 'Homeless Shelter',
                beneficiariesCount: 32,
                status: 'Completed',
                scheduledTime: new Date(Date.now() - 6 * 60 * 60 * 1000).toISOString(),
                foodItems: ['Vegetables', 'Canned Goods']
            }
        ];
    }

    generateSampleBeneficiaries() {
        return [
            { id: 1, name: 'Johnson Family', size: 4, location: 'District A', needsType: 'Regular', lastServed: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000).toISOString() },
            { id: 2, name: 'Maria Santos', size: 2, location: 'District B', needsType: 'Senior', lastServed: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString() },
            { id: 3, name: 'Community Center A', size: 50, location: 'Downtown', needsType: 'Institution', lastServed: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString() }
        ];
    }

    saveCollections() {
        localStorage.setItem(`collections_${window.dashboardManager.currentUser.email}`, JSON.stringify(this.collections));
    }

    saveDeliveries() {
        localStorage.setItem(`deliveries_${window.dashboardManager.currentUser.email}`, JSON.stringify(this.deliveries));
    }

    saveBeneficiaries() {
        localStorage.setItem(`beneficiaries_${window.dashboardManager.currentUser.email}`, JSON.stringify(this.beneficiaries));
    }

    setupEventListeners() {
        // Add any NGO-specific event listeners here
        console.log('🎧 NGO event listeners setup');
    }

    // NGO-specific methods that can be called from dashboard-common.js
    showFindFoodInterface() {
        console.log('🔍 Showing Find Food Interface');
        // Implementation will be added in Phase 2
        alert('Find Food interface coming in Phase 2!');
    }

    showCollectionsManager() {
        console.log('📋 Showing Collections Manager');
        // Implementation will be added in Phase 2
        alert('Collections manager coming in Phase 2!');
    }

    showDeliveryTracker() {
        console.log('🚚 Showing Delivery Tracker');
        // Implementation will be added in Phase 2
        alert('Delivery tracker coming in Phase 2!');
    }

    showBeneficiariesManager() {
        console.log('👥 Showing Beneficiaries Manager');
        // Implementation will be added in Phase 2
        alert('Beneficiaries manager coming in Phase 2!');
    }

    showReportsInterface() {
        console.log('📈 Showing Reports Interface');
        // Implementation will be added in Phase 2
        alert('Reports interface coming in Phase 2!');
    }
}

// Initialize NGO dashboard
const ngoDashboard = new NGODashboard();

// Export for global access
window.ngoDashboard = ngoDashboard;
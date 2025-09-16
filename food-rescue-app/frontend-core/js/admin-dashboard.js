// Admin Dashboard Specific JavaScript
// Extends dashboard-common.js with admin-specific functionality

console.log('⚙️ Admin Dashboard Script Loaded');

// Admin-specific functions and event handlers
class AdminDashboard {
    constructor() {
        this.users = [];
        this.systemMetrics = {};
        this.pendingVerifications = [];
        
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
        console.log('⚙️ Initializing Admin Dashboard...');
        
        // Load admin-specific data
        this.loadUsers();
        this.loadSystemMetrics();
        this.loadPendingVerifications();
        
        // Setup admin-specific event listeners
        this.setupEventListeners();
        
        console.log('✅ Admin Dashboard initialized');
    }

    loadUsers() {
        // Load users from localStorage
        const storedUsers = localStorage.getItem('platform_users');
        this.users = storedUsers ? JSON.parse(storedUsers) : [];
        
        // Add sample users if none exist
        if (this.users.length === 0) {
            this.users = this.generateSampleUsers();
            this.saveUsers();
        }
    }

    loadSystemMetrics() {
        // Load system metrics from localStorage
        const storedMetrics = localStorage.getItem('system_metrics');
        this.systemMetrics = storedMetrics ? JSON.parse(storedMetrics) : this.generateSampleMetrics();
        
        if (!storedMetrics) {
            this.saveSystemMetrics();
        }
    }

    loadPendingVerifications() {
        // Load pending verifications from localStorage
        const storedVerifications = localStorage.getItem('pending_verifications');
        this.pendingVerifications = storedVerifications ? JSON.parse(storedVerifications) : [];
        
        // Add sample verifications if none exist
        if (this.pendingVerifications.length === 0) {
            this.pendingVerifications = this.generateSampleVerifications();
            this.savePendingVerifications();
        }
    }

    generateSampleUsers() {
        return [
            {
                id: 1,
                name: 'John Doe',
                email: 'john@restaurant.com',
                role: 'donor',
                status: 'active',
                verified: true,
                joinDate: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString(),
                lastActive: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
                donationsCount: 12
            },
            {
                id: 2,
                name: 'Hope Kitchen NGO',
                email: 'contact@hopekitchen.org',
                role: 'ngo',
                status: 'active',
                verified: true,
                joinDate: new Date(Date.now() - 60 * 24 * 60 * 60 * 1000).toISOString(),
                lastActive: new Date(Date.now() - 30 * 60 * 1000).toISOString(),
                collectionsCount: 45
            },
            {
                id: 3,
                name: 'City Bakery',
                email: 'manager@citybakery.com',
                role: 'donor',
                status: 'active',
                verified: true,
                joinDate: new Date(Date.now() - 15 * 24 * 60 * 60 * 1000).toISOString(),
                lastActive: new Date(Date.now() - 6 * 60 * 60 * 1000).toISOString(),
                donationsCount: 8
            },
            {
                id: 4,
                name: 'Community Care Center',
                email: 'info@communitycare.org',
                role: 'ngo',
                status: 'pending',
                verified: false,
                joinDate: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(),
                lastActive: new Date(Date.now() - 12 * 60 * 60 * 1000).toISOString(),
                collectionsCount: 0
            }
        ];
    }

    generateSampleMetrics() {
        return {
            totalUsers: 1247,
            activeUsers: 892,
            totalDonations: 2456,
            activeDonations: 67,
            totalMatches: 1234,
            successRate: 89.2,
            platformUptime: 99.2,
            avgResponseTime: 120,
            foodRescued: 15674, // kg
            peopleHelped: 8934,
            co2Saved: 2344 // kg
        };
    }

    generateSampleVerifications() {
        return [
            {
                id: 1,
                organizationName: 'New Hope Food Bank',
                email: 'admin@newhopefoodbank.org',
                submittedAt: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(),
                documents: ['registration.pdf', 'tax_exemption.pdf'],
                status: 'pending'
            },
            {
                id: 2,
                organizationName: 'Feeding Families Foundation',
                email: 'contact@feedingfamilies.org',
                submittedAt: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString(),
                documents: ['501c3.pdf', 'board_resolution.pdf'],
                status: 'pending'
            },
            {
                id: 3,
                organizationName: 'Local Shelter Network',
                email: 'info@localshelter.org',
                submittedAt: new Date(Date.now() - 3 * 60 * 60 * 1000).toISOString(),
                documents: ['license.pdf', 'insurance.pdf'],
                status: 'pending'
            }
        ];
    }

    saveUsers() {
        localStorage.setItem('platform_users', JSON.stringify(this.users));
    }

    saveSystemMetrics() {
        localStorage.setItem('system_metrics', JSON.stringify(this.systemMetrics));
    }

    savePendingVerifications() {
        localStorage.setItem('pending_verifications', JSON.stringify(this.pendingVerifications));
    }

    setupEventListeners() {
        // Add any admin-specific event listeners here
        console.log('🎧 Admin event listeners setup');
    }

    // Admin-specific methods that can be called from dashboard-common.js
    showUserManagement() {
        console.log('👥 Showing User Management');
        // Implementation will be added in Phase 2
        alert('User management interface coming in Phase 2!');
    }

    showDonationManagement() {
        console.log('🍎 Showing Donation Management');
        // Implementation will be added in Phase 2
        alert('Donation management interface coming in Phase 2!');
    }

    showSystemAnalytics() {
        console.log('📈 Showing System Analytics');
        // Implementation will be added in Phase 2
        alert('System analytics interface coming in Phase 2!');
    }

    showSystemSettings() {
        console.log('⚙️ Showing System Settings');
        // Implementation will be added in Phase 2
        alert('System settings interface coming in Phase 2!');
    }

    showVerificationQueue() {
        console.log('✅ Showing Verification Queue');
        // Implementation will be added in Phase 2
        alert(`Verification queue with ${this.pendingVerifications.length} pending verifications coming in Phase 2!`);
    }

    generateSystemReport() {
        console.log('📊 Generating System Report');
        // Implementation will be added in Phase 2
        alert('System report generation coming in Phase 2!');
    }

    // Admin utility methods
    verifyUser(userId) {
        const user = this.users.find(u => u.id === userId);
        if (user) {
            user.verified = true;
            user.status = 'active';
            this.saveUsers();
            console.log('✅ User verified:', user.email);
        }
    }

    suspendUser(userId) {
        const user = this.users.find(u => u.id === userId);
        if (user) {
            user.status = 'suspended';
            this.saveUsers();
            console.log('⚠️ User suspended:', user.email);
        }
    }

    updateSystemMetrics() {
        // Update system metrics with real-time data
        this.systemMetrics.lastUpdated = new Date().toISOString();
        this.saveSystemMetrics();
    }
}

// Initialize admin dashboard
const adminDashboard = new AdminDashboard();

// Export for global access
window.adminDashboard = adminDashboard;
// Dashboard Common JavaScript - Food Rescue Matchmaker
// Handles authentication, navigation, storage, and common dashboard functionality

class DashboardManager {
    constructor() {
        this.currentUser = null;
        this.currentRole = null;
        this.notifications = [];
        this.isInitialized = false;
        
        // DOM elements
        this.elements = {};
        
        // Event listeners
        this.eventListeners = [];
        
        // Initialize when DOM is loaded
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.init());
        } else {
            this.init();
        }
    }

    // Initialize dashboard
    async init() {
        try {
            console.log('🚀 Initializing Dashboard Manager...');
            
            // Check authentication
            if (!this.checkAuthentication()) {
                this.redirectToLogin();
                return;
            }
            
            // Cache DOM elements
            this.cacheElements();
            
            // Setup event listeners
            this.setupEventListeners();
            
            // Load user data
            await this.loadUserData();
            
            // Setup role-specific content
            this.setupRoleSpecificContent();
            
            // Load notifications
            await this.loadNotifications();
            
            // Update UI
            this.updateUI();
            
            this.isInitialized = true;
            console.log('✅ Dashboard Manager initialized successfully');
            
        } catch (error) {
            console.error('❌ Error initializing dashboard:', error);
            this.showError('Failed to initialize dashboard. Please refresh the page.');
        }
    }

    // Check if user is authenticated
    checkAuthentication() {
        const user = localStorage.getItem('currentUser');
        const role = localStorage.getItem('selectedRole');
        
        if (!user || !role) {
            console.log('❌ No authentication found');
            return false;
        }
        
        try {
            this.currentUser = JSON.parse(user);
            this.currentRole = role;
            console.log('✅ Authentication verified:', { user: this.currentUser.email, role: this.currentRole });
            return true;
        } catch (error) {
            console.error('❌ Invalid user data in localStorage:', error);
            return false;
        }
    }

    // Cache DOM elements
    cacheElements() {
        this.elements = {
            // Header elements
            profileName: document.getElementById('profile-name'),
            profileFullName: document.getElementById('profile-full-name'),
            profileEmail: document.getElementById('profile-email'),
            profileRole: document.getElementById('profile-role'),
            profileBtn: document.getElementById('profile-btn'),
            profileDropdown: document.getElementById('profile-dropdown'),
            
            // Notification elements
            notificationBtn: document.getElementById('notification-btn'),
            notificationBadge: document.getElementById('notification-badge'),
            notificationDropdown: document.getElementById('notification-dropdown'),
            notificationList: document.getElementById('notification-list'),
            
            // Sidebar elements
            sidebar: document.getElementById('dashboard-sidebar'),
            sidebarNav: document.getElementById('sidebar-nav'),
            quickActions: document.getElementById('quick-actions'),
            recentActivity: document.getElementById('recent-activity'),
            
            // Main content elements
            pageTitle: document.getElementById('page-title'),
            pageActions: document.getElementById('page-actions'),
            breadcrumb: document.getElementById('breadcrumb'),
            overviewGrid: document.getElementById('overview-grid'),
            dynamicContent: document.getElementById('dynamic-content'),
            
            // Mobile elements
            mobileMenuToggle: document.getElementById('mobile-menu-toggle'),
            overlay: document.getElementById('overlay'),
            
            // Loading
            loadingSpinner: document.getElementById('loading-spinner'),
            
            // Search
            dashboardSearch: document.getElementById('dashboard-search')
        };
    }

    // Setup event listeners
    setupEventListeners() {
        // Profile dropdown toggle
        if (this.elements.profileBtn) {
            this.elements.profileBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                this.toggleProfileDropdown();
            });
        }

        // Notification dropdown toggle
        if (this.elements.notificationBtn) {
            this.elements.notificationBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                this.toggleNotificationDropdown();
            });
        }

        // Mobile menu toggle
        if (this.elements.mobileMenuToggle) {
            this.elements.mobileMenuToggle.addEventListener('click', () => {
                this.toggleMobileSidebar();
            });
        }

        // Overlay click
        if (this.elements.overlay) {
            this.elements.overlay.addEventListener('click', () => {
                this.closeMobileSidebar();
                this.closeAllDropdowns();
            });
        }

        // Search functionality
        if (this.elements.dashboardSearch) {
            this.elements.dashboardSearch.addEventListener('input', (e) => {
                this.handleSearch(e.target.value);
            });
        }

        // Close dropdowns when clicking outside
        document.addEventListener('click', () => {
            this.closeAllDropdowns();
        });

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            this.handleKeyboardShortcuts(e);
        });

        // Window resize
        window.addEventListener('resize', () => {
            this.handleResize();
        });
    }

    // Load user data
    async loadUserData() {
        try {
            // Get user data from localStorage
            const userData = localStorage.getItem('userData');
            if (userData) {
                const parsedData = JSON.parse(userData);
                this.currentUser = { ...this.currentUser, ...parsedData };
            }
            
            // Update profile display
            this.updateProfileDisplay();
            
        } catch (error) {
            console.error('❌ Error loading user data:', error);
        }
    }

    // Update profile display
    updateProfileDisplay() {
        if (this.elements.profileName) {
            this.elements.profileName.textContent = this.currentUser.name || this.currentUser.email.split('@')[0];
        }
        
        if (this.elements.profileFullName) {
            this.elements.profileFullName.textContent = this.currentUser.name || 'User Name';
        }
        
        if (this.elements.profileEmail) {
            this.elements.profileEmail.textContent = this.currentUser.email;
        }
        
        if (this.elements.profileRole) {
            this.elements.profileRole.textContent = this.currentRole.toUpperCase();
        }
    }

    // Setup role-specific content
    setupRoleSpecificContent() {
        // Update page title based on role
        const roleTitles = {
            'donor': 'Donor Dashboard',
            'ngo': 'NGO Dashboard',
            'admin': 'Admin Dashboard'
        };
        
        if (this.elements.pageTitle) {
            this.elements.pageTitle.textContent = roleTitles[this.currentRole] || 'Dashboard';
        }
        
        // Setup role-specific navigation
        this.setupNavigation();
        
        // Setup role-specific quick actions
        this.setupQuickActions();
    }

    // Setup navigation based on role
    setupNavigation() {
        const navigationItems = {
            'donor': [
                { icon: '📊', text: 'Dashboard', href: '#dashboard', active: true },
                { icon: '🍎', text: 'My Donations', href: '#donations' },
                { icon: '➕', text: 'Add Donation', href: '#add-donation' },
                { icon: '🤝', text: 'Matches', href: '#matches' },
                { icon: '📈', text: 'Impact Report', href: '#impact' },
                { icon: '⚙️', text: 'Settings', href: '#settings' }
            ],
            'ngo': [
                { icon: '📊', text: 'Dashboard', href: '#dashboard', active: true },
                { icon: '🔍', text: 'Find Food', href: '#find-food' },
                { icon: '📋', text: 'My Collections', href: '#collections' },
                { icon: '🚚', text: 'Deliveries', href: '#deliveries' },
                { icon: '👥', text: 'Beneficiaries', href: '#beneficiaries' },
                { icon: '📈', text: 'Reports', href: '#reports' },
                { icon: '⚙️', text: 'Settings', href: '#settings' }
            ],
            'admin': [
                { icon: '📊', text: 'System Overview', href: '#dashboard', active: true },
                { icon: '👥', text: 'User Management', href: '#users' },
                { icon: '🍎', text: 'Donations Management', href: '#donations' },
                { icon: '🏢', text: 'NGO Management', href: '#ngos' },
                { icon: '📈', text: 'Analytics', href: '#analytics' },
                { icon: '⚙️', text: 'System Settings', href: '#settings' }
            ]
        };
        
        const items = navigationItems[this.currentRole] || [];
        
        if (this.elements.sidebarNav) {
            this.elements.sidebarNav.innerHTML = items.map(item => `
                <a href="${item.href}" class="nav-item ${item.active ? 'active' : ''}" onclick="dashboardManager.navigate('${item.href}')">
                    <span class="nav-icon">${item.icon}</span>
                    <span class="nav-text">${item.text}</span>
                </a>
            `).join('');
        }
    }

    // Setup quick actions based on role
    setupQuickActions() {
        const quickActions = {
            'donor': [
                { icon: '➕', text: 'Add Donation', action: 'showAddDonation', class: 'btn-primary' },
                { icon: '🔍', text: 'View Matches', action: 'showMatches', class: 'btn-secondary' }
            ],
            'ngo': [
                { icon: '🔍', text: 'Find Food', action: 'showFindFood', class: 'btn-primary' },
                { icon: '📋', text: 'Schedule Pickup', action: 'showSchedulePickup', class: 'btn-secondary' }
            ],
            'admin': [
                { icon: '👤', text: 'Verify Users', action: 'showUserVerification', class: 'btn-warning' },
                { icon: '📊', text: 'Generate Report', action: 'showReports', class: 'btn-info' }
            ]
        };
        
        const actions = quickActions[this.currentRole] || [];
        
        if (this.elements.quickActions) {
            this.elements.quickActions.innerHTML = actions.map(action => `
                <button class="btn ${action.class} btn-sm" onclick="dashboardManager.${action.action}()">
                    ${action.icon} ${action.text}
                </button>
            `).join('');
        }
    }

    // Load notifications
    async loadNotifications() {
        try {
            // Get notifications from localStorage
            const storedNotifications = localStorage.getItem(`notifications_${this.currentUser.email}`);
            this.notifications = storedNotifications ? JSON.parse(storedNotifications) : [];
            
            // Add some sample notifications if none exist
            if (this.notifications.length === 0) {
                this.notifications = this.generateSampleNotifications();
                this.saveNotifications();
            }
            
            this.updateNotificationDisplay();
            
        } catch (error) {
            console.error('❌ Error loading notifications:', error);
        }
    }

    // Generate sample notifications based on role
    generateSampleNotifications() {
        const notifications = {
            'donor': [
                { id: 1, type: 'match', title: 'New Match Found!', message: 'Your food donation has been matched with Hope Kitchen NGO', time: new Date().toISOString(), read: false },
                { id: 2, type: 'pickup', title: 'Pickup Scheduled', message: 'Pickup scheduled for tomorrow at 2:00 PM', time: new Date(Date.now() - 3600000).toISOString(), read: false },
                { id: 3, type: 'impact', title: 'Impact Update', message: 'Your donations helped feed 45 people this week!', time: new Date(Date.now() - 7200000).toISOString(), read: true }
            ],
            'ngo': [
                { id: 1, type: 'donation', title: 'New Donation Available', message: 'Fresh vegetables available for pickup at Green Grocery', time: new Date().toISOString(), read: false },
                { id: 2, type: 'reminder', title: 'Pickup Reminder', message: 'Pickup scheduled in 30 minutes', time: new Date(Date.now() - 1800000).toISOString(), read: false },
                { id: 3, type: 'delivery', title: 'Delivery Completed', message: 'Successfully delivered food to Community Center', time: new Date(Date.now() - 5400000).toISOString(), read: true }
            ],
            'admin': [
                { id: 1, type: 'verification', title: 'Pending Verifications', message: '5 new NGO accounts need verification', time: new Date().toISOString(), read: false },
                { id: 2, type: 'system', title: 'System Alert', message: 'High platform activity detected', time: new Date(Date.now() - 2700000).toISOString(), read: false },
                { id: 3, type: 'report', title: 'Weekly Report Ready', message: 'Your weekly analytics report is ready to view', time: new Date(Date.now() - 9000000).toISOString(), read: true }
            ]
        };
        
        return notifications[this.currentRole] || [];
    }

    // Update notification display
    updateNotificationDisplay() {
        const unreadCount = this.notifications.filter(n => !n.read).length;
        
        if (this.elements.notificationBadge) {
            this.elements.notificationBadge.textContent = unreadCount;
            this.elements.notificationBadge.style.display = unreadCount > 0 ? 'block' : 'none';
        }
        
        if (this.elements.notificationList) {
            this.elements.notificationList.innerHTML = this.notifications.length > 0 
                ? this.notifications.slice(0, 10).map(notification => `
                    <div class="notification-item ${notification.read ? 'read' : 'unread'}" onclick="dashboardManager.markNotificationRead(${notification.id})">
                        <div class="notification-content">
                            <h4>${notification.title}</h4>
                            <p>${notification.message}</p>
                            <span class="notification-time">${this.formatTimeAgo(notification.time)}</span>
                        </div>
                        ${!notification.read ? '<div class="notification-dot"></div>' : ''}
                    </div>
                `).join('')
                : '<div class="notification-empty">No notifications</div>';
        }
    }

    // Save notifications to localStorage
    saveNotifications() {
        localStorage.setItem(`notifications_${this.currentUser.email}`, JSON.stringify(this.notifications));
    }

    // Mark notification as read
    markNotificationRead(notificationId) {
        const notification = this.notifications.find(n => n.id === notificationId);
        if (notification && !notification.read) {
            notification.read = true;
            this.saveNotifications();
            this.updateNotificationDisplay();
        }
    }

    // Format time ago
    formatTimeAgo(timeString) {
        const now = new Date();
        const time = new Date(timeString);
        const diffInSeconds = Math.floor((now - time) / 1000);
        
        if (diffInSeconds < 60) return 'Just now';
        if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}m ago`;
        if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)}h ago`;
        return `${Math.floor(diffInSeconds / 86400)}d ago`;
    }

    // Navigation methods
    navigate(href) {
        console.log('🧭 Navigating to:', href);
        
        // Update active navigation
        document.querySelectorAll('.nav-item').forEach(item => {
            item.classList.remove('active');
        });
        
        document.querySelector(`[href="${href}"]`)?.classList.add('active');
        
        // Update breadcrumb
        this.updateBreadcrumb(href);
        
        // Load content based on route
        this.loadContent(href);
    }

    // Update breadcrumb
    updateBreadcrumb(href) {
        const breadcrumbMap = {
            '#dashboard': 'Dashboard',
            '#donations': 'Donations',
            '#add-donation': 'Add Donation',
            '#matches': 'Matches',
            '#impact': 'Impact Report',
            '#find-food': 'Find Food',
            '#collections': 'Collections',
            '#deliveries': 'Deliveries',
            '#beneficiaries': 'Beneficiaries',
            '#reports': 'Reports',
            '#users': 'User Management',
            '#ngos': 'NGO Management',
            '#analytics': 'Analytics',
            '#settings': 'Settings'
        };
        
        if (this.elements.breadcrumb) {
            this.elements.breadcrumb.innerHTML = `
                <span class="breadcrumb-item">Dashboard</span>
                ${href !== '#dashboard' ? `<span class="breadcrumb-item active">${breadcrumbMap[href] || 'Page'}</span>` : ''}
            `;
        }
    }

    // Load content
    loadContent(href) {
        if (this.elements.dynamicContent) {
            // Show loading
            this.showLoading();
            
            // Simulate content loading
            setTimeout(() => {
                this.elements.dynamicContent.innerHTML = `
                    <div class="content-section">
                        <div class="section-header">
                            <h2>${href.replace('#', '').replace('-', ' ').toUpperCase()}</h2>
                        </div>
                        <div class="section-content" style="padding: 30px;">
                            <p>Content for ${href} will be loaded here.</p>
                            <p>This is a placeholder that will be replaced with actual functionality.</p>
                        </div>
                    </div>
                `;
                
                this.hideLoading();
            }, 500);
        }
    }

    // UI update methods
    updateUI() {
        // Update overview cards
        this.updateOverviewCards();
        
        // Update recent activity
        this.updateRecentActivity();
    }

    // Update overview cards
    updateOverviewCards() {
        const overviewData = this.getOverviewData();
        
        if (this.elements.overviewGrid) {
            this.elements.overviewGrid.innerHTML = overviewData.map(card => `
                <div class="dashboard-card">
                    <div class="card-header">
                        <h3 class="card-title">${card.title}</h3>
                        <div class="card-icon">${card.icon}</div>
                    </div>
                    <div class="card-value">${card.value}</div>
                    <div class="card-change ${card.change.type}">
                        ${card.change.text}
                    </div>
                </div>
            `).join('');
        }
    }

    // Get overview data based on role
    getOverviewData() {
        const overviewData = {
            'donor': [
                { title: 'Total Donations', value: '12', icon: '🍎', change: { type: 'positive', text: '+2 this week' } },
                { title: 'Active Matches', value: '3', icon: '🤝', change: { type: 'neutral', text: 'Awaiting pickup' } },
                { title: 'People Fed', value: '156', icon: '👥', change: { type: 'positive', text: '+28 this month' } },
                { title: 'CO2 Saved', value: '47kg', icon: '🌱', change: { type: 'positive', text: 'Environmental impact' } }
            ],
            'ngo': [
                { title: 'Food Collected', value: '89kg', icon: '📦', change: { type: 'positive', text: '+15kg this week' } },
                { title: 'Active Pickups', value: '5', icon: '🚚', change: { type: 'neutral', text: 'Scheduled today' } },
                { title: 'Beneficiaries', value: '234', icon: '👥', change: { type: 'positive', text: '+12 new families' } },
                { title: 'Distributions', value: '18', icon: '🎯', change: { type: 'positive', text: 'This month' } }
            ],
            'admin': [
                { title: 'Total Users', value: '1,247', icon: '👥', change: { type: 'positive', text: '+34 this week' } },
                { title: 'Active Donations', value: '67', icon: '🍎', change: { type: 'positive', text: '+12 today' } },
                { title: 'Platform Matches', value: '456', icon: '🤝', change: { type: 'positive', text: '89% success rate' } },
                { title: 'System Health', value: '99.2%', icon: '💚', change: { type: 'positive', text: 'All systems operational' } }
            ]
        };
        
        return overviewData[this.currentRole] || [];
    }

    // Update recent activity
    updateRecentActivity() {
        const activityData = this.getRecentActivityData();
        
        if (this.elements.recentActivity) {
            this.elements.recentActivity.innerHTML = activityData.length > 0 
                ? activityData.map(activity => `
                    <div class="activity-item">
                        <div class="activity-text">${activity.text}</div>
                        <div class="activity-time">${activity.time}</div>
                    </div>
                `).join('')
                : '<div class="activity-item">No recent activity</div>';
        }
    }

    // Get recent activity data
    getRecentActivityData() {
        const activityData = {
            'donor': [
                { text: 'New match found', time: '2m ago' },
                { text: 'Donation picked up', time: '1h ago' },
                { text: 'Impact report ready', time: '3h ago' }
            ],
            'ngo': [
                { text: 'Food collected', time: '15m ago' },
                { text: 'New donation available', time: '45m ago' },
                { text: 'Delivery completed', time: '2h ago' }
            ],
            'admin': [
                { text: 'New NGO verified', time: '10m ago' },
                { text: 'System backup completed', time: '30m ago' },
                { text: 'Weekly report generated', time: '1h ago' }
            ]
        };
        
        return activityData[this.currentRole] || [];
    }

    // Dropdown methods
    toggleProfileDropdown() {
        this.closeNotificationDropdown();
        this.elements.profileDropdown?.classList.toggle('active');
    }

    toggleNotificationDropdown() {
        this.closeProfileDropdown();
        this.elements.notificationDropdown?.classList.toggle('active');
    }

    closeProfileDropdown() {
        this.elements.profileDropdown?.classList.remove('active');
    }

    closeNotificationDropdown() {
        this.elements.notificationDropdown?.classList.remove('active');
    }

    closeAllDropdowns() {
        this.closeProfileDropdown();
        this.closeNotificationDropdown();
    }

    // Mobile sidebar methods
    toggleMobileSidebar() {
        this.elements.sidebar?.classList.toggle('active');
        this.elements.overlay?.classList.toggle('active');
    }

    closeMobileSidebar() {
        this.elements.sidebar?.classList.remove('active');
        this.elements.overlay?.classList.remove('active');
    }

    // Loading methods
    showLoading() {
        this.elements.loadingSpinner?.classList.add('active');
    }

    hideLoading() {
        this.elements.loadingSpinner?.classList.remove('active');
    }

    // Search handling
    handleSearch(query) {
        console.log('🔍 Searching for:', query);
        // Implement search functionality here
    }

    // Keyboard shortcuts
    handleKeyboardShortcuts(e) {
        // Ctrl/Cmd + K for search
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            this.elements.dashboardSearch?.focus();
        }
        
        // Escape to close dropdowns
        if (e.key === 'Escape') {
            this.closeAllDropdowns();
            this.closeMobileSidebar();
        }
    }

    // Window resize handling
    handleResize() {
        // Close mobile sidebar on desktop
        if (window.innerWidth > 768) {
            this.closeMobileSidebar();
        }
    }

    // Quick action methods (to be implemented by role-specific scripts)
    showAddDonation() {
        console.log('🍎 Show Add Donation');
        this.navigate('#add-donation');
    }

    showMatches() {
        console.log('🤝 Show Matches');
        this.navigate('#matches');
    }

    showFindFood() {
        console.log('🔍 Show Find Food');
        this.navigate('#find-food');
    }

    showSchedulePickup() {
        console.log('📋 Show Schedule Pickup');
        this.navigate('#collections');
    }

    showUserVerification() {
        console.log('👤 Show User Verification');
        this.navigate('#users');
    }

    showReports() {
        console.log('📊 Show Reports');
        this.navigate('#analytics');
    }

    // Utility methods
    showError(message) {
        console.error('❌ Error:', message);
        // Implement error display
        alert(message); // Temporary - replace with proper error UI
    }

    showSuccess(message) {
        console.log('✅ Success:', message);
        // Implement success display
    }

    // Logout method
    logout() {
        console.log('🚪 Logging out...');
        
        // Clear localStorage
        localStorage.removeItem('currentUser');
        localStorage.removeItem('selectedRole');
        localStorage.removeItem('userData');
        
        // Redirect to landing page
        window.location.href = '../index.html';
    }

    // Redirect to login
    redirectToLogin() {
        console.log('🔒 Redirecting to login...');
        window.location.href = '../index.html';
    }
}

// Profile management functions (called from HTML)
function showProfile() {
    console.log('👤 Show Profile');
    dashboardManager.navigate('#profile');
}

function showSettings() {
    console.log('⚙️ Show Settings');
    dashboardManager.navigate('#settings');
}

function showHelp() {
    console.log('❓ Show Help');
    // Implement help functionality
    alert('Help & Support coming soon!');
}

function showPrivacy() {
    console.log('🛡️ Show Privacy');
    // Implement privacy policy
    alert('Privacy Policy coming soon!');
}

function showTerms() {
    console.log('📄 Show Terms');
    // Implement terms of service
    alert('Terms of Service coming soon!');
}

function logout() {
    if (window.dashboardManager) {
        dashboardManager.logout();
    }
}

function refreshOverview() {
    console.log('🔄 Refreshing Overview');
    if (window.dashboardManager) {
        dashboardManager.updateUI();
        dashboardManager.showSuccess('Overview refreshed!');
    }
}

// Initialize dashboard manager
const dashboardManager = new DashboardManager();

// Export for global access
window.dashboardManager = dashboardManager;
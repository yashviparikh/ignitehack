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
        const now = new Date();
        return [
            {
                id: 'donation_' + (now.getTime() - 86400000), // 1 day ago
                foodType: 'fresh-produce',
                description: 'Fresh vegetables from restaurant prep - carrots, lettuce, tomatoes, and bell peppers',
                quantity: 15,
                quantityUnit: 'kg',
                expiryDate: new Date(now.getTime() + 2 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
                pickupAddress: '123 Main Street, Downtown Restaurant, City Center',
                pickupDate: new Date(now.getTime() + 24 * 60 * 60 * 1000).toISOString().split('T')[0],
                pickupTime: '10:00',
                pickupWindow: '60',
                contactPerson: 'Chef Maria',
                contactPhone: '+1-555-0123',
                specialInstructions: 'Please bring refrigerated truck. Access through back door.',
                isUrgent: false,
                isRecurring: true,
                status: 'posted',
                datePosted: new Date(now.getTime() - 3 * 60 * 60 * 1000).toISOString(),
                photos: []
            },
            {
                id: 'donation_' + (now.getTime() - 172800000), // 2 days ago
                foodType: 'bakery',
                description: 'Unsold bread, pastries, and sandwiches from bakery',
                quantity: 25,
                quantityUnit: 'pieces',
                expiryDate: new Date(now.getTime() + 1 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
                pickupAddress: '456 Baker Street, Golden Crust Bakery',
                pickupDate: new Date(now.getTime() + 12 * 60 * 60 * 1000).toISOString().split('T')[0],
                pickupTime: '15:30',
                pickupWindow: '30',
                contactPerson: 'John Baker',
                contactPhone: '+1-555-0456',
                specialInstructions: 'Items are already boxed and ready for pickup.',
                isUrgent: true,
                isRecurring: false,
                status: 'matched',
                datePosted: new Date(now.getTime() - 6 * 60 * 60 * 1000).toISOString(),
                photos: []
            },
            {
                id: 'donation_' + (now.getTime() - 259200000), // 3 days ago
                foodType: 'prepared-meals',
                description: 'Surplus prepared meals from conference catering',
                quantity: 50,
                quantityUnit: 'portions',
                expiryDate: new Date(now.getTime() + 1 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
                pickupAddress: '789 Conference Center, Business District',
                pickupDate: new Date(now.getTime() + 6 * 60 * 60 * 1000).toISOString().split('T')[0],
                pickupTime: '18:00',
                pickupWindow: '120',
                contactPerson: 'Sarah Event Manager',
                contactPhone: '+1-555-0789',
                specialInstructions: 'Meals are hot and ready. Please bring insulated containers.',
                isUrgent: true,
                isRecurring: false,
                status: 'picked-up',
                datePosted: new Date(now.getTime() - 12 * 60 * 60 * 1000).toISOString(),
                photos: []
            },
            {
                id: 'donation_' + (now.getTime() - 432000000), // 5 days ago
                foodType: 'dairy',
                description: 'Dairy products nearing expiry from grocery store',
                quantity: 10,
                quantityUnit: 'packages',
                expiryDate: new Date(now.getTime() + 3 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
                pickupAddress: '321 Grocery Lane, FreshMart Supermarket',
                pickupDate: new Date(now.getTime() - 24 * 60 * 60 * 1000).toISOString().split('T')[0],
                pickupTime: '09:00',
                pickupWindow: '60',
                contactPerson: 'Mike Store Manager',
                contactPhone: '+1-555-0321',
                specialInstructions: 'Products are refrigerated and well-organized.',
                isUrgent: false,
                isRecurring: true,
                status: 'delivered',
                datePosted: new Date(now.getTime() - 5 * 24 * 60 * 60 * 1000).toISOString(),
                photos: []
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
        
        // Populate sidebar navigation
        this.populateSidebarNavigation();
        
        // Populate quick actions
        this.populateQuickActions();
        
        // Populate recent activity
        this.populateRecentActivity();
    }

    populateSidebarNavigation() {
        const sidebarNav = document.getElementById('sidebar-nav');
        if (!sidebarNav) return;

        const navItems = [
            { icon: '🏠', label: 'Dashboard', action: 'showDashboard', active: true },
            { icon: '📤', label: 'My Donations', action: 'showDonationsList' },
            { icon: '🤝', label: 'Matches', action: 'showMatches' },
            { icon: '📊', label: 'Impact Report', action: 'showImpactReport' },
            { icon: '📋', label: 'History', action: 'showDonationHistory' },
            { icon: '⚙️', label: 'Settings', action: 'showSettings' }
        ];

        sidebarNav.innerHTML = navItems.map(item => `
            <a href="#" class="nav-item ${item.active ? 'active' : ''}" onclick="donorDashboard.${item.action}()">
                <span class="nav-icon">${item.icon}</span>
                <span class="nav-label">${item.label}</span>
            </a>
        `).join('');
    }

    populateQuickActions() {
        const quickActions = document.getElementById('quick-actions');
        if (!quickActions) return;

        const actions = [
            { 
                icon: '➕', 
                label: 'Post New Donation', 
                action: 'openDonationModal()',
                style: 'background: linear-gradient(135deg, #27ae60, #2ecc71);'
            },
            { 
                icon: '👀', 
                label: 'View Active Donations', 
                action: 'donorDashboard.showActiveDonations()',
                style: 'background: linear-gradient(135deg, #3498db, #2980b9);'
            },
            { 
                icon: '📋', 
                label: 'Donation History', 
                action: 'donorDashboard.showDonationHistory()',
                style: 'background: linear-gradient(135deg, #9b59b6, #8e44ad);'
            },
            { 
                icon: '🚨', 
                label: 'Emergency Alert', 
                action: 'donorDashboard.createEmergencyDonation()',
                style: 'background: linear-gradient(135deg, #e74c3c, #c0392b);'
            }
        ];

        quickActions.innerHTML = actions.map(action => `
            <button class="quick-action-btn" onclick="${action.action}" style="${action.style}">
                <span class="action-icon">${action.icon}</span>
                <span class="action-label">${action.label}</span>
            </button>
        `).join('');
    }

    populateRecentActivity() {
        const recentActivity = document.getElementById('recent-activity');
        if (!recentActivity) return;

        // Get recent donations and matches
        const recentDonations = this.donations.slice(0, 3);
        const recentMatches = this.matches.slice(0, 2);
        
        let activityHTML = '';
        
        // Add recent donations
        recentDonations.forEach(donation => {
            const timeAgo = this.getTimeAgo(donation.datePosted);
            activityHTML += `
                <div class="activity-item">
                    <div class="activity-icon donation">📤</div>
                    <div class="activity-content">
                        <div class="activity-text">Posted ${donation.foodType}</div>
                        <div class="activity-time">${timeAgo}</div>
                    </div>
                </div>
            `;
        });
        
        // Add recent matches
        recentMatches.forEach(match => {
            const timeAgo = this.getTimeAgo(match.dateMatched);
            activityHTML += `
                <div class="activity-item">
                    <div class="activity-icon match">🤝</div>
                    <div class="activity-content">
                        <div class="activity-text">Matched with ${match.ngoName}</div>
                        <div class="activity-time">${timeAgo}</div>
                    </div>
                </div>
            `;
        });
        
        if (activityHTML === '') {
            activityHTML = `
                <div class="activity-item empty">
                    <div class="activity-icon">🌟</div>
                    <div class="activity-content">
                        <div class="activity-text">Start by posting your first donation!</div>
                    </div>
                </div>
            `;
        }
        
        recentActivity.innerHTML = activityHTML;
    }

    getTimeAgo(dateString) {
        const now = new Date();
        const date = new Date(dateString);
        const diffInMinutes = Math.floor((now - date) / 60000);
        
        if (diffInMinutes < 1) return 'Just now';
        if (diffInMinutes < 60) return `${diffInMinutes}m ago`;
        if (diffInMinutes < 1440) return `${Math.floor(diffInMinutes / 60)}h ago`;
        return `${Math.floor(diffInMinutes / 1440)}d ago`;
    }

    // Donor-specific methods that can be called from dashboard-common.js
    showAddDonationForm() {
        console.log('🍎 Showing Add Donation Form');
        openDonationModal();
    }

    showDonationsList() {
        console.log('📤 Showing Donations List');
        this.showActiveDonations();
    }

    showActiveDonations() {
        console.log('👀 Showing Active Donations');
        
        // Hide welcome section and show donations section
        document.getElementById('dynamic-content').style.display = 'none';
        document.getElementById('active-donations-section').style.display = 'block';
        
        // Update page title
        document.getElementById('page-title').textContent = 'Active Donations';
        
        // Update breadcrumb
        document.getElementById('breadcrumb').innerHTML = `
            <span class="breadcrumb-item" onclick="donorDashboard.showDashboard()">Dashboard</span>
            <span class="breadcrumb-separator">›</span>
            <span class="breadcrumb-item active">Active Donations</span>
        `;
        
        // Render donations
        this.renderDonations();
        
        // Update navigation active state
        this.updateNavActiveState('My Donations');
    }

    renderDonations(filteredDonations = null) {
        const donationsGrid = document.getElementById('donations-grid');
        if (!donationsGrid) return;

        const donations = filteredDonations || this.donations.filter(d => d.status !== 'completed' && d.status !== 'cancelled');
        
        if (donations.length === 0) {
            donationsGrid.innerHTML = `
                <div class="donations-empty">
                    <div class="empty-icon">📦</div>
                    <h3>No Active Donations</h3>
                    <p>You don't have any active donations at the moment.<br>Start by posting your first donation to help feed people in need!</p>
                    <button class="btn btn-primary" onclick="openDonationModal()">➕ Post Your First Donation</button>
                </div>
            `;
            return;
        }

        donationsGrid.innerHTML = donations.map(donation => this.createDonationCard(donation)).join('');
    }

    createDonationCard(donation) {
        const statusInfo = this.getStatusInfo(donation.status);
        const isUrgent = donation.isUrgent;
        const timeAgo = this.getTimeAgo(donation.datePosted);
        const expiryDays = this.getDaysUntilExpiry(donation.expiryDate);
        
        return `
            <div class="donation-card ${isUrgent ? 'urgent' : ''}" data-donation-id="${donation.id}">
                ${isUrgent ? '<div class="urgent-badge">🚨 Urgent</div>' : ''}
                
                <div class="donation-card-header">
                    <div class="donation-title">${donation.description || 'Food Donation'}</div>
                    <div class="donation-meta">
                        <span class="donation-date">Posted ${timeAgo}</span>
                        <span class="donation-id">#${donation.id.split('_')[1]}</span>
                    </div>
                </div>
                
                <div class="donation-card-body">
                    <div class="donation-details">
                        <div class="detail-row">
                            <span class="detail-label">Food Type:</span>
                            <span class="detail-value">${this.formatFoodType(donation.foodType)}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Quantity:</span>
                            <span class="detail-value">${donation.quantity} ${donation.quantityUnit}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Pickup Date:</span>
                            <span class="detail-value">${this.formatDate(donation.pickupDate)} at ${donation.pickupTime}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Expires:</span>
                            <span class="detail-value ${expiryDays <= 1 ? 'text-danger' : ''}">${this.formatDate(donation.expiryDate)} (${expiryDays} days)</span>
                        </div>
                    </div>
                    
                    ${donation.description ? `
                        <div class="donation-description">
                            ${donation.description}
                        </div>
                    ` : ''}
                    
                    <div class="donation-status">
                        <div class="status-badge ${donation.status}">
                            <span>${statusInfo.icon}</span>
                            <span>${statusInfo.label}</span>
                        </div>
                        <div class="status-progress">
                            <div class="progress-bar">
                                <div class="progress-fill ${donation.status}"></div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="donation-actions">
                        ${this.getDonationActions(donation)}
                    </div>
                </div>
            </div>
        `;
    }

    getStatusInfo(status) {
        const statusMap = {
            'posted': { icon: '📤', label: 'Posted' },
            'matched': { icon: '🤝', label: 'Matched' },
            'picked-up': { icon: '🚚', label: 'Picked Up' },
            'delivered': { icon: '✅', label: 'Delivered' }
        };
        return statusMap[status] || { icon: '❓', label: 'Unknown' };
    }

    formatFoodType(foodType) {
        return foodType.split('-').map(word => 
            word.charAt(0).toUpperCase() + word.slice(1)
        ).join(' ');
    }

    formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString('en-US', { 
            month: 'short', 
            day: 'numeric',
            year: date.getFullYear() !== new Date().getFullYear() ? 'numeric' : undefined
        });
    }

    getDaysUntilExpiry(expiryDate) {
        const today = new Date();
        const expiry = new Date(expiryDate);
        const diffTime = expiry - today;
        return Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    }

    getDonationActions(donation) {
        switch (donation.status) {
            case 'posted':
                return `
                    <button class="donation-btn primary" onclick="donorDashboard.editDonation('${donation.id}')">✏️ Edit</button>
                    <button class="donation-btn secondary" onclick="donorDashboard.shareDonation('${donation.id}')">📢 Share</button>
                `;
            case 'matched':
                return `
                    <button class="donation-btn primary" onclick="donorDashboard.viewMatch('${donation.id}')">👀 View Match</button>
                    <button class="donation-btn secondary" onclick="donorDashboard.contactNGO('${donation.id}')">📞 Contact</button>
                `;
            case 'picked-up':
                return `
                    <button class="donation-btn primary" onclick="donorDashboard.trackDelivery('${donation.id}')">📍 Track</button>
                    <button class="donation-btn secondary" onclick="donorDashboard.viewDetails('${donation.id}')">ℹ️ Details</button>
                `;
            case 'delivered':
                return `
                    <button class="donation-btn primary" onclick="donorDashboard.viewImpact('${donation.id}')">📊 View Impact</button>
                    <button class="donation-btn secondary" onclick="donorDashboard.downloadReceipt('${donation.id}')">📄 Receipt</button>
                `;
            default:
                return `<button class="donation-btn secondary" onclick="donorDashboard.viewDetails('${donation.id}')">ℹ️ Details</button>`;
        }
    }

    filterDonations() {
        const statusFilter = document.getElementById('status-filter').value;
        const foodTypeFilter = document.getElementById('food-type-filter').value;
        
        let filteredDonations = this.donations.filter(donation => {
            // Exclude completed/cancelled donations
            if (donation.status === 'completed' || donation.status === 'cancelled') {
                return false;
            }
            
            const statusMatch = statusFilter === 'all' || donation.status === statusFilter;
            const foodTypeMatch = foodTypeFilter === 'all' || donation.foodType === foodTypeFilter;
            
            return statusMatch && foodTypeMatch;
        });
        
        this.renderDonations(filteredDonations);
        console.log(`🔍 Filtered donations: ${filteredDonations.length} results`);
    }

    refreshActiveDonations() {
        console.log('🔄 Refreshing active donations...');
        this.loadDonations();
        this.renderDonations();
        showSuccessMessage('✅ Donations refreshed!');
    }

    updateNavActiveState(activeLabel) {
        document.querySelectorAll('.nav-item').forEach(item => {
            item.classList.remove('active');
            if (item.textContent.trim().includes(activeLabel)) {
                item.classList.add('active');
            }
        });
    }

    // Placeholder methods for donation actions
    editDonation(donationId) {
        console.log('✏️ Editing donation:', donationId);
        alert('Edit donation functionality coming soon!');
    }

    shareDonation(donationId) {
        console.log('📢 Sharing donation:', donationId);
        alert('Share donation functionality coming soon!');
    }

    viewMatch(donationId) {
        console.log('👀 Viewing match for donation:', donationId);
        alert('View match functionality coming soon!');
    }

    contactNGO(donationId) {
        console.log('📞 Contacting NGO for donation:', donationId);
        alert('Contact NGO functionality coming soon!');
    }

    trackDelivery(donationId) {
        console.log('📍 Tracking delivery for donation:', donationId);
        alert('Track delivery functionality coming soon!');
    }

    viewDetails(donationId) {
        console.log('ℹ️ Viewing details for donation:', donationId);
        alert('View details functionality coming soon!');
    }

    viewImpact(donationId) {
        console.log('📊 Viewing impact for donation:', donationId);
        alert('View impact functionality coming soon!');
    }

    downloadReceipt(donationId) {
        console.log('📄 Downloading receipt for donation:', donationId);
        alert('Download receipt functionality coming soon!');
    }

    showDonationHistory() {
        console.log('📋 Showing Donation History');
        // Implementation will be added in Phase 2
        alert('Donation History coming soon!');
    }

    createEmergencyDonation() {
        console.log('🚨 Creating Emergency Donation');
        // Open donation modal with urgent flag pre-checked
        openDonationModal();
        
        // Pre-fill urgent donation checkbox
        setTimeout(() => {
            const urgentCheckbox = document.getElementById('urgent-donation');
            if (urgentCheckbox) {
                urgentCheckbox.checked = true;
            }
        }, 100);
        
        console.log('🚨 Emergency donation mode activated');
    }

    showDashboard() {
        console.log('🏠 Showing Dashboard Overview');
        
        // Show welcome section and hide other sections
        document.getElementById('dynamic-content').style.display = 'block';
        document.getElementById('active-donations-section').style.display = 'none';
        
        // Update page title
        document.getElementById('page-title').textContent = 'Donor Dashboard';
        
        // Update breadcrumb
        document.getElementById('breadcrumb').innerHTML = `
            <span class="breadcrumb-item active">Dashboard</span>
        `;
        
        // Refresh the overview data
        this.populateRecentActivity();
        
        // Update nav to show dashboard as active
        this.updateNavActiveState('Dashboard');
    }

    showMatches() {
        console.log('🤝 Showing Matches');
        // Implementation will be added in Phase 2
        alert('Matches view coming in Phase 2!');
    }

    showSettings() {
        console.log('⚙️ Showing Settings');
        // Implementation will be added in Phase 2
        alert('Settings coming in Phase 2!');
    }
}

// ========================================
// DONATION MODAL FUNCTIONALITY
// ========================================

// Global functions for donation modal
function openDonationModal() {
    const modal = document.getElementById('donation-modal');
    if (modal) {
        modal.classList.add('show');
        document.body.style.overflow = 'hidden';
        
        // Set minimum date to today
        const today = new Date().toISOString().split('T')[0];
        document.getElementById('pickup-date').setAttribute('min', today);
        document.getElementById('expiry-date').setAttribute('min', today);
        
        // Setup file upload preview
        setupFileUploadPreview();
        
        // Setup pickup mode toggle
        setupPickupModeToggle();
        
        console.log('📤 Donation modal opened');
    }
}

function setupPickupModeToggle() {
    const manualRadio = document.getElementById('pickup-manual');
    const autoRadio = document.getElementById('pickup-auto');
    const manualDetails = document.getElementById('manual-pickup-details');
    const autoDetails = document.getElementById('auto-pickup-details');
    
    if (!manualRadio || !autoRadio || !manualDetails || !autoDetails) return;
    
    // Toggle function
    function togglePickupMode() {
        if (manualRadio.checked) {
            manualDetails.classList.remove('hidden');
            autoDetails.classList.add('hidden');
            
            // Make manual fields required
            const manualRequiredFields = manualDetails.querySelectorAll('input[required], textarea[required]');
            manualRequiredFields.forEach(field => field.required = true);
            
            // Remove auto field requirements
            const autoRequiredFields = autoDetails.querySelectorAll('input[required], textarea[required]');
            autoRequiredFields.forEach(field => field.required = false);
            
            console.log('📍 Manual pickup mode selected');
        } else if (autoRadio.checked) {
            manualDetails.classList.add('hidden');
            autoDetails.classList.remove('hidden');
            
            // Remove manual field requirements
            const manualRequiredFields = manualDetails.querySelectorAll('input[required], textarea[required]');
            manualRequiredFields.forEach(field => field.required = false);
            
            // Make auto phone field required
            const autoPhoneField = document.getElementById('auto-contact-phone');
            if (autoPhoneField) autoPhoneField.required = true;
            
            console.log('🤖 Auto assignment mode selected');
        }
    }
    
    // Add event listeners
    manualRadio.addEventListener('change', togglePickupMode);
    autoRadio.addEventListener('change', togglePickupMode);
    
    // Initialize with manual mode
    togglePickupMode();
}

function closeDonationModal() {
    const modal = document.getElementById('donation-modal');
    if (modal) {
        modal.classList.remove('show');
        document.body.style.overflow = 'auto';
        
        // Reset form
        document.getElementById('donation-form').reset();
        clearPhotoPreview();
        
        console.log('❌ Donation modal closed');
    }
}

function setupFileUploadPreview() {
    const fileInput = document.getElementById('food-photos');
    const uploadArea = document.getElementById('file-upload-area');
    const previewArea = document.getElementById('photo-preview');
    
    // Handle file selection
    fileInput.addEventListener('change', handleFileSelection);
    
    // Handle drag and drop
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.style.borderColor = '#27ae60';
        uploadArea.style.background = '#f8fff9';
    });
    
    uploadArea.addEventListener('dragleave', (e) => {
        e.preventDefault();
        uploadArea.style.borderColor = '#bdc3c7';
        uploadArea.style.background = 'white';
    });
    
    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.style.borderColor = '#bdc3c7';
        uploadArea.style.background = 'white';
        
        const files = e.dataTransfer.files;
        fileInput.files = files;
        handleFileSelection({ target: { files } });
    });
}

function handleFileSelection(event) {
    const files = Array.from(event.target.files);
    const previewArea = document.getElementById('photo-preview');
    
    // Clear existing previews
    clearPhotoPreview();
    
    // Validate and preview files
    files.forEach((file, index) => {
        if (index >= 5) return; // Maximum 5 photos
        
        if (file.type.startsWith('image/') && file.size <= 5 * 1024 * 1024) {
            createPhotoPreview(file, index);
        } else {
            console.warn('⚠️ Invalid file:', file.name);
        }
    });
}

function createPhotoPreview(file, index) {
    const previewArea = document.getElementById('photo-preview');
    const previewItem = document.createElement('div');
    previewItem.className = 'photo-preview-item';
    previewItem.dataset.index = index;
    
    const img = document.createElement('img');
    const reader = new FileReader();
    
    reader.onload = (e) => {
        img.src = e.target.result;
    };
    reader.readAsDataURL(file);
    
    const removeBtn = document.createElement('button');
    removeBtn.className = 'photo-remove';
    removeBtn.innerHTML = '×';
    removeBtn.onclick = () => removePhotoPreview(index);
    
    previewItem.appendChild(img);
    previewItem.appendChild(removeBtn);
    previewArea.appendChild(previewItem);
}

function removePhotoPreview(index) {
    const previewItem = document.querySelector(`[data-index="${index}"]`);
    if (previewItem) {
        previewItem.remove();
    }
    
    // Update file input (complex operation, simplified for now)
    console.log('🗑️ Photo removed:', index);
}

function clearPhotoPreview() {
    const previewArea = document.getElementById('photo-preview');
    if (previewArea) {
        previewArea.innerHTML = '';
    }
}

// Handle donation form submission
document.addEventListener('DOMContentLoaded', function() {
    const donationForm = document.getElementById('donation-form');
    if (donationForm) {
        donationForm.addEventListener('submit', handleDonationSubmit);
    }
});

function handleDonationSubmit(event) {
    event.preventDefault();
    
    console.log('📤 Processing donation submission...');
    
    // Determine pickup mode
    const pickupMode = document.querySelector('input[name="pickup-mode"]:checked').value;
    console.log('🎯 Pickup mode:', pickupMode);
    
    // Collect form data
    const formData = {
        id: 'donation_' + Date.now(),
        foodType: document.getElementById('food-type').value,
        description: document.getElementById('food-description').value,
        quantity: document.getElementById('quantity').value,
        quantityUnit: document.getElementById('quantity-unit').value,
        expiryDate: document.getElementById('expiry-date').value,
        specialInstructions: document.getElementById('special-instructions').value,
        isUrgent: document.getElementById('urgent-donation').checked,
        isRecurring: document.getElementById('recurring-donation').checked,
        status: 'posted',
        datePosted: new Date().toISOString(),
        photos: [], // Photo handling will be enhanced later
        pickupMode: pickupMode
    };
    
    // Handle pickup details based on mode
    if (pickupMode === 'manual') {
        formData.pickupAddress = document.getElementById('pickup-address').value;
        formData.pickupDate = document.getElementById('pickup-date').value;
        formData.pickupTime = document.getElementById('pickup-time').value;
        formData.pickupWindow = document.getElementById('pickup-window').value;
        formData.contactPerson = document.getElementById('contact-person').value;
        formData.contactPhone = document.getElementById('contact-phone').value;
        
        // Validate manual pickup fields
        if (!formData.pickupAddress || !formData.pickupDate || !formData.pickupTime) {
            alert('Please fill in all required pickup details');
            return;
        }
    } else if (pickupMode === 'auto') {
        formData.preferredTime = document.getElementById('preferred-time').value;
        formData.contactPhone = document.getElementById('auto-contact-phone').value;
        formData.autoAssignment = true;
        
        // Set auto-assignment defaults
        formData.pickupAddress = 'Auto-assigned (TBD)';
        formData.pickupDate = 'Auto-scheduled';
        formData.pickupTime = 'Auto-scheduled';
        formData.pickupWindow = 'Flexible';
        formData.contactPerson = 'System Coordinator';
        
        // Validate auto pickup fields
        if (!formData.contactPhone) {
            alert('Please provide a contact phone number for coordination');
            return;
        }
    }
    
    // Validate common required fields
    if (!formData.foodType || !formData.description || !formData.quantity || 
        !formData.expiryDate) {
        alert('Please fill in all required fields');
        return;
    }
    
    // Validate dates (only for manual mode)
    if (pickupMode === 'manual') {
        const today = new Date();
        const expiryDate = new Date(formData.expiryDate);
        const pickupDate = new Date(formData.pickupDate);
        
        if (expiryDate <= today) {
            alert('Expiry date must be in the future');
            return;
        }
        
        if (pickupDate < today) {
            alert('Pickup date must be today or in the future');
            return;
        }
    }
    
    // Save donation
    saveDonation(formData);
    
    // Close modal and show success
    closeDonationModal();
    
    if (pickupMode === 'auto') {
        showSuccessMessage('🤖 Donation posted for auto-assignment! Our system will find the best NGO match and coordinate pickup details.');
    } else {
        showSuccessMessage('🎉 Donation posted successfully! NGOs will be notified.');
    }
    
    // Refresh dashboard if donor dashboard is available
    if (window.donorDashboard) {
        window.donorDashboard.loadDonations();
    }
    
    console.log('✅ Donation submitted successfully:', formData);
}

function saveDonation(donationData) {
    const currentUser = window.dashboardManager?.currentUser || { email: 'test@example.com' };
    const storageKey = `donations_${currentUser.email}`;
    
    // Get existing donations
    const existingDonations = JSON.parse(localStorage.getItem(storageKey) || '[]');
    
    // Add new donation
    existingDonations.unshift(donationData);
    
    // Save back to localStorage
    localStorage.setItem(storageKey, JSON.stringify(existingDonations));
    
    console.log('💾 Donation saved to localStorage');
}

function showSuccessMessage(message) {
    // Create a temporary success notification
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: linear-gradient(135deg, #27ae60, #2ecc71);
        color: white;
        padding: 15px 25px;
        border-radius: 8px;
        box-shadow: 0 5px 20px rgba(0,0,0,0.2);
        z-index: 10000;
        font-weight: 500;
        animation: slideInRight 0.3s ease;
    `;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    // Remove after 3 seconds
    setTimeout(() => {
        notification.style.animation = 'slideOutRight 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Update the existing dashboard manager function to open the modal
if (window.dashboardManager) {
    window.dashboardManager.showAddDonation = openDonationModal;
}

// Initialize donor dashboard
const donorDashboard = new DonorDashboard();

// Export for global access
window.donorDashboard = donorDashboard;
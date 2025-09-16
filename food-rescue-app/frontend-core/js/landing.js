// Landing Page Flow JavaScript
// Following wireframe: Landing → Role Selection → Login → Dashboard

// Global state for the landing page flow
let currentStep = 1;
let selectedRole = null;
let isRegistering = false;

// Initialize landing page
document.addEventListener('DOMContentLoaded', function() {
    console.log('Food Rescue Matchmaker - Landing Page Loaded');
    showHero();
});

// Step 1: Show Hero Section
function showHero() {
    currentStep = 1;
    updateStepsIndicator();
    
    // Hide all sections
    hideAllSections();
    
    // Show hero section and learn-more section
    document.getElementById('hero-section').classList.remove('hidden');
    document.getElementById('learn-more-section').classList.remove('hidden');
    
    console.log('Showing hero section with learn-more');
}

// Step 2: Show Role Selection
function showRoleSelection() {
    currentStep = 2;
    updateStepsIndicator();
    
    // Hide all sections
    hideAllSections();
    
    // Show role selection
    document.getElementById('role-selection').classList.remove('hidden');
    
    console.log('Showing role selection');
}

// Step 3: Role Selection Handler
function selectRole(role) {
    selectedRole = role;
    console.log('Role selected:', role);
    
    // Add visual feedback
    const roleCards = document.querySelectorAll('.role-card');
    roleCards.forEach(card => card.classList.remove('selected'));
    
    const selectedCard = document.querySelector(`.role-card.${role}`);
    if (selectedCard) {
        selectedCard.classList.add('selected');
    }
    
    // Wait a bit for visual feedback, then proceed to login
    setTimeout(() => {
        showLogin();
    }, 500);
}

// Step 4: Show Login Section
function showLogin() {
    currentStep = 3;
    updateStepsIndicator();
    
    // Hide all sections
    hideAllSections();
    
    // Update selected role display
    updateSelectedRoleDisplay();
    
    // Show login section
    document.getElementById('login-section').classList.remove('hidden');
    
    // Reset to login mode
    isRegistering = false;
    updateAuthForm();
    
    console.log('Showing login for role:', selectedRole);
}

// Show About Section
function showAbout() {
    // Note: About content is now part of the learn-more section on welcome page
    // This function scrolls to learn-more section if it's visible, otherwise shows hero
    const learnMoreSection = document.getElementById('learn-more-section');
    if (learnMoreSection && !learnMoreSection.classList.contains('hidden')) {
        learnMoreSection.scrollIntoView({ behavior: 'smooth' });
    } else {
        // If learn-more is hidden, go back to hero to show it
        showHero();
        setTimeout(() => {
            document.getElementById('learn-more-section').scrollIntoView({ behavior: 'smooth' });
        }, 300);
    }
    console.log('Scrolled to learn more section');
}

// Toggle between Login and Register
function toggleRegister() {
    isRegistering = !isRegistering;
    updateAuthForm();
    console.log('Auth mode:', isRegistering ? 'Register' : 'Login');
}

// Update the authentication form based on mode
function updateAuthForm() {
    const title = document.getElementById('login-title');
    const submitBtn = document.getElementById('auth-submit-btn');
    const toggleBtn = document.getElementById('auth-toggle-btn');
    const switchText = document.getElementById('auth-switch-text');
    const confirmPasswordGroup = document.getElementById('confirm-password-group');
    
    if (isRegistering) {
        title.textContent = '📝 Register';
        submitBtn.textContent = 'Register';
        toggleBtn.textContent = 'Login';
        switchText.textContent = 'Already have an account?';
        confirmPasswordGroup.classList.remove('hidden');
    } else {
        title.textContent = '🔐 Login';
        submitBtn.textContent = 'Login';
        toggleBtn.textContent = 'Register';
        switchText.textContent = "Don't have an account?";
        confirmPasswordGroup.classList.add('hidden');
    }
}

// Update selected role display
function updateSelectedRoleDisplay() {
    if (!selectedRole) return;
    
    const roleIcon = document.getElementById('selected-role-icon');
    const roleText = document.getElementById('selected-role-text');
    
    const roleConfig = {
        donor: { icon: '🍞', text: 'Donor' },
        ngo: { icon: '🏢', text: 'NGO' },
        admin: { icon: '⚙️', text: 'Admin' }
    };
    
    const config = roleConfig[selectedRole];
    if (config) {
        roleIcon.textContent = config.icon;
        roleText.textContent = config.text;
    }
}

// Update steps indicator
function updateStepsIndicator() {
    const steps = document.querySelectorAll('.step');
    steps.forEach((step, index) => {
        const stepNumber = index + 1;
        if (stepNumber === currentStep) {
            step.classList.add('active');
            step.classList.remove('completed');
        } else if (stepNumber < currentStep) {
            step.classList.add('completed');
            step.classList.remove('active');
        } else {
            step.classList.remove('active', 'completed');
        }
    });
}

// Hide all sections
function hideAllSections() {
    const sections = [
        'hero-section',
        'learn-more-section',
        'role-selection',
        'login-section'
    ];
    
    sections.forEach(sectionId => {
        const section = document.getElementById(sectionId);
        if (section) {
            section.classList.add('hidden');
        }
    });
}

// Handle form submission
document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', handleAuthSubmit);
    }
});

function handleAuthSubmit(event) {
    event.preventDefault();
    
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const confirmPassword = document.getElementById('confirm-password').value;
    
    // Basic validation
    if (!email || !password) {
        alert('Please fill in all required fields');
        return;
    }
    
    if (isRegistering && password !== confirmPassword) {
        alert('Passwords do not match');
        return;
    }
    
    // Show loading state
    const submitBtn = document.getElementById('auth-submit-btn');
    const originalText = submitBtn.textContent;
    submitBtn.textContent = 'Processing...';
    submitBtn.disabled = true;
    
    // Simulate API call
    setTimeout(() => {
        console.log('Auth successful for:', email, 'as', selectedRole);
        
        // Store user data in localStorage for demonstration
        const userData = {
            email: email,
            role: selectedRole,
            isAuthenticated: true,
            loginTime: new Date().toISOString()
        };
        localStorage.setItem('foodRescueUser', JSON.stringify(userData));
        
        // Redirect to appropriate dashboard
        redirectToDashboard();
        
    }, 1500);
}

// Redirect to appropriate dashboard based on role
function redirectToDashboard() {
    if (!selectedRole) {
        console.error('No role selected');
        return;
    }
    
    const dashboardUrls = {
        donor: 'html/donor-dashboard.html',
        ngo: 'html/ngo-dashboard.html',
        admin: 'html/admin-dashboard.html'
    };
    
    const dashboardUrl = dashboardUrls[selectedRole];
    if (dashboardUrl) {
        console.log('Redirecting to:', dashboardUrl);
        window.location.href = dashboardUrl;
    } else {
        console.error('Unknown role:', selectedRole);
        alert('Error: Unknown user role');
    }
}

// Check if user is already logged in
function checkAuthStatus() {
    const userData = localStorage.getItem('foodRescueUser');
    if (userData) {
        try {
            const user = JSON.parse(userData);
            if (user.isAuthenticated) {
                console.log('User already authenticated:', user.role);
                // Could redirect directly or show logged in state
                return user;
            }
        } catch (e) {
            console.error('Error parsing user data:', e);
            localStorage.removeItem('foodRescueUser');
        }
    }
    return null;
}

// Logout function
function logout() {
    localStorage.removeItem('foodRescueUser');
    window.location.href = 'index.html';
}

// Auto-detect user location (for future use)
function detectLocation() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            function(position) {
                const lat = position.coords.latitude;
                const lng = position.coords.longitude;
                console.log('Location detected:', lat, lng);
                // Could be used for NGO matching in the future
            },
            function(error) {
                console.log('Location detection failed:', error.message);
            }
        );
    } else {
        console.log('Geolocation is not supported by this browser');
    }
}

// Export functions for testing
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        showHero,
        showRoleSelection,
        selectRole,
        showLogin,
        showAbout,
        toggleRegister,
        handleAuthSubmit,
        checkAuthStatus,
        logout
    };
}
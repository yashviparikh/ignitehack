/**
 * Navigation Helper for Live Server Compatibility
 * Fixes browser navigation issues in Live Server environment
 */

class NavigationHelper {
    constructor() {
        this.isLiveServer = this.detectLiveServer();
        this.originalPushState = history.pushState.bind(history);
        this.originalReplaceState = history.replaceState.bind(history);
        this.init();
    }

    detectLiveServer() {
        // Detect if running in Live Server environment
        return window.location.port && (
            window.location.port === '5500' || 
            window.location.port === '5501' || 
            window.location.hostname === '127.0.0.1' ||
            window.location.hostname === 'localhost'
        );
    }

    init() {
        if (this.isLiveServer) {
            console.log('🧭 Live Server detected - applying navigation fixes');
            this.enhanceNavigation();
            this.addNavigationControls();
        }
    }

    enhanceNavigation() {
        // Override history methods to trigger custom events
        history.pushState = (...args) => {
            const result = this.originalPushState(...args);
            this.triggerNavigationEvent('pushstate');
            return result;
        };

        history.replaceState = (...args) => {
            const result = this.originalReplaceState(...args);
            this.triggerNavigationEvent('replacestate');
            return result;
        };

        // Listen for browser navigation
        window.addEventListener('popstate', (event) => {
            this.triggerNavigationEvent('popstate', event);
        });

        // Add keyboard shortcuts for navigation
        document.addEventListener('keydown', (event) => {
            // Alt + Left Arrow = Back
            if (event.altKey && event.key === 'ArrowLeft') {
                event.preventDefault();
                this.goBack();
            }
            
            // Alt + Right Arrow = Forward  
            if (event.altKey && event.key === 'ArrowRight') {
                event.preventDefault();
                this.goForward();
            }

            // Ctrl + R = Refresh (prevent Live Server auto-refresh conflicts)
            if (event.ctrlKey && event.key === 'r') {
                event.preventDefault();
                this.refreshPage();
            }
        });
    }

    addNavigationControls() {
        // Add floating navigation controls for better UX
        const navControls = document.createElement('div');
        navControls.id = 'live-server-nav-controls';
        navControls.innerHTML = `
            <div class="nav-control-panel">
                <button onclick="navigationHelper.goBack()" title="Go Back (Alt + ←)">←</button>
                <button onclick="navigationHelper.goForward()" title="Go Forward (Alt + →)">→</button>
                <button onclick="navigationHelper.refreshPage()" title="Refresh (Ctrl + R)">⟳</button>
                <button onclick="navigationHelper.goHome()" title="Go to Landing Page">🏠</button>
            </div>
        `;

        // Add styles
        const styles = `
            #live-server-nav-controls {
                position: fixed;
                top: 20px;
                right: 20px;
                z-index: 10000;
                background: rgba(0, 0, 0, 0.8);
                border-radius: 25px;
                padding: 10px;
                display: flex;
                gap: 5px;
                box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
                transition: opacity 0.3s ease;
            }
            
            #live-server-nav-controls:hover {
                opacity: 1;
            }
            
            #live-server-nav-controls.minimized {
                opacity: 0.6;
            }
            
            .nav-control-panel button {
                background: transparent;
                border: 1px solid rgba(255, 255, 255, 0.3);
                color: white;
                padding: 8px 12px;
                border-radius: 15px;
                cursor: pointer;
                font-size: 14px;
                transition: all 0.2s ease;
            }
            
            .nav-control-panel button:hover {
                background: rgba(255, 255, 255, 0.2);
                border-color: rgba(255, 255, 255, 0.6);
                transform: scale(1.1);
            }
            
            .nav-control-panel button:active {
                transform: scale(0.95);
            }
            
            @media (max-width: 768px) {
                #live-server-nav-controls {
                    top: 10px;
                    right: 10px;
                    padding: 8px;
                }
                
                .nav-control-panel button {
                    padding: 6px 8px;
                    font-size: 12px;
                }
            }
        `;

        // Inject styles
        const styleSheet = document.createElement('style');
        styleSheet.textContent = styles;
        document.head.appendChild(styleSheet);

        // Add controls to page
        document.body.appendChild(navControls);

        // Auto-minimize after 3 seconds
        setTimeout(() => {
            navControls.classList.add('minimized');
        }, 3000);
    }

    triggerNavigationEvent(type, event = null) {
        const customEvent = new CustomEvent('navigation-change', {
            detail: { type, originalEvent: event, timestamp: Date.now() }
        });
        window.dispatchEvent(customEvent);
    }

    goBack() {
        if (window.history.length > 1) {
            window.history.back();
            console.log('🧭 Navigation: Going back');
        } else {
            console.log('🧭 Navigation: No previous page, going to landing');
            this.goHome();
        }
    }

    goForward() {
        window.history.forward();
        console.log('🧭 Navigation: Going forward');
    }

    refreshPage() {
        console.log('🧭 Navigation: Refreshing page');
        window.location.reload();
    }

    goHome() {
        console.log('🧭 Navigation: Going to landing page');
        // Determine the correct path to landing page
        const currentPath = window.location.pathname;
        const landingPath = currentPath.includes('/html/') ? '../index.html' : './html/index.html';
        window.location.href = landingPath;
    }

    // Utility method to check if navigation is working
    testNavigation() {
        return {
            isLiveServer: this.isLiveServer,
            historyLength: window.history.length,
            currentPath: window.location.pathname,
            canGoBack: window.history.length > 1,
            userAgent: navigator.userAgent,
            timestamp: new Date().toISOString()
        };
    }
}

// Initialize navigation helper when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.navigationHelper = new NavigationHelper();
    
    // Expose test function globally for debugging
    window.testNavigation = () => {
        const result = window.navigationHelper.testNavigation();
        console.table(result);
        return result;
    };
});

// Export for testing purposes
if (typeof module !== 'undefined' && module.exports) {
    module.exports = NavigationHelper;
}
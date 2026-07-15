// Progressive Web App (PWA) functionality
// Service Worker registration and PWA features

// Register Service Worker
if ('serviceWorker' in navigator) {
    window.addEventListener('load', function() {
        navigator.serviceWorker.register('/static/sw.js')
            .then(function(registration) {
                console.log('ServiceWorker registration successful');
            })
            .catch(function(err) {
                console.log('ServiceWorker registration failed: ', err);
            });
    });
}

// PWA Install Prompt
let deferredPrompt;
const installButton = document.createElement('button');
installButton.className = 'btn btn-success position-fixed';
installButton.style.cssText = 'bottom: 20px; right: 20px; z-index: 1000; display: none; border-radius: 50px; padding: 12px 20px;';
installButton.innerHTML = '<i class="fas fa-download me-2"></i>Install App';
document.body.appendChild(installButton);

window.addEventListener('beforeinstallprompt', (e) => {
    // Prevent Chrome 67 and earlier from automatically showing the prompt
    e.preventDefault();
    // Stash the event so it can be triggered later
    deferredPrompt = e;
    // Show install button
    installButton.style.display = 'block';
});

installButton.addEventListener('click', (e) => {
    // Hide the install button
    installButton.style.display = 'none';
    // Show the install prompt
    deferredPrompt.prompt();
    // Wait for the user to respond to the prompt
    deferredPrompt.userChoice.then((choiceResult) => {
        if (choiceResult.outcome === 'accepted') {
            console.log('User accepted the install prompt');
        } else {
            console.log('User dismissed the install prompt');
        }
        deferredPrompt = null;
    });
});

// Handle app installed
window.addEventListener('appinstalled', (evt) => {
    console.log('App was installed');
    installButton.style.display = 'none';
});

// Touch and Gesture Support
class TouchHandler {
    constructor() {
        this.startX = 0;
        this.startY = 0;
        this.endX = 0;
        this.endY = 0;
        this.threshold = 50; // Minimum distance for swipe
        
        this.init();
    }
    
    init() {
        // Add touch event listeners
        document.addEventListener('touchstart', this.handleTouchStart.bind(this), { passive: true });
        document.addEventListener('touchend', this.handleTouchEnd.bind(this), { passive: true });
        
        // Add pull-to-refresh functionality
        this.initPullToRefresh();
        
        // Improve tap targets
        this.improveTapTargets();
    }
    
    handleTouchStart(e) {
        this.startX = e.touches[0].clientX;
        this.startY = e.touches[0].clientY;
    }
    
    handleTouchEnd(e) {
        this.endX = e.changedTouches[0].clientX;
        this.endY = e.changedTouches[0].clientY;
        
        this.handleSwipe();
    }
    
    handleSwipe() {
        const deltaX = this.endX - this.startX;
        const deltaY = this.endY - this.startY;
        
        // Check if it's a horizontal swipe
        if (Math.abs(deltaX) > Math.abs(deltaY) && Math.abs(deltaX) > this.threshold) {
            if (deltaX > 0) {
                this.onSwipeRight();
            } else {
                this.onSwipeLeft();
            }
        }
        
        // Check if it's a vertical swipe
        if (Math.abs(deltaY) > Math.abs(deltaX) && Math.abs(deltaY) > this.threshold) {
            if (deltaY > 0) {
                this.onSwipeDown();
            } else {
                this.onSwipeUp();
            }
        }
    }
    
    onSwipeRight() {
        // Navigate back or open sidebar
        if (window.history.length > 1) {
            window.history.back();
        }
    }
    
    onSwipeLeft() {
        // Could be used for navigation or actions
        console.log('Swipe left detected');
    }
    
    onSwipeDown() {
        // Pull to refresh
        if (window.scrollY === 0) {
            this.refreshPage();
        }
    }
    
    onSwipeUp() {
        // Could be used for quick actions
        console.log('Swipe up detected');
    }
    
    refreshPage() {
        // Add visual feedback
        const refreshIndicator = document.createElement('div');
        refreshIndicator.className = 'alert alert-info position-fixed';
        refreshIndicator.style.cssText = 'top: 70px; left: 50%; transform: translateX(-50%); z-index: 9999;';
        refreshIndicator.innerHTML = '<i class="fas fa-sync-alt fa-spin me-2"></i>Refreshing...';
        document.body.appendChild(refreshIndicator);
        
        setTimeout(() => {
            location.reload();
        }, 1000);
    }
    
    initPullToRefresh() {
        let startY = 0;
        let pullDistance = 0;
        const pullThreshold = 100;
        
        document.addEventListener('touchstart', (e) => {
            if (window.scrollY === 0) {
                startY = e.touches[0].clientY;
            }
        }, { passive: true });
        
        document.addEventListener('touchmove', (e) => {
            if (window.scrollY === 0 && startY > 0) {
                pullDistance = e.touches[0].clientY - startY;
                
                if (pullDistance > 0) {
                    // Add visual feedback for pull to refresh
                    document.body.style.transform = `translateY(${Math.min(pullDistance / 3, 30)}px)`;
                    document.body.style.transition = 'none';
                }
            }
        }, { passive: true });
        
        document.addEventListener('touchend', () => {
            if (pullDistance > pullThreshold) {
                this.refreshPage();
            }
            
            // Reset transform
            document.body.style.transform = '';
            document.body.style.transition = 'transform 0.3s ease';
            startY = 0;
            pullDistance = 0;
        }, { passive: true });
    }
    
    improveTapTargets() {
        // Ensure all interactive elements are touch-friendly
        const interactiveElements = document.querySelectorAll('button, a, input, select, textarea');
        
        interactiveElements.forEach(element => {
            const computedStyle = window.getComputedStyle(element);
            const height = parseInt(computedStyle.height);
            const width = parseInt(computedStyle.width);
            
            // Ensure minimum touch target size (44px x 44px)
            if (height < 44) {
                element.style.minHeight = '44px';
                element.style.display = 'flex';
                element.style.alignItems = 'center';
                element.style.justifyContent = 'center';
            }
            
            if (width < 44) {
                element.style.minWidth = '44px';
            }
        });
    }
}

// Device Detection and Optimization
class DeviceOptimizer {
    constructor() {
        this.isMobile = this.detectMobile();
        this.isTablet = this.detectTablet();
        this.isTouch = this.detectTouch();
        this.init();
    }
    
    detectMobile() {
        return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent) ||
               window.innerWidth <= 768;
    }
    
    detectTablet() {
        return /iPad|Android/i.test(navigator.userAgent) && 
               window.innerWidth > 768 && window.innerWidth <= 1024;
    }
    
    detectTouch() {
        return 'ontouchstart' in window || navigator.maxTouchPoints > 0;
    }
    
    init() {
        // Add device classes to body
        document.body.classList.add(this.isMobile ? 'mobile-device' : 'desktop-device');
        if (this.isTablet) {
            document.body.classList.add('tablet-device');
        }
        document.body.classList.add(this.isTouch ? 'touch-device' : 'no-touch');
        
        // Optimize for device type
        if (this.isMobile) {
            this.optimizeForMobile();
        }
        
        if (this.isTablet) {
            this.optimizeForTablet();
        }
        
        // Handle orientation changes
        window.addEventListener('orientationchange', this.handleOrientationChange.bind(this));
        window.addEventListener('resize', this.handleResize.bind(this));
    }
    
    optimizeForMobile() {
        // Disable hover effects on mobile
        const style = document.createElement('style');
        style.textContent = `
            @media (hover: none) {
                .card:hover,
                .btn:hover,
                .nav-link:hover {
                    transform: none !important;
                    box-shadow: inherit !important;
                }
            }
        `;
        document.head.appendChild(style);
        
        // Optimize forms for mobile
        this.optimizeForms();
        
        // Add mobile-specific interactions
        this.addMobileInteractions();
    }
    
    optimizeForTablet() {
        // Tablet-specific optimizations
        document.body.classList.add('tablet-optimized');
    }
    
    optimizeForms() {
        // Set appropriate input types for better mobile keyboards
        const inputs = document.querySelectorAll('input');
        inputs.forEach(input => {
            if (input.name === 'email' || input.type === 'email') {
                input.type = 'email';
                input.autocomplete = 'email';
            }
            
            if (input.name === 'phone' || input.type === 'tel') {
                input.type = 'tel';
                input.autocomplete = 'tel';
            }
            
            if (input.name === 'password') {
                input.autocomplete = 'current-password';
            }
            
            // Prevent zoom on input focus for iOS
            if (/iPad|iPhone|iPod/.test(navigator.userAgent)) {
                input.style.fontSize = '16px';
            }
        });
    }
    
    addMobileInteractions() {
        // Add haptic feedback for supported devices
        if ('vibrate' in navigator) {
            document.addEventListener('click', (e) => {
                if (e.target.matches('button, .btn')) {
                    navigator.vibrate(10); // Short vibration
                }
            });
        }
        
        // Improve scrolling performance
        document.addEventListener('touchstart', () => {}, { passive: true });
        document.addEventListener('touchmove', () => {}, { passive: true });
    }
    
    handleOrientationChange() {
        // Handle orientation changes
        setTimeout(() => {
            // Recalculate layouts after orientation change
            window.dispatchEvent(new Event('resize'));
        }, 100);
    }
    
    handleResize() {
        // Update device detection on resize
        this.isMobile = this.detectMobile();
        this.isTablet = this.detectTablet();
        
        // Update body classes
        document.body.classList.toggle('mobile-device', this.isMobile);
        document.body.classList.toggle('desktop-device', !this.isMobile);
        document.body.classList.toggle('tablet-device', this.isTablet);
    }
}

// Network Status Monitoring
class NetworkMonitor {
    constructor() {
        this.isOnline = navigator.onLine;
        this.init();
    }
    
    init() {
        window.addEventListener('online', this.handleOnline.bind(this));
        window.addEventListener('offline', this.handleOffline.bind(this));
        
        // Monitor connection quality
        if ('connection' in navigator) {
            this.monitorConnection();
        }
    }
    
    handleOnline() {
        this.isOnline = true;
        this.showNetworkStatus('Connected', 'success');
        
        // Sync any pending data
        this.syncPendingData();
    }
    
    handleOffline() {
        this.isOnline = false;
        this.showNetworkStatus('Offline - Some features may not work', 'warning');
    }
    
    showNetworkStatus(message, type) {
        const alert = document.createElement('div');
        alert.className = `alert alert-${type} position-fixed`;
        alert.style.cssText = 'top: 70px; left: 50%; transform: translateX(-50%); z-index: 9999; min-width: 300px;';
        alert.innerHTML = `<i class="fas fa-${type === 'success' ? 'wifi' : 'exclamation-triangle'} me-2"></i>${message}`;
        
        document.body.appendChild(alert);
        
        setTimeout(() => {
            if (alert.parentNode) {
                alert.remove();
            }
        }, 3000);
    }
    
    monitorConnection() {
        const connection = navigator.connection;
        
        connection.addEventListener('change', () => {
            console.log(`Connection type: ${connection.effectiveType}`);
            
            if (connection.effectiveType === 'slow-2g' || connection.effectiveType === '2g') {
                this.showNetworkStatus('Slow connection detected', 'info');
            }
        });
    }
    
    syncPendingData() {
        // Implement data synchronization logic here
        console.log('Syncing pending data...');
    }
}

// Initialize all mobile optimizations
document.addEventListener('DOMContentLoaded', function() {
    new TouchHandler();
    new DeviceOptimizer();
    new NetworkMonitor();
    
    // Add loading states for better perceived performance
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function() {
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Loading...';
            }
        });
    });
});

// Export for use in other scripts
window.PWA = {
    TouchHandler,
    DeviceOptimizer,
    NetworkMonitor
};

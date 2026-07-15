// Main JavaScript file for E-Waste Management System

// Global variables
let currentUser = null;
let authToken = null;

// Initialize app
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

function initializeApp() {
    // Check authentication
    authToken = localStorage.getItem('access_token');
    const userData = localStorage.getItem('user_data');
    
    if (authToken && userData) {
        try {
            currentUser = JSON.parse(userData);
            updateUIForLoggedInUser();
        } catch (e) {
            console.error('Error parsing user data:', e);
            logout();
        }
    }
    
    // Set up global event listeners
    setupGlobalEventListeners();
}

function setupGlobalEventListeners() {
    // Handle form submissions with loading states
    document.addEventListener('submit', function(e) {
        const form = e.target;
        if (form.classList.contains('api-form')) {
            handleFormSubmission(e);
        }
    });
    
    // Handle API errors globally
    window.addEventListener('unhandledrejection', function(e) {
        console.error('Unhandled promise rejection:', e.reason);
        if (e.reason.status === 401) {
            logout();
        }
    });
}

function updateUIForLoggedInUser() {
    const navbar = document.getElementById('navbar');
    const userDisplayName = document.getElementById('userDisplayName');
    
    if (navbar) {
        navbar.style.display = 'block';
    }
    
    if (userDisplayName && currentUser) {
        userDisplayName.textContent = currentUser.first_name || currentUser.username;
    }
}

// Authentication functions
async function login(credentials) {
    try {
        const response = await apiRequest('/api/auth/login', {
            method: 'POST',
            body: JSON.stringify(credentials)
        });
        
        if (response.access_token) {
            localStorage.setItem('access_token', response.access_token);
            localStorage.setItem('user_data', JSON.stringify(response.user));
            authToken = response.access_token;
            currentUser = response.user;
            return response;
        }
        
        throw new Error(response.error || 'Login failed');
    } catch (error) {
        throw error;
    }
}

async function register(userData) {
    try {
        const response = await apiRequest('/api/auth/register-with-otp', {
            method: 'POST',
            body: JSON.stringify(userData)
        });
        
        if (response.access_token) {
            localStorage.setItem('access_token', response.access_token);
            localStorage.setItem('user_data', JSON.stringify(response.user));
            authToken = response.access_token;
            currentUser = response.user;
            return response;
        }
        
        throw new Error(response.error || 'Registration failed');
    } catch (error) {
        throw error;
    }
}



function logout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user_data');
    authToken = null;
    currentUser = null;
    window.location.href = '/';
}

// API request helper
async function apiRequest(url, options = {}) {
    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json',
        }
    };
    
    if (authToken) {
        defaultOptions.headers['Authorization'] = `Bearer ${authToken}`;
    }
    
    const finalOptions = {
        ...defaultOptions,
        ...options,
        headers: {
            ...defaultOptions.headers,
            ...options.headers
        }
    };
    
    try {
        const response = await fetch(url, finalOptions);
        const data = await response.json();
        
        if (!response.ok) {
            if (response.status === 401) {
                logout();
                throw new Error('Session expired. Please login again.');
            }
            throw new Error(data.error || `HTTP ${response.status}`);
        }
        
        return data;
    } catch (error) {
        console.error('API Request Error:', error);
        throw error;
    }
}

// Form handling utilities
function handleFormSubmission(event) {
    event.preventDefault();
    const form = event.target;
    const submitBtn = form.querySelector('button[type="submit"]');
    const originalText = submitBtn.textContent;
    
    // Show loading state
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Loading...';
    
    // Reset after 10 seconds as fallback
    setTimeout(() => {
        if (submitBtn.disabled) {
            submitBtn.disabled = false;
            submitBtn.textContent = originalText;
        }
    }, 10000);
}

function resetFormButton(form) {
    const submitBtn = form.querySelector('button[type="submit"]');
    if (submitBtn) {
        submitBtn.disabled = false;
        const originalText = submitBtn.dataset.originalText || 'Submit';
        submitBtn.textContent = originalText;
    }
}

// Notification system
function showNotification(message, type = 'info', duration = 5000) {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show notification`;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 9999;
        min-width: 300px;
        max-width: 500px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    `;
    
    notification.innerHTML = `
        <div class="d-flex align-items-center">
            <i class="fas fa-${getNotificationIcon(type)} me-2"></i>
            <div class="flex-grow-1">${message}</div>
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    
    document.body.appendChild(notification);
    
    // Auto remove
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, duration);
    
    return notification;
}

function getNotificationIcon(type) {
    const icons = {
        success: 'check-circle',
        danger: 'exclamation-triangle',
        warning: 'exclamation-circle',
        info: 'info-circle',
        primary: 'info-circle'
    };
    return icons[type] || 'info-circle';
}

// Utility functions
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

function formatDateTime(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

function formatCurrency(amount) {
    return new Intl.NumberFormat('en-IN', {
        style: 'currency',
        currency: 'INR',
        maximumFractionDigits: 2
    }).format(amount);
}

function capitalizeFirst(str) {
    return str.charAt(0).toUpperCase() + str.slice(1);
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Loading states
function showLoading(element, message = 'Loading...') {
    if (typeof element === 'string') {
        element = document.getElementById(element);
    }
    
    if (element) {
        element.innerHTML = `
            <div class="text-center py-4">
                <div class="spinner-border text-primary mb-3" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
                <p class="text-muted">${message}</p>
            </div>
        `;
    }
}

function showError(element, message = 'An error occurred') {
    if (typeof element === 'string') {
        element = document.getElementById(element);
    }
    
    if (element) {
        element.innerHTML = `
            <div class="text-center py-4">
                <i class="fas fa-exclamation-triangle text-warning fa-2x mb-3"></i>
                <p class="text-muted">${message}</p>
                <button class="btn btn-outline-primary btn-sm" onclick="location.reload()">
                    <i class="fas fa-redo me-2"></i>Retry
                </button>
            </div>
        `;
    }
}

function showEmpty(element, message = 'No data available', actionText = null, actionCallback = null) {
    if (typeof element === 'string') {
        element = document.getElementById(element);
    }
    
    if (element) {
        let actionButton = '';
        if (actionText && actionCallback) {
            actionButton = `
                <button class="btn btn-success mt-3" onclick="${actionCallback}">
                    <i class="fas fa-plus me-2"></i>${actionText}
                </button>
            `;
        }
        
        element.innerHTML = `
            <div class="text-center py-4">
                <i class="fas fa-inbox text-muted" style="font-size: 3rem;"></i>
                <p class="mt-3 text-muted">${message}</p>
                ${actionButton}
            </div>
        `;
    }
}

// Modal utilities
function showModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        const bsModal = new bootstrap.Modal(modal);
        bsModal.show();
        return bsModal;
    }
}

function hideModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        const bsModal = bootstrap.Modal.getInstance(modal);
        if (bsModal) {
            bsModal.hide();
        }
    }
}

// Validation utilities
function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

function validatePassword(password) {
    return password.length >= 6;
}

function validateRequired(value) {
    return value && value.trim().length > 0;
}

// Local storage utilities
function setLocalStorage(key, value) {
    try {
        localStorage.setItem(key, JSON.stringify(value));
    } catch (e) {
        console.error('Error saving to localStorage:', e);
    }
}

function getLocalStorage(key, defaultValue = null) {
    try {
        const item = localStorage.getItem(key);
        return item ? JSON.parse(item) : defaultValue;
    } catch (e) {
        console.error('Error reading from localStorage:', e);
        return defaultValue;
    }
}

// Export functions for global use
window.EWasteApp = {
    login,
    register,
    logout,
    apiRequest,
    showNotification,
    formatDate,
    formatDateTime,
    formatCurrency,
    showLoading,
    showError,
    showEmpty,
    showModal,
    hideModal,
    validateEmail,
    validatePassword,
    validateRequired
};

/**
 * Task Management System - Main JavaScript
 */

// API Base URL
const API_URL = '/api/v1';

// Auth helpers
function getToken() {
    return localStorage.getItem('token');
}

function setToken(token) {
    localStorage.setItem('token', token);
}

function removeToken() {
    localStorage.removeItem('token');
}

function isAuthenticated() {
    return !!getToken();
}

function getAuthHeaders() {
    const token = getToken();
    return {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
    };
}

// Update UI based on auth state
function updateAuthUI() {
    const authButtons = document.getElementById('auth-buttons');
    const userMenu = document.getElementById('user-menu');
    const navLinks = document.getElementById('nav-links');

    if (isAuthenticated()) {
        if (authButtons) authButtons.classList.add('hidden');
        if (userMenu) userMenu.classList.remove('hidden');
        if (navLinks) navLinks.classList.remove('hidden');

        // Load user info
        loadCurrentUser();
    } else {
        if (authButtons) authButtons.classList.remove('hidden');
        if (userMenu) userMenu.classList.add('hidden');
        if (navLinks) navLinks.classList.add('hidden');
    }
}

// Load current user info
async function loadCurrentUser() {
    try {
        const response = await fetch(`${API_URL}/users/me`, {
            headers: getAuthHeaders()
        });

        if (response.ok) {
            const user = await response.json();
            const usernameDisplay = document.getElementById('username-display');
            if (usernameDisplay) {
                usernameDisplay.textContent = user.username;
            }
        } else if (response.status === 401) {
            // Token expired
            logout();
        }
    } catch (error) {
        console.error('Failed to load user:', error);
    }
}

// Logout
function logout() {
    removeToken();
    window.location.href = '/';
}

// Toggle dropdown menu
function toggleDropdown() {
    const menu = document.getElementById('dropdown-menu');
    menu.classList.toggle('hidden');
}

// Close dropdown when clicking outside
document.addEventListener('click', (e) => {
    const dropdown = document.getElementById('dropdown-menu');
    const userMenu = document.getElementById('user-menu');

    if (dropdown && userMenu && !userMenu.contains(e.target)) {
        dropdown.classList.add('hidden');
    }
});

// Toast notifications
function showToast(message, type = 'success') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    document.body.appendChild(toast);

    setTimeout(() => {
        toast.remove();
    }, 3000);
}

// API helper function
async function apiRequest(endpoint, options = {}) {
    const defaultOptions = {
        headers: getAuthHeaders()
    };

    const mergedOptions = {
        ...defaultOptions,
        ...options,
        headers: {
            ...defaultOptions.headers,
            ...options.headers
        }
    };

    const response = await fetch(`${API_URL}${endpoint}`, mergedOptions);

    if (response.status === 401) {
        logout();
        throw new Error('Unauthorized');
    }

    return response;
}

// Format date
function formatDate(dateString) {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleDateString('zh-CN', {
        month: 'short',
        day: 'numeric'
    });
}

// Format datetime
function formatDateTime(dateString) {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    updateAuthUI();
});

/**
 * Secure Authentication Module
 * Uses httpOnly cookies instead of localStorage for JWT tokens
 * Prevents XSS token theft
 */

class SecureAuth {
    constructor() {
        this.baseURL = window.location.origin;
    }

    /**
     * Login user and set secure cookie
     */
    async login(email, password) {
        try {
            const formData = new FormData();
            formData.append('username', email);
            formData.append('password', password);

            const response = await fetch(`${this.baseURL}/auth/login`, {
                method: 'POST',
                body: formData,
                credentials: 'include' // Important: include cookies
            });

            const data = await response.json();

            if (response.ok) {
                // Token is now in httpOnly cookie, not accessible to JavaScript
                return { success: true, data };
            } else if (response.status === 429) {
                // Rate limit exceeded
                return { 
                    success: false, 
                    error: data.message || 'Too many login attempts',
                    rateLimited: true,
                    retryAfter: data.retry_after || 60,
                    errorCode: data.error || 'too_many_login_attempts'
                };
            } else {
                return { success: false, error: data.detail || 'Login failed' };
            }
        } catch (error) {
            return { success: false, error: 'Network error' };
        }
    }

    /**
     * Register user
     */
    async register(email, password, fullName) {
        try {
            const response = await fetch(`${this.baseURL}/auth/register`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    email,
                    password,
                    full_name: fullName
                }),
                credentials: 'include'
            });

            const data = await response.json();

            if (response.ok) {
                return { success: true, data };
            } else if (response.status === 429) {
                // Rate limit exceeded
                return { 
                    success: false, 
                    error: data.message || 'Too many registration attempts',
                    rateLimited: true,
                    retryAfter: data.retry_after || 60,
                    errorCode: data.error || 'too_many_registration_attempts'
                };
            } else {
                return { success: false, error: data.detail || 'Registration failed' };
            }
        } catch (error) {
            return { success: false, error: 'Network error' };
        }
    }

    /**
     * Make authenticated API request
     */
    async apiRequest(url, options = {}) {
        const defaultOptions = {
            credentials: 'include', // Include httpOnly cookie
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            }
        };

        const response = await fetch(url, { ...defaultOptions, ...options });

        if (response.status === 401) {
            // Token expired or invalid, redirect to login
            this.redirectToLogin();
            return null;
        }

        return response;
    }

    /**
     * Get current user info
     */
    async getCurrentUser() {
        try {
            const response = await this.apiRequest(`${this.baseURL}/auth/me`);
            if (response && response.ok) {
                return await response.json();
            }
            return null;
        } catch (error) {
            console.error('Error getting current user:', error);
            return null;
        }
    }

    /**
     * Check if user is authenticated
     */
    async isAuthenticated() {
        const user = await this.getCurrentUser();
        return user !== null;
    }

    /**
     * Logout user (clear cookie)
     */
    async logout() {
        try {
            await fetch(`${this.baseURL}/auth/logout`, {
                method: 'POST',
                credentials: 'include'
            });
        } catch (error) {
            console.error('Logout error:', error);
        } finally {
            // Always redirect to login after logout attempt
            this.redirectToLogin();
        }
    }

    /**
     * Redirect to login page
     */
    redirectToLogin() {
        // Don't redirect if already on login/register pages
        const currentPage = window.location.pathname;
        if (!currentPage.includes('login') && !currentPage.includes('register')) {
            window.location.href = '/static/login.html';
        }
    }

    /**
     * Protect page - redirect if not authenticated
     */
    async protectPage() {
        const isAuth = await this.isAuthenticated();
        if (!isAuth) {
            this.redirectToLogin();
            return false;
        }
        return true;
    }
}

// Global instance
window.secureAuth = new SecureAuth();

// Auto-protect pages that require authentication
document.addEventListener('DOMContentLoaded', async () => {
    const protectedPages = [
        'dashboard.html',
        'client_home.html',
        'admin.html'
    ];

    const currentPage = window.location.pathname;
    const isProtectedPage = protectedPages.some(page => currentPage.includes(page));

    if (isProtectedPage) {
        await window.secureAuth.protectPage();
    }
});
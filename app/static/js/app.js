/**
 * Toast Notification System
 */
class Toast {
    static container = null;

    static init() {
        this.container = document.createElement('div');
        this.container.className = 'toast-container';
        document.body.appendChild(this.container);
    }

    static show(message, type = 'info', duration = 4000) {
        if (!this.container) this.init();

        const icons = {
            success: '✅', error: '❌', warning: '⚠️', info: 'ℹ️'
        };

        const toast = document.createElement('div');
        toast.className = `toast toast--${type}`;
        toast.innerHTML = `
            <span>${icons[type]}</span>
            <span>${message}</span>
        `;

        this.container.appendChild(toast);

        setTimeout(() => {
            toast.style.animation = 'toastOut 0.3s ease forwards';
            setTimeout(() => toast.remove(), 300);
        }, duration);
    }
}


/**
 * API Helper - wrapper for fetch with JWT refresh
 */
class API {
    static async request(url, options = {}) {
        const defaults = {
            headers: { 'Content-Type': 'application/json' },
        };

        let response = await fetch(url, { ...defaults, ...options });

        // If 401 - try refresh
        if (response.status === 401) {
            const refreshed = await this.refreshToken();
            if (refreshed) {
                response = await fetch(url, { ...defaults, ...options });
            } else {
                window.location.href = '/login';
                return null;
            }
        }

        return response;
    }

    static async refreshToken() {
        try {
            const res = await fetch('/api/v1/auth/refresh', { method: 'POST' });
            return res.ok;
        } catch {
            return false;
        }
    }
}


/**
 * Logout function
 */
async function logout() {
    try {
        await fetch('/api/v1/auth/logout', { method: 'POST' });
        window.location.href = '/login';
    } catch (e) {
        Toast.show('Logout failed', 'error');
    }
}


// Initialize on load
document.addEventListener('DOMContentLoaded', () => {
    Toast.init();
});

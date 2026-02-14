/**
 * Theme Manager
 * Saves choice in localStorage + syncs with server
 */
class ThemeManager {
    constructor() {
        this.currentTheme = this.getSavedTheme();
        this.apply(this.currentTheme);
        this.bindToggle();
    }

    getSavedTheme() {
        const saved = localStorage.getItem('theme');
        if (saved) return saved;

        return window.matchMedia('(prefers-color-scheme: dark)').matches
            ? 'dark'
            : 'light';
    }

    apply(theme) {
        document.documentElement.setAttribute('data-theme-transition', '');
        document.documentElement.setAttribute('data-theme', theme);
        this.currentTheme = theme;
        localStorage.setItem('theme', theme);

        setTimeout(() => {
            document.documentElement.removeAttribute('data-theme-transition');
        }, 500);
    }

    toggle() {
        const next = this.currentTheme === 'light' ? 'dark' : 'light';
        this.apply(next);
        this.syncWithServer(next);
    }

    async syncWithServer(theme) {
        try {
            await fetch('/api/v1/users/me/theme', {
                method: 'PATCH',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ theme }),
            });
        } catch (e) {
            // Not critical - localStorage already saved
        }
    }

    bindToggle() {
        document.querySelectorAll('.theme-toggle').forEach(btn => {
            btn.addEventListener('click', () => this.toggle());
        });
    }
}

// Initialize on load
const themeManager = new ThemeManager();

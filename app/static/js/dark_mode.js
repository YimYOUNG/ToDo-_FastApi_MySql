(function() {
    const THEME_KEY = 'theme_preference';

    function getSystemTheme() {
        return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    }

    function getSavedTheme() {
        return localStorage.getItem(THEME_KEY);
    }

    function setTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem(THEME_KEY, theme);

        const btn = document.getElementById('darkModeToggle');
        if (btn) {
            btn.textContent = theme === 'dark' ? '☀️' : '🌙';
            btn.title = theme === 'dark' ? '切换亮色模式' : '切换暗色模式';
        }
    }

    function initTheme() {
        const saved = getSavedTheme();
        if (saved) {
            setTheme(saved);
        } else {
            setTheme(getSystemTheme());
        }
    }

    function toggleDarkMode() {
        const current = document.documentElement.getAttribute('data-theme') || 'light';
        const next = current === 'dark' ? 'light' : 'dark';
        setTheme(next);
    }

    window.toggleDarkMode = toggleDarkMode;

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initTheme);
    } else {
        initTheme();
    }

    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
        if (!getSavedTheme()) {
            setTheme(e.matches ? 'dark' : 'light');
        }
    });
})();

/* Smart Campus shared light/dark theme.
   Include this script on every page so the home-page choice persists everywhere. */
(function () {
    const STORAGE_KEY = 'smartCampusTheme';

    function getSavedTheme() {
        try {
            const saved = localStorage.getItem(STORAGE_KEY);
            return saved === 'dark' ? 'dark' : 'light';
        } catch (error) {
            return 'light';
        }
    }

    function applyTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        const button = document.querySelector('.theme-toggle');
        if (button) {
            const dark = theme === 'dark';
            button.innerHTML = dark ? '☀️ Light mode' : '🌙 Dark mode';
            button.setAttribute('aria-label', dark ? 'Switch to light mode' : 'Switch to dark mode');
            button.setAttribute('aria-pressed', String(dark));
            button.title = dark ? 'Switch to light mode' : 'Switch to dark mode';
        }
    }

    function addToggle() {
        if (document.querySelector('.theme-toggle')) return;

        const button = document.createElement('button');
        button.type = 'button';
        button.className = 'theme-toggle';
        button.addEventListener('click', function () {
            const current = document.documentElement.getAttribute('data-theme') === 'dark' ? 'dark' : 'light';
            const next = current === 'dark' ? 'light' : 'dark';
            try { localStorage.setItem(STORAGE_KEY, next); } catch (error) { /* Theme still works for this page. */ }
            applyTheme(next);
        });

        const navLinks = document.querySelector('.nav-links');
        const navbar = document.querySelector('.navbar');
        const target = navLinks || navbar;
        if (target) {
            target.appendChild(button);
            applyTheme(document.documentElement.getAttribute('data-theme') || getSavedTheme());
        }
    }

    /* Apply before the page is fully ready to reduce light/dark flashing. */
    applyTheme(getSavedTheme());
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', addToggle);
    } else {
        addToggle();
    }
})();

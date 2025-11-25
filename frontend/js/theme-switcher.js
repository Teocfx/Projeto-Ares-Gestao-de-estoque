/**
 * Theme Switcher JavaScript
 * Gerencia a troca de temas (claro/escuro) e persiste no localStorage
 */

(function() {
    'use strict';
    
    const THEME_KEY = 'ares-theme';
    const THEMES = {
        LIGHT: 'light',
        DARK: 'dark'
    };
    
    /**
     * Obtém o tema atual do localStorage ou usa o padrão
     */
    function getCurrentTheme() {
        const savedTheme = localStorage.getItem(THEME_KEY);
        if (savedTheme && Object.values(THEMES).includes(savedTheme)) {
            return savedTheme;
        }
        
        // Detectar preferência do sistema
        if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
            return THEMES.DARK;
        }
        
        return THEMES.LIGHT;
    }
    
    /**
     * Aplica o tema ao documento
     */
    function applyTheme(theme) {
        const html = document.documentElement;
        
        // Atualizar data-theme e data-bs-theme
        html.setAttribute('data-theme', theme);
        html.setAttribute('data-bs-theme', theme);
        
        // Salvar no localStorage
        localStorage.setItem(THEME_KEY, theme);
        
        // Disparar evento customizado
        const event = new CustomEvent('themeChanged', {
            detail: { theme }
        });
        document.dispatchEvent(event);
        
        // Atualizar ícones dos botões
        updateThemeButtons(theme);
    }
    
    /**
     * Alterna entre temas
     */
    function toggleTheme() {
        const currentTheme = getCurrentTheme();
        const newTheme = currentTheme === THEMES.LIGHT ? THEMES.DARK : THEMES.LIGHT;
        applyTheme(newTheme);
        
        // Feedback visual
        showToast(`Tema ${newTheme === THEMES.DARK ? 'Escuro' : 'Claro'} ativado`);
    }
    
    /**
     * Atualiza os ícones dos botões do theme switcher
     */
    function updateThemeButtons(theme) {
        document.querySelectorAll('[data-theme-toggle]').forEach(button => {
            const iconLight = button.querySelector('.theme-icon-light');
            const iconDark = button.querySelector('.theme-icon-dark');
            const label = button.querySelector('.theme-label');
            
            if (theme === THEMES.DARK) {
                if (iconLight) iconLight.classList.add('d-none');
                if (iconDark) iconDark.classList.remove('d-none');
                if (label) label.textContent = 'Escuro';
                button.setAttribute('aria-label', 'Mudar para tema claro');
                button.setAttribute('title', 'Mudar para tema claro');
            } else {
                if (iconLight) iconLight.classList.remove('d-none');
                if (iconDark) iconDark.classList.add('d-none');
                if (label) label.textContent = 'Claro';
                button.setAttribute('aria-label', 'Mudar para tema escuro');
                button.setAttribute('title', 'Mudar para tema escuro');
            }
        });
    }
    
    /**
     * Mostra toast de feedback
     */
    function showToast(message) {
        // Verificar se Bootstrap Toast está disponível
        if (typeof bootstrap !== 'undefined' && bootstrap.Toast) {
            // Criar toast element se não existir
            let toastContainer = document.getElementById('theme-toast-container');
            if (!toastContainer) {
                toastContainer = document.createElement('div');
                toastContainer.id = 'theme-toast-container';
                toastContainer.className = 'toast-container position-fixed bottom-0 end-0 p-3';
                toastContainer.style.zIndex = '9999';
                document.body.appendChild(toastContainer);
            }
            
            const toastId = 'theme-toast-' + Date.now();
            const toastHtml = `
                <div id="${toastId}" class="toast align-items-center border-0" role="alert" aria-live="assertive" aria-atomic="true">
                    <div class="d-flex">
                        <div class="toast-body">
                            <i class="bi bi-check-circle me-2"></i>${message}
                        </div>
                        <button type="button" class="btn-close me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
                    </div>
                </div>
            `;
            
            toastContainer.insertAdjacentHTML('beforeend', toastHtml);
            const toastElement = document.getElementById(toastId);
            const toast = new bootstrap.Toast(toastElement, { delay: 2000 });
            toast.show();
            
            // Remover após esconder
            toastElement.addEventListener('hidden.bs.toast', () => {
                toastElement.remove();
            });
        }
    }
    
    /**
     * Inicializa o theme switcher
     */
    function init() {
        // Aplicar tema inicial imediatamente para evitar flash
        const initialTheme = getCurrentTheme();
        applyTheme(initialTheme);
        
        // Adicionar event listeners quando DOM estiver pronto
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', setupEventListeners);
        } else {
            setupEventListeners();
        }
    }
    
    /**
     * Configura event listeners
     */
    function setupEventListeners() {
        // Event listeners para botões de toggle
        document.querySelectorAll('[data-theme-toggle]').forEach(button => {
            button.addEventListener('click', (e) => {
                e.preventDefault();
                toggleTheme();
            });
        });
        
        // Atalho de teclado (Ctrl+Shift+T)
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey && e.shiftKey && e.key === 'T') {
                e.preventDefault();
                toggleTheme();
            }
        });
        
        // Detectar mudanças de preferência do sistema
        if (window.matchMedia) {
            window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
                // Só aplicar se o usuário não tiver preferência salva
                if (!localStorage.getItem(THEME_KEY)) {
                    applyTheme(e.matches ? THEMES.DARK : THEMES.LIGHT);
                }
            });
        }
        
        // Atualizar ícones iniciais
        updateThemeButtons(getCurrentTheme());
    }
    
    /**
     * API pública
     */
    window.ThemeSwitcher = {
        getCurrentTheme,
        applyTheme,
        toggleTheme,
        THEMES
    };
    
    // Inicializar
    init();
})();

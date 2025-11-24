/**
 * ARES - Gerenciador de Temas
 * Sistema de troca de temas com persistência em localStorage
 */

class ThemeManager {
    constructor() {
        this.themes = ['default', 'dark', 'high-contrast'];
        this.currentTheme = this.getStoredTheme() || this.getSystemTheme();
        this.init();
    }

    /**
     * Inicializa o gerenciador de temas
     */
    init() {
        this.applyTheme(this.currentTheme);
        this.setupEventListeners();
        this.detectSystemThemeChange();
    }

    /**
     * Obtém o tema armazenado no localStorage
     */
    getStoredTheme() {
        return localStorage.getItem('ares-theme');
    }

    /**
     * Obtém o tema do sistema operacional
     */
    getSystemTheme() {
        if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
            return 'dark';
        }
        if (window.matchMedia && window.matchMedia('(prefers-contrast: high)').matches) {
            return 'high-contrast';
        }
        return 'default';
    }

    /**
     * Aplica um tema
     * @param {string} theme - Nome do tema (default, dark, high-contrast)
     */
    applyTheme(theme) {
        if (!this.themes.includes(theme)) {
            console.error(`Tema "${theme}" não existe. Usando tema padrão.`);
            theme = 'default';
        }

        // Remove tema anterior
        document.documentElement.removeAttribute('data-theme');
        
        // Aplica novo tema
        if (theme !== 'default') {
            document.documentElement.setAttribute('data-theme', theme);
        }

        this.currentTheme = theme;
        localStorage.setItem('ares-theme', theme);

        // Dispara evento customizado
        window.dispatchEvent(new CustomEvent('themeChange', { 
            detail: { theme } 
        }));

        // Atualiza seletor de tema se existir
        this.updateThemeSelector();

        console.log(`✅ Tema aplicado: ${theme}`);
    }

    /**
     * Alterna para o próximo tema
     */
    cycleTheme() {
        const currentIndex = this.themes.indexOf(this.currentTheme);
        const nextIndex = (currentIndex + 1) % this.themes.length;
        this.applyTheme(this.themes[nextIndex]);
    }

    /**
     * Configura event listeners
     */
    setupEventListeners() {
        // Atalho de teclado: Alt + T para alternar tema
        document.addEventListener('keydown', (e) => {
            if (e.altKey && e.key === 't') {
                e.preventDefault();
                this.cycleTheme();
                this.showNotification(`Tema alterado para: ${this.getThemeName(this.currentTheme)}`);
            }
        });

        // Event listeners para botões de tema
        document.addEventListener('click', (e) => {
            if (e.target.matches('[data-theme-toggle]')) {
                const theme = e.target.getAttribute('data-theme-toggle');
                this.applyTheme(theme);
            }
        });
    }

    /**
     * Detecta mudanças no tema do sistema
     */
    detectSystemThemeChange() {
        if (window.matchMedia) {
            // Detectar mudança para modo escuro
            window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
                if (!this.getStoredTheme()) {
                    this.applyTheme(e.matches ? 'dark' : 'default');
                }
            });

            // Detectar mudança para alto contraste
            window.matchMedia('(prefers-contrast: high)').addEventListener('change', (e) => {
                if (!this.getStoredTheme() && e.matches) {
                    this.applyTheme('high-contrast');
                }
            });
        }
    }

    /**
     * Atualiza o seletor de tema na UI
     */
    updateThemeSelector() {
        const selector = document.getElementById('theme-selector');
        if (selector) {
            selector.value = this.currentTheme;
        }

        // Atualiza botões de tema
        document.querySelectorAll('[data-theme-toggle]').forEach(btn => {
            const theme = btn.getAttribute('data-theme-toggle');
            if (theme === this.currentTheme) {
                btn.classList.add('active');
                btn.setAttribute('aria-pressed', 'true');
            } else {
                btn.classList.remove('active');
                btn.setAttribute('aria-pressed', 'false');
            }
        });
    }

    /**
     * Retorna o nome amigável do tema
     */
    getThemeName(theme) {
        const names = {
            'default': 'Padrão',
            'dark': 'Escuro',
            'high-contrast': 'Alto Contraste'
        };
        return names[theme] || theme;
    }

    /**
     * Mostra notificação de mudança de tema
     */
    showNotification(message) {
        // Remove notificação existente
        const existing = document.getElementById('theme-notification');
        if (existing) {
            existing.remove();
        }

        // Cria nova notificação
        const notification = document.createElement('div');
        notification.id = 'theme-notification';
        notification.className = 'theme-notification';
        notification.textContent = message;
        notification.style.cssText = `
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: var(--color-primary);
            color: var(--text-inverse);
            padding: var(--spacing-md) var(--spacing-lg);
            border-radius: var(--border-radius-md);
            box-shadow: var(--shadow-lg);
            z-index: var(--z-tooltip);
            animation: slideInUp 0.3s ease;
        `;

        document.body.appendChild(notification);

        // Remove após 3 segundos
        setTimeout(() => {
            notification.style.animation = 'slideOutDown 0.3s ease';
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }

    /**
     * Cria widget de seleção de tema
     * @param {string} containerId - ID do elemento container
     */
    createThemeSelector(containerId) {
        const container = document.getElementById(containerId);
        if (!container) {
            console.error(`Container "${containerId}" não encontrado`);
            return;
        }

        const html = `
            <div class="theme-selector-widget">
                <label for="theme-selector" class="theme-selector-label">
                    <svg width="20" height="20" fill="currentColor" viewBox="0 0 16 16">
                        <path d="M8 11a3 3 0 1 1 0-6 3 3 0 0 1 0 6zm0 1a4 4 0 1 0 0-8 4 4 0 0 0 0 8zM8 0a.5.5 0 0 1 .5.5v2a.5.5 0 0 1-1 0v-2A.5.5 0 0 1 8 0zm0 13a.5.5 0 0 1 .5.5v2a.5.5 0 0 1-1 0v-2A.5.5 0 0 1 8 13zm8-5a.5.5 0 0 1-.5.5h-2a.5.5 0 0 1 0-1h2a.5.5 0 0 1 .5.5zM3 8a.5.5 0 0 1-.5.5h-2a.5.5 0 0 1 0-1h2A.5.5 0 0 1 3 8zm10.657-5.657a.5.5 0 0 1 0 .707l-1.414 1.415a.5.5 0 1 1-.707-.708l1.414-1.414a.5.5 0 0 1 .707 0zm-9.193 9.193a.5.5 0 0 1 0 .707L3.05 13.657a.5.5 0 0 1-.707-.707l1.414-1.414a.5.5 0 0 1 .707 0zm9.193 2.121a.5.5 0 0 1-.707 0l-1.414-1.414a.5.5 0 0 1 .707-.707l1.414 1.414a.5.5 0 0 1 0 .707zM4.464 4.465a.5.5 0 0 1-.707 0L2.343 3.05a.5.5 0 1 1 .707-.707l1.414 1.414a.5.5 0 0 1 0 .708z"/>
                    </svg>
                    Tema:
                </label>
                <select id="theme-selector" class="theme-selector-select">
                    <option value="default">Padrão</option>
                    <option value="dark">Escuro</option>
                    <option value="high-contrast">Alto Contraste</option>
                </select>
            </div>
        `;

        container.innerHTML = html;

        // Atualiza seletor com tema atual
        this.updateThemeSelector();

        // Event listener para mudança
        document.getElementById('theme-selector').addEventListener('change', (e) => {
            this.applyTheme(e.target.value);
        });
    }

    /**
     * Cria botões de tema (alternativa ao select)
     */
    createThemeButtons(containerId) {
        const container = document.getElementById(containerId);
        if (!container) {
            console.error(`Container "${containerId}" não encontrado`);
            return;
        }

        const html = `
            <div class="theme-buttons">
                <span class="theme-buttons-label">Tema:</span>
                <button 
                    type="button" 
                    data-theme-toggle="default" 
                    class="btn btn-sm"
                    aria-label="Tema Padrão"
                    title="Tema Padrão (Alt+T para alternar)">
                    ☀️ Padrão
                </button>
                <button 
                    type="button" 
                    data-theme-toggle="dark" 
                    class="btn btn-sm"
                    aria-label="Tema Escuro"
                    title="Tema Escuro (Alt+T para alternar)">
                    🌙 Escuro
                </button>
                <button 
                    type="button" 
                    data-theme-toggle="high-contrast" 
                    class="btn btn-sm"
                    aria-label="Alto Contraste"
                    title="Alto Contraste (Alt+T para alternar)">
                    ⚡ Alto Contraste
                </button>
            </div>
        `;

        container.innerHTML = html;
        this.updateThemeSelector();
    }
}

// Adiciona animações CSS
const style = document.createElement('style');
style.textContent = `
    @keyframes slideInUp {
        from {
            transform: translateY(100%);
            opacity: 0;
        }
        to {
            transform: translateY(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOutDown {
        from {
            transform: translateY(0);
            opacity: 1;
        }
        to {
            transform: translateY(100%);
            opacity: 0;
        }
    }

    .theme-selector-widget {
        display: flex;
        align-items: center;
        gap: var(--spacing-sm);
    }

    .theme-selector-label {
        display: flex;
        align-items: center;
        gap: var(--spacing-xs);
        font-weight: var(--font-weight-medium);
        color: var(--text-secondary);
        margin: 0;
    }

    .theme-selector-select {
        padding: var(--spacing-xs) var(--spacing-sm);
        border: var(--border-width) solid var(--border-color);
        border-radius: var(--border-radius-sm);
        background-color: var(--bg-primary);
        color: var(--text-primary);
        cursor: pointer;
        transition: all var(--transition-fast);
    }

    .theme-selector-select:focus {
        outline: none;
        border-color: var(--color-primary);
        box-shadow: 0 0 0 3px rgba(var(--color-primary-rgb), 0.1);
    }

    .theme-buttons {
        display: flex;
        align-items: center;
        gap: var(--spacing-sm);
        flex-wrap: wrap;
    }

    .theme-buttons-label {
        font-weight: var(--font-weight-medium);
        color: var(--text-secondary);
    }

    .theme-buttons button {
        transition: all var(--transition-fast);
    }

    .theme-buttons button.active {
        background-color: var(--color-primary);
        color: var(--text-inverse);
        box-shadow: var(--shadow-sm);
    }
`;
document.head.appendChild(style);

// Inicializa automaticamente ao carregar
let aresThemeManager;

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        aresThemeManager = new ThemeManager();
        window.aresThemeManager = aresThemeManager;
    });
} else {
    aresThemeManager = new ThemeManager();
    window.aresThemeManager = aresThemeManager;
}

// Exporta para uso global
window.ThemeManager = ThemeManager;

/**
 * Theme Manager
 * Sistema de gerenciamento de temas (padrão vermelho / escuro azul)
 * Sistema de Gestão de Estoque ARES
 */

class ThemeManager {
    constructor() {
        this.themes = ['ares-light', 'ares-dark', 'athena-light', 'athena-dark'];
        this.currentTheme = this.getStoredTheme() || 'ares-light';
        this.init();
    }

    init() {
        // Aplicar tema armazenado
        this.applyTheme(this.currentTheme);
        
        // Configurar event listeners
        this.setupEventListeners();
        
        // Criar widget de seleção de tema (se não existir)
        this.createThemeSelector();
    }

    /**
     * Obter tema armazenado do localStorage
     */
    getStoredTheme() {
        try {
            return localStorage.getItem('ares-theme');
        } catch (e) {
            console.warn('localStorage não disponível:', e);
            return null;
        }
    }

    /**
     * Armazenar tema no localStorage
     */
    setStoredTheme(theme) {
        try {
            localStorage.setItem('ares-theme', theme);
        } catch (e) {
            console.warn('Erro ao salvar tema:', e);
        }
    }

    /**
     * Aplicar tema ao documento
     */
    applyTheme(theme) {
        // Remover tema anterior
        document.documentElement.removeAttribute('data-theme');
        document.body.classList.remove('theme-default', 'theme-dark');
        
        // Aplicar novo tema
        if (theme !== 'default') {
            document.documentElement.setAttribute('data-theme', theme);
        }
        document.body.classList.add(`theme-${theme}`);
        
        this.currentTheme = theme;
        this.setStoredTheme(theme);
        
        // Atualizar widget de seleção
        this.updateThemeSelector();
        
        // Emitir evento customizado
        document.dispatchEvent(new CustomEvent('themeChanged', { 
            detail: { theme: theme } 
        }));
        
        console.log(`Tema aplicado: ${theme}`);
    }

    /**
     * Alternar entre temas
     */
    toggleTheme() {
        const currentIndex = this.themes.indexOf(this.currentTheme);
        const nextIndex = (currentIndex + 1) % this.themes.length;
        const nextTheme = this.themes[nextIndex];
        
        this.applyTheme(nextTheme);
    }

    /**
     * Definir tema específico
     */
    setTheme(theme) {
        if (this.themes.includes(theme)) {
            this.applyTheme(theme);
        } else {
            console.error(`Tema inválido: ${theme}`);
        }
    }

    /**
     * Configurar event listeners
     */
    setupEventListeners() {
        // Atalho de teclado: Alt + T
        document.addEventListener('keydown', (e) => {
            if (e.altKey && e.key === 't') {
                e.preventDefault();
                this.toggleTheme();
            }
        });

        // Event listener para botões de tema customizados
        document.addEventListener('click', (e) => {
            if (e.target.matches('[data-theme-toggle]')) {
                e.preventDefault();
                this.toggleTheme();
            }
            
            if (e.target.matches('[data-theme-set]')) {
                e.preventDefault();
                const theme = e.target.getAttribute('data-theme-set');
                this.setTheme(theme);
            }
        });
    }

    /**
     * Criar widget de seleção de tema
     */
    createThemeSelector() {
        // Verificar se já existe
        if (document.getElementById('theme-selector-widget')) {
            return;
        }

        // Criar widget flutuante
        const widget = document.createElement('div');
        widget.id = 'theme-selector-widget';
        widget.className = 'theme-selector-widget';
        widget.innerHTML = `
            <button class="theme-toggle-btn" data-theme-toggle title="Alternar tema (Alt + T)">
                <span class="theme-icon theme-icon-ares-light">🔴</span>
                <span class="theme-icon theme-icon-ares-dark">🔴</span>
                <span class="theme-icon theme-icon-athena-light">🔵</span>
                <span class="theme-icon theme-icon-athena-dark">🔵</span>
            </button>
            <div class="theme-options">
                <button data-theme-set="ares-light" class="theme-option" title="ARES Claro (Vermelho + Branco)">
                    🔴 ARES Claro
                </button>
                <button data-theme-set="ares-dark" class="theme-option" title="ARES Escuro (Vermelho + Preto)">
                    🔴 ARES Escuro
                </button>
                <button data-theme-set="athena-light" class="theme-option" title="ATHENA Claro (Azul + Branco)">
                    🔵 ATHENA Claro
                </button>
                <button data-theme-set="athena-dark" class="theme-option" title="ATHENA Escuro (Azul + Preto)">
                    🔵 ATHENA Escuro
                </button>
            </div>
        `;

        // Adicionar ao body
        document.body.appendChild(widget);

        // Toggle do menu de opções
        const toggleBtn = widget.querySelector('.theme-toggle-btn');
        const optionsMenu = widget.querySelector('.theme-options');

        toggleBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            optionsMenu.classList.toggle('show');
        });

        // Fechar menu ao clicar fora
        document.addEventListener('click', () => {
            optionsMenu.classList.remove('show');
        });

        // Atualizar estado inicial
        this.updateThemeSelector();
    }

    /**
     * Atualizar widget de seleção de tema
     */
    updateThemeSelector() {
        const widget = document.getElementById('theme-selector-widget');
        if (!widget) return;

        // Remover classe active de todos os botões
        widget.querySelectorAll('.theme-option').forEach(btn => {
            btn.classList.remove('active');
        });

        // Adicionar classe active ao botão do tema atual
        const activeBtn = widget.querySelector(`[data-theme-set="${this.currentTheme}"]`);
        if (activeBtn) {
            activeBtn.classList.add('active');
        }

        // Atualizar ícone do toggle button
        const icons = widget.querySelectorAll('.theme-icon');
        icons.forEach(icon => icon.style.display = 'none');
        
        const currentIcon = widget.querySelector(`.theme-icon-${this.currentTheme}`);
        if (currentIcon) {
            currentIcon.style.display = 'inline-block';
        }

        // Atualizar data-theme no widget
        widget.setAttribute('data-current-theme', this.currentTheme);
    }

    /**
     * Obter tema atual
     */
    getCurrentTheme() {
        return this.currentTheme;
    }

    /**
     * Verificar se é tema escuro
     */
    isDarkTheme() {
        return this.currentTheme.includes('dark');
    }
}

// Inicializar automaticamente quando o DOM estiver pronto
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.themeManager = new ThemeManager();
    });
} else {
    window.themeManager = new ThemeManager();
}

// Exportar para uso em módulos
export default ThemeManager;

/**
 * Módulo de validação e UX para inputs de código 2FA
 */

class TwoFactorInput {
    constructor(inputSelector) {
        this.input = document.querySelector(inputSelector);
        if (!this.input) {
            console.warn(`TwoFactorInput: Input ${inputSelector} não encontrado`);
            return;
        }
        
        this.form = this.input.form;
        this.autoSubmit = this.input.dataset.autoSubmit === 'true';
        this.init();
    }
    
    init() {
        this.attachEvents();
        this.input.focus();
    }
    
    attachEvents() {
        // Permitir apenas números
        this.input.addEventListener('input', (e) => this.filterNumeric(e));
        
        // Auto-submit quando completar (se habilitado)
        if (this.autoSubmit) {
            this.input.addEventListener('input', (e) => this.handleAutoSubmit(e));
        }
        
        // Adicionar feedback visual
        this.input.addEventListener('focus', () => this.handleFocus());
        this.input.addEventListener('blur', () => this.handleBlur());
    }
    
    filterNumeric(e) {
        const value = e.target.value;
        const filtered = value.replace(/[^0-9]/g, '');
        
        if (value !== filtered) {
            e.target.value = filtered;
        }
    }
    
    handleAutoSubmit(e) {
        const value = e.target.value;
        const maxLength = parseInt(e.target.maxLength) || 6;
        
        if (value.length === maxLength) {
            // Pequeno delay para o usuário ver o código completo
            setTimeout(() => {
                if (this.form && this.validateInput()) {
                    this.addLoadingState();
                    this.form.submit();
                }
            }, 300);
        }
    }
    
    validateInput() {
        const value = this.input.value;
        const pattern = this.input.pattern || '[0-9]{6}';
        const regex = new RegExp(pattern);
        
        return regex.test(value);
    }
    
    handleFocus() {
        this.input.parentElement?.classList.add('focused');
    }
    
    handleBlur() {
        this.input.parentElement?.classList.remove('focused');
    }
    
    addLoadingState() {
        const container = this.input.closest('.verify-2fa-container, .setup-2fa-container');
        if (container) {
            container.classList.add('loading');
        }
    }
    
    addErrorState() {
        const container = this.input.closest('.verify-2fa-container, .setup-2fa-container');
        if (container) {
            container.classList.add('error');
            
            // Remover estado de erro após animação
            setTimeout(() => {
                container.classList.remove('error');
            }, 500);
        }
    }
    
    addSuccessState() {
        const container = this.input.closest('.verify-2fa-container, .setup-2fa-container');
        if (container) {
            container.classList.add('success');
        }
    }
}

// Inicializar automaticamente quando o DOM estiver pronto
document.addEventListener('DOMContentLoaded', function() {
    const tokenInput = document.getElementById('token');
    if (tokenInput) {
        new TwoFactorInput('#token');
    }
});

// Exportar para uso em outros módulos se necessário
if (typeof module !== 'undefined' && module.exports) {
    module.exports = TwoFactorInput;
}

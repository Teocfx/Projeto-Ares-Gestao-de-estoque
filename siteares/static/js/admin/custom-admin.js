/**
 * ARES - Customizações JavaScript do Wagtail Admin
 * Sistema de Gestão de Estoque
 */

(function() {
    'use strict';

    /**
     * Inicialização quando o DOM estiver pronto
     */
    document.addEventListener('DOMContentLoaded', function() {
        initAresAdmin();
    });

    /**
     * Função principal de inicialização
     */
    function initAresAdmin() {
        addWelcomeMessage();
        enhanceStockIndicators();
        addKeyboardShortcuts();
        improveTableInteraction();
        addConfirmationDialogs();
    }

    /**
     * Adiciona mensagem de boas-vindas personalizada
     */
    function addWelcomeMessage() {
        const header = document.querySelector('.w-header');
        if (header && !document.querySelector('.ares-welcome')) {
            const now = new Date();
            const hour = now.getHours();
            let greeting = 'Bom dia';
            
            if (hour >= 12 && hour < 18) {
                greeting = 'Boa tarde';
            } else if (hour >= 18) {
                greeting = 'Boa noite';
            }
            
            const userName = document.querySelector('[data-account-settings]');
            if (userName) {
                const name = userName.textContent.trim();
                console.log(`${greeting}, ${name}! Bem-vindo ao ARES.`);
            }
        }
    }

    /**
     * Melhora indicadores de estoque
     */
    function enhanceStockIndicators() {
        // Adiciona indicadores visuais para status de estoque
        const stockCells = document.querySelectorAll('[data-stock-status]');
        
        stockCells.forEach(function(cell) {
            const status = cell.getAttribute('data-stock-status');
            const indicator = document.createElement('span');
            indicator.className = 'ares-indicator ares-indicator--' + status;
            cell.insertBefore(indicator, cell.firstChild);
        });
    }

    /**
     * Adiciona atalhos de teclado úteis
     */
    function addKeyboardShortcuts() {
        document.addEventListener('keydown', function(e) {
            // Ctrl/Cmd + K: Foco na busca
            if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
                e.preventDefault();
                const searchInput = document.querySelector('.w-search-input input');
                if (searchInput) {
                    searchInput.focus();
                    searchInput.select();
                }
            }
            
            // Ctrl/Cmd + S: Salvar (se estiver em formulário)
            if ((e.ctrlKey || e.metaKey) && e.key === 's') {
                const saveButton = document.querySelector('button[type="submit"].button-primary');
                if (saveButton) {
                    e.preventDefault();
                    saveButton.click();
                }
            }
            
            // ESC: Fechar modais
            if (e.key === 'Escape') {
                const closeButtons = document.querySelectorAll('.modal-close, [data-modal-close]');
                if (closeButtons.length > 0) {
                    closeButtons[0].click();
                }
            }
        });
    }

    /**
     * Melhora interação com tabelas
     */
    function improveTableInteraction() {
        // Adiciona ordenação visual
        const tableHeaders = document.querySelectorAll('.w-table th[data-sortable]');
        tableHeaders.forEach(function(header) {
            header.style.cursor = 'pointer';
            header.addEventListener('mouseenter', function() {
                this.style.backgroundColor = 'var(--ares-primary-light)';
            });
            header.addEventListener('mouseleave', function() {
                this.style.backgroundColor = '';
            });
        });

        // Highlight de linha ao passar o mouse
        const tableRows = document.querySelectorAll('.w-table tbody tr');
        tableRows.forEach(function(row) {
            row.addEventListener('click', function() {
                // Remove highlight de outras linhas
                tableRows.forEach(r => r.classList.remove('ares-row-selected'));
                // Adiciona highlight na linha clicada
                this.classList.add('ares-row-selected');
            });
        });
    }

    /**
     * Adiciona diálogos de confirmação para ações críticas
     */
    function addConfirmationDialogs() {
        // Confirmação para deletar
        const deleteLinks = document.querySelectorAll('a[href*="delete"], .button-danger');
        deleteLinks.forEach(function(link) {
            if (!link.hasAttribute('data-confirm-added')) {
                link.setAttribute('data-confirm-added', 'true');
                link.addEventListener('click', function(e) {
                    const confirmMessage = this.getAttribute('data-confirm-message') || 
                                         'Tem certeza que deseja excluir este item? Esta ação não pode ser desfeita.';
                    
                    if (!confirm(confirmMessage)) {
                        e.preventDefault();
                        return false;
                    }
                });
            }
        });
    }

    /**
     * Utilitário: Mostrar notificação toast
     */
    window.aresShowToast = function(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `ares-toast ares-toast--${type}`;
        toast.textContent = message;
        toast.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 15px 20px;
            background: var(--ares-${type});
            color: white;
            border-radius: 4px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            z-index: 9999;
            animation: slideInRight 0.3s ease;
        `;
        
        document.body.appendChild(toast);
        
        setTimeout(function() {
            toast.style.animation = 'slideOutRight 0.3s ease';
            setTimeout(function() {
                toast.remove();
            }, 300);
        }, 3000);
    };

    /**
     * Utilitário: Formatar números como moeda
     */
    window.aresFormatCurrency = function(value) {
        return new Intl.NumberFormat('pt-BR', {
            style: 'currency',
            currency: 'BRL'
        }).format(value);
    };

    /**
     * Utilitário: Formatar datas
     */
    window.aresFormatDate = function(date) {
        return new Intl.DateTimeFormat('pt-BR', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric'
        }).format(new Date(date));
    };

    /**
     * Adiciona animações CSS necessárias
     */
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideInRight {
            from {
                transform: translateX(100%);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }
        
        @keyframes slideOutRight {
            from {
                transform: translateX(0);
                opacity: 1;
            }
            to {
                transform: translateX(100%);
                opacity: 0;
            }
        }
        
        .ares-row-selected {
            background-color: #e8f5e9 !important;
            border-left: 3px solid var(--ares-success);
        }
        
        .ares-toast {
            font-weight: 500;
        }
        
        .ares-toast--success {
            background: var(--ares-success);
        }
        
        .ares-toast--warning {
            background: var(--ares-warning);
        }
        
        .ares-toast--danger {
            background: var(--ares-danger);
        }
        
        .ares-toast--info {
            background: var(--ares-info);
        }
    `;
    document.head.appendChild(style);

    /**
     * Log de inicialização
     */
    console.log('%c🎯 ARES Admin Customizado', 'color: #27ae60; font-weight: bold; font-size: 14px;');
    console.log('%cSistema de Gestão de Estoque', 'color: #2c3e50; font-size: 12px;');
    console.log('%cAtalhos disponíveis:', 'font-weight: bold;');
    console.log('• Ctrl/Cmd + K: Busca rápida');
    console.log('• Ctrl/Cmd + S: Salvar formulário');
    console.log('• ESC: Fechar modal');

})();

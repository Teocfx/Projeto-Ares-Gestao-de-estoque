/**
 * ==========================================================================
 * Gestão de Estoque - JavaScript Principal
 * Sistema completo de gestão de estoque
 * ==========================================================================
 */

(function() {
    'use strict';

    /**
     * Configurações globais do sistema
     */
    const EstoqueSystem = {
        config: {
            theme: 'light',
            notifications: true,
            autoSave: true,
            language: 'pt-BR',
            currency: 'BRL'
        },
        
        init: function() {
            this.setupEventListeners();
            this.initializeTheme();
            this.initializeTooltips();
            this.initializeBackToTop();
            this.initializeNotifications();
            this.initializeFormValidation();
            this.initializeTableFeatures();
            console.log('Sistema de Gestão de Estoque inicializado com sucesso!');
        },

        /**
         * Configurar event listeners globais
         */
        setupEventListeners: function() {
            // Theme toggle
            const themeToggle = document.getElementById('theme-toggle');
            if (themeToggle) {
                themeToggle.addEventListener('click', this.toggleTheme.bind(this));
            }

            // Loading overlay para formulários
            const forms = document.querySelectorAll('form[data-loading="true"]');
            forms.forEach(form => {
                form.addEventListener('submit', this.showLoading);
            });

            // Auto-dismiss alerts
            const alerts = document.querySelectorAll('.alert[data-auto-dismiss]');
            alerts.forEach(alert => {
                const timeout = alert.dataset.autoDismiss || 5000;
                setTimeout(() => {
                    this.fadeOut(alert);
                }, parseInt(timeout));
            });

            // Search functionality
            this.initializeSearch();

            // Print functionality
            const printBtns = document.querySelectorAll('[data-print]');
            printBtns.forEach(btn => {
                btn.addEventListener('click', this.handlePrint);
            });
        },

        /**
         * Inicializar tema do sistema
         */
        initializeTheme: function() {
            const savedTheme = localStorage.getItem('estoque-theme') || 'light';
            this.setTheme(savedTheme);
        },

        /**
         * Alternar tema
         */
        toggleTheme: function() {
            const currentTheme = document.documentElement.getAttribute('data-bs-theme');
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            this.setTheme(newTheme);
        },

        /**
         * Definir tema
         */
        setTheme: function(theme) {
            document.documentElement.setAttribute('data-bs-theme', theme);
            localStorage.setItem('estoque-theme', theme);
            
            const themeToggle = document.getElementById('theme-toggle');
            if (themeToggle) {
                const lightIcon = themeToggle.querySelector('.theme-icon-light');
                const darkIcon = themeToggle.querySelector('.theme-icon-dark');
                
                if (theme === 'dark') {
                    lightIcon?.classList.add('d-none');
                    darkIcon?.classList.remove('d-none');
                } else {
                    lightIcon?.classList.remove('d-none');
                    darkIcon?.classList.add('d-none');
                }
            }
            
            this.config.theme = theme;
        },

        /**
         * Inicializar tooltips do Bootstrap
         */
        initializeTooltips: function() {
            const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
            tooltipTriggerList.map(function (tooltipTriggerEl) {
                return new bootstrap.Tooltip(tooltipTriggerEl);
            });
        },

        /**
         * Inicializar botão "Voltar ao Topo"
         */
        initializeBackToTop: function() {
            const backToTopBtn = document.getElementById('backToTop');
            if (!backToTopBtn) return;

            // Mostrar/esconder botão baseado no scroll
            window.addEventListener('scroll', function() {
                if (window.pageYOffset > 300) {
                    backToTopBtn.classList.remove('d-none');
                } else {
                    backToTopBtn.classList.add('d-none');
                }
            });

            // Scroll suave para o topo
            backToTopBtn.addEventListener('click', function() {
                window.scrollTo({
                    top: 0,
                    behavior: 'smooth'
                });
            });
        },

        /**
         * Sistema de notificações
         */
        initializeNotifications: function() {
            // Verificar permissão para notificações
            if ('Notification' in window && this.config.notifications) {
                if (Notification.permission === 'default') {
                    Notification.requestPermission();
                }
            }
        },

        /**
         * Mostrar notificação
         */
        showNotification: function(title, options = {}) {
            if ('Notification' in window && Notification.permission === 'granted' && this.config.notifications) {
                const notification = new Notification(title, {
                    icon: '/static/img/logo.png',
                    badge: '/static/img/logo.png',
                    ...options
                });

                // Auto-fechar após 5 segundos
                setTimeout(() => notification.close(), 5000);

                return notification;
            }
        },

        /**
         * Inicializar validação de formulários
         */
        initializeFormValidation: function() {
            const forms = document.querySelectorAll('.needs-validation');
            
            Array.from(forms).forEach(form => {
                form.addEventListener('submit', event => {
                    if (!form.checkValidity()) {
                        event.preventDefault();
                        event.stopPropagation();
                        
                        // Focar no primeiro campo inválido
                        const firstInvalid = form.querySelector(':invalid');
                        if (firstInvalid) {
                            firstInvalid.focus();
                        }
                    }
                    
                    form.classList.add('was-validated');
                }, false);

                // Validação em tempo real
                const inputs = form.querySelectorAll('input, select, textarea');
                inputs.forEach(input => {
                    input.addEventListener('blur', () => {
                        if (form.classList.contains('was-validated')) {
                            input.classList.toggle('is-valid', input.checkValidity());
                            input.classList.toggle('is-invalid', !input.checkValidity());
                        }
                    });
                });
            });
        },

        /**
         * Funcionalidades de tabela
         */
        initializeTableFeatures: function() {
            // Seleção múltipla
            const selectAllCheckboxes = document.querySelectorAll('.select-all');
            selectAllCheckboxes.forEach(checkbox => {
                checkbox.addEventListener('change', function() {
                    const table = this.closest('table');
                    const rowCheckboxes = table.querySelectorAll('tbody input[type="checkbox"]');
                    
                    rowCheckboxes.forEach(cb => {
                        cb.checked = this.checked;
                        cb.dispatchEvent(new Event('change'));
                    });
                });
            });

            // Highlight de linhas selecionadas
            const rowCheckboxes = document.querySelectorAll('table tbody input[type="checkbox"]');
            rowCheckboxes.forEach(checkbox => {
                checkbox.addEventListener('change', function() {
                    const row = this.closest('tr');
                    row.classList.toggle('table-active', this.checked);
                    
                    // Atualizar botões de ação em lote
                    this.updateBatchActions();
                }.bind(this));
            });
        },

        /**
         * Atualizar botões de ação em lote
         */
        updateBatchActions: function() {
            const selectedCount = document.querySelectorAll('table tbody input[type="checkbox"]:checked').length;
            const batchActions = document.querySelectorAll('.batch-actions');
            
            batchActions.forEach(element => {
                element.style.display = selectedCount > 0 ? 'block' : 'none';
            });

            // Atualizar contador
            const counters = document.querySelectorAll('.selected-count');
            counters.forEach(counter => {
                counter.textContent = selectedCount;
            });
        },

        /**
         * Inicializar busca
         */
        initializeSearch: function() {
            const searchInputs = document.querySelectorAll('[data-search]');
            
            searchInputs.forEach(input => {
                const target = document.querySelector(input.dataset.search);
                if (!target) return;

                input.addEventListener('input', this.debounce(() => {
                    this.performSearch(input.value.toLowerCase(), target);
                }, 300));
            });
        },

        /**
         * Realizar busca na tabela
         */
        performSearch: function(searchTerm, target) {
            const rows = target.querySelectorAll('tbody tr');
            let visibleCount = 0;

            rows.forEach(row => {
                const text = row.textContent.toLowerCase();
                const isVisible = text.includes(searchTerm);
                
                row.style.display = isVisible ? '' : 'none';
                if (isVisible) visibleCount++;
            });

            // Mostrar mensagem se nenhum resultado encontrado
            this.toggleNoResults(target, visibleCount === 0);
        },

        /**
         * Mostrar/esconder mensagem de "nenhum resultado"
         */
        toggleNoResults: function(table, show) {
            let noResultsRow = table.querySelector('.no-results-row');
            
            if (show && !noResultsRow) {
                const tbody = table.querySelector('tbody');
                const colCount = table.querySelectorAll('thead th').length;
                
                noResultsRow = document.createElement('tr');
                noResultsRow.className = 'no-results-row';
                noResultsRow.innerHTML = `
                    <td colspan="${colCount}" class="text-center py-4 text-muted">
                        <i class="bi bi-search fs-1 mb-3 d-block"></i>
                        Nenhum resultado encontrado
                    </td>
                `;
                
                tbody.appendChild(noResultsRow);
            } else if (!show && noResultsRow) {
                noResultsRow.remove();
            }
        },

        /**
         * Mostrar loading overlay
         */
        showLoading: function() {
            const overlay = document.getElementById('loading-overlay');
            if (overlay) {
                overlay.classList.remove('d-none');
            }
        },

        /**
         * Esconder loading overlay
         */
        hideLoading: function() {
            const overlay = document.getElementById('loading-overlay');
            if (overlay) {
                overlay.classList.add('d-none');
            }
        },

        /**
         * Fade out elemento
         */
        fadeOut: function(element) {
            element.style.transition = 'opacity 0.3s ease';
            element.style.opacity = '0';
            
            setTimeout(() => {
                element.remove();
            }, 300);
        },

        /**
         * Confirmar ação
         */
        confirmAction: function(message, callback) {
            if (confirm(message)) {
                callback();
            }
        },

        /**
         * Formatar valor monetário
         */
        formatCurrency: function(value) {
            return new Intl.NumberFormat('pt-BR', {
                style: 'currency',
                currency: this.config.currency
            }).format(value);
        },

        /**
         * Formatar data
         */
        formatDate: function(date, options = {}) {
            const defaultOptions = {
                year: 'numeric',
                month: '2-digit',
                day: '2-digit'
            };
            
            return new Intl.DateTimeFormat(this.config.language, {
                ...defaultOptions,
                ...options
            }).format(new Date(date));
        },

        /**
         * Debounce function
         */
        debounce: function(func, wait) {
            let timeout;
            return function executedFunction(...args) {
                const later = () => {
                    clearTimeout(timeout);
                    func(...args);
                };
                clearTimeout(timeout);
                timeout = setTimeout(later, wait);
            };
        },

        /**
         * Manipular impressão
         */
        handlePrint: function(event) {
            event.preventDefault();
            
            const target = event.currentTarget.dataset.print;
            const element = target ? document.querySelector(target) : document.body;
            
            // Criar janela de impressão
            const printWindow = window.open('', '_blank');
            printWindow.document.write(`
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Gestão de Estoque - Impressão</title>
                    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
                    <style>
                        @media print {
                            .no-print { display: none !important; }
                            body { font-size: 12px; }
                            .table { font-size: 11px; }
                        }
                    </style>
                </head>
                <body class="p-3">
                    ${element.innerHTML}
                </body>
                </html>
            `);
            
            printWindow.document.close();
            printWindow.focus();
            
            // Aguardar carregamento e imprimir
            setTimeout(() => {
                printWindow.print();
                printWindow.close();
            }, 500);
        },

        /**
         * API Helper para requisições AJAX
         */
        api: {
            request: async function(url, options = {}) {
                const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value ||
                                document.querySelector('meta[name="csrf-token"]')?.getAttribute('content');

                const defaultOptions = {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken
                    },
                    credentials: 'same-origin'
                };

                try {
                    EstoqueSystem.showLoading();
                    
                    const response = await fetch(url, {
                        ...defaultOptions,
                        ...options,
                        headers: {
                            ...defaultOptions.headers,
                            ...options.headers
                        }
                    });

                    if (!response.ok) {
                        throw new Error(`HTTP error! status: ${response.status}`);
                    }

                    const data = await response.json();
                    return data;
                    
                } catch (error) {
                    console.error('API Error:', error);
                    EstoqueSystem.showNotification('Erro na comunicação com o servidor', {
                        body: error.message,
                        icon: '/static/img/error-icon.png'
                    });
                    throw error;
                } finally {
                    EstoqueSystem.hideLoading();
                }
            },

            get: function(url, options = {}) {
                return this.request(url, { ...options, method: 'GET' });
            },

            post: function(url, data, options = {}) {
                return this.request(url, {
                    ...options,
                    method: 'POST',
                    body: JSON.stringify(data)
                });
            },

            put: function(url, data, options = {}) {
                return this.request(url, {
                    ...options,
                    method: 'PUT',
                    body: JSON.stringify(data)
                });
            },

            delete: function(url, options = {}) {
                return this.request(url, { ...options, method: 'DELETE' });
            }
        }
    };

    // Aguardar DOM estar pronto
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            EstoqueSystem.init();
        });
    } else {
        EstoqueSystem.init();
    }

    // Expor sistema globalmente
    window.EstoqueSystem = EstoqueSystem;

})();
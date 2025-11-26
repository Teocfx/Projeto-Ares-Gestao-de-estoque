/**
 * Módulo de funcionalidade da página de busca
 */

class SearchPage {
    constructor() {
        this.searchForm = document.getElementById('search-form');
        this.searchInput = document.getElementById('search-input');
        this.headerSearch = document.querySelector('.header-input-search');
        
        if (!this.searchForm || !this.searchInput) {
            return;
        }
        
        this.init();
    }
    
    init() {
        this.syncHeaderSearch();
        this.attachFormEvents();
        this.attachTypeCheckboxEvents();
        this.attachDateRadioEvents();
        this.attachClearFiltersEvent();
    }
    
    syncHeaderSearch() {
        const urlParams = new URLSearchParams(window.location.search);
        const searchQuery = urlParams.get('query');
        
        if (this.headerSearch && searchQuery) {
            this.headerSearch.value = searchQuery;
        }
    }
    
    submitSearchForm() {
        const currentQuery = this.searchInput.value.trim();
        const params = new URLSearchParams();
        
        // Adiciona a query se existir
        if (currentQuery) {
            params.append('query', currentQuery);
        }
        
        // Adiciona tipos selecionados (exceto 'all')
        document.querySelectorAll('input[name="type"]:checked:not([value="all"])').forEach(checkbox => {
            params.append('type', checkbox.value);
        });
        
        // Adiciona filtro de data (se não for 'sempre')
        const selectedDate = document.querySelector('input[name="date"]:checked');
        if (selectedDate && selectedDate.value !== 'sempre') {
            params.append('date', selectedDate.value);
        }
        
        // Redireciona mantendo apenas os parâmetros relevantes
        window.location = '/search/' + (params.toString() ? '?' + params.toString() : '');
    }
    
    attachFormEvents() {
        this.searchForm.addEventListener('submit', (e) => {
            e.preventDefault();
            this.submitSearchForm();
        });
    }
    
    attachTypeCheckboxEvents() {
        const typeCheckboxes = document.querySelectorAll('input[name="type"]');
        
        typeCheckboxes.forEach(checkbox => {
            checkbox.addEventListener('change', () => {
                if (checkbox.value === 'all' && checkbox.checked) {
                    // Desmarca todos os outros checkboxes
                    document.querySelectorAll('input[name="type"]:not([value="all"])').forEach(cb => {
                        cb.checked = false;
                    });
                } else if (checkbox.value !== 'all' && checkbox.checked) {
                    // Desmarca "Todos" quando outro tipo é selecionado
                    const allCheckbox = document.querySelector('input[name="type"][value="all"]');
                    if (allCheckbox) {
                        allCheckbox.checked = false;
                    }
                }
                
                // Submete o formulário após mudança
                this.submitSearchForm();
            });
        });
    }
    
    attachDateRadioEvents() {
        const dateRadios = document.querySelectorAll('input[name="date"]');
        
        dateRadios.forEach(radio => {
            radio.addEventListener('change', () => {
                this.submitSearchForm();
            });
        });
    }
    
    attachClearFiltersEvent() {
        const clearFilters = document.querySelector('.clear-filters');
        
        if (clearFilters) {
            clearFilters.addEventListener('click', (e) => {
                e.preventDefault();
                
                // Redireciona mantendo apenas a query se existir
                const currentQuery = this.searchInput.value.trim();
                if (currentQuery) {
                    window.location = '/search/?query=' + encodeURIComponent(currentQuery);
                } else {
                    window.location = '/search/';
                }
            });
        }
    }
}

// Inicializa automaticamente quando o DOM estiver pronto
document.addEventListener('DOMContentLoaded', function() {
    new SearchPage();
});

// Exportar para uso em outros módulos se necessário
if (typeof module !== 'undefined' && module.exports) {
    module.exports = SearchPage;
}

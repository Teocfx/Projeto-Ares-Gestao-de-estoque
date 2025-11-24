/**
 * Produtos - Gerenciamento de Produtos
 * Sistema de Gestão de Estoque ARES
 */

document.addEventListener('DOMContentLoaded', function() {
    // Configurar seleção múltipla
    setupBulkSelection();
    
    // Configurar formulário de ações em lote
    setupBulkActions();
    
    // Auto-submit no formulário de busca (com delay)
    setupSearchForm();
});

/**
 * Configurar sistema de seleção múltipla de produtos
 */
function setupBulkSelection() {
    const selectAllCheckbox = document.getElementById('selectAll');
    if (!selectAllCheckbox) return;
    
    const itemCheckboxes = document.querySelectorAll('.product-checkbox');
    
    // Select all/none
    selectAllCheckbox.addEventListener('change', function() {
        itemCheckboxes.forEach(checkbox => {
            checkbox.checked = this.checked;
        });
        updateBulkActionsBar();
    });
    
    // Individual checkbox change
    itemCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            // Atualizar "select all" se necessário
            const allChecked = Array.from(itemCheckboxes).every(cb => cb.checked);
            const someChecked = Array.from(itemCheckboxes).some(cb => cb.checked);
            
            selectAllCheckbox.checked = allChecked;
            selectAllCheckbox.indeterminate = someChecked && !allChecked;
            
            updateBulkActionsBar();
        });
    });
}

/**
 * Atualizar barra de ações em lote
 */
function updateBulkActionsBar() {
    const checkedCount = document.querySelectorAll('.product-checkbox:checked').length;
    const bulkActionsBar = document.getElementById('bulkActionsBar');
    
    if (bulkActionsBar) {
        if (checkedCount > 0) {
            bulkActionsBar.classList.remove('d-none');
            const countSpan = bulkActionsBar.querySelector('.selected-count');
            if (countSpan) {
                countSpan.textContent = checkedCount;
            }
        } else {
            bulkActionsBar.classList.add('d-none');
        }
    }
}

/**
 * Configurar formulário de ações em lote
 */
function setupBulkActions() {
    const bulkActionForm = document.getElementById('bulkActionForm');
    if (!bulkActionForm) return;
    
    bulkActionForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const action = document.getElementById('bulkAction').value;
        const checkedBoxes = document.querySelectorAll('.product-checkbox:checked');
        
        if (!action) {
            alert('Selecione uma ação');
            return;
        }
        
        if (checkedBoxes.length === 0) {
            alert('Selecione pelo menos um produto');
            return;
        }
        
        // Confirmar ação
        const confirmMsg = `Tem certeza que deseja ${action} ${checkedBoxes.length} produto(s)?`;
        if (!confirm(confirmMsg)) {
            return;
        }
        
        // Coletar IDs dos produtos selecionados
        const productIds = Array.from(checkedBoxes).map(cb => cb.value);
        
        // Enviar via AJAX ou form submit
        console.log('Ação:', action, 'Produtos:', productIds);
        
        // TODO: Implementar envio real
        alert('Funcionalidade em desenvolvimento');
    });
}

/**
 * Auto-submit no formulário de busca (com delay para não sobrecarregar)
 */
function setupSearchForm() {
    const searchInput = document.getElementById('searchInput');
    if (!searchInput) return;
    
    let searchTimeout;
    
    searchInput.addEventListener('input', function() {
        clearTimeout(searchTimeout);
        
        searchTimeout = setTimeout(() => {
            // Auto-submit após 500ms de inatividade
            const form = this.closest('form');
            if (form) {
                form.submit();
            }
        }, 500);
    });
}

/**
 * Exportar produtos (função placeholder)
 */
window.exportProducts = function() {
    // TODO: Implementar exportação
    alert('Funcionalidade de exportação em desenvolvimento');
};

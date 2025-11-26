/**
 * Módulo de funcionalidade para tabelas
 */

document.addEventListener('DOMContentLoaded', function() {
    // Inicializar seleção múltipla em tabelas
    initTableSelection();
    
    // Inicializar ordenação
    initTableSorting();
});

function initTableSelection() {
    const selectAll = document.getElementById('selectAll');
    const rowSelects = document.querySelectorAll('.row-select');
    
    if (!selectAll || rowSelects.length === 0) return;

    selectAll.addEventListener('change', function() {
        rowSelects.forEach(checkbox => {
            checkbox.checked = this.checked;
        });
        updateSelectionState();
    });
    
    rowSelects.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            updateSelectionState();
        });
    });
}

function updateSelectionState() {
    const selectAll = document.getElementById('selectAll');
    const rowSelects = document.querySelectorAll('.row-select');
    
    if (!selectAll) return;
    
    const allChecked = Array.from(rowSelects).every(cb => cb.checked);
    const someChecked = Array.from(rowSelects).some(cb => cb.checked);
    
    selectAll.checked = allChecked;
    selectAll.indeterminate = someChecked && !allChecked;
}

function initTableSorting() {
    const sortableHeaders = document.querySelectorAll('.sortable');
    
    sortableHeaders.forEach(header => {
        header.addEventListener('click', function() {
            const field = this.dataset.field;
            const tableId = this.closest('table')?.id;
            
            // Dispatch evento customizado para permitir implementação externa
            document.dispatchEvent(new CustomEvent('tableSortRequested', {
                detail: { field, tableId }
            }));
        });
    });
}

// Exportar funções se necessário
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { initTableSelection, initTableSorting, updateSelectionState };
}

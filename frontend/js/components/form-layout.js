/**
 * Módulo de funcionalidade para formulários
 * Adiciona classes Bootstrap automaticamente
 */

document.addEventListener('DOMContentLoaded', function() {
    const forms = document.querySelectorAll('.form-layout-wrapper form');
    
    forms.forEach(form => {
        enhanceFormFields(form);
    });
});

function enhanceFormFields(form) {
    // Inputs de texto, email, número, etc
    const textInputs = form.querySelectorAll(
        'input[type="text"], input[type="email"], input[type="number"], ' +
        'input[type="password"], input[type="date"], input[type="time"], ' +
        'input[type="url"], textarea'
    );
    
    textInputs.forEach(input => {
        if (!input.classList.contains('form-control')) {
            input.classList.add('form-control');
        }
    });
    
    // Selects
    form.querySelectorAll('select').forEach(select => {
        if (!select.classList.contains('form-select')) {
            select.classList.add('form-select');
        }
    });
    
    // Checkboxes
    form.querySelectorAll('input[type="checkbox"]').forEach(checkbox => {
        if (!checkbox.classList.contains('form-check-input')) {
            checkbox.classList.add('form-check-input');
        }
    });
    
    // Radio buttons
    form.querySelectorAll('input[type="radio"]').forEach(radio => {
        if (!radio.classList.contains('form-check-input')) {
            radio.classList.add('form-check-input');
        }
    });
}

// Exportar se necessário
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { enhanceFormFields };
}

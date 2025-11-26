/**
 * Módulo do Menu Wrapper (menu flutuante)
 */

document.addEventListener('DOMContentLoaded', function() {
    const toggle = document.getElementById('menuWrapperToggle');
    const content = document.getElementById('menuWrapperContent');
    const close = document.getElementById('menuWrapperClose');
    
    if (!toggle || !content) return;

    // Toggle do menu
    toggle.addEventListener('click', function(e) {
        e.stopPropagation();
        content.classList.toggle('show');
    });

    // Fechar com botão X
    if (close) {
        close.addEventListener('click', function() {
            content.classList.remove('show');
        });
    }

    // Fechar ao clicar fora
    document.addEventListener('click', function(e) {
        if (!content.contains(e.target) && !toggle.contains(e.target)) {
            content.classList.remove('show');
        }
    });
});

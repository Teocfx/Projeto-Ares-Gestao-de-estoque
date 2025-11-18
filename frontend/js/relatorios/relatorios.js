/**
 * Relatórios - Efeitos Visuais e Interações
 * Sistema de Gestão de Estoque ARES
 */

document.addEventListener('DOMContentLoaded', function() {
    const reportCards = document.querySelectorAll('.report-card');
    
    // Adicionar efeitos visuais nos cards
    reportCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.borderColor = 'var(--primary-color)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.borderColor = '';
        });
    });
});

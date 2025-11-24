/**
 * Filtros Automáticos
 * Sistema de filtros com auto-submit
 */

(function() {
    document.addEventListener('DOMContentLoaded', function() {
        const filtroAno = document.getElementById('filtroAno');
        const filtroTag = document.getElementById('filtroTag');
        const form = document.getElementById('filtrosForm');
        
        if (!form) return;
        
        // Função para submeter o formulário com loading
        function submitFormWithLoading() {
            const button = form.querySelector('button[type="submit"]');
            if (!button) return;
            
            const originalText = button.textContent;
            button.innerHTML = '<span class="carregamento-pequeno"></span>Filtrando...';
            button.disabled = true;
            
            form.submit();
        }
        
        // Event listeners para os selects
        if (filtroAno) {
            filtroAno.addEventListener('change', submitFormWithLoading);
        }
        
        if (filtroTag) {
            filtroTag.addEventListener('change', submitFormWithLoading);
        }
        
        // Previne a submissão dupla
        form.addEventListener('submit', function(e) {
            const button = form.querySelector('button[type="submit"]');
            if (button && button.disabled) {
                e.preventDefault();
                return false;
            }
            
            if (button) {
                setTimeout(() => {
                    button.innerHTML = '<span class="carregamento-pequeno"></span>Filtrando...';
                    button.disabled = true;
                }, 100);
            }
        });
    });
})();

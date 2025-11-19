document.addEventListener('DOMContentLoaded', function() {
    const toggleButton = document.querySelector('.site-menu-navbar-toggler');
    const navbarCollapse = document.querySelector('.site-menu-navbar-collapse');
    
    // Função para calcular e definir a posição top do navbar collapse
    function calculateNavbarPosition() {
        const mobileNavbar = document.querySelector('.site-menu-navbar-mobile');
        const navbarCollapse = document.querySelector('.site-menu-navbar-collapse');
        // const barraBrasil = document.getElementById('barra-brasil'); // Comentado temporariamente

        console.info('Calculando posição do navbar collapse');
        
        if (mobileNavbar && navbarCollapse) {
            const mobileRect = mobileNavbar.getBoundingClientRect();
            let topPosition = mobileRect.height;

            console.info('Altura do navbar mobile:', mobileRect.height);
            
            // Adiciona a altura da barra-brasil se ela existir
            // if (barraBrasil) {
            //     const barraRect = barraBrasil.getBoundingClientRect();
            //     topPosition += barraRect.height;
            // }
            
            navbarCollapse.style.top = `${topPosition}px`;
            console.info('navbarCollapse.style.top:', navbarCollapse.style.top);
        }
    }

    // Criar backdrop para fechar menu ao clicar fora
    function createBackdrop() {
        // Remover backdrop existente primeiro
        removeBackdrop();

        const backdrop = document.createElement('div');
        backdrop.className = 'modal-backdrop-trigger';
        backdrop.style.cssText = 'position: fixed; top: 0; left: 0; width: 100%; height: 100%; background-color: rgba(0,0,0,0.5); z-index: 1020;';
        
        backdrop.addEventListener('click', function() {
            if (navbarCollapse) {
                navbarCollapse.classList.remove('show');
            }
            if (toggleButton) {
                toggleButton.setAttribute('aria-expanded', 'false');
                toggleButton.classList.add('collapsed');
            }
            removeBackdrop();
        });

        document.body.appendChild(backdrop);
    }

    function removeBackdrop() {
        const existingBackdrop = document.querySelector('.modal-backdrop-trigger');
        if (existingBackdrop) {
            existingBackdrop.remove();
        }
    }
    
    if (toggleButton) {
        toggleButton.addEventListener('click', function() {
            console.log('click');

            // Calcula a posição usando a função
            calculateNavbarPosition();
            
            // Gerenciar backdrop baseado no estado do menu
            const isExpanded = toggleButton.getAttribute('aria-expanded') === 'true';
            if (isExpanded) {
                createBackdrop();
            } else {
                removeBackdrop();
            }
        });
    }

    // Listener para resize da tela - recalcula posição do menu
    window.addEventListener('resize', function() {
        const toggleButton = document.querySelector('.site-menu-navbar-toggler');
        const isExpanded = toggleButton ? toggleButton.getAttribute('aria-expanded') === 'true' : false;
        
        if (isExpanded && window.innerWidth <= 992) {
            calculateNavbarPosition();
        }
        
        // Remover backdrop se janela for maior que 992px
        if (window.innerWidth >= 992) {
            removeBackdrop();
        }
    });
});
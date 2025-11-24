/**
 * Login Page - Form Validation and Effects
 * Extracted from: autenticacao/templates/autenticacao/login.html
 */

document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('.login-form form');
    const inputs = document.querySelectorAll('.form-control');
    const container = document.querySelector('.login-container');
    
    if (!form || !container) return;
    
    // Add focus effects to inputs
    inputs.forEach(input => {
        input.addEventListener('focus', function() {
            this.parentElement.classList.add('focused');
        });
        
        input.addEventListener('blur', function() {
            this.parentElement.classList.remove('focused');
        });
    });
    
    // Form validation
    form.addEventListener('submit', function(e) {
        let isValid = true;
        
        inputs.forEach(input => {
            if (!input.value.trim()) {
                input.style.borderColor = '#dc3545';
                isValid = false;
            } else {
                input.style.borderColor = '#e9ecef';
            }
        });
        
        if (!isValid) {
            e.preventDefault();
            
            // Show error message
            let existingAlert = document.querySelector('.alert-danger');
            if (!existingAlert) {
                const alert = document.createElement('div');
                alert.className = 'alert alert-danger';
                alert.textContent = '⚠️ Por favor, preencha todos os campos.';
                form.insertBefore(alert, form.firstChild);
                
                // Remove alert after 3 seconds
                setTimeout(() => {
                    alert.remove();
                }, 3000);
            }
        }
    });
    
    // Entry animation
    container.style.opacity = '0';
    container.style.transform = 'translateY(20px)';
    
    setTimeout(() => {
        container.style.transition = 'all 0.5s ease';
        container.style.opacity = '1';
        container.style.transform = 'translateY(0)';
    }, 100);
});

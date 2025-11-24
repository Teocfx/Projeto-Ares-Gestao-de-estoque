/**
 * Movimentações - Formulário Dinâmico
 * Sistema de Gestão de Estoque ARES
 */

document.addEventListener('DOMContentLoaded', function() {
    const productSelect = document.getElementById('id_product');
    const typeSelect = document.getElementById('id_type');
    const quantityInput = document.getElementById('id_quantity');
    const productInfo = document.getElementById('productInfo');
    
    if (!productSelect || !typeSelect || !quantityInput) return;
    
    // Função para buscar informações do produto
    function updateProductInfo(productId) {
        if (!productId) {
            if (productInfo) {
                productInfo.classList.remove('show');
            }
            return;
        }
        
        fetch(`/movimentacoes/api/product-stock/${productId}/`)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    const currentStockEl = document.getElementById('currentStock');
                    const minStockEl = document.getElementById('minStock');
                    const statusElement = document.getElementById('stockStatus');
                    
                    if (currentStockEl) {
                        currentStockEl.textContent = `${data.current_stock} ${data.unit}`;
                    }
                    if (minStockEl) {
                        minStockEl.textContent = `${data.min_stock} ${data.unit}`;
                    }
                    
                    // Atualizar classe e status baseado no estoque
                    if (currentStockEl) {
                        currentStockEl.className = 'stock-indicator';
                        if (data.status === 'CRITICO') {
                            currentStockEl.classList.add('stock-critico');
                            if (statusElement) {
                                statusElement.innerHTML = '<span class="badge bg-danger">Crítico</span>';
                            }
                        } else if (data.status === 'BAIXO') {
                            currentStockEl.classList.add('stock-baixo');
                            if (statusElement) {
                                statusElement.innerHTML = '<span class="badge bg-warning">Baixo</span>';
                            }
                        } else {
                            currentStockEl.classList.add('stock-ok');
                            if (statusElement) {
                                statusElement.innerHTML = '<span class="badge bg-success">OK</span>';
                            }
                        }
                    }
                    
                    if (productInfo) {
                        productInfo.classList.add('show');
                    }
                } else {
                    console.error('Erro ao buscar produto:', data.error);
                    if (productInfo) {
                        productInfo.classList.remove('show');
                    }
                }
            })
            .catch(error => {
                console.error('Erro na requisição:', error);
                if (productInfo) {
                    productInfo.classList.remove('show');
                }
            });
    }
    
    // Função para atualizar comportamento baseado no tipo
    function updateFormBehavior(type) {
        const quantityLabel = document.querySelector('label[for="id_quantity"]');
        
        if (!quantityLabel) return;
        
        if (type === 'AJUSTE') {
            quantityInput.placeholder = 'Valor final desejado (ex: 50.00)';
            quantityLabel.innerHTML = 'Quantidade Final <span class="text-danger">*</span>';
        } else if (type === 'ENTRADA') {
            quantityInput.placeholder = 'Quantidade a adicionar (ex: 10.50)';
            quantityLabel.innerHTML = 'Quantidade a Adicionar <span class="text-danger">*</span>';
        } else if (type === 'SAIDA') {
            quantityInput.placeholder = 'Quantidade a retirar (ex: 5.25)';
            quantityLabel.innerHTML = 'Quantidade a Retirar <span class="text-danger">*</span>';
        }
    }
    
    // Event listeners
    productSelect.addEventListener('change', function() {
        updateProductInfo(this.value);
    });
    
    typeSelect.addEventListener('change', function() {
        updateFormBehavior(this.value);
    });
    
    // Inicializar se já houver valores
    if (productSelect.value) {
        updateProductInfo(productSelect.value);
    }
    if (typeSelect.value) {
        updateFormBehavior(typeSelect.value);
    }
});

// Disponibilizar funções globalmente para uso nos widgets
window.updateProductInfo = function(productId) {
    const productSelect = document.getElementById('id_product');
    if (productSelect) {
        productSelect.value = productId;
        productSelect.dispatchEvent(new Event('change'));
    }
};

window.updateFormBehavior = function(type) {
    const typeSelect = document.getElementById('id_type');
    if (typeSelect) {
        typeSelect.value = type;
        typeSelect.dispatchEvent(new Event('change'));
    }
};

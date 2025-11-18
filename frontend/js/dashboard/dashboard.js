/**
 * Dashboard - Gráficos e Estatísticas
 * Sistema de Gestão de Estoque ARES
 */

document.addEventListener('DOMContentLoaded', function() {
    // Verifica se há produtos disponíveis
    const hasProducts = document.body.dataset.hasProducts === 'true';
    
    if (hasProducts) {
        initStockStatusChart();
    }
    
    initMovimentacoesChart();
    setupAutoRefresh();
});

/**
 * Inicializa o gráfico de status do estoque (doughnut)
 */
function initStockStatusChart() {
    const ctx = document.getElementById('stockStatusChart');
    if (!ctx) return;
    
    // Pega dados do DOM (data attributes)
    const okStock = parseInt(ctx.dataset.okStock) || 0;
    const lowStock = parseInt(ctx.dataset.lowStock) || 0;
    const criticalStock = parseInt(ctx.dataset.criticalStock) || 0;
    
    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Estoque OK', 'Estoque Baixo', 'Estoque Crítico'],
            datasets: [{
                data: [okStock, lowStock, criticalStock],
                backgroundColor: [
                    '#198754', // Verde - OK
                    '#ffc107', // Amarelo - Baixo  
                    '#dc3545'  // Vermelho - Crítico
                ],
                borderWidth: 2,
                borderColor: '#fff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        padding: 20,
                        usePointStyle: true
                    }
                }
            }
        }
    });
}

/**
 * Inicializa o gráfico de movimentações (linha)
 */
function initMovimentacoesChart() {
    const ctx = document.getElementById('movimentacoesChart');
    if (!ctx) return;
    
    // Dados simulados (em produção viriam do backend)
    const entradasData = [12, 19, 3, 5, 2, 3, 7];
    const saidasData = [5, 8, 12, 15, 8, 10, 5];
    
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb', 'Dom'],
            datasets: [{
                label: 'Entradas',
                data: entradasData,
                borderColor: 'rgb(25, 135, 84)',
                backgroundColor: 'rgba(25, 135, 84, 0.1)',
                tension: 0.4
            }, {
                label: 'Saídas',
                data: saidasData,
                borderColor: 'rgb(220, 53, 69)',
                backgroundColor: 'rgba(220, 53, 69, 0.1)',
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'top'
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(0,0,0,0.05)'
                    }
                },
                x: {
                    grid: {
                        display: false
                    }
                }
            }
        }
    });
}

/**
 * Auto-refresh da página a cada 5 minutos
 */
function setupAutoRefresh() {
    setTimeout(function() {
        location.reload();
    }, 300000); // 5 minutos
}

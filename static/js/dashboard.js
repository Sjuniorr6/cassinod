// Dashboard JavaScript

document.addEventListener('DOMContentLoaded', function() {
    console.log('🎯 Dashboard carregado');
    
    // Inicializar funcionalidades
    initFiltros();
    initAnimações();
    initAtualizaçõesAutomáticas();
});

// Inicializar filtros de data
function initFiltros() {
    const filtroForm = document.getElementById('filtroDatas');
    if (filtroForm) {
        filtroForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const dataInicio = document.getElementById('dataInicio').value;
            const dataFim = document.getElementById('dataFim').value;
            
            if (dataInicio && dataFim) {
                // Redirecionar com os parâmetros de data
                const url = new URL(window.location);
                url.searchParams.set('data_inicio', dataInicio);
                url.searchParams.set('data_fim', dataFim);
                window.location.href = url.toString();
            }
        });
    }
}

// Inicializar animações
function initAnimações() {
    // Animar cards quando entram na viewport
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);
    
    // Observar todos os cards
    document.querySelectorAll('.bg-white\\/95').forEach(card => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        card.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(card);
    });
}

// Atualizações automáticas
function initAtualizaçõesAutomáticas() {
    // Atualizar dados a cada 5 minutos
    setInterval(atualizarDados, 5 * 60 * 1000);
}

// Função para atualizar dados via API
async function atualizarDados() {
    try {
        const dataInicio = document.getElementById('dataInicio')?.value;
        const dataFim = document.getElementById('dataFim')?.value;
        
        const params = new URLSearchParams();
        if (dataInicio) params.append('data_inicio', dataInicio);
        if (dataFim) params.append('data_fim', dataFim);
        
        const response = await fetch(`/dashboard/api/estatisticas/?${params}`);
        const data = await response.json();
        
        if (data.success) {
            atualizarInterface(data.data);
        }
    } catch (error) {
        console.error('Erro ao atualizar dados:', error);
    }
}

// Atualizar interface com novos dados
function atualizarInterface(data) {
    // Atualizar top sanges
    atualizarTopSanges(data.top_sanges);
    
    // Atualizar top clientes
    atualizarTopClientes(data.top_clientes);
    
    // Atualizar gráficos
    atualizarGráficos(data);
    
    console.log('✅ Dados atualizados com sucesso');
}

// Atualizar top sanges
function atualizarTopSanges(topSanges) {
    const container = document.querySelector('.bg-white\\/95:nth-child(1) .space-y-3');
    if (!container) return;
    
    container.innerHTML = '';
    
    if (topSanges.length === 0) {
        container.innerHTML = `
            <div class="text-center text-gray-500 py-8">
                <svg class="w-12 h-12 mx-auto mb-4 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
                </svg>
                <p>Nenhuma venda registrada ainda</p>
            </div>
        `;
        return;
    }
    
    topSanges.forEach((sange, index) => {
        const item = document.createElement('div');
        item.className = 'flex items-center justify-between p-3 bg-gray-50 rounded-lg';
        item.innerHTML = `
            <div class="flex items-center gap-3">
                <div class="w-8 h-8 bg-red-100 rounded-full flex items-center justify-center">
                    <span class="text-sm font-bold text-red-600">${index + 1}</span>
                </div>
                <div>
                    <div class="font-semibold text-gray-800">${sange.nome}</div>
                    <div class="text-sm text-gray-600">${sange.total_vendas.toLocaleString()} vendas</div>
                </div>
            </div>
            <div class="text-right">
                <div class="font-bold text-red-600">R$ ${sange.total_vendas.toLocaleString()}</div>
            </div>
        `;
        container.appendChild(item);
    });
}

// Atualizar top clientes
function atualizarTopClientes(topClientes) {
    const container = document.querySelector('.bg-white\\/95:nth-child(2) .space-y-3');
    if (!container) return;
    
    container.innerHTML = '';
    
    if (topClientes.length === 0) {
        container.innerHTML = `
            <div class="text-center text-gray-500 py-8">
                <svg class="w-12 h-12 mx-auto mb-4 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path>
                </svg>
                <p>Nenhum cliente registrado ainda</p>
            </div>
        `;
        return;
    }
    
    topClientes.forEach((cliente, index) => {
        const item = document.createElement('div');
        item.className = 'flex items-center justify-between p-3 bg-gray-50 rounded-lg';
        item.innerHTML = `
            <div class="flex items-center gap-3">
                <div class="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                    <span class="text-sm font-bold text-blue-600">${index + 1}</span>
                </div>
                <div>
                    <div class="font-semibold text-gray-800">${cliente.nome}</div>
                    <div class="text-sm text-gray-600">${cliente.total_compras.toLocaleString()} compras</div>
                </div>
            </div>
            <div class="text-right">
                <div class="font-bold text-blue-600">R$ ${cliente.total_compras.toLocaleString()}</div>
            </div>
        `;
        container.appendChild(item);
    });
}

// Atualizar gráficos
function atualizarGráficos(data) {
    // Atualizar gráfico de vendas por dia
    if (window.chartVendasPorDia && data.vendas_por_dia) {
        window.chartVendasPorDia.data.datasets[0].data = Object.values(data.vendas_por_dia);
        window.chartVendasPorDia.update();
    }
    
    // Atualizar gráfico de vendas por hora
    if (window.chartVendasPorHora && data.vendas_por_hora) {
        window.chartVendasPorHora.data.datasets[0].data = Object.values(data.vendas_por_hora);
        window.chartVendasPorHora.update();
    }
}

// Função para exportar dados
function exportarDados() {
    const dataInicio = document.getElementById('dataInicio')?.value;
    const dataFim = document.getElementById('dataFim')?.value;
    
    const params = new URLSearchParams();
    if (dataInicio) params.append('data_inicio', dataInicio);
    if (dataFim) params.append('data_fim', dataFim);
    
    // Criar link de download
    const link = document.createElement('a');
    link.href = `/dashboard/api/estatisticas/?${params}&format=csv`;
    link.download = `dashboard_${dataInicio || 'inicio'}_${dataFim || 'fim'}.csv`;
    link.click();
}

// Função para imprimir dashboard
function imprimirDashboard() {
    window.print();
}

// Função para compartilhar dashboard
function compartilharDashboard() {
    if (navigator.share) {
        navigator.share({
            title: 'Dashboard Saint Paul',
            text: 'Confira as estatísticas do cassino',
            url: window.location.href
        });
    } else {
        // Fallback para copiar URL
        navigator.clipboard.writeText(window.location.href).then(() => {
            alert('URL copiada para a área de transferência!');
        });
    }
}

// Função para alternar modo escuro (futuro)
function alternarModoEscuro() {
    document.body.classList.toggle('dark-mode');
    localStorage.setItem('darkMode', document.body.classList.contains('dark-mode'));
}

// Verificar preferência de modo escuro
function verificarModoEscuro() {
    const darkMode = localStorage.getItem('darkMode') === 'true';
    if (darkMode) {
        document.body.classList.add('dark-mode');
    }
}

// Inicializar verificações
verificarModoEscuro();

// Expor funções globalmente
window.dashboard = {
    exportarDados,
    imprimirDashboard,
    compartilharDashboard,
    alternarModoEscuro,
    atualizarDados
};

console.log('🎯 Dashboard inicializado com sucesso');
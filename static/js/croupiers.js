// ===== CROUPIERS PAGE JAVASCRIPT =====

// URLs das APIs
window.API_URLS = {
    criarCroupier: '/croupiers/api/criar/',
    editarCroupier: '/croupiers/api/0/editar/',
    excluirCroupier: '/croupiers/api/0/excluir/',
    obterCroupier: '/croupiers/api/0/',
};

// Variáveis globais
let croupierParaExcluir = null;

document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Página de Croupiers carregada');
    
    // Animar entrada dos elementos
    animateElements();
    
    // Configurar interações
    setupInteractions();
    
    // Configurar responsividade
    setupResponsiveness();
    
    // Configurar formulários
    setupForms();
});

// Animar elementos na entrada
function animateElements() {
    const elements = document.querySelectorAll('.metric-card, .croupiers-table');
    
    elements.forEach((element, index) => {
        element.style.opacity = '0';
        element.style.transform = 'translateY(30px)';
        
        setTimeout(() => {
            element.style.transition = 'all 0.6s ease-out';
            element.style.opacity = '1';
            element.style.transform = 'translateY(0)';
        }, index * 200);
    });
}

// Configurar interações
function setupInteractions() {
    // Hover effects para cards de métricas
    const metricCards = document.querySelectorAll('.metric-card');
    metricCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px) scale(1.02)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
        });
    });
    
    // Hover effects para linhas da tabela
    const tableRows = document.querySelectorAll('tbody tr');
    tableRows.forEach(row => {
        row.addEventListener('mouseenter', function() {
            this.style.backgroundColor = 'rgba(59, 130, 246, 0.05)';
        });
        
        row.addEventListener('mouseleave', function() {
            this.style.backgroundColor = '';
        });
    });
    
    // Botões de ação
    const actionButtons = document.querySelectorAll('.btn-primary, .btn-secondary');
    actionButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            // Efeito de ripple
            const ripple = document.createElement('span');
            const rect = this.getBoundingClientRect();
            const size = Math.max(rect.width, rect.height);
            const x = e.clientX - rect.left - size / 2;
            const y = e.clientY - rect.top - size / 2;
            
            ripple.style.width = ripple.style.height = size + 'px';
            ripple.style.left = x + 'px';
            ripple.style.top = y + 'px';
            ripple.classList.add('ripple');
            
            this.appendChild(ripple);
            
            setTimeout(() => {
                ripple.remove();
            }, 600);
        });
    });
}

// Configurar formulários
function setupForms() {
    // Formulário de criar croupier
    const formCriarCroupier = document.getElementById('formCriarCroupier');
    if (formCriarCroupier) {
        formCriarCroupier.addEventListener('submit', function(e) {
            e.preventDefault();
            criarCroupier();
        });
    }
    
    // Formulário de editar croupier
    const formEditarCroupier = document.getElementById('formEditarCroupier');
    if (formEditarCroupier) {
        formEditarCroupier.addEventListener('submit', function(e) {
            e.preventDefault();
            salvarEdicaoCroupier();
        });
    }
}

// Configurar responsividade
function setupResponsiveness() {
    // Ajustar layout baseado no tamanho da tela
    function adjustLayout() {
        const isMobile = window.innerWidth <= 768;
        const isTablet = window.innerWidth > 768 && window.innerWidth <= 1024;
        
        const cardsContainer = document.querySelector('.cards-container');
        const metricCards = document.querySelectorAll('.metric-card');
        
        if (isMobile) {
            // Layout mobile: cards em coluna única
            if (cardsContainer) {
                cardsContainer.style.gridTemplateColumns = '1fr';
            }
            
            // Ajustar tamanho dos cards
            metricCards.forEach(card => {
                card.style.marginBottom = '1rem';
            });
        } else if (isTablet) {
            // Layout tablet: cards em 2 colunas
            if (cardsContainer) {
                cardsContainer.style.gridTemplateColumns = 'repeat(2, 1fr)';
            }
        } else {
            // Layout desktop: cards em 3 colunas
            if (cardsContainer) {
                cardsContainer.style.gridTemplateColumns = 'repeat(3, 1fr)';
            }
        }
    }
    
    // Executar ajuste inicial
    adjustLayout();
    
    // Ajustar quando a janela é redimensionada
    window.addEventListener('resize', adjustLayout);
}

// ===== FUNÇÕES DOS MODAIS =====

// Abrir modal criar croupier
function abrirModalCriarCroupier() {
    console.log('🔧 Abrindo modal para criar croupier');
    const modal = document.getElementById('modalCriarCroupier');
    if (modal) {
        modal.classList.remove('hidden');
        // Limpar formulário
        document.getElementById('formCriarCroupier').reset();
    }
}

// Fechar modal criar croupier
function fecharModalCriarCroupier() {
    console.log('🔧 Fechando modal criar croupier');
    const modal = document.getElementById('modalCriarCroupier');
    if (modal) {
        modal.classList.add('hidden');
    }
}

// Abrir modal editar croupier (versão otimizada)
function editarCroupier(croupierId, nome, ativo) {
    console.log('🔧 Abrindo modal para editar croupier:', croupierId, nome, ativo);
    
    // Preencher formulário diretamente com os dados passados
    document.getElementById('croupierIdEditar').value = croupierId;
    document.getElementById('nomeCroupierEditar').value = nome;
    document.getElementById('ativoCroupierEditar').value = ativo.toString();
    
    // Abrir modal
    const modal = document.getElementById('modalEditarCroupier');
    if (modal) {
        modal.classList.remove('hidden');
    }
}

// Fechar modal editar croupier
function fecharModalEditarCroupier() {
    console.log('🔧 Fechando modal editar croupier');
    const modal = document.getElementById('modalEditarCroupier');
    if (modal) {
        modal.classList.add('hidden');
    }
}

// Abrir modal de confirmação de exclusão
function confirmarExclusao(croupierId, nome) {
    console.log('🔧 Abrindo modal de confirmação para excluir croupier:', croupierId, nome);
    
    // Armazenar dados do croupier para exclusão
    croupierParaExcluir = { id: croupierId, nome: nome };
    
    // Preencher nome no modal
    document.getElementById('nomeCroupierExcluir').textContent = nome;
    
    // Abrir modal
    const modal = document.getElementById('modalConfirmarExclusao');
    if (modal) {
        modal.classList.remove('hidden');
    }
}

// Fechar modal de confirmação de exclusão
function fecharModalConfirmarExclusao() {
    console.log('🔧 Fechando modal de confirmação de exclusão');
    const modal = document.getElementById('modalConfirmarExclusao');
    if (modal) {
        modal.classList.add('hidden');
    }
    // Limpar dados do croupier
    croupierParaExcluir = null;
}

// Executar exclusão após confirmação
async function executarExclusao() {
    if (!croupierParaExcluir) {
        console.error('❌ Nenhum croupier selecionado para exclusão');
        return;
    }
    
    console.log('🔧 Executando exclusão do croupier:', croupierParaExcluir.id);
    
    try {
        const url = window.API_URLS.excluirCroupier.replace('0', croupierParaExcluir.id);
        const response = await fetch(url, {
            method: 'DELETE',
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            }
        });
        
        if (!response.ok) {
            throw new Error('Erro ao excluir croupier');
        }
        
        const result = await response.json();
        
        if (result.success) {
            console.log('✅ Croupier excluído com sucesso');
            fecharModalConfirmarExclusao();
            // Recarregar página para remover o croupier da lista
            window.location.reload();
        } else {
            throw new Error(result.error || 'Erro ao excluir croupier');
        }
        
    } catch (error) {
        console.error('Erro ao excluir croupier:', error);
        alert('Erro ao excluir croupier: ' + error.message);
        fecharModalConfirmarExclusao();
    }
}

// ===== FUNÇÕES CRUD =====

// Criar croupier
async function criarCroupier() {
    console.log('🔧 Criando novo croupier');
    
    const formData = new FormData(document.getElementById('formCriarCroupier'));
    const data = {
        nome: formData.get('nome'),
        ativo: formData.get('ativo') === 'true'
    };
    
    try {
        const response = await fetch(window.API_URLS.criarCroupier, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            },
            body: JSON.stringify(data)
        });
        
        if (!response.ok) {
            throw new Error('Erro ao criar croupier');
        }
        
        const result = await response.json();
        
        if (result.success) {
            console.log('✅ Croupier criado com sucesso');
            fecharModalCriarCroupier();
            // Recarregar página para mostrar o novo croupier
            window.location.reload();
        } else {
            throw new Error(result.error || 'Erro ao criar croupier');
        }
        
    } catch (error) {
        console.error('Erro ao criar croupier:', error);
        alert('Erro ao criar croupier: ' + error.message);
    }
}

// Salvar edição do croupier
async function salvarEdicaoCroupier() {
    console.log('🔧 Salvando edição do croupier');
    
    const formData = new FormData(document.getElementById('formEditarCroupier'));
    const croupierId = formData.get('id');
    
    const data = {
        nome: formData.get('nome'),
        ativo: formData.get('ativo') === 'true'
    };
    
    try {
        const url = window.API_URLS.editarCroupier.replace('0', croupierId);
        const response = await fetch(url, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            },
            body: JSON.stringify(data)
        });
        
        if (!response.ok) {
            throw new Error('Erro ao editar croupier');
        }
        
        const result = await response.json();
        
        if (result.success) {
            console.log('✅ Croupier editado com sucesso');
            fecharModalEditarCroupier();
            // Recarregar página para mostrar as alterações
            window.location.reload();
        } else {
            throw new Error(result.error || 'Erro ao editar croupier');
        }
        
    } catch (error) {
        console.error('Erro ao editar croupier:', error);
        alert('Erro ao editar croupier: ' + error.message);
    }
}

// Função para atualizar métricas
function updateMetrics() {
    console.log('🔄 Atualizando métricas...');
    
    // Simular atualização das métricas
    const metricElements = document.querySelectorAll('.metric-card .text-3xl');
    metricElements.forEach(element => {
        const currentValue = parseInt(element.textContent);
        const newValue = currentValue + Math.floor(Math.random() * 5);
        
        // Animar mudança de valor
        animateValueChange(element, currentValue, newValue);
    });
}

// Animar mudança de valor
function animateValueChange(element, startValue, endValue) {
    const duration = 1000;
    const startTime = performance.now();
    
    function updateValue(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        
        const currentValue = Math.floor(startValue + (endValue - startValue) * progress);
        element.textContent = currentValue;
        
        if (progress < 1) {
            requestAnimationFrame(updateValue);
        }
    }
    
    requestAnimationFrame(updateValue);
}

// Função para filtrar croupiers
function filterCroupiers(status) {
    console.log('🔍 Filtrando croupiers por status:', status);
    
    const tableRows = document.querySelectorAll('tbody tr');
    
    tableRows.forEach(row => {
        const statusCell = row.querySelector('td:nth-child(2)');
        if (statusCell) {
            const isActive = statusCell.textContent.includes('Ativo');
            
            if (status === 'all' || 
                (status === 'active' && isActive) || 
                (status === 'inactive' && !isActive)) {
                row.style.display = '';
                row.style.opacity = '1';
            } else {
                row.style.display = 'none';
                row.style.opacity = '0';
            }
        }
    });
}

// Função para buscar croupiers
function searchCroupiers(query) {
    console.log('🔍 Buscando croupiers:', query);
    
    const tableRows = document.querySelectorAll('tbody tr');
    const searchTerm = query.toLowerCase();
    
    tableRows.forEach(row => {
        const nameCell = row.querySelector('td:nth-child(1)');
        if (nameCell) {
            const name = nameCell.textContent.toLowerCase();
            
            if (name.includes(searchTerm)) {
                row.style.display = '';
                row.style.opacity = '1';
            } else {
                row.style.display = 'none';
                row.style.opacity = '0';
            }
        }
    });
}

// Função para exportar dados
function exportCroupiersData() {
    console.log('📊 Exportando dados dos croupiers...');
    
    const table = document.querySelector('table');
    if (!table) return;
    
    const rows = Array.from(table.querySelectorAll('tbody tr'));
    const data = rows.map(row => {
        const cells = Array.from(row.querySelectorAll('td'));
        return {
            nome: cells[0]?.textContent?.trim() || '',
            status: cells[1]?.textContent?.trim() || '',
            dataCriacao: cells[2]?.textContent?.trim() || '',
            dataAtualizacao: cells[3]?.textContent?.trim() || ''
        };
    });
    
    // Criar arquivo CSV
    const csvContent = [
        ['Nome', 'Status', 'Data de Criação', 'Última Atualização'],
        ...data.map(row => [row.nome, row.status, row.dataCriacao, row.dataAtualizacao])
    ].map(row => row.join(',')).join('\n');
    
    // Download do arquivo
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    link.setAttribute('href', url);
    link.setAttribute('download', 'croupiers.csv');
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

// Expor funções globalmente
window.croupiersPage = {
    updateMetrics,
    filterCroupiers,
    searchCroupiers,
    exportCroupiersData,
    abrirModalCriarCroupier,
    fecharModalCriarCroupier,
    editarCroupier,
    fecharModalEditarCroupier,
    confirmarExclusao,
    fecharModalConfirmarExclusao,
    executarExclusao,
    criarCroupier,
    salvarEdicaoCroupier
};

// CSS para efeito ripple
const style = document.createElement('style');
style.textContent = `
    .ripple {
        position: absolute;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.3);
        transform: scale(0);
        animation: ripple-animation 0.6s linear;
        pointer-events: none;
    }
    
    @keyframes ripple-animation {
        to {
            transform: scale(4);
            opacity: 0;
        }
    }
    
    .btn-primary, .btn-secondary {
        position: relative;
        overflow: hidden;
    }
`;
document.head.appendChild(style);

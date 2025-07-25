// Funções para interagir com as APIs do módulo financeiro - Versão Django

// API Functions - Integradas com Django
const FinanceiroAPI = {
    // Função para listar todos os clientes
    async listarClientes() {
        try {
            const response = await fetch('/financeiro/api/clientes/', {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCsrfToken()
                }
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            
            if (data.success) {
                console.log('Clientes encontrados:', data.clientes);
                return data.clientes;
            } else {
                throw new Error(data.error || 'Erro ao carregar clientes');
            }
        } catch (error) {
            console.error('Erro na requisição:', error);
            throw error;
        }
    },

    // Função para obter um cliente específico por ID
    async obterCliente(clienteId) {
        try {
            const response = await fetch(`/financeiro/api/clientes/${clienteId}/`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCsrfToken()
                }
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            
            if (data.success) {
                console.log('Cliente encontrado:', data.cliente);
                return data.cliente;
            } else {
                throw new Error(data.error || 'Cliente não encontrado');
            }
        } catch (error) {
            console.error('Erro na requisição:', error);
            throw error;
        }
    },

    // Função para criar um novo cliente
    async criarCliente(dadosCliente) {
        try {
            const response = await fetch('/financeiro/api/clientes/criar/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCsrfToken()
                },
                body: JSON.stringify(dadosCliente)
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            
            if (data.success) {
                console.log('Cliente criado com sucesso:', data.cliente);
                return data.cliente;
            } else {
                throw new Error(data.error || 'Erro ao criar cliente');
            }
        } catch (error) {
            console.error('Erro na requisição:', error);
            throw error;
        }
    },

    // Função para adicionar fichas a um cliente
    async adicionarFichas(clienteId, quantidade) {
        try {
            const response = await fetch(`/financeiro/api/clientes/${clienteId}/adicionar_fichas/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCsrfToken()
                },
                body: JSON.stringify({ quantidade: quantidade })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            
            if (data.success) {
                console.log('Fichas adicionadas com sucesso:', data);
                return data;
            } else {
                throw new Error(data.error || 'Erro ao adicionar fichas');
            }
        } catch (error) {
            console.error('Erro na requisição:', error);
            throw error;
        }
    },

    // Função para dar baixa (subtrair) fichas de um cliente
    async darBaixaFichas(clienteId, quantidade) {
        console.log('=== API darBaixaFichas ===');
        console.log('Cliente ID:', clienteId);
        console.log('Quantidade:', quantidade);
        
        try {
            const url = `/financeiro/api/clientes/${clienteId}/dar_baixa_fichas/`;
            console.log('URL da requisição:', url);
            
            const requestBody = { quantidade: quantidade };
            console.log('Body da requisição:', requestBody);
            
            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCsrfToken()
                },
                body: JSON.stringify(requestBody)
            });
            
            console.log('Status da resposta:', response.status);
            console.log('Headers da resposta:', response.headers);
            
            if (!response.ok) {
                const errorText = await response.text();
                console.error('Erro HTTP:', response.status, errorText);
                throw new Error(`HTTP error! status: ${response.status} - ${errorText}`);
            }
            
            const data = await response.json();
            console.log('Dados da resposta:', data);
            
            if (data.success) {
                console.log('Baixa de fichas realizada com sucesso:', data);
                return data;
            } else {
                console.error('API retornou erro:', data.error);
                throw new Error(data.error || 'Erro ao dar baixa nas fichas');
            }
        } catch (error) {
            console.error('Erro na requisição darBaixaFichas:', error);
            throw error;
        }
    },

    // Função para testar todas as APIs
    async testarAPIs() {
        console.log('=== Testando APIs do Financeiro ===');
        
        // Teste 1: Criar um cliente
        console.log('\n1. Criando cliente de teste...');
        const novoCliente = await this.criarCliente({
            nome: 'João',
            sobrenome: 'Silva',
            cpf: '123.456.789-00',
            saldo: 1000.00,
            telefone: '(11) 99999-9999',
            fichas_iniciais: 50
        });
        
        if (novoCliente) {
            // Teste 2: Obter o cliente criado
            console.log('\n2. Obtendo cliente criado...');
            const clienteObtido = await this.obterCliente(novoCliente.id);
            
            // Teste 3: Listar todos os clientes
            console.log('\n3. Listando todos os clientes...');
            const todosClientes = await this.listarClientes();
        }
        
        console.log('\n=== Teste concluído ===');
    },

    // Função para formatar dados do cliente para exibição
    formatarClienteParaExibicao(cliente) {
        return {
            id: cliente.id,
            nomeCompleto: cliente.nome_completo,
            cpf: cliente.cpf || 'Não informado',
            saldo: cliente.saldo_formatado,
            telefone: cliente.telefone || 'Não informado',
            dataCriacao: cliente.data_criacao
        };
    },

    // Função para validar dados do cliente antes de enviar
    validarDadosCliente(dados) {
        const erros = [];
        
        if (!dados.nome || dados.nome.trim() === '') {
            erros.push('Nome é obrigatório');
        }
        
        if (dados.saldo && isNaN(parseFloat(dados.saldo))) {
            erros.push('Saldo deve ser um número válido');
        }
        
        if (dados.cpf && !this.validarCPF(dados.cpf)) {
            erros.push('CPF inválido');
        }
        
        return erros;
    },

    // Função para validar CPF (formato básico)
    validarCPF(cpf) {
        // Remove caracteres não numéricos
        cpf = cpf.replace(/[^\d]/g, '');
        
        // Verifica se tem 11 dígitos
        if (cpf.length !== 11) {
            return false;
        }
        
        // Verifica se todos os dígitos são iguais
        if (/^(\d)\1{10}$/.test(cpf)) {
            return false;
        }
        
        return true; // Validação simplificada para demonstração
    },

    // Função para formatar CPF
    formatarCPF(cpf) {
        cpf = cpf.replace(/\D/g, '');
        return cpf.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, '$1.$2.$3-$4');
    },

    // Função para formatar telefone
    formatarTelefone(telefone) {
        telefone = telefone.replace(/\D/g, '');
        if (telefone.length === 11) {
            return telefone.replace(/(\d{2})(\d{5})(\d{4})/, '($1) $2-$3');
        } else if (telefone.length === 10) {
            return telefone.replace(/(\d{2})(\d{4})(\d{4})/, '($1) $2-$3');
        }
        return telefone;
    },

    // Função para formatar moeda
    formatarMoeda(valor) {
        return new Intl.NumberFormat('pt-BR', {
            style: 'currency',
            currency: 'BRL'
        }).format(valor);
    },

    // Função para parsear moeda (converter string formatada para número)
    parsearMoeda(valorFormatado) {
        if (typeof valorFormatado === 'number') {
            return valorFormatado;
        }
        
        return parseFloat(
            valorFormatado
                .replace('R$', '')
                .replace(/\s/g, '')
                .replace(/\./g, '')
                .replace(',', '.')
        ) || 0;
    },

    // Função para obter o token CSRF
    getCsrfToken() {
        const token = document.querySelector('[name=csrfmiddlewaretoken]');
        return token ? token.value : '';
    }
};

// Funções utilitárias globais
function formatarMoeda(valor) {
    return FinanceiroAPI.formatarMoeda(valor);
}

function formatarCPF(cpf) {
    return FinanceiroAPI.formatarCPF(cpf);
}

function formatarTelefone(telefone) {
    return FinanceiroAPI.formatarTelefone(telefone);
}

// Dar baixa fichas
async function darBaixaFichasCliente() {
    console.log('=== INICIANDO DAR BAIXA FICHAS ===');
    
    const form = document.getElementById('formDarBaixaFichas');
    console.log('Form encontrado:', form);
    
    if (!form) {
        console.error('Form não encontrado!');
        alert('Erro: Formulário não encontrado');
        return;
    }
    
    const quantidade = parseInt(form.quantidade.value);
    console.log('Quantidade:', quantidade);
    console.log('Cliente atual ID:', window.clienteAtualId);
    
    if (!quantidade || quantidade <= 0) {
        alert('Por favor, insira uma quantidade válida');
        return;
    }

    if (!window.clienteAtualId) {
        console.error('Cliente atual não definido!');
        alert('Erro: Cliente não selecionado');
        return;
    }

    try {
        console.log('Chamando API darBaixaFichas...');
        const resultado = await FinanceiroAPI.darBaixaFichas(window.clienteAtualId, quantidade);
        console.log('Resultado da API:', resultado);
        
        if (resultado.success) {
            alert(`Baixa de ${quantidade} fichas realizada com sucesso!`);
            
            console.log('Fechando modal...');
            fecharModalDarBaixaFichas();
            
            // Atualizar saldo de fichas em tempo real
            const saldoElement = document.getElementById('saldoFichasCliente');
            console.log('Elemento saldo encontrado:', saldoElement);
            
            if (saldoElement) {
                const saldoAtualStr = saldoElement.textContent;
                console.log('Saldo atual (string):', saldoAtualStr);
                const saldoAtual = parseInt(saldoAtualStr.replace(/\D/g, '')) || 0;
                console.log('Saldo atual (número):', saldoAtual);
                let novoSaldo = saldoAtual - quantidade;
                if (novoSaldo < 0) novoSaldo = 0;
                console.log('Novo saldo:', novoSaldo);
                saldoElement.textContent = `${novoSaldo} fichas`;
            }
            
            // Recarregar detalhes do cliente para atualizar histórico
            if (window.clienteAtualId) {
                console.log('Recarregando detalhes do cliente...');
                verDetalhesCliente(window.clienteAtualId);
            }
        } else {
            console.error('API retornou erro:', resultado);
            alert('Erro ao dar baixa nas fichas. Tente novamente.');
        }
    } catch (error) {
        console.error('Erro ao dar baixa nas fichas:', error);
        alert(`Erro ao dar baixa nas fichas: ${error.message}`);
    }
    
    console.log('=== FIM DAR BAIXA FICHAS ===');
}

// Função para testar a API de dar baixa fichas
async function testarDarBaixaFichas() {
    console.log('=== TESTE DAR BAIXA FICHAS ===');
    
    // Verificar se há clientes disponíveis
    try {
        const clientes = await FinanceiroAPI.listarClientes();
        console.log('Clientes disponíveis:', clientes);
        
        if (clientes && clientes.length > 0) {
            const primeiroCliente = clientes[0];
            console.log('Testando com cliente:', primeiroCliente);
            
            // Testar dar baixa de 1 ficha
            const resultado = await FinanceiroAPI.darBaixaFichas(primeiroCliente.id, 1);
            console.log('Resultado do teste:', resultado);
            
            if (resultado.success) {
                alert('Teste de dar baixa funcionou!');
            } else {
                alert('Teste falhou: ' + resultado.error);
            }
        } else {
            alert('Nenhum cliente disponível para teste');
        }
    } catch (error) {
        console.error('Erro no teste:', error);
        alert('Erro no teste: ' + error.message);
    }
}

// Aplicar máscaras aos campos de entrada
function aplicarMascaras() {
    // Máscara para CPF
    const cpfInputs = document.querySelectorAll('input[name="cpf"]');
    cpfInputs.forEach(input => {
        input.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\D/g, '');
            if (value.length <= 11) {
                value = value.replace(/(\d{3})(\d)/, '$1.$2');
                value = value.replace(/(\d{3})(\d)/, '$1.$2');
                value = value.replace(/(\d{3})(\d{1,2})$/, '$1-$2');
                e.target.value = value;
            }
        });
    });

    // Máscara para telefone
    const telefoneInputs = document.querySelectorAll('input[name="telefone"]');
    telefoneInputs.forEach(input => {
        input.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\D/g, '');
            if (value.length <= 11) {
                if (value.length <= 10) {
                    value = value.replace(/(\d{2})(\d)/, '($1) $2');
                    value = value.replace(/(\d{4})(\d)/, '$1-$2');
                } else {
                    value = value.replace(/(\d{2})(\d)/, '($1) $2');
                    value = value.replace(/(\d{5})(\d)/, '$1-$2');
                }
                e.target.value = value;
            }
        });
    });

    // Máscara para valores monetários
    const saldoInputs = document.querySelectorAll('input[name="saldo"]');
    saldoInputs.forEach(input => {
        input.addEventListener('blur', function(e) {
            const value = parseFloat(e.target.value) || 0;
            e.target.value = value.toFixed(2);
        });
    });
}

// Funções de notificação
function mostrarNotificacao(mensagem, tipo = 'info') {
    // Criar elemento de notificação
    const notificacao = document.createElement('div');
    notificacao.className = `notificacao notificacao-${tipo}`;
    notificacao.innerHTML = `
        <div class="notificacao-content">
            <span>${mensagem}</span>
            <button class="notificacao-close" onclick="fecharNotificacao(this)">×</button>
        </div>
    `;

    // Adicionar estilos se não existirem
    if (!document.querySelector('#notificacao-styles')) {
        const styles = document.createElement('style');
        styles.id = 'notificacao-styles';
        styles.textContent = `
            .notificacao {
                position: fixed;
                top: 20px;
                right: 20px;
                z-index: 9999;
                padding: 1rem 1.5rem;
                border-radius: 0.5rem;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
                animation: slideIn 0.3s ease-out;
                max-width: 400px;
            }
            .notificacao-success {
                background: #10b981;
                color: white;
            }
            .notificacao-error {
                background: #ef4444;
                color: white;
            }
            .notificacao-warning {
                background: #f59e0b;
                color: white;
            }
            .notificacao-info {
                background: #3b82f6;
                color: white;
            }
            .notificacao-content {
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            .notificacao-close {
                background: none;
                border: none;
                color: inherit;
                font-size: 1.5rem;
                cursor: pointer;
                margin-left: 1rem;
            }
            @keyframes slideIn {
                from { transform: translateX(100%); opacity: 0; }
                to { transform: translateX(0); opacity: 1; }
            }
        `;
        document.head.appendChild(styles);
    }

    // Adicionar ao DOM
    document.body.appendChild(notificacao);

    // Remover automaticamente após 5 segundos
    setTimeout(() => {
        fecharNotificacao(notificacao.querySelector('.notificacao-close'));
    }, 5000);
}

function fecharNotificacao(botao) {
    const notificacao = botao.closest('.notificacao');
    if (notificacao) {
        notificacao.style.animation = 'slideOut 0.3s ease-in forwards';
        notificacao.addEventListener('animationend', () => {
            notificacao.remove();
        });
    }
}

// Função para debounce (evitar muitas chamadas seguidas)
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Função para salvar dados no localStorage (para persistência local)
function salvarDadosLocais(chave, dados) {
    try {
        localStorage.setItem(`financeiro_${chave}`, JSON.stringify(dados));
    } catch (error) {
        console.warn('Não foi possível salvar dados locais:', error);
    }
}

// Função para carregar dados do localStorage
function carregarDadosLocais(chave) {
    try {
        const dados = localStorage.getItem(`financeiro_${chave}`);
        return dados ? JSON.parse(dados) : null;
    } catch (error) {
        console.warn('Não foi possível carregar dados locais:', error);
        return null;
    }
}

// Função para limpar dados locais
function limparDadosLocais(chave) {
    try {
        localStorage.removeItem(`financeiro_${chave}`);
    } catch (error) {
        console.warn('Não foi possível limpar dados locais:', error);
    }
}

// Função para exportar dados para CSV
function exportarParaCSV(dados, nomeArquivo) {
    if (!dados || dados.length === 0) {
        mostrarNotificacao('Nenhum dado para exportar', 'warning');
        return;
    }

    // Cabeçalhos das colunas
    const colunas = ['Nome', 'CPF', 'Telefone', 'Saldo', 'Fichas Iniciais', 'Data Criação'];
    
    // Converter dados para formato CSV
    const csvContent = [
        colunas.join(','),
        ...dados.map(cliente => [
            cliente.nome_completo || '',
            cliente.cpf || '',
            cliente.telefone || '',
            cliente.saldo || 0,
            cliente.fichas_iniciais || 0,
            cliente.data_criacao || ''
        ].join(','))
    ].join('\n');

    // Criar e baixar arquivo
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    
    link.setAttribute('href', url);
    link.setAttribute('download', nomeArquivo || 'clientes.csv');
    link.style.visibility = 'hidden';
    
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    mostrarNotificacao('Arquivo CSV exportado com sucesso!', 'success');
}

// Função para validar formulários
function validarFormulario(form) {
    const campos = form.querySelectorAll('input[required]');
    let valido = true;
    
    campos.forEach(campo => {
        if (!campo.value.trim()) {
            campo.classList.add('campo-invalido');
            valido = false;
        } else {
            campo.classList.remove('campo-invalido');
        }
    });
    
    return valido;
}

// Função para limpar validações visuais
function limparValidacoes(form) {
    const campos = form.querySelectorAll('.campo-invalido');
    campos.forEach(campo => {
        campo.classList.remove('campo-invalido');
    });
}

// Função para confirmar ações
function confirmarAcao(mensagem, callback) {
    if (confirm(mensagem)) {
        callback();
    }
}

// Função para formatar data
function formatarData(data) {
    if (data instanceof Date) {
        return data.toLocaleDateString('pt-BR');
    }
    
    if (typeof data === 'string') {
        const dataObj = new Date(data);
        if (!isNaN(dataObj.getTime())) {
            return dataObj.toLocaleDateString('pt-BR');
        }
    }
    
    return data || 'Data não informada';
}

// Função para ordenar array de objetos
function ordenarPor(array, campo, ordem = 'asc') {
    return [...array].sort((a, b) => {
        const valorA = a[campo];
        const valorB = b[campo];
        
        if (typeof valorA === 'string' && typeof valorB === 'string') {
            return ordem === 'asc' 
                ? valorA.localeCompare(valorB)
                : valorB.localeCompare(valorA);
        }
        
        if (ordem === 'asc') {
            return valorA > valorB ? 1 : valorA < valorB ? -1 : 0;
        } else {
            return valorB > valorA ? 1 : valorB < valorA ? -1 : 0;
        }
    });
}

// Função para filtrar array de objetos
function filtrarPor(array, termo, campos) {
    if (!termo) return array;
    
    const termoLower = termo.toLowerCase();
    
    return array.filter(item => {
        return campos.some(campo => {
            const valor = item[campo];
            return valor && valor.toString().toLowerCase().includes(termoLower);
        });
    });
}

// Inicialização quando o DOM estiver carregado
document.addEventListener('DOMContentLoaded', function() {
    // Aplicar máscaras aos campos
    aplicarMascaras();
    
    // Adicionar estilos para campos inválidos
    if (!document.querySelector('#validacao-styles')) {
        const styles = document.createElement('style');
        styles.id = 'validacao-styles';
        styles.textContent = `
            .campo-invalido {
                border-color: #ef4444 !important;
                box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.1) !important;
            }
            .campo-invalido:focus {
                border-color: #ef4444 !important;
                box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.2) !important;
            }
        `;
        document.head.appendChild(styles);
    }
    
    console.log('FinanceiroAPI carregado e pronto para uso!');
    console.log('Funções disponíveis:', Object.keys(FinanceiroAPI));
});

// Event listeners para melhorar a experiência do usuário
document.addEventListener('keydown', function(e) {
    // Atalho para criar novo cliente (Ctrl/Cmd + N)
    if ((e.ctrlKey || e.metaKey) && e.key === 'n') {
        e.preventDefault();
        if (typeof abrirModalCriarCliente === 'function') {
            abrirModalCriarCliente();
        }
    }
    
    // Atalho para pesquisar (Ctrl/Cmd + F)
    if ((e.ctrlKey || e.metaKey) && e.key === 'f') {
        e.preventDefault();
        const searchInput = document.getElementById('searchClientes');
        if (searchInput) {
            searchInput.focus();
        }
    }
});

// Detectar quando o usuário está offline/online
window.addEventListener('online', function() {
    mostrarNotificacao('Conexão restabelecida', 'success');
});

window.addEventListener('offline', function() {
    mostrarNotificacao('Você está offline. Algumas funcionalidades podem não funcionar.', 'warning');
});

// Função para detectar dispositivo móvel
function isMobile() {
    return window.innerWidth <= 768;
}

// Função para detectar se é touch device
function isTouchDevice() {
    return 'ontouchstart' in window || navigator.maxTouchPoints > 0;
}

// Adicionar classe ao body baseado no dispositivo
if (isMobile()) {
    document.body.classList.add('mobile-device');
}

if (isTouchDevice()) {
    document.body.classList.add('touch-device');
}

// Monitorar mudanças no tamanho da tela
window.addEventListener('resize', debounce(function() {
    if (isMobile()) {
        document.body.classList.add('mobile-device');
    } else {
        document.body.classList.remove('mobile-device');
    }
}, 250));

// Função para performance - lazy loading de imagens
function setupLazyLoading() {
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.classList.remove('lazy');
                    observer.unobserve(img);
                }
            });
        });

        document.querySelectorAll('img[data-src]').forEach(img => {
            imageObserver.observe(img);
        });
    }
}

// Configurar lazy loading quando necessário
setupLazyLoading();

// Adicionar suporte a Service Worker para funcionalidade offline (opcional)
if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('/sw.js')
        .then(registration => {
            console.log('Service Worker registrado:', registration);
        })
        .catch(error => {
            console.log('Falha ao registrar Service Worker:', error);
        });
}

// Log de inicialização
console.log('🎰 Sistema Financeiro Saint Paul inicializado com sucesso!');
console.log('📱 Dispositivo móvel:', isMobile());
console.log('👆 Touch device:', isTouchDevice());
console.log('🌐 Status da conexão:', navigator.onLine ? 'Online' : 'Offline');

// Exportar para uso global
window.FinanceiroAPI = FinanceiroAPI;
window.formatarMoeda = formatarMoeda;
window.formatarCPF = formatarCPF;
window.formatarTelefone = formatarTelefone;
window.mostrarNotificacao = mostrarNotificacao;
window.exportarParaCSV = exportarParaCSV;
window.validarFormulario = validarFormulario;
window.confirmarAcao = confirmarAcao;
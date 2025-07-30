
    // Sidebar functionality is handled in base.html
    
    // Função para verificar se é mobile
    const isMobile = () => window.innerWidth <= 1024;

    // Animar contadores
    function animateCounter(element) {
        const target = parseInt(element.getAttribute('data-count'));
        const duration = 2000;
        const step = target / (duration / 16);
        let current = 0;

        const timer = setInterval(() => {
            current += step;
            if (current >= target) {
                current = target;
                clearInterval(timer);
            }
            
            if (element.textContent.includes('R$')) {
                element.textContent = 'R$ ' + Math.floor(current).toLocaleString();
            } else {
                element.textContent = Math.floor(current).toLocaleString();
            }
        }, 16);
    }

    // Observer para animar contadores quando os cards entram na tela
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const counters = entry.target.querySelectorAll('[data-count]');
                counters.forEach((counter, index) => {
                    setTimeout(() => {
                        animateCounter(counter);
                    }, index * 200);
                });
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.3 });

    // Observar cards de métricas (corrigido para usar o seletor correto)
    const metricCards = document.querySelectorAll('#metricasContainer > div');
    metricCards.forEach(card => {
        observer.observe(card);
    });

    // Função para fechar mesa
    function fecharMesa(mesaId) {
        console.log('🔴 Iniciando fechamento da mesa:', mesaId);
        
        showConfirmModal(
            'Fechar Mesa',
            'Tem certeza que deseja fechar esta mesa? Esta ação não pode ser desfeita.',
            'Fechar Mesa',
            'bg-red-600 hover:bg-red-700',
            () => {
                console.log('✅ Confirmação aceita, enviando requisição...');
                const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
                console.log('🔑 CSRF Token:', csrfToken ? 'Presente' : 'Ausente');
                
                fetch(window.API_URLS.fecharMesa.replace('0', mesaId), {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken
                    }
                })
                .then(response => {
                    console.log('📥 Resposta recebida:', response.status, response.statusText);
                    return response.json();
                })
                .then(data => {
                    console.log('📊 Dados recebidos:', data);
                    if (data.success) {
                        showSuccessModal(data.message);
                        
                        // Atualizar a interface com os dados retornados
                        if (data.mesa_atualizada) {
                            console.log('🔄 Atualizando interface com dados:', data.mesa_atualizada);
                            atualizarMesaNaInterface(data.mesa_atualizada);
                        }
                        
                        // Atualizar métricas e saldos dinamicamente
                        setTimeout(() => {
                            atualizarMetricasESaldos();
                        }, 500);
                    } else {
                        console.error('❌ Erro retornado pela API:', data.message);
                        showErrorModal('Erro: ' + data.message);
                    }
                })
                .catch(error => {
                    console.error('❌ Erro ao fechar mesa:', error);
                    showErrorModal('Erro ao fechar mesa. Tente novamente.');
                });
            }
        );
    }

    // Função para abrir mesa
    function abrirMesa(mesaId) {
        console.log('🟢 Iniciando abertura da mesa:', mesaId);
        
        showConfirmModal(
            'Abrir Mesa',
            'Tem certeza que deseja abrir esta mesa?',
            'Abrir Mesa',
            'bg-green-600 hover:bg-green-700',
            () => {
                console.log('✅ Confirmação aceita, enviando requisição...');
                const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
                console.log('🔑 CSRF Token:', csrfToken ? 'Presente' : 'Ausente');
                
                fetch(window.API_URLS.abrirMesa.replace('0', mesaId), {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken
                    }
                })
                .then(response => {
                    console.log('📥 Resposta recebida:', response.status, response.statusText);
                    return response.json();
                })
                .then(data => {
                    console.log('📊 Dados recebidos:', data);
                    if (data.success) {
                        showSuccessModal(data.message);
                        
                        // Atualizar a interface com os dados retornados
                        if (data.mesa_atualizada) {
                            console.log('🔄 Atualizando interface com dados:', data.mesa_atualizada);
                            atualizarMesaNaInterface(data.mesa_atualizada);
                        }
                        
                        // Atualizar métricas e saldos dinamicamente
                        setTimeout(() => {
                            atualizarMetricasESaldos();
                        }, 500);
                    } else {
                        console.error('❌ Erro retornado pela API:', data.message);
                        showErrorModal('Erro: ' + data.message);
                    }
                })
                .catch(error => {
                    console.error('❌ Erro ao abrir mesa:', error);
                    showErrorModal('Erro ao abrir mesa. Tente novamente.');
                });
            }
        );
    }

    // Função para encerrar mesa
    function encerrarMesa(mesaId) {
        console.log('⚫ Iniciando encerramento da mesa:', mesaId);
        
        showConfirmModal(
            'Encerrar Mesa',
            'Tem certeza que deseja encerrar esta mesa? Esta ação é irreversível e a mesa não aparecerá mais no painel.',
            'Encerrar Mesa',
            'bg-gray-600 hover:bg-gray-700',
            () => {
                console.log('✅ Confirmação aceita, enviando requisição...');
                const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
                console.log('🔑 CSRF Token:', csrfToken ? 'Presente' : 'Ausente');
                
                fetch(window.API_URLS.encerrarMesa.replace('0', mesaId), {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken
                    }
                })
                .then(response => {
                    console.log('📥 Resposta recebida:', response.status, response.statusText);
                    return response.json();
                })
                .then(data => {
                    console.log('📊 Dados recebidos:', data);
                    if (data.success) {
                        showSuccessModal(data.message);
                        // Recarregar a página após 1.5 segundos para atualizar o status
                        setTimeout(() => {
                            window.location.reload();
                        }, 1500);
                    } else {
                        console.error('❌ Erro retornado pela API:', data.message);
                        showErrorModal('Erro: ' + data.message);
                    }
                })
                .catch(error => {
                    console.error('❌ Erro ao encerrar mesa:', error);
                    showErrorModal('Erro ao encerrar mesa. Tente novamente.');
                });
            }
        );
    }

    // Modal Criar Mesa
    const modalCriarMesa = document.getElementById('modalCriarMesa');
    const btnCriarMesa = document.getElementById('btnCriarMesa');
    const fecharModal = document.getElementById('fecharModal');
    const cancelarCriar = document.getElementById('cancelarCriar');
    const formCriarMesa = document.getElementById('formCriarMesa');

    // Abrir modal
    function abrirModalCriarMesa() {
        modalCriarMesa.classList.remove('hidden');
        document.body.style.overflow = 'hidden';
        
        // Adicionar proteção contra fechamento acidental
        modalCriarMesa.setAttribute('data-modal-protected', 'true');
        
        // Animar entrada do modal
        setTimeout(() => {
            const modalContent = document.getElementById('modalContentCriar');
            modalContent.classList.remove('scale-95', 'opacity-0');
            modalContent.classList.add('show');
            
            // Garantir que o scroll do modal funcione corretamente
            const modalBody = modalContent.querySelector('.modal-body');
            if (modalBody) {
                modalBody.scrollTop = 0;
            }
        }, 10);
    }

    // Fechar modal
    function fecharModalCriarMesa() {
        const modalContent = document.getElementById('modalContentCriar');
        modalContent.classList.remove('show');
        modalContent.classList.add('hide');
        
        setTimeout(() => {
            modalCriarMesa.classList.add('hidden');
            document.body.style.overflow = 'auto';
            formCriarMesa.reset();
            modalContent.classList.remove('hide');
            modalContent.classList.add('scale-95', 'opacity-0');
            
            // Remover proteção
            modalCriarMesa.removeAttribute('data-modal-protected');
            
            // Resetar scroll do modal
            const modalBody = modalContent.querySelector('.modal-body');
            if (modalBody) {
                modalBody.scrollTop = 0;
            }
        }, 300);
    }

    // Event listeners para o modal
    btnCriarMesa.addEventListener('click', abrirModalCriarMesa);
    fecharModal.addEventListener('click', fecharModalCriarMesa);
    cancelarCriar.addEventListener('click', fecharModalCriarMesa);
    
    // Proteção contra fechamento acidental - PREVINE QUALQUER FECHAMENTO NÃO AUTORIZADO
    modalCriarMesa.addEventListener('click', (e) => {
        // Se clicou no modal (background) mas não no conteúdo, IGNORAR
        if (e.target === modalCriarMesa) {
            e.preventDefault();
            e.stopPropagation();
            return false;
        }
    });
    
    // Prevenir qualquer tecla de fechar o modal
    document.addEventListener('keydown', (e) => {
        const modalAberto = !modalCriarMesa.classList.contains('hidden');
        if (modalAberto) {
            // Bloquear ESC e qualquer outra tecla que possa fechar
            if (e.key === 'Escape' || e.key === 'F4' || (e.ctrlKey && e.key === 'w')) {
                e.preventDefault();
                e.stopPropagation();
                return false;
            }
        }
    });



    // Submeter formulário
    formCriarMesa.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const formData = new FormData(formCriarMesa);
        
        const data = {
            numero_mesa: parseInt(formData.get('numero_mesa')),
            tipo_jogo: formData.get('tipo_jogo'),
            status: 'aberta',
            fichas_5: parseInt(formData.get('fichas_5') || '0'),
            fichas_25: parseInt(formData.get('fichas_25') || '0'),
            fichas_100: parseInt(formData.get('fichas_100') || '0'),
            fichas_500: parseInt(formData.get('fichas_500') || '0'),
            fichas_1000: parseInt(formData.get('fichas_1000') || '0'),
            fichas_5000: parseInt(formData.get('fichas_5000') || '0'),
            fichas_10000: parseInt(formData.get('fichas_10000') || '0')
        };
        
        // Validação
        if (!data.numero_mesa || data.numero_mesa < 1) {
            showErrorModal('Por favor, insira um número de mesa válido.');
            return;
        }

        if (!data.tipo_jogo) {
            showErrorModal('Por favor, selecione um tipo de jogo.');
            return;
        }
        
        // Validar se pelo menos uma ficha foi informada
        const totalFichas = data.fichas_5 + data.fichas_25 + data.fichas_100 + 
                           data.fichas_500 + data.fichas_1000 + data.fichas_5000 + data.fichas_10000;
        
        if (totalFichas === 0) {
            showErrorModal('Por favor, informe pelo menos uma ficha.');
            return;
        }
        
        console.log('📤 Enviando dados para criar mesa:', data);

        try {
            const response = await fetch(window.API_URLS.criarMesa, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                },
                body: JSON.stringify(data)
            });

            const result = await response.json();
            
            if (result.success) {
                // Fechar modal primeiro
                fecharModalCriarMesa();
                
                // Mostrar modal de sucesso
                showSuccessModal(result.message);
                
                // Aguardar um pouco e então aplicar filtros para mostrar a nova mesa
                setTimeout(() => {
                    // Verificar se há filtros ativos
                    const urlParams = new URLSearchParams(window.location.search);
                    const hasFilters = urlParams.has('data_inicio') || urlParams.has('data_fim') || urlParams.has('status');
                    
                    if (hasFilters) {
                        // Se há filtros, aplicar filtros dinamicamente
                        filtrarMesasDinamicamente();
                    } else {
                        // Se não há filtros, apenas criar o card da nova mesa
                        if (result.mesa_criada) {
                            criarNovoCardMesa(result.mesa_criada);
                        }
                    }
                    
                    // Atualizar métricas e saldos dinamicamente
                    setTimeout(() => {
                        atualizarMetricasESaldos();
                    }, 1000);
                }, 400);
            } else {
                showErrorModal('Erro: ' + result.message);
            }
        } catch (error) {
            console.error('Erro ao criar mesa:', error);
            showErrorModal('Erro ao criar mesa. Tente novamente.');
        }
    });

    // Modal Editar Mesa
    const modalEditarMesa = document.getElementById('modalEditarMesa');
    const fecharModalEditar = document.getElementById('fecharModalEditar');
    const cancelarEditar = document.getElementById('cancelarEditar');
    const formEditarMesa = document.getElementById('formEditarMesa');

    // Função para abrir modal de edição
    function editarMesa(mesaId) {
        console.log('🔧 Iniciando edição da mesa:', mesaId);
        
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        const url = window.API_URLS.obterMesa.replace('0', mesaId);
        console.log('🔗 URL da API:', url);
        
        fetch(url, {
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
            .then(response => {
                console.log('📥 Resposta da API:', response.status, response.statusText);
                
                // Verificar se a resposta é JSON
                const contentType = response.headers.get('content-type');
                if (!contentType || !contentType.includes('application/json')) {
                    throw new Error('Resposta não é JSON válido. Status: ' + response.status);
                }
                
                return response.json();
            })
            .then(result => {
                console.log('📊 Dados recebidos:', result);
                
                if (!result.success) {
                    showErrorModal('Erro ao buscar dados da mesa: ' + (result.message || ''));
                    return;
                }
                
                const mesaData = result.mesa;
                console.log('📋 Dados da mesa:', mesaData);

                // Checar se todos os campos existem antes de preencher
                const campos = [
                    'mesaIdEditar',
                    'numeroMesaEditar',
                    'tipoJogoEditar',
                    'statusEditar',
                    'valorInicialEditar',
                    'fichas5Editar',
                    'fichas25Editar',
                    'fichas100Editar',
                    'fichas500Editar',
                    'fichas1000Editar',
                    'fichas5000Editar',
                    'fichas10000Editar'
                ];
                
                let algumCampoFaltando = false;
                campos.forEach(id => {
                    const elemento = document.getElementById(id);
                    if (!elemento) {
                        console.error('❌ Campo não encontrado:', id);
                        algumCampoFaltando = true;
                    }
                });
                
                if (algumCampoFaltando) {
                    showErrorModal('Erro interno: Algum campo do formulário de edição não foi encontrado. Verifique o HTML do modal de edição.');
                    return;
                }

                // Preencher o formulário com os dados atuais
                document.getElementById('mesaIdEditar').value = mesaData.id;
                document.getElementById('numeroMesaEditar').value = mesaData.numero_mesa;
                document.getElementById('tipoJogoEditar').value = mesaData.tipo_jogo;
                document.getElementById('statusEditar').value = mesaData.status;
                document.getElementById('valorInicialEditar').value = `R$ ${parseFloat(mesaData.valor_inicial || 0).toLocaleString()}`;
                document.getElementById('fichas5Editar').value = mesaData.fichas_5 || 0;
                document.getElementById('fichas25Editar').value = mesaData.fichas_25 || 0;
                document.getElementById('fichas100Editar').value = mesaData.fichas_100 || 0;
                document.getElementById('fichas500Editar').value = mesaData.fichas_500 || 0;
                document.getElementById('fichas1000Editar').value = mesaData.fichas_1000 || 0;
                document.getElementById('fichas5000Editar').value = mesaData.fichas_5000 || 0;
                document.getElementById('fichas10000Editar').value = mesaData.fichas_10000 || 0;

                console.log('✅ Formulário preenchido com sucesso');

                // Abrir modal
                modalEditarMesa.classList.remove('hidden');
                document.body.style.overflow = 'hidden';

                // Animar entrada do modal
                setTimeout(() => {
                    const modalContent = document.getElementById('modalContentEditar');
                    modalContent.classList.remove('scale-95', 'opacity-0');
                    modalContent.classList.add('show');
                    
                    // Garantir que o scroll do modal funcione corretamente
                    const modalBody = modalContent.querySelector('.modal-body');
                    if (modalBody) {
                        modalBody.scrollTop = 0;
                    }
                }, 10);
            })
            .catch(error => {
                console.error('❌ Erro ao buscar dados da mesa:', error);
                
                // Verificar se é erro de autenticação
                if (error.message.includes('Status: 302') || error.message.includes('Status: 403')) {
                    showErrorModal('Sessão expirada. Por favor, faça login novamente.');
                    // Redirecionar para login após 2 segundos
                    setTimeout(() => {
                        window.location.href = '/usuarios/login/';
                    }, 2000);
                } else {
                    showErrorModal('Erro ao buscar dados da mesa: ' + error.message);
                }
            });
    }

    // Fechar modal de edição
    function fecharModalEditarMesa() {
        const modalContent = document.getElementById('modalContentEditar');
        modalContent.classList.remove('show');
        modalContent.classList.add('hide');
        
        setTimeout(() => {
            modalEditarMesa.classList.add('hidden');
            document.body.style.overflow = 'auto';
            // Não resetar o formulário para preservar os valores
            modalContent.classList.remove('hide');
            modalContent.classList.add('scale-95', 'opacity-0');
            
            // Resetar scroll do modal
            const modalBody = modalContent.querySelector('.modal-body');
            if (modalBody) {
                modalBody.scrollTop = 0;
            }
        }, 300);
    }

    // Event listeners para o modal de edição
    fecharModalEditar.addEventListener('click', fecharModalEditarMesa);
    cancelarEditar.addEventListener('click', fecharModalEditarMesa);

    // Fechar modal ao clicar fora
    modalEditarMesa.addEventListener('click', (e) => {
        if (e.target === modalEditarMesa) {
            fecharModalEditarMesa();
        }
    });

    // Submeter formulário de edição
    formEditarMesa.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const mesaId = document.getElementById('mesaIdEditar').value;
        const formData = new FormData(formEditarMesa);
        

        
        const data = {
            numero_mesa: parseInt(formData.get('numero_mesa')),
            tipo_jogo: formData.get('tipo_jogo'),
            status: formData.get('status'),
            fichas_5: parseInt(formData.get('fichas_5') || '0'),
            fichas_25: parseInt(formData.get('fichas_25') || '0'),
            fichas_100: parseInt(formData.get('fichas_100') || '0'),
            fichas_500: parseInt(formData.get('fichas_500') || '0'),
            fichas_1000: parseInt(formData.get('fichas_1000') || '0'),
            fichas_5000: parseInt(formData.get('fichas_5000') || '0'),
            fichas_10000: parseInt(formData.get('fichas_10000') || '0')
        };
        


        // Validação
        if (!data.numero_mesa || data.numero_mesa < 1) {
            showErrorModal('Por favor, insira um número de mesa válido.');
            return;
        }

        if (!data.tipo_jogo) {
            showErrorModal('Por favor, selecione um tipo de jogo.');
            return;
        }

        try {
            const response = await fetch(`/mesas/api/mesa/${mesaId}/editar/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                },
                body: JSON.stringify(data)
            });

            const result = await response.json();
            
            if (result.success) {
                showSuccessModal(result.message);
                fecharModalEditarMesa();
                
                // Atualizar a interface com os dados retornados
                if (result.mesa_atualizada) {
                    atualizarMesaNaInterface(result.mesa_atualizada);
                }
                
                // Atualizar métricas e saldos dinamicamente
                setTimeout(() => {
                    atualizarMetricasESaldos();
                }, 500);
                
                // Não recarregar a página - os dados já foram atualizados na interface
            } else {
                showErrorModal('Erro: ' + result.message);
            }
        } catch (error) {
            showErrorModal('Erro ao atualizar mesa. Tente novamente.');
        }
    });

    // Função para criar um novo card de mesa
    function criarNovoCardMesa(mesaData) {
        console.log('🔄 Criando novo card para mesa:', mesaData);
        
        // Encontrar o container de mesas
        const mesasContainer = document.getElementById('cards-container');
        if (!mesasContainer) {
            console.error('❌ Container de mesas não encontrado');
            return;
        }
        
        // Remover a mensagem "Nenhuma Mesa Criada" se existir
        const noMesasMessage = mesasContainer.querySelector('.col-span-full');
        if (noMesasMessage) {
            noMesasMessage.remove();
        }
        
        // Criar o JSON da mesa
        const mesaJson = {
            id: mesaData.id,
            numero_mesa: mesaData.numero_mesa,
            tipo_jogo: mesaData.tipo_jogo,
            tipo_jogo_display: mesaData.tipo_jogo_display || mesaData.tipo_jogo,
            status: mesaData.status,
            status_display: mesaData.status_display || mesaData.status,
            valor_inicial: mesaData.valor_inicial,
            valor_total: mesaData.valor_total,
            saldo: mesaData.saldo,
            fichas_5: mesaData.fichas_5,
            fichas_25: mesaData.fichas_25,
            fichas_100: mesaData.fichas_100,
            fichas_500: mesaData.fichas_500,
            fichas_1000: mesaData.fichas_1000,
            fichas_5000: mesaData.fichas_5000,
            fichas_10000: mesaData.fichas_10000,
            total_fichas: mesaData.fichas_5 + mesaData.fichas_25 + mesaData.fichas_100 + 
                         mesaData.fichas_500 + mesaData.fichas_1000 + mesaData.fichas_5000 + mesaData.fichas_10000,
            data_criacao: mesaData.data_criacao || new Date().toLocaleString('pt-BR'),
            data_atualizacao: mesaData.data_atualizacao || new Date().toLocaleString('pt-BR')
        };
        
        // Determinar classes de status
        let statusClasses = '';
        let statusText = '';
        if (mesaData.status === 'aberta') {
            statusClasses = 'bg-green-100 text-green-800';
            statusText = 'ABERTA';
        } else if (mesaData.status === 'fechada') {
            statusClasses = 'bg-red-100 text-red-800';
            statusText = 'FECHADA';
        } else {
            statusClasses = 'bg-yellow-100 text-yellow-800';
            statusText = 'ENCERRADA';
        }
        
        // Determinar classes de saldo
        const saldoClasses = mesaData.saldo >= 0 ? 'text-green-600' : 'text-red-600';
        const saldoPrefix = mesaData.saldo >= 0 ? '+' : '';
        
        // Determinar classes de status no texto
        let statusTextClasses = '';
        if (mesaData.status === 'aberta') {
            statusTextClasses = 'text-green-600';
        } else if (mesaData.status === 'fechada') {
            statusTextClasses = 'text-red-600';
        } else {
            statusTextClasses = 'text-yellow-600';
        }
        
        // Determinar largura da barra de progresso
        let progressWidth = '0%';
        if (mesaData.status === 'aberta') {
            progressWidth = '75%';
        } else if (mesaData.status === 'fechada') {
            progressWidth = '100%';
        }
        
        // Determinar texto de tempo
        let timeText = 'Agora mesmo';
        if (mesaData.status === 'aberta') {
            timeText = 'Agora mesmo';
        } else if (mesaData.status === 'fechada') {
            timeText = 'Agora mesmo';
        }
        
        // Criar o HTML do card
        const cardHTML = `
            <div class="bg-white/95 backdrop-blur-xl rounded-lg p-4 shadow-xl border border-red-500/10 hover:shadow-2xl hover:-translate-y-2 transition-all duration-300 relative overflow-hidden group min-h-[70px]" 
                 data-mesa-id="${mesaData.id}">
                <div class="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-red-600 to-red-400 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
                
                <div class="flex justify-between items-start mb-2">
                    <div class="text-xs font-bold text-gray-800">${mesaData.tipo_jogo_display || mesaData.tipo_jogo} ${mesaData.numero_mesa}</div>
                    <div class="px-2 py-1 rounded text-xs font-bold uppercase ${statusClasses}">
                        ${statusText}
                    </div>
                </div>
                
                <div class="text-xs text-red-600 font-semibold mb-2">${mesaData.tipo_jogo}</div>
                
                <div class="space-y-1 mb-2">
                    <div class="flex justify-between items-center text-xs">
                        <span class="text-gray-600">Valor Total:</span>
                        <span class="font-bold text-green-600 valor-total">R$ ${parseFloat(mesaData.valor_total).toLocaleString()}</span>
                    </div>
                    <div class="flex justify-between items-center text-xs">
                        <span class="text-gray-600">Valor Inicial:</span>
                        <span class="font-semibold text-blue-600 valor-inicial">R$ ${parseFloat(mesaData.valor_inicial).toLocaleString()}</span>
                    </div>
                    <div class="flex justify-between items-center text-xs">
                        <span class="text-gray-600">Saldo:</span>
                        <span class="font-bold saldo ${saldoClasses}">
                            ${saldoPrefix}R$ ${parseFloat(mesaData.saldo).toLocaleString()}
                        </span>
                    </div>
                    <div class="flex justify-between items-center text-xs">
                        <span class="text-gray-600">Fichas:</span>
                        <span class="text-xs fichas-total">${mesaJson.total_fichas}</span>
                    </div>
                    <div class="flex justify-between items-center text-xs">
                        <span class="text-gray-600">Status:</span>
                        <span class="text-xs font-semibold ${statusTextClasses}">
                            ${statusText}
                        </span>
                    </div>
                </div>
                
                <div class="w-full h-1 bg-gray-200 rounded-full mb-2 overflow-hidden">
                    <div class="h-full bg-gradient-to-r from-amber-500 to-amber-400 rounded-full transition-all duration-300" 
                         style="width: ${progressWidth}"></div>
                </div>
                
                <div class="text-xs text-gray-400 mb-3">${timeText}</div>
                
                <div class="flex gap-2 mt-3">
                    ${mesaData.status !== 'encerrada' ? `
                    <button class="flex-1 py-2 px-3 bg-gradient-to-r from-blue-600 to-blue-500 hover:from-blue-700 hover:to-blue-600 text-white text-xs font-bold rounded-md shadow-lg hover:shadow-xl hover:-translate-y-1 transition-all duration-300 flex items-center justify-center gap-1" 
                            onclick="editarMesa(${mesaData.id})">
                        <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
                        </svg>
                        Editar
                    </button>
                    ` : ''}
                    ${mesaData.status === 'aberta' ? `
                        <button class="flex-1 py-2 px-3 bg-gradient-to-r from-red-600 to-red-500 hover:from-red-700 hover:to-red-600 text-white text-xs font-bold rounded-md shadow-lg hover:shadow-xl hover:-translate-y-1 transition-all duration-300 uppercase" 
                                onclick="fecharMesa(${mesaData.id})">
                            Fechar
                        </button>
                    ` : ''}
                    ${mesaData.status === 'fechada' ? `
                        <div class="flex gap-1 flex-1">
                            <button class="flex-1 py-2 px-2 bg-gradient-to-r from-amber-500 to-amber-400 hover:from-amber-600 hover:to-amber-500 text-white text-xs font-bold rounded-md shadow-lg hover:shadow-xl hover:-translate-y-1 transition-all duration-300 uppercase" 
                                    onclick="abrirMesa(${mesaData.id})">
                                Abrir
                            </button>
                            <button class="flex-1 py-2 px-2 bg-gradient-to-r from-gray-600 to-gray-500 hover:from-gray-700 hover:to-gray-600 text-white text-xs font-bold rounded-md shadow-lg hover:shadow-xl hover:-translate-y-1 transition-all duration-300 uppercase" 
                                    onclick="encerrarMesa(${mesaData.id})">
                                Encerrar
                            </button>
                        </div>
                    ` : ''}
                </div>
            </div>
        `;
        
        // Adicionar o card ao container
        mesasContainer.insertAdjacentHTML('beforeend', cardHTML);
        
        // Animar a entrada do novo card
        const novoCard = mesasContainer.lastElementChild;
        if (novoCard) {
            novoCard.style.opacity = '0';
            novoCard.style.transform = 'scale(0.8) translateY(20px)';
            
            setTimeout(() => {
                novoCard.style.transition = 'all 0.5s ease-out';
                novoCard.style.opacity = '1';
                novoCard.style.transform = 'scale(1) translateY(0)';
            }, 50);
        }
        
        console.log('✅ Card criado com sucesso para mesa', mesaData.numero_mesa);
    }

    // Função para atualizar a mesa na interface
    function atualizarMesaNaInterface(mesaData) {
        console.log('🔄 Atualizando mesa na interface:', mesaData);
        
        // Encontrar o card da mesa pelo ID
        const mesaCard = document.querySelector(`[data-mesa-id="${mesaData.id}"]`);
        if (!mesaCard) {
            console.error('❌ Card da mesa não encontrado:', mesaData.id);
            return;
        }
        
        // Atualizar os valores exibidos
        const valorTotalElement = mesaCard.querySelector('.valor-total');
        const valorInicialElement = mesaCard.querySelector('.valor-inicial');
        const saldoElement = mesaCard.querySelector('.saldo');
        const fichasElement = mesaCard.querySelector('.fichas-total');
        const statusElement = mesaCard.querySelector('.px-2.py-1.rounded.text-xs.font-bold.uppercase');
        
        if (valorTotalElement) {
            valorTotalElement.textContent = `R$ ${parseFloat(mesaData.valor_total).toLocaleString()}`;
        }
        
        if (valorInicialElement) {
            valorInicialElement.textContent = `R$ ${parseFloat(mesaData.valor_inicial).toLocaleString()}`;
        }
        
        if (saldoElement) {
            const saldo = parseFloat(mesaData.saldo);
            saldoElement.textContent = `${saldo >= 0 ? '+' : ''}R$ ${saldo.toLocaleString()}`;
            saldoElement.className = `font-bold ${saldo >= 0 ? 'text-green-600' : 'text-red-600'}`;
        }
        
        if (fichasElement) {
            const totalFichas = mesaData.fichas_5 + mesaData.fichas_25 + mesaData.fichas_100 + 
                               mesaData.fichas_500 + mesaData.fichas_1000 + mesaData.fichas_5000 + mesaData.fichas_10000;
            fichasElement.textContent = totalFichas;
        }
        
        // Atualizar status visual
        if (statusElement) {
            // Remover classes de status anteriores
            statusElement.classList.remove('bg-green-100', 'text-green-800', 'bg-red-100', 'text-red-800', 'bg-yellow-100', 'text-yellow-800');
            
            // Aplicar classes do novo status
            if (mesaData.status === 'aberta') {
                statusElement.classList.add('bg-green-100', 'text-green-800');
                statusElement.textContent = 'ABERTA';
            } else if (mesaData.status === 'fechada') {
                statusElement.classList.add('bg-red-100', 'text-red-800');
                statusElement.textContent = 'FECHADA';
            } else if (mesaData.status === 'encerrada') {
                statusElement.classList.add('bg-yellow-100', 'text-yellow-800');
                statusElement.textContent = 'ENCERRADA';
            }
        }
        
        // Atualizar a seção de botões completamente
        const buttonsContainer = mesaCard.querySelector('.flex.gap-2.mt-3');
        if (buttonsContainer) {
            let buttonsHTML = '';
            
            // Botão Editar (sempre presente exceto para mesas encerradas)
            if (mesaData.status !== 'encerrada') {
                buttonsHTML += `
                    <button class="flex-1 py-2 px-3 bg-gradient-to-r from-blue-600 to-blue-500 hover:from-blue-700 hover:to-blue-600 text-white text-xs font-bold rounded-md shadow-lg hover:shadow-xl hover:-translate-y-1 transition-all duration-300 flex items-center justify-center gap-1" 
                            onclick="editarMesa(${mesaData.id})">
                        <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
                        </svg>
                        Editar
                    </button>
                `;
            }
            
            // Botões específicos por status
            if (mesaData.status === 'aberta') {
                buttonsHTML += `
                    <button class="flex-1 py-2 px-3 bg-gradient-to-r from-red-600 to-red-500 hover:from-red-700 hover:to-red-600 text-white text-xs font-bold rounded-md shadow-lg hover:shadow-xl hover:-translate-y-1 transition-all duration-300 uppercase" 
                            onclick="fecharMesa(${mesaData.id})">
                        Fechar
                    </button>
                `;
            } else if (mesaData.status === 'fechada') {
                buttonsHTML += `
                    <div class="flex gap-1 flex-1">
                        <button class="flex-1 py-2 px-2 bg-gradient-to-r from-amber-500 to-amber-400 hover:from-amber-600 hover:to-amber-500 text-white text-xs font-bold rounded-md shadow-lg hover:shadow-xl hover:-translate-y-1 transition-all duration-300 uppercase" 
                                onclick="abrirMesa(${mesaData.id})">
                            Abrir
                        </button>
                        <button class="flex-1 py-2 px-2 bg-gradient-to-r from-gray-600 to-gray-500 hover:from-gray-700 hover:to-gray-600 text-white text-xs font-bold rounded-md shadow-lg hover:shadow-xl hover:-translate-y-1 transition-all duration-300 uppercase" 
                                onclick="encerrarMesa(${mesaData.id})">
                            Encerrar
                        </button>
                    </div>
                `;
            }
            
            // Substituir o conteúdo dos botões
            buttonsContainer.innerHTML = buttonsHTML;
        }
        
        console.log('✅ Mesa atualizada com sucesso:', mesaData.numero_mesa);
    }

    // Função para atualizar métricas e saldos dinamicamente
    function atualizarMetricasESaldos() {
        console.log('🔄 Iniciando atualização de métricas e saldos...');
        
        // Verificar se o container existe
        const metricasContainer = document.getElementById('metricasContainer');
        if (!metricasContainer) {
            console.error('❌ Container de métricas não encontrado!');
            return;
        }
        
        console.log('✅ Container de métricas encontrado');
        
        // Obter parâmetros de filtro atuais
        const urlParams = new URLSearchParams(window.location.search);
        const dataInicio = urlParams.get('data_inicio') || '';
        const dataFim = urlParams.get('data_fim') || '';
        const statusFiltro = urlParams.get('status') || '';
        
        // Construir URL da API com parâmetros
        let apiUrl = '/mesas/api/atualizar-metricas/';
        const params = new URLSearchParams();
        if (dataInicio) params.append('data_inicio', dataInicio);
        if (dataFim) params.append('data_fim', dataFim);
        if (statusFiltro) params.append('status', statusFiltro);
        
        if (params.toString()) {
            apiUrl += '?' + params.toString();
        }
        
        console.log('📡 Fazendo requisição para:', apiUrl);
        
        // Obter token CSRF
        const csrfElement = document.querySelector('[name=csrfmiddlewaretoken]');
        if (!csrfElement) {
            console.error('❌ CSRF token não encontrado!');
            return;
        }
        const csrfToken = csrfElement.value;
        console.log('🔑 CSRF Token:', csrfToken ? 'Presente' : 'Ausente');
        
        fetch(apiUrl, {
            method: 'GET',
            headers: {
                'X-CSRFToken': csrfToken,
                'Content-Type': 'application/json',
            },
        })
            .then(response => {
                console.log('📥 Resposta recebida:', response.status);
                return response.json();
            })
            .then(data => {
                console.log('📊 Dados recebidos:', data);
                console.log('💰 Receita Total recebida:', data.metricas.receita_total);
                if (!data.success) {
                    console.log('❌ Dados não foram bem-sucedidos');
                    return;
                }
                
                // Atualizar métricas
                const metricas = data.metricas;
                
                // Atualizar receita total
                const receitaElement = document.querySelector('#metricasContainer > div:nth-child(1) [data-count]');
                console.log('🔍 Elemento receita encontrado:', !!receitaElement);
                if (receitaElement) {
                    const oldValue = receitaElement.textContent;
                    const newValue = `R$ ${parseFloat(metricas.receita_total).toLocaleString()}`;
                    console.log('🔄 Atualizando Receita Total:', oldValue, '→', newValue);
                    receitaElement.textContent = newValue;
                    receitaElement.setAttribute('data-count', parseFloat(metricas.receita_total).toFixed(0));
                } else {
                    console.error('❌ Elemento de receita não encontrado');
                }
                
                // Atualizar mesas ativas
                const mesasAtivasElement = document.querySelector('#metricasContainer > div:nth-child(2) [data-count]');
                console.log('🔍 Elemento mesas ativas encontrado:', !!mesasAtivasElement);
                if (mesasAtivasElement) {
                    mesasAtivasElement.textContent = metricas.mesas_ativas;
                    mesasAtivasElement.setAttribute('data-count', metricas.mesas_ativas);
                } else {
                    console.error('❌ Elemento de mesas ativas não encontrado');
                }
                
                // Atualizar fichas vendidas
                const fichasVendidasElement = document.querySelector('#metricasContainer > div:nth-child(3) [data-count]');
                console.log('🔍 Elemento fichas vendidas encontrado:', !!fichasVendidasElement);
                if (fichasVendidasElement) {
                    fichasVendidasElement.textContent = `R$ ${parseFloat(metricas.fichas_vendidas).toLocaleString()}`;
                    fichasVendidasElement.setAttribute('data-count', parseFloat(metricas.fichas_vendidas).toFixed(0));
                } else {
                    console.error('❌ Elemento de fichas vendidas não encontrado');
                }
                
                // Atualizar estoque restante
                const estoqueElement = document.querySelector('#metricasContainer > div:nth-child(3) .text-xs.font-medium.text-blue-600');
                if (estoqueElement) {
                    estoqueElement.textContent = `Estoque: R$ ${parseFloat(metricas.estoque_restante).toLocaleString()}`;
                }
                
                // Atualizar variação percentual
                const variacaoElement = document.querySelector('#metricasContainer > div:nth-child(1) .text-xs.font-medium');
                if (variacaoElement) {
                    const variacao = parseFloat(metricas.variacao_percentual);
                    variacaoElement.textContent = `${variacao >= 0 ? '+' : ''}${variacao.toFixed(1)}% vs período anterior`;
                    variacaoElement.className = `text-xs font-medium ${variacao >= 0 ? 'text-green-600' : 'text-red-600'}`;
                }
                
                // Atualizar saldos das mesas
                if (data.mesas) {
                    data.mesas.forEach(mesa => {
                        const mesaCard = document.querySelector(`[data-mesa-id="${mesa.id}"]`);
                        if (mesaCard) {
                            const saldoElement = mesaCard.querySelector('.saldo');
                            if (saldoElement) {
                                const saldo = parseFloat(mesa.saldo);
                                saldoElement.textContent = `${saldo >= 0 ? '+' : ''}R$ ${saldo.toLocaleString()}`;
                                saldoElement.className = `font-bold ${saldo >= 0 ? 'text-green-600' : 'text-red-600'}`;
                            }
                            
                            // Atualizar valor total também
                            const valorTotalElement = mesaCard.querySelector('.valor-total');
                            if (valorTotalElement) {
                                valorTotalElement.textContent = `R$ ${parseFloat(mesa.valor_total).toLocaleString()}`;
                            }
                            
                            // Atualizar fichas total
                            const fichasElement = mesaCard.querySelector('.fichas-total');
                            if (fichasElement) {
                                const totalFichas = mesa.fichas_5 + mesa.fichas_25 + mesa.fichas_100 + 
                                                   mesa.fichas_500 + mesa.fichas_1000 + mesa.fichas_5000 + mesa.fichas_10000;
                                fichasElement.textContent = totalFichas;
                            }
                        }
                    });
                }
                
                console.log('✅ Atualização concluída com sucesso!');
                
                // Mostrar notificação de sucesso
                const notification = document.createElement('div');
                notification.className = 'fixed top-4 right-4 bg-green-500 text-white px-4 py-2 rounded-lg shadow-lg z-50 transform transition-all duration-300 translate-x-full';
                notification.innerHTML = `
                    <div class="flex items-center gap-2">
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                        </svg>
                        <span>Dados atualizados com sucesso!</span>
                    </div>
                `;
                document.body.appendChild(notification);
                
                // Animar entrada
                setTimeout(() => {
                    notification.classList.remove('translate-x-full');
                }, 100);
                
                // Remover após 3 segundos
                setTimeout(() => {
                    notification.classList.add('translate-x-full');
                    setTimeout(() => {
                        notification.remove();
                    }, 300);
                }, 3000);
            })
            .catch(error => {
                console.log('❌ Erro na atualização:', error);
                // Silenciar erros para não interromper a experiência do usuário
            });
    }

    // Função para filtrar mesas dinamicamente
    function filtrarMesasDinamicamente() {
        console.log('🔄 Filtrando mesas dinamicamente...');
        
        // Obter parâmetros de filtro atuais
        const urlParams = new URLSearchParams(window.location.search);
        const dataInicio = urlParams.get('data_inicio') || '';
        const dataFim = urlParams.get('data_fim') || '';
        const statusFiltro = urlParams.get('status') || '';
        
        // Construir URL da API com parâmetros
        let apiUrl = '/mesas/api/atualizar-metricas/';
        const params = new URLSearchParams();
        if (dataInicio) params.append('data_inicio', dataInicio);
        if (dataFim) params.append('data_fim', dataFim);
        if (statusFiltro) params.append('status', statusFiltro);
        
        if (params.toString()) {
            apiUrl += '?' + params.toString();
        }
        
        console.log('📡 Fazendo requisição para filtrar mesas:', apiUrl);
        console.log('🔍 Parâmetros de filtro:', { dataInicio, dataFim, statusFiltro });
        
        // Obter token CSRF
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        console.log('🔑 CSRF Token (filtro):', csrfToken ? 'Presente' : 'Ausente');
        
        fetch(apiUrl, {
            method: 'GET',
            headers: {
                'X-CSRFToken': csrfToken,
                'Content-Type': 'application/json',
            },
        })
            .then(response => response.json())
            .then(data => {
                if (!data.success) {
                    console.log('❌ Dados não foram bem-sucedidos');
                    return;
                }
                
                // Atualizar container de mesas
                const mesasContainer = document.getElementById('cards-container');
                if (!mesasContainer) {
                    console.error('❌ Container de mesas não encontrado');
                    return;
                }
                
                // Limpar container
                mesasContainer.innerHTML = '';
                
                // Adicionar mesas filtradas
                if (data.mesas && data.mesas.length > 0) {
                    data.mesas.forEach(mesa => {
                        criarNovoCardMesa(mesa);
                    });
                } else {
                    // Mostrar mensagem de nenhuma mesa encontrada
                    const noMesasHTML = `
                        <div class="col-span-full bg-white/95 backdrop-blur-xl rounded-2xl p-8 shadow-xl border border-red-500/10 text-center">
                            <div class="text-4xl mb-4">🎰</div>
                            <h3 class="text-xl font-bold text-gray-800 mb-2">Nenhuma Mesa Encontrada</h3>
                            <p class="text-gray-600 mb-6">
                                ${statusFiltro ? `Não há mesas com status "${statusFiltro}"` : 'Não há mesas no período selecionado'}.
                            </p>
                            <button class="bg-gradient-to-r from-red-600 to-red-500 hover:from-red-700 hover:to-red-600 text-white font-bold py-3 px-6 rounded-lg shadow-lg hover:shadow-xl hover:-translate-y-1 transition-all duration-300" 
                                    onclick="abrirModalCriarMesa()">
                                Criar Nova Mesa
                            </button>
                        </div>
                    `;
                    mesasContainer.innerHTML = noMesasHTML;
                }
                
                console.log('✅ Filtro aplicado com sucesso');
            })
            .catch(error => {
                console.log('❌ Erro ao filtrar mesas:', error);
            });
    }


    // Toggle Filtro e Métricas
    const toggleFiltro = document.getElementById('toggleFiltro');
    const toggleMetricas = document.getElementById('toggleMetricas');
    const filtroContainer = document.getElementById('filtroContainer');
    const metricasContainer = document.getElementById('metricasContainer');
    const filtroText = document.getElementById('filtroText');
    const metricasText = document.getElementById('metricasText');

    // Função para salvar estado no localStorage
    function salvarEstadoFiltros(filtroVisivel, metricasVisiveis) {
        localStorage.setItem('filtroVisivel', filtroVisivel);
        localStorage.setItem('metricasVisiveis', metricasVisiveis);
    }

    // Função para carregar estado do localStorage
    function carregarEstadoFiltros() {
        const filtroVisivel = localStorage.getItem('filtroVisivel');
        const metricasVisiveis = localStorage.getItem('metricasVisiveis');
        
        // Se não há dados salvos, usar true como padrão
        return {
            filtroVisivel: filtroVisivel === null ? true : filtroVisivel === 'true',
            metricasVisiveis: metricasVisiveis === null ? true : metricasVisiveis === 'true'
        };
    }

    // Carregar estado inicial do localStorage
    let { filtroVisivel, metricasVisiveis } = carregarEstadoFiltros();

    // Aplicar estado inicial
    function aplicarEstadoInicial() {
        if (!filtroVisivel) {
            filtroContainer.style.display = 'none';
            filtroContainer.style.opacity = '0';
            filtroText.textContent = 'Mostrar Filtro';
        }
        
        if (!metricasVisiveis) {
            metricasContainer.style.display = 'none';
            metricasContainer.style.opacity = '0';
            metricasText.textContent = 'Mostrar Métricas';
        }
    }

    // Aplicar estado inicial quando a página carrega
    aplicarEstadoInicial();

    // Toggle Filtro
    toggleFiltro.addEventListener('click', () => {
        filtroVisivel = !filtroVisivel;
        
        if (filtroVisivel) {
            filtroContainer.style.display = 'block';
            filtroContainer.style.opacity = '0';
            setTimeout(() => {
                filtroContainer.style.opacity = '1';
            }, 10);
            filtroText.textContent = 'Esconder Filtro';
        } else {
            filtroContainer.style.opacity = '0';
            setTimeout(() => {
                filtroContainer.style.display = 'none';
            }, 300);
            filtroText.textContent = 'Mostrar Filtro';
        }
        
        // Salvar estado no localStorage
        salvarEstadoFiltros(filtroVisivel, metricasVisiveis);
    });

    // Toggle Métricas
    toggleMetricas.addEventListener('click', () => {
        metricasVisiveis = !metricasVisiveis;
        
        if (metricasVisiveis) {
            metricasContainer.style.display = 'grid';
            metricasContainer.style.opacity = '0';
            setTimeout(() => {
                metricasContainer.style.opacity = '1';
            }, 10);
            metricasText.textContent = 'Esconder Métricas';
        } else {
            metricasContainer.style.opacity = '0';
            setTimeout(() => {
                metricasContainer.style.display = 'none';
            }, 300);
            metricasText.textContent = 'Mostrar Métricas';
        }
        
        // Salvar estado no localStorage
        salvarEstadoFiltros(filtroVisivel, metricasVisiveis);
    });

    // Filtro de Datas
    const filtroDatas = document.getElementById('filtroDatas');
    const limparFiltro = document.getElementById('limparFiltro');
    const dataInicio = document.getElementById('dataInicio');
    const dataFim = document.getElementById('dataFim');

    // Validar datas
    function validarDatas() {
        const inicio = new Date(dataInicio.value);
        const fim = new Date(dataFim.value);
        
        if (inicio > fim) {
            showErrorModal('A data de início não pode ser maior que a data de fim.');
            return false;
        }
        
        return true;
    }

    // Submeter filtro
    filtroDatas.addEventListener('submit', (e) => {
        e.preventDefault();
        
        if (!validarDatas()) {
            return;
        }
        
        // Construir URL com parâmetros
        const url = new URL(window.location);
        url.searchParams.set('data_inicio', dataInicio.value);
        url.searchParams.set('data_fim', dataFim.value);
        
        // Adicionar parâmetro de status se selecionado
        if (statusFiltroInput.value) {
            url.searchParams.set('status', statusFiltroInput.value);
        } else {
            url.searchParams.delete('status');
        }
        
        // Atualizar URL sem recarregar a página
        window.history.pushState({}, '', url.toString());
        
        // Aplicar filtros dinamicamente
        filtrarMesasDinamicamente();
        
        // Atualizar métricas
        setTimeout(() => {
            atualizarMetricasESaldos();
        }, 500);
    });

    // Limpar filtro
    limparFiltro.addEventListener('click', () => {
        // Limpar o input de status
        statusFiltroInput.value = '';
        
        // Limpar inputs de data
        dataInicio.value = '';
        dataFim.value = '';
        
        // Atualizar URL para remover parâmetros
        const url = new URL(window.location);
        url.searchParams.delete('data_inicio');
        url.searchParams.delete('data_fim');
        url.searchParams.delete('status');
        window.history.pushState({}, '', url.toString());
        
        // Aplicar filtros dinamicamente (sem filtros)
        filtrarMesasDinamicamente();
        
        // Atualizar métricas
        setTimeout(() => {
            atualizarMetricasESaldos();
        }, 500);
    });

    // Atualizar data fim quando data início mudar
    dataInicio.addEventListener('change', () => {
        if (dataInicio.value && !dataFim.value) {
            dataFim.value = dataInicio.value;
        }
    });

    // Gerenciar filtros de status
    const filtrosStatus = document.querySelectorAll('.filtro-status');
    const statusFiltroInput = document.getElementById('statusFiltro');

    filtrosStatus.forEach(button => {
        button.addEventListener('click', () => {
            const status = button.getAttribute('data-status');
            
            // Atualizar o input hidden
            statusFiltroInput.value = status;
            
            // Atualizar classes dos botões
            filtrosStatus.forEach(btn => {
                btn.classList.remove('bg-gradient-to-r', 'from-blue-600', 'to-blue-500', 'from-green-600', 'to-green-500', 'from-amber-600', 'to-amber-500', 'from-red-600', 'to-red-500', 'text-white', 'shadow-lg');
                btn.classList.add('bg-gray-100', 'hover:bg-gray-200', 'text-gray-700');
            });
            
            // Aplicar estilo ativo ao botão clicado
            if (status === '') {
                button.classList.remove('bg-gray-100', 'hover:bg-gray-200', 'text-gray-700');
                button.classList.add('bg-gradient-to-r', 'from-blue-600', 'to-blue-500', 'text-white', 'shadow-lg');
            } else if (status === 'aberta') {
                button.classList.remove('bg-gray-100', 'hover:bg-gray-200', 'text-gray-700');
                button.classList.add('bg-gradient-to-r', 'from-green-600', 'to-green-500', 'text-white', 'shadow-lg');
            } else if (status === 'fechada') {
                button.classList.remove('bg-gray-100', 'hover:bg-gray-200', 'text-gray-700');
                button.classList.add('bg-gradient-to-r', 'from-amber-600', 'to-amber-500', 'text-white', 'shadow-lg');
            } else if (status === 'encerrada') {
                button.classList.remove('bg-gray-100', 'hover:bg-gray-200', 'text-gray-700');
                button.classList.add('bg-gradient-to-r', 'from-red-600', 'to-red-500', 'text-white', 'shadow-lg');
            }
            
            // Atualizar URL com o novo status
            const url = new URL(window.location);
            if (status) {
                url.searchParams.set('status', status);
            } else {
                url.searchParams.delete('status');
            }
            window.history.pushState({}, '', url.toString());
            
            // Aplicar filtros dinamicamente
            filtrarMesasDinamicamente();
            
            // Atualizar métricas
            setTimeout(() => {
                atualizarMetricasESaldos();
            }, 500);
        });
    });

    // Funções para modais de notificação
    function showConfirmModal(title, message, confirmText, confirmClass, onConfirm) {
        const modal = document.createElement('div');
        modal.className = 'fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4 animate-fade-in';
        
        const handleConfirm = () => {
            modal.remove();
            document.body.style.overflow = 'auto';
            onConfirm();
        };
        
        const handleCancel = () => {
            modal.remove();
            document.body.style.overflow = 'auto';
        };
        
        modal.innerHTML = `
            <div class="bg-white/95 backdrop-blur-xl rounded-2xl shadow-2xl border border-gray-200/20 max-w-md w-full transform transition-all duration-300 scale-95 opacity-0">
                <div class="p-6">
                    <div class="flex items-center gap-3 mb-4">
                        <div class="w-10 h-10 bg-yellow-100 rounded-xl flex items-center justify-center">
                            <svg class="w-6 h-6 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z"></path>
                            </svg>
                        </div>
                        <h3 class="text-xl font-bold text-gray-800">${title}</h3>
                    </div>
                    <p class="text-gray-600 mb-6">${message}</p>
                    <div class="flex gap-3">
                        <button class="flex-1 px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 font-semibold rounded-xl transition-all duration-300" id="cancelBtn">
                            Cancelar
                        </button>
                        <button class="flex-1 px-4 py-2 ${confirmClass} text-white font-semibold rounded-xl transition-all duration-300 hover:shadow-lg" id="confirmBtn">
                            ${confirmText}
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        document.body.style.overflow = 'hidden';
        
        // Adicionar event listeners após criar o modal
        const confirmBtn = modal.querySelector('#confirmBtn');
        const cancelBtn = modal.querySelector('#cancelBtn');
        
        confirmBtn.addEventListener('click', handleConfirm);
        cancelBtn.addEventListener('click', handleCancel);
        
        // Fechar modal ao clicar fora
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                handleCancel();
            }
        });
        
        // Fechar modal com ESC
        const handleEsc = (e) => {
            if (e.key === 'Escape') {
                handleCancel();
                document.removeEventListener('keydown', handleEsc);
            }
        };
        document.addEventListener('keydown', handleEsc);
        
        setTimeout(() => {
            const modalContent = modal.querySelector('div > div');
            modalContent.classList.remove('scale-95', 'opacity-0');
            modalContent.classList.add('show');
        }, 10);
    }

    function showSuccessModal(message) {
        const modal = document.createElement('div');
        modal.className = 'fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4 animate-fade-in';
        
        const handleClose = () => {
            modal.remove();
            document.body.style.overflow = 'auto';
        };
        
        modal.innerHTML = `
            <div class="bg-white/95 backdrop-blur-xl rounded-2xl shadow-2xl border border-green-200/20 max-w-md w-full transform transition-all duration-300 scale-95 opacity-0">
                <div class="p-6 text-center">
                    <div class="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                        <svg class="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                        </svg>
                    </div>
                    <h3 class="text-xl font-bold text-gray-800 mb-2">Sucesso!</h3>
                    <p class="text-gray-600 mb-6">${message}</p>
                    <button class="px-6 py-2 bg-green-600 hover:bg-green-700 text-white font-semibold rounded-xl transition-all duration-300" id="successOkBtn">
                        OK
                    </button>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        document.body.style.overflow = 'hidden';
        
        // Adicionar event listener ao botão
        const okBtn = modal.querySelector('#successOkBtn');
        okBtn.addEventListener('click', handleClose);
        
        // Fechar modal ao clicar fora
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                handleClose();
            }
        });
        
        // Fechar modal com ESC
        const handleEsc = (e) => {
            if (e.key === 'Escape') {
                handleClose();
                document.removeEventListener('keydown', handleEsc);
            }
        };
        document.addEventListener('keydown', handleEsc);
        
        setTimeout(() => {
            const modalContent = modal.querySelector('div > div');
            modalContent.classList.remove('scale-95', 'opacity-0');
            modalContent.classList.add('show');
        }, 10);
        
        // Auto-close após 3 segundos para não bloquear a interface
        setTimeout(() => {
            if (document.body.contains(modal)) {
                handleClose();
            }
        }, 3000);
    }

    function showErrorModal(message) {
        const modal = document.createElement('div');
        modal.className = 'fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4 animate-fade-in';
        
        const handleClose = () => {
            modal.remove();
            document.body.style.overflow = 'auto';
        };
        
        modal.innerHTML = `
            <div class="bg-white/95 backdrop-blur-xl rounded-2xl shadow-2xl border border-red-200/20 max-w-md w-full transform transition-all duration-300 scale-95 opacity-0">
                <div class="p-6 text-center">
                    <div class="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
                        <svg class="w-8 h-8 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                        </svg>
                    </div>
                    <h3 class="text-xl font-bold text-gray-800 mb-2">Erro!</h3>
                    <p class="text-gray-600 mb-6">${message}</p>
                    <button class="px-6 py-2 bg-red-600 hover:bg-red-700 text-white font-semibold rounded-xl transition-all duration-300" id="errorOkBtn">
                        OK
                    </button>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        document.body.style.overflow = 'hidden';
        
        // Adicionar event listener ao botão
        const okBtn = modal.querySelector('#errorOkBtn');
        okBtn.addEventListener('click', handleClose);
        
        // Fechar modal ao clicar fora
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                handleClose();
            }
        });
        
        // Fechar modal com ESC
        const handleEsc = (e) => {
            if (e.key === 'Escape') {
                handleClose();
                document.removeEventListener('keydown', handleEsc);
            }
        };
        document.addEventListener('keydown', handleEsc);
        
        setTimeout(() => {
            const modalContent = modal.querySelector('div > div');
            modalContent.classList.remove('scale-95', 'opacity-0');
            modalContent.classList.add('show');
        }, 10);
    }

    // Atualizar métricas e saldos quando a página carrega
    document.addEventListener('DOMContentLoaded', function() {
        console.log('🚀 DOM carregado, iniciando atualização de métricas...');
        
        // Verificar se os elementos existem
        const metricasContainer = document.getElementById('metricasContainer');
        console.log('🔍 Container de métricas encontrado:', !!metricasContainer);
        
        if (metricasContainer) {
            const cards = metricasContainer.querySelectorAll('div');
            console.log('🔍 Número de cards de métricas encontrados:', cards.length);
        }
        
        // Aguardar um pouco para garantir que todos os elementos estão carregados
        setTimeout(() => {
            console.log('⏰ Executando atualização de métricas após delay...');
            atualizarMetricasESaldos();
        }, 1000);
        
        // Botão de refresh para atualizar métricas e saldos
        const refreshBtn = document.getElementById('btnRefresh');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => {
                // Mostrar indicador de carregamento
                refreshBtn.innerHTML = `
                    <svg class="w-3 h-3 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
                    </svg>
                    Atualizando...
                `;
                refreshBtn.disabled = true;
                
                // Aplicar filtros dinamicamente
                filtrarMesasDinamicamente();
                
                // Atualizar métricas
                setTimeout(() => {
                    atualizarMetricasESaldos();
                    
                    // Restaurar botão
                    setTimeout(() => {
                        refreshBtn.innerHTML = `
                            <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
                            </svg>
                            Atualizar
                        `;
                        refreshBtn.disabled = false;
                    }, 1000);
                }, 500);
            });
        }
    });

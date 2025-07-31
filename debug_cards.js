// Script de debug para verificar os cards
console.log('🔍 Iniciando debug dos cards...');

// Verificar se o container existe
const metricasContainer = document.getElementById('metricasContainer');
console.log('Container de métricas:', metricasContainer);

if (metricasContainer) {
    const cards = metricasContainer.querySelectorAll('div');
    console.log('Número de cards encontrados:', cards.length);
    
    cards.forEach((card, index) => {
        console.log(`Card ${index + 1}:`, card);
        const dataCountElement = card.querySelector('[data-count]');
        console.log(`  - Elemento data-count:`, dataCountElement);
        if (dataCountElement) {
            console.log(`  - Valor atual:`, dataCountElement.textContent);
            console.log(`  - Data-count:`, dataCountElement.getAttribute('data-count'));
        }
    });
} else {
    console.error('❌ Container de métricas não encontrado!');
}

// Verificar se há CSRF token
const csrfElement = document.querySelector('[name=csrfmiddlewaretoken]');
console.log('CSRF element:', csrfElement);
if (csrfElement) {
    console.log('CSRF value:', csrfElement.value);
} else {
    console.error('❌ CSRF token não encontrado!');
}

// Testar a API diretamente
async function testarAPIDireto() {
    try {
        const response = await fetch('/mesas/api/atualizar-metricas/', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            },
        });
        
        console.log('Status da resposta:', response.status);
        const data = await response.json();
        console.log('Dados da API:', data);
        
        return data;
    } catch (error) {
        console.error('Erro na API:', error);
        return null;
    }
}

// Executar teste da API
testarAPIDireto(); 
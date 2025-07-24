# Filtro de Datas - Sistema de Receita Total

## Funcionalidade Implementada

O sistema agora possui um filtro de datas que permite calcular a **Receita Total** baseada no saldo das mesas em um período específico.

## Como Funciona

### 1. Filtro de Período
- **Localização**: Card de filtro no topo da página principal
- **Campos**: Data Início e Data Fim
- **Funcionalidade**: Permite selecionar um período específico para análise

### 2. Cálculo da Receita Total
A receita total é calculada somando os **saldos** das mesas que:
- Estão com status "Aberta" ou "Fechada" (não encerradas)
- Foram criadas ou atualizadas no período selecionado
- O saldo é calculado como: `valor_total - valor_inicial`

### 3. Variação Percentual
O sistema compara a receita do período selecionado com o período anterior de mesma duração:
- **Período anterior**: Mesmo número de dias antes do período selecionado
- **Cálculo**: `((receita_atual - receita_anterior) / receita_anterior) * 100`
- **Exibição**: Verde para positivo, vermelho para negativo

### 4. Período Padrão
Se nenhuma data for selecionada, o sistema usa automaticamente:
- **Data fim**: Hoje
- **Data início**: 30 dias atrás

## Interface do Usuário

### Card de Filtro
```
┌─────────────────────────────────────────────────────────┐
│ Filtro de Período                                       │
│ Selecione o período para calcular a receita total       │
│                                                         │
│ [Data Início] [Data Fim] [Filtrar] [Limpar]            │
└─────────────────────────────────────────────────────────┘
```

### Card de Receita Total Atualizado
```
┌─────────────────────────────────────────────────────────┐
│ R$ 132.000                                              │
│ Receita Total                                           │
│ de 01/12/2024 a 31/12/2024                             │
│ +12.5% vs período anterior                              │
└─────────────────────────────────────────────────────────┘
```

## Validações

1. **Datas válidas**: O sistema valida se as datas estão no formato correto
2. **Ordem das datas**: Data início não pode ser maior que data fim
3. **Período vazio**: Se não há mesas no período, usa todas as mesas ativas

## Tecnologias Utilizadas

- **Backend**: Django com filtros de data usando `Q` objects
- **Frontend**: JavaScript para validação e submissão do formulário
- **Template**: Django Template Language com filtros de data
- **Estilização**: Tailwind CSS para interface moderna

## Exemplo de Uso

1. **Selecionar período**: Escolher data início e fim no filtro
2. **Aplicar filtro**: Clicar em "Filtrar"
3. **Visualizar resultado**: A receita total será recalculada
4. **Comparar períodos**: A variação percentual mostra a evolução

## Benefícios

- **Análise temporal**: Permite acompanhar a evolução da receita
- **Flexibilidade**: Qualquer período pode ser analisado
- **Comparação**: Mostra variação em relação ao período anterior
- **Interface intuitiva**: Filtro fácil de usar com validações 
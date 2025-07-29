# Screenshots do Sistema Cass

Este diretório deve conter as screenshots do sistema para a landing page.

## ⚠️ IMPORTANTE: Imagens Temporárias

Atualmente, a landing page está usando placeholders temporários. Para adicionar as imagens reais:

## Imagens Necessárias:

### 1. `dashboard-screenshot.jpg`
- **Descrição**: Screenshot do dashboard principal
- **Conteúdo**: Painel com métricas, gráficos e estatísticas
- **Dimensões recomendadas**: 1200x800px
- **Formato**: JPG ou PNG

### 2. `financeiro-screenshot.jpg`
- **Descrição**: Screenshot do sistema financeiro
- **Conteúdo**: Interface de gestão de clientes e carteiras
- **Dimensões recomendadas**: 1200x800px
- **Formato**: JPG ou PNG

### 3. `mesas-screenshot.jpg`
- **Descrição**: Screenshot da gestão de mesas
- **Conteúdo**: Lista de mesas com status e controles
- **Dimensões recomendadas**: 1200x800px
- **Formato**: JPG ou PNG

### 4. `login-screenshot.jpg`
- **Descrição**: Screenshot da tela de login
- **Conteúdo**: Formulário de login com design moderno
- **Dimensões recomendadas**: 1200x800px
- **Formato**: JPG ou PNG

## Como Adicionar as Imagens Reais:

1. **Tire as screenshots** do sistema:
   - Dashboard: `/dashboard/`
   - Financeiro: `/financeiro/`
   - Mesas: `/mesas/todas/`
   - Login: `/usuarios/login/`

2. **Salve as imagens** com os nomes exatos:
   - `dashboard-screenshot.jpg`
   - `financeiro-screenshot.jpg`
   - `mesas-screenshot.jpg`
   - `login-screenshot.jpg`

3. **Coloque as imagens** neste diretório: `static/images/screenshots/`

4. **Edite o template** `divulgacao/templates/divulgacao/landing.html`:
   - Substitua os placeholders por `<img>` tags
   - Use: `<img src="{% static 'images/screenshots/nome-da-imagem.jpg' %}" alt="Descrição" class="w-full rounded-lg shadow-lg">`

## Exemplo de como ficará:

```html
<!-- Antes (placeholder) -->
<div class="bg-gray-700 rounded-lg p-8 text-center">
    <i class="fas fa-chart-bar text-6xl text-red-400 mb-4"></i>
    <h4 class="text-xl font-semibold text-white mb-2">Dashboard Cass</h4>
</div>

<!-- Depois (imagem real) -->
<img src="{% static 'images/screenshots/dashboard-screenshot.jpg' %}" alt="Dashboard Cass" class="w-full rounded-lg shadow-lg">
```

## Dicas:

- Use imagens de alta qualidade
- Mantenha proporções consistentes (1200x800px)
- Otimize as imagens para carregamento rápido
- Teste a responsividade em diferentes dispositivos
- Use formato JPG para melhor compressão 
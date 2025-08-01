from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.db import transaction
from decimal import Decimal
import json

from .models import Sange, CaixaSange, VendaFicha, TrocaFicha
from financeiro.models import Cliente, Carteira

@login_required
def listar_sanges(request):
    """Lista todas as sanges com caixas abertos primeiro"""
    # Busca todas as sanges ativas
    sanges = Sange.objects.filter(ativo=True)
    
    # Ordena: primeiro as que têm caixa aberto, depois por nome
    sanges_ordenadas = sorted(sanges, key=lambda s: (not s.caixa_aberto, s.nome))
    
    return render(request, 'sange/listar_sanges.html', {
        'sanges': sanges_ordenadas
    })

@login_required
def nova_sange(request):
    """Cria uma nova sange sem caixa aberto"""
    if request.method == 'POST':
        nome = request.POST.get('nome')
        if nome:
            # Cria apenas a sange, sem caixa
            sange = Sange.objects.create(nome=nome)
            
            messages.success(request, f'Sange "{nome}" criada com sucesso! Use o botão "Abrir Caixa" para iniciar as operações.')
            return redirect('sange:listar_sanges')
        else:
            messages.error(request, 'Nome é obrigatório!')
    
    return render(request, 'sange/nova_sange.html')

@login_required
def abrir_caixa(request, sange_id):
    """Abre um novo caixa para uma sange"""
    sange = get_object_or_404(Sange, id=sange_id, ativo=True)
    
    # Verifica se já existe um caixa aberto
    if sange.caixa_aberto:
        messages.error(request, 'Esta sange já possui um caixa aberto!')
        return redirect('sange:listar_sanges')
    
    if request.method == 'POST':
        try:
            # Coleta as fichas iniciais do formulário
            fichas_iniciais = {}
            valores_fichas = [5, 10, 25, 50, 100, 500, 1000, 5000, 10000]
            
            for valor in valores_fichas:
                quantidade = request.POST.get(f'ficha_{valor}', 0)
                if quantidade and int(quantidade) > 0:
                    fichas_iniciais[str(valor)] = int(quantidade)
            
            if not fichas_iniciais:
                messages.error(request, 'É necessário informar pelo menos uma ficha inicial!')
                return render(request, 'sange/abrir_caixa.html', {'sange': sange})
            
            # Cria o caixa
            caixa = CaixaSange.objects.create(
                sange=sange,
                fichas_iniciais=fichas_iniciais
            )
            
            messages.success(request, f'Caixa aberto para {sange.nome} com sucesso!')
            return redirect('sange:detalhes_caixa', caixa_id=caixa.id)
            
        except Exception as e:
            messages.error(request, f'Erro ao abrir caixa: {str(e)}')
    
    return render(request, 'sange/abrir_caixa.html', {
        'sange': sange,
        'valores_fichas': [5, 10, 25, 50, 100, 500, 1000, 5000, 10000]
    })

@login_required
def detalhes_caixa(request, caixa_id):
    """Mostra os detalhes de um caixa"""
    caixa = get_object_or_404(CaixaSange, id=caixa_id)
    
    # Busca vendas e trocas do caixa
    vendas = VendaFicha.objects.filter(caixa_sange=caixa).order_by('-data')
    trocas = TrocaFicha.objects.filter(caixa_sange=caixa).order_by('-data')
    
    return render(request, 'sange/detalhes_caixa.html', {
        'caixa': caixa,
        'vendas': vendas,
        'trocas': trocas
    })

@login_required
def vender_fichas(request, caixa_id):
    """Realiza uma venda de fichas"""
    caixa = get_object_or_404(CaixaSange, id=caixa_id)
    
    if not caixa.esta_aberto:
        messages.error(request, 'Este caixa está fechado!')
        return redirect('sange:listar_sanges')
    
    if request.method == 'POST':
        try:
            valor_total_venda = int(request.POST.get('valor_total_venda'))
            jogador_id = request.POST.get('jogador')
            
            # Coleta as quantidades de cada tipo de ficha
            fichas_vendidas = {}
            valores_fichas = [5, 10, 25, 50, 100, 500, 1000, 5000, 10000]
            total_calculado = 0
            
            for valor in valores_fichas:
                quantidade = int(request.POST.get(f'quantidade_{valor}', 0))
                if quantidade > 0:
                    fichas_vendidas[str(valor)] = quantidade
                    total_calculado += valor * quantidade
            
            # Verifica se o total calculado é igual ao valor total informado
            if total_calculado != valor_total_venda:
                messages.error(request, f'Valor total não confere! Calculado: R$ {total_calculado}, Informado: R$ {valor_total_venda}')
                return render(request, 'sange/vender_fichas.html', {
                    'caixa': caixa,
                    'jogadores': Cliente.objects.all().order_by('nome'),
                    'valores_fichas': valores_fichas
                })
            
            # Verifica se há fichas suficientes para cada tipo
            for valor, quantidade in fichas_vendidas.items():
                fichas_disponiveis = caixa.fichas_atuais.get(valor, 0)
                if fichas_disponiveis < quantidade:
                    messages.error(request, f'Fichas de R$ {valor} insuficientes! Disponível: {fichas_disponiveis}, Solicitado: {quantidade}')
                    return render(request, 'sange/vender_fichas.html', {
                        'caixa': caixa,
                        'jogadores': Cliente.objects.all().order_by('nome'),
                        'valores_fichas': valores_fichas
                    })
            
            # Cria as vendas para cada tipo de ficha
            jogador = None
            if jogador_id:
                jogador = Cliente.objects.get(id=jogador_id)
            
            vendas_criadas = []
            for valor, quantidade in fichas_vendidas.items():
                venda = VendaFicha.objects.create(
                    caixa_sange=caixa,
                    jogador=jogador,
                    valor_unitario=int(valor),
                    quantidade=quantidade
                )
                vendas_criadas.append(venda)
            
            # Atualiza o saldo do jogador se foi selecionado
            if jogador:
                valor_total_venda_decimal = Decimal(str(valor_total_venda))
                
                # Atualizar saldo em dinheiro
                jogador.saldo += valor_total_venda_decimal
                jogador.save()
                
                # Atualizar ou criar carteira com saldo de fichas
                try:
                    carteira = jogador.carteira
                except:
                    # Se não tem carteira, criar uma
                    carteira = Carteira.objects.create(cliente=jogador, saldo_fichas=0)
                
                # Adicionar fichas à carteira (cada R$ 1,00 = 1 ficha)
                fichas_adicionadas = int(valor_total_venda_decimal)
                carteira.saldo_fichas += fichas_adicionadas
                carteira.save()
                
                messages.success(request, f'Venda registrada: R$ {valor_total_venda} em fichas. Saldo do jogador atualizado: R$ {jogador.saldo} ({fichas_adicionadas} fichas adicionadas)')
            else:
                messages.success(request, f'Venda registrada: R$ {valor_total_venda} em fichas')
            
            return redirect('sange:detalhes_caixa', caixa_id=caixa.id)
            
        except Exception as e:
            messages.error(request, f'Erro ao registrar venda: {str(e)}')
    
    return render(request, 'sange/vender_fichas.html', {
        'caixa': caixa,
        'jogadores': Cliente.objects.all().order_by('nome'),
        'valores_fichas': [5, 10, 25, 50, 100, 500, 1000, 5000, 10000]
    })

@login_required
def trocar_fichas(request, caixa_id):
    """Realiza uma troca de fichas"""
    caixa = get_object_or_404(CaixaSange, id=caixa_id)
    
    if not caixa.esta_aberto:
        messages.error(request, 'Este caixa está fechado!')
        return redirect('sange:listar_sanges')
    
    if request.method == 'POST':
        try:
            valor_total_troca = int(request.POST.get('valor_total_troca'))
            valor_ficha_troca = int(request.POST.get('valor_ficha_troca'))
            
            # Coleta as quantidades de cada tipo de ficha a ser trocada
            fichas_trocadas = {}
            valores_fichas = [5, 10, 25, 50, 100, 500, 1000, 5000, 10000]
            total_calculado = 0
            
            for valor in valores_fichas:
                quantidade = int(request.POST.get(f'quantidade_{valor}', 0))
                if quantidade > 0:
                    fichas_trocadas[str(valor)] = quantidade
                    total_calculado += valor * quantidade
            
            # Verifica se o total calculado é igual ao valor total informado
            if total_calculado != valor_total_troca:
                messages.error(request, f'Valor total não confere! Calculado: R$ {total_calculado}, Informado: R$ {valor_total_troca}')
                return render(request, 'sange/trocar_fichas.html', {
                    'caixa': caixa,
                    'valores_fichas': valores_fichas
                })
            
            # Verifica se há fichas suficientes para cada tipo
            for valor, quantidade in fichas_trocadas.items():
                fichas_disponiveis = caixa.fichas_atuais.get(valor, 0)
                if fichas_disponiveis < quantidade:
                    messages.error(request, f'Fichas de R$ {valor} insuficientes! Disponível: {fichas_disponiveis}, Solicitado: {quantidade}')
                    return render(request, 'sange/trocar_fichas.html', {
                        'caixa': caixa,
                        'valores_fichas': valores_fichas
                    })
            
            # Verifica se a divisão é exata
            if valor_total_troca % valor_ficha_troca != 0:
                messages.error(request, f'Valor R$ {valor_total_troca} não é divisível por R$ {valor_ficha_troca}!')
                return render(request, 'sange/trocar_fichas.html', {
                    'caixa': caixa,
                    'valores_fichas': valores_fichas
                })
            
            quantidade_gerada = valor_total_troca // valor_ficha_troca
            
            # Cria a troca
            troca = TrocaFicha.objects.create(
                caixa_sange=caixa,
                valor_original=valor_total_troca,
                valor_ficha_troca=valor_ficha_troca,
                quantidade_gerada=quantidade_gerada
            )
            
            messages.success(request, f'Troca registrada: R$ {valor_total_troca} por {quantidade_gerada}x R$ {valor_ficha_troca}')
            return redirect('sange:detalhes_caixa', caixa_id=caixa.id)
            
        except Exception as e:
            messages.error(request, f'Erro ao registrar troca: {str(e)}')
    
    return render(request, 'sange/trocar_fichas.html', {
        'caixa': caixa,
        'valores_fichas': [5, 10, 25, 50, 100, 500, 1000, 5000, 10000]
    })

@login_required
def fechar_caixa(request, caixa_id):
    """Fecha um caixa"""
    caixa = get_object_or_404(CaixaSange, id=caixa_id)
    
    if not caixa.esta_aberto:
        messages.error(request, 'Este caixa já está fechado!')
        return redirect('sange:listar_sanges')
    
    if request.method == 'POST':
        try:
            caixa.fechar_caixa()
            messages.success(request, f'Caixa de {caixa.sange.nome} fechado com sucesso!')
            return redirect('sange:listar_sanges')
        except Exception as e:
            messages.error(request, f'Erro ao fechar caixa: {str(e)}')
    
    return render(request, 'sange/fechar_caixa.html', {'caixa': caixa})

# APIs para AJAX
@csrf_exempt
@require_http_methods(["POST"])
def api_calcular_valor_total(request):
    """API para calcular o valor total das fichas"""
    try:
        data = json.loads(request.body)
        fichas = data.get('fichas', {})
        
        total = Decimal('0.00')
        for valor, quantidade in fichas.items():
            if quantidade and valor:
                total += Decimal(str(valor)) * Decimal(str(quantidade))
        
        return JsonResponse({
            'success': True,
            'valor_total': str(total)
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

@csrf_exempt
@require_http_methods(["POST"])
def api_calcular_troca(request):
    """API para calcular quantidade de fichas na troca"""
    try:
        data = json.loads(request.body)
        valor_original = int(data.get('valor_original', 0))
        valor_ficha_troca = int(data.get('valor_ficha_troca', 0))
        
        if valor_original % valor_ficha_troca != 0:
            return JsonResponse({
                'success': False,
                'error': f'Valor R$ {valor_original} não é divisível por R$ {valor_ficha_troca}'
            })
        
        quantidade_gerada = valor_original // valor_ficha_troca
        
        return JsonResponse({
            'success': True,
            'quantidade_gerada': quantidade_gerada
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

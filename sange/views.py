from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.db import transaction
from decimal import Decimal
import json

from .models import Sange, CaixaSange, VendaFicha as VendaFichaSange, TrocaFicha
from financeiro.models import Cliente, Carteira

@login_required
def listar_sanges(request):
    """Lista todas as sanges"""
    sanges = Sange.objects.filter(ativo=True).order_by('nome')
    return render(request, 'sange/listar_sanges.html', {
        'sanges': sanges
    })

@login_required
def nova_sange(request):
    """Cria uma nova sange"""
    if request.method == 'POST':
        nome = request.POST.get('nome')
        if nome:
            Sange.objects.create(nome=nome)
            messages.success(request, 'Sange criada com sucesso!')
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
    vendas = VendaFichaSange.objects.filter(caixa_sange=caixa).order_by('-data')
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
            valor_unitario = int(request.POST.get('valor_unitario'))
            quantidade = int(request.POST.get('quantidade'))
            jogador_id = request.POST.get('jogador')
            
            # Verifica se há fichas suficientes
            fichas_disponiveis = caixa.fichas_atuais.get(str(valor_unitario), 0)
            if fichas_disponiveis < quantidade:
                messages.error(request, f'Fichas insuficientes! Disponível: {fichas_disponiveis}')
                return render(request, 'sange/vender_fichas.html', {
                    'caixa': caixa,
                    'jogadores': Cliente.objects.all().order_by('nome')
                })
            
            # Cria a venda
            jogador = None
            if jogador_id:
                jogador = Cliente.objects.get(id=jogador_id)
            
            venda = VendaFichaSange.objects.create(
                caixa_sange=caixa,
                jogador=jogador,
                valor_unitario=valor_unitario,
                quantidade=quantidade
            )
            
            # Atualiza o saldo do jogador se foi selecionado
            if jogador:
                valor_total_venda = Decimal(str(venda.valor_total))
                
                # Atualizar saldo em dinheiro
                jogador.saldo += valor_total_venda
                jogador.save()
                
                # Atualizar ou criar carteira com saldo de fichas
                try:
                    carteira = jogador.carteira
                except:
                    # Se não tem carteira, criar uma
                    carteira = Carteira.objects.create(cliente=jogador, saldo_fichas=0)
                
                # Adicionar fichas à carteira (cada R$ 1,00 = 1 ficha)
                fichas_adicionadas = int(valor_total_venda)
                carteira.saldo_fichas += fichas_adicionadas
                carteira.save()
                
                messages.success(request, f'Venda registrada: {quantidade}x R$ {valor_unitario} = R$ {venda.valor_total}. Saldo do jogador atualizado: R$ {jogador.saldo} ({fichas_adicionadas} fichas adicionadas)')
            else:
                messages.success(request, f'Venda registrada: {quantidade}x R$ {valor_unitario} = R$ {venda.valor_total}')
            
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
            valor_original = int(request.POST.get('valor_original'))
            valor_ficha_troca = int(request.POST.get('valor_ficha_troca'))
            
            # Verifica se há fichas do valor original
            fichas_originais = caixa.fichas_atuais.get(str(valor_original), 0)
            if fichas_originais < 1:
                messages.error(request, f'Fichas de R$ {valor_original} insuficientes!')
                return render(request, 'sange/trocar_fichas.html', {
                    'caixa': caixa,
                    'valores_fichas': [5, 10, 25, 50, 100, 500, 1000, 5000, 10000]
                })
            
            # Verifica se a divisão é exata
            if valor_original % valor_ficha_troca != 0:
                messages.error(request, f'Valor R$ {valor_original} não é divisível por R$ {valor_ficha_troca}!')
                return render(request, 'sange/trocar_fichas.html', {
                    'caixa': caixa,
                    'valores_fichas': [5, 10, 25, 50, 100, 500, 1000, 5000, 10000]
                })
            
            quantidade_gerada = valor_original // valor_ficha_troca
            
            # Cria a troca
            troca = TrocaFicha.objects.create(
                caixa_sange=caixa,
                valor_original=valor_original,
                valor_ficha_troca=valor_ficha_troca,
                quantidade_gerada=quantidade_gerada
            )
            
            messages.success(request, f'Troca registrada: R$ {valor_original} por {quantidade_gerada}x R$ {valor_ficha_troca}')
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

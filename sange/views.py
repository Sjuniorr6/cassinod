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
def historico_movimentos(request):
    """Histórico unificado de vendas e trocas com filtros."""
    # Filtros
    data_inicio = request.GET.get('data_inicio')
    data_fim = request.GET.get('data_fim')
    sange_id = request.GET.get('sange')
    caixa_id = request.GET.get('caixa')
    jogador_id = request.GET.get('jogador')
    tipo = request.GET.get('tipo')  # 'venda', 'troca' ou None

    vendas_qs = VendaFicha.objects.select_related('caixa_sange__sange', 'jogador')
    trocas_qs = TrocaFicha.objects.select_related('caixa_sange__sange')

    # Aplicar filtros
    from django.utils.dateparse import parse_date
    if data_inicio:
        di = parse_date(data_inicio)
        if di:
            vendas_qs = vendas_qs.filter(data__date__gte=di)
            trocas_qs = trocas_qs.filter(data__date__gte=di)
    if data_fim:
        df = parse_date(data_fim)
        if df:
            vendas_qs = vendas_qs.filter(data__date__lte=df)
            trocas_qs = trocas_qs.filter(data__date__lte=df)
    if sange_id:
        vendas_qs = vendas_qs.filter(caixa_sange__sange_id=sange_id)
        trocas_qs = trocas_qs.filter(caixa_sange__sange_id=sange_id)
    if caixa_id:
        vendas_qs = vendas_qs.filter(caixa_sange_id=caixa_id)
        trocas_qs = trocas_qs.filter(caixa_sange_id=caixa_id)
    if jogador_id:
        vendas_qs = vendas_qs.filter(jogador_id=jogador_id)
    # tipo: aplicamos abaixo quando unificar

    # Unificar em uma lista com campos comuns
    movimentos = []
    total_vendas_valor = Decimal('0.00')
    total_trocas_valor = Decimal('0.00')
    for v in vendas_qs:
        movimentos.append({
            'tipo': 'venda',
            'data': v.data,
            'sange': v.caixa_sange.sange.nome,
            'caixa_id': v.caixa_sange_id,
            'descricao': f"Venda {v.quantidade}x R$ {v.valor_unitario}",
            'valor': float(v.valor_total),
            'jogador': v.jogador.nome_completo if v.jogador else '—',
        })
        try:
            total_vendas_valor += Decimal(v.valor_total)
        except Exception:
            total_vendas_valor += Decimal(str(v.valor_total))
    for t in trocas_qs:
        movimentos.append({
            'tipo': 'troca',
            'data': t.data,
            'sange': t.caixa_sange.sange.nome,
            'caixa_id': t.caixa_sange_id,
            'descricao': f"Troca R$ {t.valor_original} por {t.quantidade_gerada}x R$ {t.valor_ficha_troca}",
            'valor': float(t.valor_original),
            'jogador': '—',
        })
        total_trocas_valor += Decimal(str(t.valor_original))

    if tipo in ('venda', 'troca'):
        movimentos = [m for m in movimentos if m['tipo'] == tipo]

    # Ordenar por data desc
    movimentos.sort(key=lambda m: m['data'], reverse=True)

    # Opções de selects
    sanges = Sange.objects.all().order_by('nome')
    caixas = CaixaSange.objects.all().order_by('-data_abertura')
    jogadores = Cliente.objects.all().order_by('nome')

    return render(request, 'sange/historico.html', {
        'movimentos': movimentos,
        'sanges': sanges,
        'caixas': caixas,
        'jogadores': jogadores,
        'totais': {
            'vendas': float(total_vendas_valor),
            'trocas': float(total_trocas_valor),
            'saldo': float(total_vendas_valor - total_trocas_valor),
            'qtd_movimentos': len(movimentos),
        },
        'f': {
            'data_inicio': data_inicio or '',
            'data_fim': data_fim or '',
            'sange': int(sange_id) if sange_id else '',
            'caixa': int(caixa_id) if caixa_id else '',
            'jogador': int(jogador_id) if jogador_id else '',
            'tipo': tipo or '',
        }
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
            canhoto = request.POST.get('canhoto', '').strip()
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
                
                mensagem_extra = f" | Canhoto: {canhoto}" if canhoto else ""
                messages.success(request, f'Venda registrada: R$ {valor_total_venda} em fichas. Saldo do jogador atualizado: R$ {jogador.saldo} ({fichas_adicionadas} fichas adicionadas){mensagem_extra}')
            else:
                mensagem_extra = f" | Canhoto: {canhoto}" if canhoto else ""
                messages.success(request, f'Venda registrada: R$ {valor_total_venda} em fichas{mensagem_extra}')
            
            return redirect('sange:detalhes_caixa', caixa_id=caixa.id)
            
        except Exception as e:
            messages.error(request, f'Erro ao registrar venda: {str(e)}')
    
    return render(request, 'sange/vender_fichas.html', {
        'caixa': caixa,
        'jogadores': Cliente.objects.all().order_by('nome'),
        # Remover fichas de 10 e 50
        'valores_fichas': [5, 25, 100, 500, 1000, 5000, 10000]
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

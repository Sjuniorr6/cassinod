from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import datetime, timedelta
import json

from sange.models import VendaFicha, Sange, CaixaSange
from financeiro.models import Cliente
from mesas.models import Mesa, RegistroSaldoMesa

@login_required
def dashboard_home(request):
    """Dashboard principal com estatísticas gerais"""
    
    # Período para análise (últimos 30 dias por padrão)
    data_fim = timezone.now().date()
    data_inicio = data_fim - timedelta(days=30)
    
    # Obter parâmetros de data do request
    if request.GET.get('data_inicio') and request.GET.get('data_fim'):
        try:
            data_inicio = datetime.strptime(request.GET.get('data_inicio'), '%Y-%m-%d').date()
            data_fim = datetime.strptime(request.GET.get('data_fim'), '%Y-%m-%d').date()
        except ValueError:
            pass
    
    # Estatísticas gerais
    total_vendas = VendaFicha.objects.filter(
        data__date__gte=data_inicio,
        data__date__lte=data_fim
    ).aggregate(total=Sum('valor_total'))['total'] or 0
    
    total_vendas_quantidade = VendaFicha.objects.filter(
        data__date__gte=data_inicio,
        data__date__lte=data_fim
    ).aggregate(total=Sum('quantidade'))['total'] or 0
    
    # Top 5 Sanges que mais venderam
    top_sanges = []
    sanges_com_vendas = Sange.objects.all()
    
    for sange in sanges_com_vendas:
        total_vendas_sange = sange.total_vendas
        if total_vendas_sange > 0:
            top_sanges.append({
                'nome': sange.nome,
                'total_vendas': total_vendas_sange
            })
    
    # Ordenar por total de vendas e pegar top 5
    top_sanges.sort(key=lambda x: x['total_vendas'], reverse=True)
    top_sanges = top_sanges[:5]
    
    # Top 5 Clientes que mais compraram
    top_clientes = Cliente.objects.annotate(
        total_compras=Sum('vendaficha__valor_total')
    ).filter(
        total_compras__gt=0
    ).order_by('-total_compras')[:5]
    
    # Vendas por dia da semana
    vendas_por_dia = {}
    dias_semana = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo']
    
    for i in range(7):
        vendas_por_dia[dias_semana[i]] = float(VendaFicha.objects.filter(
            data__date__gte=data_inicio,
            data__date__lte=data_fim,
            data__week_day=(i + 2) % 7 or 7  # Django usa 1=Domingo, 2=Segunda, etc.
        ).aggregate(total=Sum('valor_total'))['total'] or 0)
    
    # Vendas por hora do dia
    vendas_por_hora = {}
    for hora in range(24):
        vendas_por_hora[hora] = float(VendaFicha.objects.filter(
            data__date__gte=data_inicio,
            data__date__lte=data_fim,
            data__hour=hora
        ).aggregate(total=Sum('valor_total'))['total'] or 0)
    
    # Vendas por valor de ficha
    vendas_por_valor = {}
    valores_fichas = [5, 10, 25, 50, 100, 500, 1000, 5000, 10000]
    
    for valor in valores_fichas:
        vendas_por_valor[valor] = VendaFicha.objects.filter(
            data__date__gte=data_inicio,
            data__date__lte=data_fim,
            valor_unitario=valor
        ).aggregate(total=Sum('valor_total'))['total'] or 0
    
    # Estatísticas de mesas
    mesas_ativas = Mesa.objects.filter(status='aberta').count()
    total_mesas = Mesa.objects.exclude(status='encerrada').count()
    
    # Caixas abertos
    caixas_abertos = CaixaSange.objects.filter(data_fechamento__isnull=True).count()
    
    # Performance correta por croupier baseada em SESSÕES por mesa:
    # Sequências contínuas de registros com o mesmo croupier formam uma sessão.
    # Delta da sessão = último_saldo - primeiro_saldo. Somamos por croupier.
    registros = RegistroSaldoMesa.objects.filter(
        criado_em__date__gte=data_inicio,
        criado_em__date__lte=data_fim
    ).order_by('mesa_id', 'criado_em')

    deltas_por_croupier = {}
    sessao_por_mesa = {}  # mesa_id -> { 'cid': int|None, 'first': float, 'last': float }
    prev_saldo_por_mesa = {}

    # Pré-seedar saldo anterior ao período para cada mesa envolvida
    mesa_ids_periodo = list(registros.values_list('mesa_id', flat=True).distinct())
    if mesa_ids_periodo:
        anteriores = (
            RegistroSaldoMesa.objects
            .filter(mesa_id__in=mesa_ids_periodo, criado_em__date__lt=data_inicio)
            .order_by('mesa_id', '-criado_em')
        )
        visto = set()
        for rprev in anteriores:
            if rprev.mesa_id in visto:
                continue
            prev_saldo_por_mesa[rprev.mesa_id] = float(rprev.saldo)
            visto.add(rprev.mesa_id)

    def fechar_sessao(mesa_id):
        sess = sessao_por_mesa.get(mesa_id)
        if not sess:
            return
        cid = sess.get('cid')
        if cid:
            delta = float(sess.get('last', 0.0)) - float(sess.get('first', 0.0))
            deltas_por_croupier[cid] = deltas_por_croupier.get(cid, 0.0) + delta
        sessao_por_mesa.pop(mesa_id, None)

    for r in registros:
        mesa_id = r.mesa_id
        cid_atual = r.croupier_id
        saldo_atual = float(r.saldo)

        sess = sessao_por_mesa.get(mesa_id)

        # Sem croupier no registro -> fecha sessão atual (se existir) e não inicia nova
        if not cid_atual:
            fechar_sessao(mesa_id)
            prev_saldo_por_mesa[mesa_id] = saldo_atual
            continue

        if not sess:
            # inicia sessão usando saldo anterior como baseline (ou 0 se não houver)
            first_baseline = prev_saldo_por_mesa.get(mesa_id, 0.0)
            sessao_por_mesa[mesa_id] = {'cid': cid_atual, 'first': first_baseline, 'last': saldo_atual}
        else:
            if sess['cid'] == cid_atual:
                # prossegue mesma sessão
                sess['last'] = saldo_atual
            else:
                # troca de croupier: fecha sessão anterior e inicia nova
                fechar_sessao(mesa_id)
                first_baseline = prev_saldo_por_mesa.get(mesa_id, 0.0)
                sessao_por_mesa[mesa_id] = {'cid': cid_atual, 'first': first_baseline, 'last': saldo_atual}

        # atualizar saldo anterior para a mesa
        prev_saldo_por_mesa[mesa_id] = saldo_atual

    # Fechar sessões em aberto ao final
    for mesa_id in list(sessao_por_mesa.keys()):
        fechar_sessao(mesa_id)
    
    # Transformar em lista com nomes
    croupier_labels = []
    croupier_values = []
    if deltas_por_croupier:
        from croupiers.models import Croupier
        for cid, valor in deltas_por_croupier.items():
            try:
                nome = Croupier.objects.get(id=cid).nome
            except Croupier.DoesNotExist:
                nome = f"Croupier {cid}"
            croupier_labels.append(nome)
            croupier_values.append(round(valor, 2))
    
    context = {
        'data_inicio': data_inicio,
        'data_fim': data_fim,
        'total_vendas': total_vendas,
        'total_vendas_quantidade': total_vendas_quantidade,
        'top_sanges': top_sanges,
        'top_clientes': top_clientes,
        'vendas_por_dia_json': json.dumps(vendas_por_dia, ensure_ascii=False),
        'vendas_por_hora_json': json.dumps(vendas_por_hora),
        'vendas_por_valor': vendas_por_valor,
        'mesas_ativas': mesas_ativas,
        'total_mesas': total_mesas,
        'caixas_abertos': caixas_abertos,
        'dias_semana_json': json.dumps(dias_semana, ensure_ascii=False),
        'croupier_perf_labels_json': json.dumps(croupier_labels, ensure_ascii=False),
        'croupier_perf_values_json': json.dumps(croupier_values),
    }
    
    return render(request, 'dashboard/home.html', context)

@login_required
def api_estatisticas(request):
    """API para obter estatísticas em formato JSON"""
    try:
        # Período para análise
        data_fim = timezone.now().date()
        data_inicio = data_fim - timedelta(days=30)
        
        if request.GET.get('data_inicio') and request.GET.get('data_fim'):
            try:
                data_inicio = datetime.strptime(request.GET.get('data_inicio'), '%Y-%m-%d').date()
                data_fim = datetime.strptime(request.GET.get('data_fim'), '%Y-%m-%d').date()
            except ValueError:
                pass
        
        # Top 5 Sanges
        top_sanges_data = []
        sanges_com_vendas = Sange.objects.all()
        
        for sange in sanges_com_vendas:
            total_vendas_sange = sange.total_vendas
            if total_vendas_sange > 0:
                top_sanges_data.append({
                    'nome': sange.nome,
                    'total_vendas': float(total_vendas_sange)
                })
        
        # Ordenar por total de vendas e pegar top 5
        top_sanges_data.sort(key=lambda x: x['total_vendas'], reverse=True)
        top_sanges_data = top_sanges_data[:5]
        
        # Top 5 Clientes
        top_clientes_data = []
        top_clientes = Cliente.objects.annotate(
            total_compras=Sum('vendaficha__valor_total')
        ).filter(
            total_compras__gt=0
        ).order_by('-total_compras')[:5]
        
        for cliente in top_clientes:
            top_clientes_data.append({
                'nome': cliente.nome_completo,
                'total_compras': float(cliente.total_compras or 0)
            })
        
        # Vendas por dia da semana
        vendas_por_dia = {}
        dias_semana = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo']
        
        for i in range(7):
            vendas_por_dia[dias_semana[i]] = float(VendaFicha.objects.filter(
                data__date__gte=data_inicio,
                data__date__lte=data_fim,
                data__week_day=(i + 2) % 7 or 7
            ).aggregate(total=Sum('valor_total'))['total'] or 0)
        
        # Vendas por hora
        vendas_por_hora = {}
        for hora in range(24):
            vendas_por_hora[hora] = float(VendaFicha.objects.filter(
                data__date__gte=data_inicio,
                data__date__lte=data_fim,
                data__hour=hora
            ).aggregate(total=Sum('valor_total'))['total'] or 0)
        
        return JsonResponse({
            'success': True,
            'data': {
                'top_sanges': top_sanges_data,
                'top_clientes': top_clientes_data,
                'vendas_por_dia': vendas_por_dia,
                'vendas_por_hora': vendas_por_hora,
                'periodo': {
                    'inicio': data_inicio.strftime('%Y-%m-%d'),
                    'fim': data_fim.strftime('%Y-%m-%d')
                }
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

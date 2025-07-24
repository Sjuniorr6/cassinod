from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db import models
from django.utils import timezone
from datetime import datetime, timedelta
import json
from .models import Mesa

def mesas_home(request):
    # Obter parâmetros de data do request
    data_inicio = request.GET.get('data_inicio')
    data_fim = request.GET.get('data_fim')
    
    # Se não foram fornecidas datas, usar o último mês como padrão
    if not data_inicio or not data_fim:
        data_fim = timezone.now().date()
        data_inicio = data_fim - timedelta(days=30)
    else:
        try:
            data_inicio = datetime.strptime(data_inicio, '%Y-%m-%d').date()
            data_fim = datetime.strptime(data_fim, '%Y-%m-%d').date()
        except ValueError:
            # Se as datas não são válidas, usar o último mês
            data_fim = timezone.now().date()
            data_inicio = data_fim - timedelta(days=30)
    
    # Filtrar apenas mesas que não estão encerradas
    mesas = Mesa.objects.exclude(status='encerrada').order_by('numero_mesa')
    
    # Calcular estatísticas gerais (sempre mostradas)
    mesas_ativas = Mesa.objects.filter(status='aberta').count()
    total_mesas = Mesa.objects.exclude(status='encerrada').count()
    
    # Calcular receita total ESPECIFICAMENTE do período selecionado
    # Filtra mesas que foram criadas ou atualizadas no período
    mesas_periodo = Mesa.objects.filter(
        models.Q(data_criacao__date__range=[data_inicio, data_fim]) |
        models.Q(data_atualizacao__date__range=[data_inicio, data_fim])
    ).exclude(status='encerrada')
    
    # Receita total do período (soma dos saldos das mesas no período)
    receita_total = mesas_periodo.filter(
        status__in=['aberta', 'fechada']
    ).aggregate(
        total=models.Sum('saldo')
    )['total'] or 0
    
    # Se não há mesas no período, mostrar 0 (não usar todas as mesas)
    if not mesas_periodo.exists():
        receita_total = 0
    
    # Calcular total de fichas vendidas (soma dos valores totais de mesas abertas)
    fichas_vendidas = Mesa.objects.filter(status='aberta').aggregate(
        total=models.Sum('valor_total')
    )['total'] or 0
    
    # Estoque restante (valor total de todas as mesas menos fichas vendidas)
    estoque_restante = Mesa.objects.aggregate(
        total=models.Sum('valor_total')
    )['total'] or 0
    estoque_restante -= fichas_vendidas
    
    # Calcular variação percentual (comparar com período anterior)
    periodo_anterior_inicio = data_inicio - timedelta(days=(data_fim - data_inicio).days)
    periodo_anterior_fim = data_inicio - timedelta(days=1)
    
    mesas_periodo_anterior = Mesa.objects.filter(
        models.Q(data_criacao__date__range=[periodo_anterior_inicio, periodo_anterior_fim]) |
        models.Q(data_atualizacao__date__range=[periodo_anterior_inicio, periodo_anterior_fim])
    ).exclude(status='encerrada').filter(
        status__in=['aberta', 'fechada']
    ).aggregate(
        total=models.Sum('saldo')
    )['total'] or 0
    
    # Calcular variação percentual
    if mesas_periodo_anterior > 0:
        variacao_percentual = ((receita_total - mesas_periodo_anterior) / mesas_periodo_anterior) * 100
    else:
        variacao_percentual = 0 if receita_total == 0 else 100
    
    # Determinar se há filtro ativo
    filtro_ativo = bool(data_inicio and data_fim)
    
    context = {
        'mesas': mesas,
        'mesas_ativas': mesas_ativas,
        'total_mesas': total_mesas,
        'receita_total': receita_total,
        'fichas_vendidas': fichas_vendidas,
        'estoque_restante': estoque_restante,
        'data_inicio': data_inicio,
        'data_fim': data_fim,
        'variacao_percentual': variacao_percentual,
        'periodo_texto': f"de {data_inicio.strftime('%d/%m/%Y')} a {data_fim.strftime('%d/%m/%Y')}",
        'filtro_ativo': filtro_ativo,
        'mesas_periodo_count': mesas_periodo.count()  # Quantidade de mesas no período
    }
    
    return render(request, 'home.html', context)

@csrf_exempt
def criar_mesa(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            numero_mesa = data.get('numero_mesa')
            
            # Verificar se já existe uma mesa com o mesmo número que esteja aberta ou fechada
            mesa_existente = Mesa.objects.filter(
                numero_mesa=numero_mesa,
                status__in=['aberta', 'fechada']
            ).first()
            
            if mesa_existente:
                return JsonResponse({
                    'success': False,
                    'message': f'Já existe uma mesa {numero_mesa} com status "{mesa_existente.get_status_display()}". Encerre a mesa existente antes de criar uma nova.'
                }, status=400)
            
            mesa = Mesa.objects.create(
                numero_mesa=numero_mesa,
                tipo_jogo=data.get('tipo_jogo'),
                status=data.get('status', 'aberta'),
                fichas_5=data.get('fichas_5', 0),
                fichas_25=data.get('fichas_25', 0),
                fichas_100=data.get('fichas_100', 0),
                fichas_500=data.get('fichas_500', 0),
                fichas_1000=data.get('fichas_1000', 0),
                fichas_5000=data.get('fichas_5000', 0),
                fichas_10000=data.get('fichas_10000', 0)
            )
            return JsonResponse({
                'success': True,
                'message': f'Mesa {mesa.numero_mesa} criada com sucesso!',
                'mesa_id': mesa.id
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            }, status=400)
    return JsonResponse({'success': False, 'message': 'Método não permitido'}, status=405)

def listar_mesas_api(request):
    mesas = Mesa.objects.all()
    data = []
    for mesa in mesas:
        data.append({
            'id': mesa.id,
            'numero_mesa': mesa.numero_mesa,
            'tipo_jogo': mesa.tipo_jogo,
            'tipo_jogo_display': mesa.get_tipo_jogo_display(),
            'valor_total': mesa.valor_total,
            'status': mesa.status,
            'status_display': mesa.get_status_display(),
        })
    return JsonResponse({'mesas': data})

def obter_mesa_api(request, mesa_id):
    try:
        mesa = Mesa.objects.get(id=mesa_id)
        data = {
            'id': mesa.id,
            'numero_mesa': mesa.numero_mesa,
            'tipo_jogo': mesa.tipo_jogo,
            'tipo_jogo_display': mesa.get_tipo_jogo_display(),
            'valor_total': mesa.valor_total,
            'status': mesa.status,
            'status_display': mesa.get_status_display(),
        }
        return JsonResponse(data)
    except Mesa.DoesNotExist:
        return JsonResponse({'error': 'Mesa não encontrada'}, status=404)

def modelo_info_api(request):
    model_info = {
        'fields': {
            'numero_mesa': {
                'type': 'CharField',
                'max_length': 10,
                'verbose_name': 'Número da Mesa'
            },
            'tipo_jogo': {
                'type': 'CharField',
                'choices': [
                    ('poker', 'Poker'),
                    ('blackjack', 'Blackjack'),
                    ('roleta', 'Roleta'),
                    ('baccarat', 'Baccarat'),
                    ('craps', 'Craps')
                ],
                'verbose_name': 'Tipo de Jogo'
            },
            'valor_total': {
                'type': 'DecimalField',
                'max_digits': 10,
                'decimal_places': 2,
                'verbose_name': 'Valor Total'
            },
            'status': {
                'type': 'CharField',
                'choices': [
                    ('aberta', 'Aberta'),
                    ('fechada', 'Fechada'),
                    ('encerrada', 'Encerrada')
                ],
                'verbose_name': 'Status'
            }
        }
    }
    return JsonResponse(model_info)

@csrf_exempt
def fechar_mesa_api(request, mesa_id):
    if request.method == 'POST':
        try:
            mesa = Mesa.objects.get(id=mesa_id)
            mesa.status = 'fechada'
            mesa.save()
            return JsonResponse({
                'success': True,
                'message': f'Mesa {mesa.numero_mesa} fechada com sucesso!'
            })
        except Mesa.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Mesa não encontrada'
            }, status=404)
    return JsonResponse({'success': False, 'message': 'Método não permitido'}, status=405)

@csrf_exempt
def abrir_mesa_api(request, mesa_id):
    if request.method == 'POST':
        try:
            mesa = Mesa.objects.get(id=mesa_id)
            mesa.status = 'aberta'
            mesa.save()
            return JsonResponse({
                'success': True,
                'message': f'Mesa {mesa.numero_mesa} aberta com sucesso!'
            })
        except Mesa.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Mesa não encontrada'
            }, status=404)
    return JsonResponse({'success': False, 'message': 'Método não permitido'}, status=405)

@csrf_exempt
def editar_mesa_api(request, mesa_id):
    if request.method == 'POST':
        try:
            mesa = Mesa.objects.get(id=mesa_id)
            data = json.loads(request.body)
            
            # Verificar se já existe outra mesa com o mesmo número que esteja aberta ou fechada
            numero_mesa = data.get('numero_mesa')
            mesa_existente = Mesa.objects.filter(
                numero_mesa=numero_mesa,
                status__in=['aberta', 'fechada']
            ).exclude(id=mesa_id).first()
            
            if mesa_existente:
                return JsonResponse({
                    'success': False,
                    'message': f'Já existe uma mesa {numero_mesa} com status "{mesa_existente.get_status_display()}". Encerre a mesa existente antes de usar este número.'
                }, status=400)
            
            # Atualizar os campos da mesa (exceto valor_inicial que não pode ser alterado)
            mesa.numero_mesa = numero_mesa
            mesa.tipo_jogo = data.get('tipo_jogo')
            mesa.status = data.get('status')
            mesa.fichas_5 = data.get('fichas_5', 0)
            mesa.fichas_25 = data.get('fichas_25', 0)
            mesa.fichas_100 = data.get('fichas_100', 0)
            mesa.fichas_500 = data.get('fichas_500', 0)
            mesa.fichas_1000 = data.get('fichas_1000', 0)
            mesa.fichas_5000 = data.get('fichas_5000', 0)
            mesa.fichas_10000 = data.get('fichas_10000', 0)
            
            mesa.save()  # Isso vai automaticamente recalcular o valor_total
            
            return JsonResponse({
                'success': True,
                'message': f'Mesa {mesa.numero_mesa} atualizada com sucesso!'
            })
        except Mesa.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Mesa não encontrada'
            }, status=404)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            }, status=400)
    return JsonResponse({'success': False, 'message': 'Método não permitido'}, status=405) 

@csrf_exempt
def encerrar_mesa_api(request, mesa_id):
    if request.method == 'POST':
        try:
            mesa = Mesa.objects.get(id=mesa_id)
            mesa.status = 'encerrada'
            mesa.save()
            return JsonResponse({
                'success': True,
                'message': f'Mesa {mesa.numero_mesa} encerrada com sucesso!'
            })
        except Mesa.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Mesa não encontrada'
            }, status=404)
    return JsonResponse({'success': False, 'message': 'Método não permitido'}, status=405) 
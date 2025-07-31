from django.shortcuts import render, redirect
from django.http import JsonResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.db import models
from django.utils import timezone
from datetime import datetime, timedelta
import json
from .models import Mesa
from sange.models import VendaFicha

def safe_int(value, default=0):
    """Converter valores para inteiros de forma segura"""
    try:
        if value is None or value == '' or value == 'None' or value == 'null' or value == 'undefined':
            return default
        # Se for string, remover espaços e tentar converter
        if isinstance(value, str):
            value = value.strip()
            if value == '':
                return default
        # Usar float primeiro para lidar com decimais, depois converter para int
        return int(float(value))
    except (ValueError, TypeError, AttributeError):
        return default

@login_required(login_url='/usuarios/login/')
def mesas_home(request):
    # Obter parâmetros de data do request
    data_inicio = request.GET.get('data_inicio')
    data_fim = request.GET.get('data_fim')
    
    # Obter parâmetros de status do request
    status_filtro = request.GET.get('status', '')
    
    # Converter datas apenas se foram fornecidas
    data_inicio_parsed = None
    data_fim_parsed = None
    
    if data_inicio and data_fim:
        try:
            data_inicio_parsed = datetime.strptime(data_inicio, '%Y-%m-%d').date()
            data_fim_parsed = datetime.strptime(data_fim, '%Y-%m-%d').date()
        except ValueError:
            # Se as datas não são válidas, ignorar o filtro de data
            data_inicio_parsed = None
            data_fim_parsed = None
    
    # Filtrar mesas por status se especificado
    if status_filtro and status_filtro in ['aberta', 'fechada', 'encerrada']:
        mesas = Mesa.objects.filter(status=status_filtro).order_by('numero_mesa')
    else:
        # Filtrar apenas mesas que não estão encerradas (comportamento padrão)
        mesas = Mesa.objects.exclude(status='encerrada').order_by('numero_mesa')
    
    # Calcular estatísticas gerais
    mesas_ativas = Mesa.objects.filter(status='aberta').count()  # Mesas abertas no momento
    total_mesas = Mesa.objects.exclude(status='encerrada').count()
    
    # Calcular receita total - soma do saldo das mesas no período filtrado ou com status filtrado
    if status_filtro and status_filtro in ['aberta', 'fechada', 'encerrada']:
        # Filtrar por status específico
        mesas_filtradas = Mesa.objects.filter(status=status_filtro)
    else:
        # Filtrar apenas mesas que não estão encerradas (comportamento padrão)
        mesas_filtradas = Mesa.objects.exclude(status='encerrada')
    
    # Se há filtro de data válido, aplicar também
    if data_inicio_parsed and data_fim_parsed:
        mesas_filtradas = mesas_filtradas.filter(
            data_criacao__date__gte=data_inicio_parsed,
            data_criacao__date__lte=data_fim_parsed
        )
    
    # Calcular receita total como soma dos saldos das mesas filtradas
    receita_total = mesas_filtradas.aggregate(
        total=models.Sum('saldo')
    )['total'] or 0
    
    # Calcular total de fichas vendidas do SANGE no período filtrado
    try:
        from sange.models import VendaFicha
        if data_inicio_parsed and data_fim_parsed:
            # Filtrar vendas por período
            fichas_vendidas_sange = VendaFicha.objects.filter(
                data__date__gte=data_inicio_parsed,
                data__date__lte=data_fim_parsed
            ).aggregate(
                total=models.Sum('valor_total')
            )['total'] or 0
        else:
            # Todas as vendas se não há filtro de data
            fichas_vendidas_sange = VendaFicha.objects.aggregate(
                total=models.Sum('valor_total')
            )['total'] or 0
    except:
        fichas_vendidas_sange = 0
    
    # Calcular total de fichas vendidas do FINANCEIRO no período filtrado
    try:
        from financeiro.models import VendaFicha as VendaFichaFinanceiro
        if data_inicio_parsed and data_fim_parsed:
            # Filtrar vendas por período
            fichas_vendidas_financeiro = VendaFichaFinanceiro.objects.filter(
                data_venda__date__gte=data_inicio_parsed,
                data_venda__date__lte=data_fim_parsed
            ).aggregate(
                total=models.Sum('quantidade')
            )['total'] or 0
        else:
            # Todas as vendas se não há filtro de data
            fichas_vendidas_financeiro = VendaFichaFinanceiro.objects.aggregate(
                total=models.Sum('quantidade')
            )['total'] or 0
    except:
        fichas_vendidas_financeiro = 0
    
    # Soma total das fichas vendidas (SANGE + FINANCEIRO)
    fichas_vendidas = fichas_vendidas_sange + fichas_vendidas_financeiro
    
    # Calcular variação percentual (simplificado - sempre 0 por enquanto)
    variacao_percentual = 0
    
    # Determinar se há filtros ativos
    filtro_ativo = bool((status_filtro and status_filtro in ['aberta', 'fechada', 'encerrada']) or (data_inicio_parsed and data_fim_parsed))
    
    # Gerar texto do período
    if data_inicio_parsed and data_fim_parsed:
        if status_filtro and status_filtro in ['aberta', 'fechada', 'encerrada']:
            periodo_texto = f"Período: {data_inicio_parsed.strftime('%d/%m/%Y')} a {data_fim_parsed.strftime('%d/%m/%Y')} - Status: {status_filtro.title()}"
        else:
            periodo_texto = f"Período: {data_inicio_parsed.strftime('%d/%m/%Y')} a {data_fim_parsed.strftime('%d/%m/%Y')}"
    elif status_filtro and status_filtro in ['aberta', 'fechada', 'encerrada']:
        periodo_texto = f"Filtro: {status_filtro.title()}"
    else:
        periodo_texto = "Todas as mesas ativas"
    
    # Contar mesas filtradas
    mesas_periodo_count = mesas_filtradas.count()
    
    # Garantir que todos os valores são números válidos
    receita_total = float(receita_total) if receita_total is not None else 0.0
    fichas_vendidas = float(fichas_vendidas) if fichas_vendidas is not None else 0.0
    variacao_percentual = float(variacao_percentual) if variacao_percentual is not None else 0.0
    mesas_ativas = int(mesas_ativas) if mesas_ativas is not None else 0
    total_mesas = int(total_mesas) if total_mesas is not None else 0
    

    
    context = {
        'mesas': mesas,
        'mesas_ativas': mesas_ativas,
        'total_mesas': total_mesas,
        'receita_total': receita_total,
        'fichas_vendidas': fichas_vendidas,
        'variacao_percentual': variacao_percentual,
        'data_inicio': data_inicio,
        'data_fim': data_fim,
        'status_filtro': status_filtro,
        'filtro_ativo': filtro_ativo,
        'periodo_texto': periodo_texto,
        'mesas_periodo_count': mesas_periodo_count,
    }
    
    return render(request, 'home.html', context)

@login_required(login_url='/usuarios/login/')
def todas_mesas(request):
    """View para mostrar todas as mesas em formato de lista"""
    return render(request, 'mesas/todas_mesas.html')

@csrf_exempt
def criar_mesa(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            print(f"DEBUG - Dados recebidos: {data}")  # Debug log
            
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
            
            # Debug logs para fichas
            print(f"DEBUG - Fichas 5: {data.get('fichas_5', 0)}")
            print(f"DEBUG - Fichas 25: {data.get('fichas_25', 0)}")
            print(f"DEBUG - Fichas 100: {data.get('fichas_100', 0)}")
            print(f"DEBUG - Fichas 500: {data.get('fichas_500', 0)}")
            print(f"DEBUG - Fichas 1000: {data.get('fichas_1000', 0)}")
            print(f"DEBUG - Fichas 5000: {data.get('fichas_5000', 0)}")
            print(f"DEBUG - Fichas 10000: {data.get('fichas_10000', 0)}")
            
            mesa = Mesa.objects.create(
                numero_mesa=numero_mesa,
                tipo_jogo=data.get('tipo_jogo'),
                status=data.get('status', 'aberta'),
                fichas_5=safe_int(data.get('fichas_5'), 0),
                fichas_25=safe_int(data.get('fichas_25'), 0),
                fichas_100=safe_int(data.get('fichas_100'), 0),
                fichas_500=safe_int(data.get('fichas_500'), 0),
                fichas_1000=safe_int(data.get('fichas_1000'), 0),
                fichas_5000=safe_int(data.get('fichas_5000'), 0),
                fichas_10000=safe_int(data.get('fichas_10000'), 0)
            )
            
            print(f"DEBUG - Mesa criada com ID: {mesa.id}")
            print(f"DEBUG - Fichas salvas - 5: {mesa.fichas_5}, 25: {mesa.fichas_25}, 100: {mesa.fichas_100}")
            
            return JsonResponse({
                'success': True,
                'message': f'Mesa {mesa.numero_mesa} criada com sucesso!',
                'mesa_criada': {
                    'id': mesa.id,
                    'numero_mesa': mesa.numero_mesa,
                    'tipo_jogo': mesa.tipo_jogo,
                    'tipo_jogo_display': mesa.get_tipo_jogo_display(),
                    'status': mesa.status,
                    'status_display': mesa.get_status_display(),
                    'valor_inicial': float(mesa.valor_inicial),
                    'valor_total': float(mesa.valor_total),
                    'saldo': float(mesa.saldo),
                    'fichas_5': mesa.fichas_5,
                    'fichas_25': mesa.fichas_25,
                    'fichas_100': mesa.fichas_100,
                    'fichas_500': mesa.fichas_500,
                    'fichas_1000': mesa.fichas_1000,
                    'fichas_5000': mesa.fichas_5000,
                    'fichas_10000': mesa.fichas_10000,
                    'data_criacao': mesa.data_criacao.strftime('%d/%m/%Y %H:%M'),
                    'data_atualizacao': mesa.data_atualizacao.strftime('%d/%m/%Y %H:%M'),
                }
            })
        except Exception as e:
            print(f"DEBUG - Erro: {str(e)}")  # Debug log
            import traceback
            print(f"DEBUG - Traceback: {traceback.format_exc()}")
            return JsonResponse({
                'success': False,
                'message': f'Erro interno: {str(e)}'
            }, status=400)
    return JsonResponse({'success': False, 'message': 'Método não permitido'}, status=405)

@csrf_exempt
def criar_mesa_api(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            print(f"DEBUG - Dados recebidos: {data}")  # Debug log
            
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
            
            # Debug logs para fichas
            print(f"DEBUG - Fichas 5: {data.get('fichas_5', 0)}")
            print(f"DEBUG - Fichas 25: {data.get('fichas_25', 0)}")
            print(f"DEBUG - Fichas 100: {data.get('fichas_100', 0)}")
            print(f"DEBUG - Fichas 500: {data.get('fichas_500', 0)}")
            print(f"DEBUG - Fichas 1000: {data.get('fichas_1000', 0)}")
            print(f"DEBUG - Fichas 5000: {data.get('fichas_5000', 0)}")
            print(f"DEBUG - Fichas 10000: {data.get('fichas_10000', 0)}")
            
            mesa = Mesa.objects.create(
                numero_mesa=numero_mesa,
                tipo_jogo=data.get('tipo_jogo'),
                status=data.get('status', 'aberta'),
                fichas_5=safe_int(data.get('fichas_5'), 0),
                fichas_25=safe_int(data.get('fichas_25'), 0),
                fichas_100=safe_int(data.get('fichas_100'), 0),
                fichas_500=safe_int(data.get('fichas_500'), 0),
                fichas_1000=safe_int(data.get('fichas_1000'), 0),
                fichas_5000=safe_int(data.get('fichas_5000'), 0),
                fichas_10000=safe_int(data.get('fichas_10000'), 0)
            )
            
            print(f"DEBUG - Mesa criada com ID: {mesa.id}")
            print(f"DEBUG - Fichas salvas - 5: {mesa.fichas_5}, 25: {mesa.fichas_25}, 100: {mesa.fichas_100}")
            print(f"DEBUG - Valor total: {mesa.valor_total}, Valor inicial: {mesa.valor_inicial}, Saldo: {mesa.saldo}")
            
            return JsonResponse({
                'success': True,
                'message': f'Mesa {mesa.numero_mesa} criada com sucesso!',
                'mesa_criada': {
                    'id': mesa.id,
                    'numero_mesa': mesa.numero_mesa,
                    'tipo_jogo': mesa.tipo_jogo,
                    'tipo_jogo_display': mesa.get_tipo_jogo_display(),
                    'status': mesa.status,
                    'status_display': mesa.get_status_display(),
                    'valor_inicial': float(mesa.valor_inicial),
                    'valor_total': float(mesa.valor_total),
                    'saldo': float(mesa.saldo),
                    'fichas_5': mesa.fichas_5,
                    'fichas_25': mesa.fichas_25,
                    'fichas_100': mesa.fichas_100,
                    'fichas_500': mesa.fichas_500,
                    'fichas_1000': mesa.fichas_1000,
                    'fichas_5000': mesa.fichas_5000,
                    'fichas_10000': mesa.fichas_10000,
                    'data_criacao': mesa.data_criacao.strftime('%d/%m/%Y %H:%M'),
                    'data_atualizacao': mesa.data_atualizacao.strftime('%d/%m/%Y %H:%M'),
                }
            })
        except Exception as e:
            print(f"DEBUG - Erro: {str(e)}")  # Debug log
            import traceback
            print(f"DEBUG - Traceback: {traceback.format_exc()}")
            return JsonResponse({
                'success': False,
                'message': f'Erro interno: {str(e)}'
            }, status=400)
    return JsonResponse({'success': False, 'message': 'Método não permitido'}, status=405)

@login_required(login_url='/usuarios/login/')
def listar_mesas_api(request):
    mesas = Mesa.objects.all()
    data = []
    for mesa in mesas:
        data.append({
            'id': mesa.id,
            'numero_mesa': mesa.numero_mesa,
            'tipo_jogo': mesa.tipo_jogo,
            'tipo_jogo_display': mesa.get_tipo_jogo_display(),
            'valor_total': float(mesa.valor_total),
            'saldo': float(mesa.saldo),
            'status': mesa.status,
            'status_display': mesa.get_status_display(),
        })
    return JsonResponse({'mesas': data})

@csrf_exempt
@login_required(login_url='/usuarios/login/')
def obter_mesa_api(request, mesa_id):
    print(f"DEBUG - obter_mesa_api chamada para mesa_id: {mesa_id}")
    print(f"DEBUG - Usuário autenticado: {request.user.is_authenticated}")
    print(f"DEBUG - Método da requisição: {request.method}")
    print(f"DEBUG - Path da requisição: {request.path}")
    print(f"DEBUG - Headers da requisição: {dict(request.headers)}")
    
    try:
        mesa = Mesa.objects.get(id=mesa_id)
        print(f"DEBUG - Mesa encontrada: {mesa.numero_mesa}")
        data = {
            'success': True,
            'mesa': {
                'id': mesa.id,
                'numero_mesa': mesa.numero_mesa,
                'tipo_jogo': mesa.tipo_jogo,
                'tipo_jogo_display': mesa.get_tipo_jogo_display(),
                'valor_inicial': float(mesa.valor_inicial),
                'valor_total': float(mesa.valor_total),
                'saldo': float(mesa.saldo),
                'status': mesa.status,
                'status_display': mesa.get_status_display(),
                'fichas_5': mesa.fichas_5 or 0,
                'fichas_25': mesa.fichas_25 or 0,
                'fichas_100': mesa.fichas_100 or 0,
                'fichas_500': mesa.fichas_500 or 0,
                'fichas_1000': mesa.fichas_1000 or 0,
                'fichas_5000': mesa.fichas_5000 or 0,
                'fichas_10000': mesa.fichas_10000 or 0,
                'data_criacao': mesa.data_criacao.strftime('%d/%m/%Y %H:%M'),
                'data_atualizacao': mesa.data_atualizacao.strftime('%d/%m/%Y %H:%M'),
            }
        }
        print(f"DEBUG - Retornando dados da mesa: {data}")
        return JsonResponse(data)
    except Mesa.DoesNotExist:
        print(f"DEBUG - Mesa {mesa_id} não encontrada")
        return JsonResponse({'success': False, 'message': 'Mesa não encontrada'}, status=404)
    except Exception as e:
        print(f"DEBUG - Erro inesperado na obter_mesa_api: {str(e)}")
        return JsonResponse({'success': False, 'message': f'Erro interno: {str(e)}'}, status=500)

@login_required(login_url='/usuarios/login/')
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
    print(f"DEBUG - fechar_mesa_api chamada para mesa_id: {mesa_id}")
    print(f"DEBUG - Método da requisição: {request.method}")
    
    if request.method == 'POST':
        try:
            mesa = Mesa.objects.get(id=mesa_id)
            print(f"DEBUG - Mesa encontrada: {mesa.numero_mesa} (status atual: {mesa.status})")
            
            mesa.status = 'fechada'
            mesa.save()
            print(f"DEBUG - Mesa {mesa.numero_mesa} fechada com sucesso")
            
            mesa_atualizada = {
                'id': mesa.id,
                'numero_mesa': mesa.numero_mesa,
                'tipo_jogo': mesa.tipo_jogo,
                'tipo_jogo_display': mesa.get_tipo_jogo_display(),
                'status': mesa.status,
                'status_display': mesa.get_status_display(),
                'valor_inicial': float(mesa.valor_inicial),
                'valor_total': float(mesa.valor_total),
                'saldo': float(mesa.saldo),
                'fichas_5': mesa.fichas_5,
                'fichas_25': mesa.fichas_25,
                'fichas_100': mesa.fichas_100,
                'fichas_500': mesa.fichas_500,
                'fichas_1000': mesa.fichas_1000,
                'fichas_5000': mesa.fichas_5000,
                'fichas_10000': mesa.fichas_10000,
                'data_criacao': mesa.data_criacao.strftime('%d/%m/%Y %H:%M'),
                'data_atualizacao': mesa.data_atualizacao.strftime('%d/%m/%Y %H:%M'),
            }
            print(f"DEBUG - Dados da mesa atualizada: {mesa_atualizada}")
            
            return JsonResponse({
                'success': True,
                'message': f'Mesa {mesa.numero_mesa} fechada com sucesso!',
                'mesa_atualizada': mesa_atualizada
            })
        except Mesa.DoesNotExist:
            print(f"DEBUG - Mesa {mesa_id} não encontrada")
            return JsonResponse({
                'success': False,
                'message': 'Mesa não encontrada'
            }, status=404)
        except Exception as e:
            print(f"DEBUG - Erro inesperado: {str(e)}")
            return JsonResponse({
                'success': False,
                'message': f'Erro interno: {str(e)}'
            }, status=500)
    
    print(f"DEBUG - Método {request.method} não permitido")
    return JsonResponse({'success': False, 'message': 'Método não permitido'}, status=405)

@csrf_exempt
def abrir_mesa_api(request, mesa_id):
    print(f"DEBUG - abrir_mesa_api chamada para mesa_id: {mesa_id}")
    print(f"DEBUG - Método da requisição: {request.method}")
    
    if request.method == 'POST':
        try:
            mesa = Mesa.objects.get(id=mesa_id)
            print(f"DEBUG - Mesa encontrada: {mesa.numero_mesa} (status atual: {mesa.status})")
            
            mesa.status = 'aberta'
            mesa.save()
            print(f"DEBUG - Mesa {mesa.numero_mesa} aberta com sucesso")
            
            mesa_atualizada = {
                'id': mesa.id,
                'numero_mesa': mesa.numero_mesa,
                'tipo_jogo': mesa.tipo_jogo,
                'tipo_jogo_display': mesa.get_tipo_jogo_display(),
                'status': mesa.status,
                'status_display': mesa.get_status_display(),
                'valor_inicial': float(mesa.valor_inicial),
                'valor_total': float(mesa.valor_total),
                'saldo': float(mesa.saldo),
                'fichas_5': mesa.fichas_5,
                'fichas_25': mesa.fichas_25,
                'fichas_100': mesa.fichas_100,
                'fichas_500': mesa.fichas_500,
                'fichas_1000': mesa.fichas_1000,
                'fichas_5000': mesa.fichas_5000,
                'fichas_10000': mesa.fichas_10000,
                'data_criacao': mesa.data_criacao.strftime('%d/%m/%Y %H:%M'),
                'data_atualizacao': mesa.data_atualizacao.strftime('%d/%m/%Y %H:%M'),
            }
            print(f"DEBUG - Dados da mesa atualizada: {mesa_atualizada}")
            
            return JsonResponse({
                'success': True,
                'message': f'Mesa {mesa.numero_mesa} aberta com sucesso!',
                'mesa_atualizada': mesa_atualizada
            })
        except Mesa.DoesNotExist:
            print(f"DEBUG - Mesa {mesa_id} não encontrada")
            return JsonResponse({
                'success': False,
                'message': 'Mesa não encontrada'
            }, status=404)
        except Exception as e:
            print(f"DEBUG - Erro inesperado: {str(e)}")
            return JsonResponse({
                'success': False,
                'message': f'Erro interno: {str(e)}'
            }, status=500)
    
    print(f"DEBUG - Método {request.method} não permitido")
    return JsonResponse({'success': False, 'message': 'Método não permitido'}, status=405)

@csrf_exempt
def editar_mesa_api(request, mesa_id):
    if request.method == 'POST':
        try:
            mesa = Mesa.objects.get(id=mesa_id)
            data = json.loads(request.body)
            print(f"DEBUG EDITAR - Dados recebidos: {data}")  # Debug log
            
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
            
            # Debug logs para fichas
            print(f"DEBUG EDITAR - Fichas 5: {data.get('fichas_5', 0)}")
            print(f"DEBUG EDITAR - Fichas 25: {data.get('fichas_25', 0)}")
            print(f"DEBUG EDITAR - Fichas 100: {data.get('fichas_100', 0)}")
            print(f"DEBUG EDITAR - Fichas 500: {data.get('fichas_500', 0)}")
            print(f"DEBUG EDITAR - Fichas 1000: {data.get('fichas_1000', 0)}")
            print(f"DEBUG EDITAR - Fichas 5000: {data.get('fichas_5000', 0)}")
            print(f"DEBUG EDITAR - Fichas 10000: {data.get('fichas_10000', 0)}")
            
            # Atualizar os campos da mesa (exceto valor_inicial que não pode ser alterado)
            mesa.numero_mesa = numero_mesa
            mesa.tipo_jogo = data.get('tipo_jogo')
            mesa.status = data.get('status')
            
            # Debug: verificar valores antes da conversão
            print(f"DEBUG EDITAR - Valores brutos recebidos:")
            print(f"fichas_5 raw: '{data.get('fichas_5')}' (type: {type(data.get('fichas_5'))})")
            print(f"fichas_25 raw: '{data.get('fichas_25')}' (type: {type(data.get('fichas_25'))})")
            print(f"fichas_100 raw: '{data.get('fichas_100')}' (type: {type(data.get('fichas_100'))})")
            
            # Converter e atribuir valores das fichas
            mesa.fichas_5 = safe_int(data.get('fichas_5'), 0)
            mesa.fichas_25 = safe_int(data.get('fichas_25'), 0)
            mesa.fichas_100 = safe_int(data.get('fichas_100'), 0)
            mesa.fichas_500 = safe_int(data.get('fichas_500'), 0)
            mesa.fichas_1000 = safe_int(data.get('fichas_1000'), 0)
            mesa.fichas_5000 = safe_int(data.get('fichas_5000'), 0)
            mesa.fichas_10000 = safe_int(data.get('fichas_10000'), 0)
            
            print(f"DEBUG EDITAR - Valores convertidos:")
            print(f"fichas_5: {mesa.fichas_5}")
            print(f"fichas_25: {mesa.fichas_25}")
            print(f"fichas_100: {mesa.fichas_100}")
            print(f"fichas_500: {mesa.fichas_500}")
            print(f"fichas_1000: {mesa.fichas_1000}")
            print(f"fichas_5000: {mesa.fichas_5000}")
            print(f"fichas_10000: {mesa.fichas_10000}")
            
            # Salvar a mesa
            mesa.save()  # Isso vai automaticamente recalcular o valor_total
            
            # Recarregar a mesa do banco para verificar se os valores foram salvos
            mesa.refresh_from_db()
            
            print(f"DEBUG EDITAR - Mesa atualizada - Fichas salvas - 5: {mesa.fichas_5}, 25: {mesa.fichas_25}, 100: {mesa.fichas_100}")
            print(f"DEBUG EDITAR - Valores após save e refresh:")
            print(f"fichas_5: {mesa.fichas_5}")
            print(f"fichas_25: {mesa.fichas_25}")
            print(f"fichas_100: {mesa.fichas_100}")
            print(f"fichas_500: {mesa.fichas_500}")
            print(f"fichas_1000: {mesa.fichas_1000}")
            print(f"fichas_5000: {mesa.fichas_5000}")
            print(f"fichas_10000: {mesa.fichas_10000}")
            print(f"valor_total: {mesa.valor_total}")
            print(f"saldo: {mesa.saldo}")
            
            # Retornar dados atualizados para o frontend
            return JsonResponse({
                'success': True,
                'message': f'Mesa {mesa.numero_mesa} atualizada com sucesso!',
                'mesa_atualizada': {
                    'id': mesa.id,
                    'numero_mesa': mesa.numero_mesa,
                    'tipo_jogo': mesa.tipo_jogo,
                    'tipo_jogo_display': mesa.get_tipo_jogo_display(),
                    'status': mesa.status,
                    'status_display': mesa.get_status_display(),
                    'valor_inicial': float(mesa.valor_inicial),
                    'valor_total': float(mesa.valor_total),
                    'saldo': float(mesa.saldo),
                    'fichas_5': mesa.fichas_5,
                    'fichas_25': mesa.fichas_25,
                    'fichas_100': mesa.fichas_100,
                    'fichas_500': mesa.fichas_500,
                    'fichas_1000': mesa.fichas_1000,
                    'fichas_5000': mesa.fichas_5000,
                    'fichas_10000': mesa.fichas_10000,
                    'data_criacao': mesa.data_criacao.strftime('%d/%m/%Y %H:%M'),
                    'data_atualizacao': mesa.data_atualizacao.strftime('%d/%m/%Y %H:%M'),
                }
            })
        except Mesa.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Mesa não encontrada'
            }, status=404)
        except Exception as e:
            print(f"DEBUG EDITAR - Erro: {str(e)}")  # Debug log
            return JsonResponse({
                'success': False,
                'message': str(e)
            }, status=400)
    return JsonResponse({'success': False, 'message': 'Método não permitido'}, status=405)

@csrf_exempt
def encerrar_mesa_api(request, mesa_id):
    print(f"DEBUG - encerrar_mesa_api chamada para mesa_id: {mesa_id}")
    print(f"DEBUG - Método da requisição: {request.method}")
    
    if request.method == 'POST':
        try:
            mesa = Mesa.objects.get(id=mesa_id)
            print(f"DEBUG - Mesa encontrada: {mesa.numero_mesa} (status atual: {mesa.status})")
            
            mesa.status = 'encerrada'
            mesa.save()
            print(f"DEBUG - Mesa {mesa.numero_mesa} encerrada com sucesso")
            
            return JsonResponse({
                'success': True,
                'message': f'Mesa {mesa.numero_mesa} encerrada com sucesso!'
            })
        except Mesa.DoesNotExist:
            print(f"DEBUG - Mesa {mesa_id} não encontrada")
            return JsonResponse({
                'success': False,
                'message': 'Mesa não encontrada'
            }, status=404)
        except Exception as e:
            print(f"DEBUG - Erro inesperado: {str(e)}")
            return JsonResponse({
                'success': False,
                'message': str(e)
            }, status=400)
    
    print(f"DEBUG - Método {request.method} não permitido")
    return JsonResponse({'success': False, 'message': 'Método não permitido'}, status=405)

@csrf_exempt
def testar_mesa_api(request, mesa_id):
    """Endpoint de teste para verificar os dados de uma mesa"""
    if request.method == 'GET':
        try:
            mesa = Mesa.objects.get(id=mesa_id)
            
            # Calcular valores manualmente para comparação
            valor_total_calculado = mesa.calcular_valor_total()
            saldo_calculado = valor_total_calculado - float(mesa.valor_inicial)
            
            return JsonResponse({
                'success': True,
                'mesa': {
                    'id': mesa.id,
                    'numero_mesa': mesa.numero_mesa,
                    'tipo_jogo': mesa.tipo_jogo,
                    'status': mesa.status,
                    'valor_inicial': float(mesa.valor_inicial),
                    'valor_total_salvo': float(mesa.valor_total),
                    'valor_total_calculado': valor_total_calculado,
                    'saldo_salvo': float(mesa.saldo),
                    'saldo_calculado': saldo_calculado,
                    'fichas_5': mesa.fichas_5,
                    'fichas_25': mesa.fichas_25,
                    'fichas_100': mesa.fichas_100,
                    'fichas_500': mesa.fichas_500,
                    'fichas_1000': mesa.fichas_1000,
                    'fichas_5000': mesa.fichas_5000,
                    'fichas_10000': mesa.fichas_10000,
                    'data_criacao': mesa.data_criacao.isoformat(),
                    'data_atualizacao': mesa.data_atualizacao.isoformat(),
                }
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
def mesa_detail_api(request, mesa_id):
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'message': 'Não autorizado'}, status=403)
    try:
        mesa = Mesa.objects.get(id=mesa_id)
    except Mesa.DoesNotExist:
        raise Http404

    data = {
        'id': mesa.id,
        'numero_mesa': mesa.numero_mesa,
        'tipo_jogo': mesa.tipo_jogo,
        'tipo_jogo_display': mesa.get_tipo_jogo_display(),
        'status': mesa.status,
        'status_display': mesa.get_status_display(),
        'valor_inicial': float(mesa.valor_inicial),
        'valor_total': float(mesa.valor_total),
        'saldo': float(mesa.saldo),
        'fichas_5': mesa.fichas_5 or 0,
        'fichas_25': mesa.fichas_25 or 0,
        'fichas_100': mesa.fichas_100 or 0,
        'fichas_500': mesa.fichas_500 or 0,
        'fichas_1000': mesa.fichas_1000 or 0,
        'fichas_5000': mesa.fichas_5000 or 0,
        'fichas_10000': mesa.fichas_10000 or 0,
        'data_criacao': mesa.data_criacao.strftime('%d/%m/%Y %H:%M'),
        'data_atualizacao': mesa.data_atualizacao.strftime('%d/%m/%Y %H:%M'),
    }
    return JsonResponse({'success': True, 'mesa': data})

@csrf_exempt
def atualizar_metricas_api(request):
    """API para atualizar métricas e saldos dinamicamente"""
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'message': 'Não autorizado'}, status=403)
    
    try:
        # Obter parâmetros de filtro do request
        data_inicio = request.GET.get('data_inicio')
        data_fim = request.GET.get('data_fim')
        status_filtro = request.GET.get('status', '')
        
        # Converter datas apenas se foram fornecidas
        data_inicio_parsed = None
        data_fim_parsed = None
        
        if data_inicio and data_fim:
            try:
                data_inicio_parsed = datetime.strptime(data_inicio, '%Y-%m-%d').date()
                data_fim_parsed = datetime.strptime(data_fim, '%Y-%m-%d').date()
            except ValueError:
                # Se as datas não são válidas, ignorar o filtro de data
                data_inicio_parsed = None
                data_fim_parsed = None
        
        # Calcular métricas atualizadas
        mesas_ativas = Mesa.objects.filter(status='aberta').count()  # Mesas abertas no momento
        total_mesas = Mesa.objects.exclude(status='encerrada').count()
        
        # Calcular receita total - soma do saldo das mesas no período filtrado ou com status filtrado
        if status_filtro and status_filtro in ['aberta', 'fechada', 'encerrada']:
            # Filtrar por status específico
            mesas_filtradas = Mesa.objects.filter(status=status_filtro)
        else:
            # Filtrar apenas mesas que não estão encerradas (comportamento padrão)
            mesas_filtradas = Mesa.objects.exclude(status='encerrada')
        
        # Se há filtro de data válido, aplicar também
        if data_inicio_parsed and data_fim_parsed:
            mesas_filtradas = mesas_filtradas.filter(
                data_criacao__date__gte=data_inicio_parsed,
                data_criacao__date__lte=data_fim_parsed
            )
        
        # Calcular receita total como soma dos saldos das mesas filtradas
        receita_total = mesas_filtradas.aggregate(
            total=models.Sum('saldo')
        )['total'] or 0
        

        
        # Calcular total de fichas vendidas do SANGE no período filtrado
        try:
            from sange.models import VendaFicha
            if data_inicio_parsed and data_fim_parsed:
                # Filtrar vendas por período
                fichas_vendidas_sange = VendaFicha.objects.filter(
                    data__date__gte=data_inicio_parsed,
                    data__date__lte=data_fim_parsed
                ).aggregate(
                    total=models.Sum('valor_total')
                )['total'] or 0
            else:
                # Todas as vendas se não há filtro de data
                fichas_vendidas_sange = VendaFicha.objects.aggregate(
                    total=models.Sum('valor_total')
                )['total'] or 0
        except:
            fichas_vendidas_sange = 0
        
        # Calcular total de fichas vendidas do FINANCEIRO no período filtrado
        try:
            from financeiro.models import VendaFicha as VendaFichaFinanceiro
            if data_inicio_parsed and data_fim_parsed:
                # Filtrar vendas por período
                fichas_vendidas_financeiro = VendaFichaFinanceiro.objects.filter(
                    data_venda__date__gte=data_inicio_parsed,
                    data_venda__date__lte=data_fim_parsed
                ).aggregate(
                    total=models.Sum('quantidade')
                )['total'] or 0
            else:
                # Todas as vendas se não há filtro de data
                fichas_vendidas_financeiro = VendaFichaFinanceiro.objects.aggregate(
                    total=models.Sum('quantidade')
                )['total'] or 0
        except:
            fichas_vendidas_financeiro = 0
        
        # Soma total das fichas vendidas (SANGE + FINANCEIRO)
        fichas_vendidas = fichas_vendidas_sange + fichas_vendidas_financeiro
        
        # Calcular variação percentual (simplificado - sempre 0 por enquanto)
        variacao_percentual = 0
        
        # Obter todas as mesas com saldos atualizados
        if status_filtro and status_filtro in ['aberta', 'fechada', 'encerrada']:
            mesas = Mesa.objects.filter(status=status_filtro).order_by('numero_mesa')
        else:
            mesas = Mesa.objects.exclude(status='encerrada').order_by('numero_mesa')
        
        # Preparar dados das mesas
        mesas_data = []
        for mesa in mesas:
            mesas_data.append({
                'id': mesa.id,
                'numero_mesa': mesa.numero_mesa,
                'tipo_jogo': mesa.tipo_jogo,
                'tipo_jogo_display': mesa.get_tipo_jogo_display(),
                'status': mesa.status,
                'status_display': mesa.get_status_display(),
                'valor_inicial': float(mesa.valor_inicial),
                'valor_total': float(mesa.valor_total),
                'saldo': float(mesa.saldo),
                'fichas_5': mesa.fichas_5 or 0,
                'fichas_25': mesa.fichas_25 or 0,
                'fichas_100': mesa.fichas_100 or 0,
                'fichas_500': mesa.fichas_500 or 0,
                'fichas_1000': mesa.fichas_1000 or 0,
                'fichas_5000': mesa.fichas_5000 or 0,
                'fichas_10000': mesa.fichas_10000 or 0,
            })
        
        # Garantir que todos os valores são números válidos
        receita_total = float(receita_total) if receita_total is not None else 0.0
        fichas_vendidas = float(fichas_vendidas) if fichas_vendidas is not None else 0.0
        variacao_percentual = float(variacao_percentual) if variacao_percentual is not None else 0.0
        mesas_ativas = int(mesas_ativas) if mesas_ativas is not None else 0
        total_mesas = int(total_mesas) if total_mesas is not None else 0
        
        return JsonResponse({
            'success': True,
            'metricas': {
                'receita_total': receita_total,
                'mesas_ativas': mesas_ativas,
                'total_mesas': total_mesas,
                'fichas_vendidas': fichas_vendidas,
                'variacao_percentual': variacao_percentual
            },
            'mesas': mesas_data
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Erro ao atualizar métricas: {str(e)}'}, status=500) 
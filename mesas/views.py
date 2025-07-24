from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from .models import Mesa

def mesas_home(request):
    mesas = Mesa.objects.all().order_by('numero_mesa')
    return render(request, 'home.html', {'mesas': mesas})

@csrf_exempt
def criar_mesa(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            mesa = Mesa.objects.create(
                numero_mesa=data.get('numero_mesa'),
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
            
            # Atualizar os campos da mesa
            mesa.numero_mesa = data.get('numero_mesa')
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
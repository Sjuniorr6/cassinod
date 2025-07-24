from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
import json
from .models import Mesa

@login_required
def mesas_home(request):
    mesas = Mesa.objects.all().order_by('numero_mesa')
    return render(request, 'mesas/home.html', {'mesas': mesas})

@login_required
@csrf_exempt
@require_http_methods(["POST"])
def criar_mesa(request):
    try:
        data = json.loads(request.body)
        
        # Criar nova mesa
        mesa = Mesa.objects.create(
            tipo_jogo=data['tipo_jogo'],
            numero_mesa=data['numero_mesa'],
            fichas_5=data.get('fichas_5', 0),
            fichas_25=data.get('fichas_25', 0),
            fichas_100=data.get('fichas_100', 0),
            fichas_500=data.get('fichas_500', 0),
            fichas_1000=data.get('fichas_1000', 0),
            fichas_5000=data.get('fichas_5000', 0),
            fichas_10000=data.get('fichas_10000', 0),
        )
        
        return JsonResponse({
            'success': True,
            'message': f'Mesa {mesa.numero_mesa} criada com sucesso!',
            'mesa': {
                'id': mesa.id,
                'numero_mesa': mesa.numero_mesa,
                'tipo_jogo': mesa.get_tipo_jogo_display(),
                'valor_total': float(mesa.valor_total)
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erro ao criar mesa: {str(e)}'
        }, status=400) 
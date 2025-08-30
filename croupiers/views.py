from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from .models import Croupier

# Create your views here.

@login_required(login_url='/usuarios/login/')
def listar_croupiers(request):
    """View para listar todos os croupiers"""
    try:
        croupiers = Croupier.objects.all().order_by('nome')
        context = {
            'croupiers': croupiers,
            'total_croupiers': croupiers.count(),
            'croupiers_ativos': croupiers.filter(ativo=True).count(),
            'croupiers_inativos': croupiers.filter(ativo=False).count(),
        }
        return render(request, 'croupiers/listar_croupiers.html', context)
    except Exception as e:
        context = {
            'error': f'Erro ao carregar croupiers: {str(e)}',
            'croupiers': [],
            'total_croupiers': 0,
            'croupiers_ativos': 0,
            'croupiers_inativos': 0,
        }
        return render(request, 'croupiers/listar_croupiers.html', context)

@login_required(login_url='/usuarios/login/')
def listar_croupiers_api(request):
    """API para listar croupiers ativos"""
    try:
        croupiers = Croupier.objects.filter(ativo=True).order_by('nome')
        croupiers_data = []
        
        for croupier in croupiers:
            croupiers_data.append({
                'id': croupier.id,
                'nome': croupier.nome,
                'ativo': croupier.ativo,
                'data_criacao': croupier.data_criacao.strftime('%d/%m/%Y %H:%M'),
                'data_atualizacao': croupier.data_atualizacao.strftime('%d/%m/%Y %H:%M'),
            })
        
        return JsonResponse({
            'success': True,
            'croupiers': croupiers_data
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@login_required(login_url='/usuarios/login/')
@csrf_exempt
@require_http_methods(["POST"])
def criar_croupier_api(request):
    """API para criar um novo croupier"""
    try:
        data = json.loads(request.body)
        nome = data.get('nome')
        ativo = data.get('ativo', True)
        
        if not nome:
            return JsonResponse({
                'success': False,
                'error': 'Nome é obrigatório'
            }, status=400)
        
        # Verificar se já existe um croupier com este nome
        if Croupier.objects.filter(nome=nome).exists():
            return JsonResponse({
                'success': False,
                'error': 'Já existe um croupier com este nome'
            }, status=400)
        
        croupier = Croupier.objects.create(
            nome=nome,
            ativo=ativo
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Croupier criado com sucesso',
            'croupier': {
                'id': croupier.id,
                'nome': croupier.nome,
                'ativo': croupier.ativo,
                'data_criacao': croupier.data_criacao.strftime('%d/%m/%Y %H:%M'),
                'data_atualizacao': croupier.data_atualizacao.strftime('%d/%m/%Y %H:%M'),
            }
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Dados JSON inválidos'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@login_required(login_url='/usuarios/login/')
def obter_croupier_api(request, croupier_id):
    """API para obter dados de um croupier específico"""
    try:
        croupier = Croupier.objects.get(id=croupier_id)
        
        return JsonResponse({
            'success': True,
            'croupier': {
                'id': croupier.id,
                'nome': croupier.nome,
                'ativo': croupier.ativo,
                'data_criacao': croupier.data_criacao.strftime('%d/%m/%Y %H:%M'),
                'data_atualizacao': croupier.data_atualizacao.strftime('%d/%m/%Y %H:%M'),
            }
        })
        
    except Croupier.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Croupier não encontrado'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@login_required(login_url='/usuarios/login/')
@csrf_exempt
@require_http_methods(["PUT"])
def editar_croupier_api(request, croupier_id):
    """API para editar um croupier"""
    try:
        croupier = Croupier.objects.get(id=croupier_id)
        data = json.loads(request.body)
        
        nome = data.get('nome')
        ativo = data.get('ativo', True)
        
        if not nome:
            return JsonResponse({
                'success': False,
                'error': 'Nome é obrigatório'
            }, status=400)
        
        # Verificar se já existe outro croupier com este nome
        if Croupier.objects.filter(nome=nome).exclude(id=croupier_id).exists():
            return JsonResponse({
                'success': False,
                'error': 'Já existe outro croupier com este nome'
            }, status=400)
        
        croupier.nome = nome
        croupier.ativo = ativo
        croupier.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Croupier atualizado com sucesso',
            'croupier': {
                'id': croupier.id,
                'nome': croupier.nome,
                'ativo': croupier.ativo,
                'data_criacao': croupier.data_criacao.strftime('%d/%m/%Y %H:%M'),
                'data_atualizacao': croupier.data_atualizacao.strftime('%d/%m/%Y %H:%M'),
            }
        })
        
    except Croupier.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Croupier não encontrado'
        }, status=404)
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Dados JSON inválidos'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@login_required(login_url='/usuarios/login/')
@csrf_exempt
@require_http_methods(["DELETE"])
def excluir_croupier_api(request, croupier_id):
    """API para excluir um croupier"""
    try:
        croupier = Croupier.objects.get(id=croupier_id)
        
        # Verificar se o croupier está sendo usado em alguma mesa
        from mesas.models import Mesa
        mesas_using_croupier = Mesa.objects.filter(croupier=croupier)
        
        if mesas_using_croupier.exists():
            return JsonResponse({
                'success': False,
                'error': 'Não é possível excluir este croupier pois está sendo usado em mesas ativas'
            }, status=400)
        
        croupier.delete()
        
        return JsonResponse({
            'success': True,
            'message': 'Croupier excluído com sucesso'
        })
        
    except Croupier.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Croupier não encontrado'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

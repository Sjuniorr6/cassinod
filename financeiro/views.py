from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from .models import Cliente, Carteira, VendaFicha

# Create your views here.

def financeiro_home(request):
    """View principal do módulo financeiro"""
    return render(request, 'financeiro/home.html')

@csrf_exempt
@require_http_methods(["GET"])
def listar_clientes(request):
    """API para listar todos os clientes"""
    try:
        clientes = Cliente.objects.all()
        clientes_data = []
        
        for cliente in clientes:
            # Buscar carteira e fichas
            try:
                carteira = cliente.carteira
                saldo_fichas = carteira.saldo_fichas
            except:
                saldo_fichas = 0
            
            clientes_data.append({
                'id': cliente.id,
                'nome': cliente.nome,
                'sobrenome': cliente.sobrenome,
                'nome_completo': cliente.nome_completo,
                'cpf': cliente.cpf,
                'saldo': float(cliente.saldo),
                'saldo_formatado': cliente.saldo_formatado,
                'telefone': cliente.telefone,
                'data_criacao': cliente.data_criacao.strftime('%d/%m/%Y %H:%M'),
                'data_atualizacao': cliente.data_atualizacao.strftime('%d/%m/%Y %H:%M'),
                'saldo_fichas': saldo_fichas
            })
        
        return JsonResponse({
            'success': True,
            'clientes': clientes_data,
            'total': len(clientes_data)
        })
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@csrf_exempt
@require_http_methods(["GET"])
def obter_cliente(request, cliente_id):
    """API para obter um cliente específico por ID"""
    try:
        cliente = Cliente.objects.get(id=cliente_id)
        try:
            carteira = cliente.carteira
            saldo_fichas = carteira.saldo_fichas
        except:
            saldo_fichas = 0
        vendas = VendaFicha.objects.filter(cliente=cliente).order_by('-data_venda')
        vendas_data = [
            {
                'id': venda.id,
                'quantidade': venda.quantidade,
                'data_venda': venda.data_venda.strftime('%d/%m/%Y %H:%M')
            } for venda in vendas
        ]
        cliente_data = {
            'id': cliente.id,
            'nome': cliente.nome,
            'sobrenome': cliente.sobrenome,
            'nome_completo': cliente.nome_completo,
            'cpf': cliente.cpf,
            'saldo': float(cliente.saldo),
            'saldo_formatado': cliente.saldo_formatado,
            'telefone': cliente.telefone,
            'data_criacao': cliente.data_criacao.strftime('%d/%m/%Y %H:%M'),
            'data_atualizacao': cliente.data_atualizacao.strftime('%d/%m/%Y %H:%M'),
            'saldo_fichas': saldo_fichas,
            'vendas_fichas': vendas_data
        }
        return JsonResponse({
            'success': True,
            'cliente': cliente_data
        })
    
    except Cliente.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Cliente não encontrado'
        }, status=404)
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def criar_cliente(request):
    """API para criar um novo cliente"""
    try:
        data = json.loads(request.body)
        nome = data.get('nome')
        sobrenome = data.get('sobrenome', '')
        cpf = data.get('cpf', '')
        saldo = float(data.get('saldo', 0))
        telefone = data.get('telefone', '')
        fichas_iniciais = int(data.get('fichas_iniciais', 0))

        cliente = Cliente.objects.create(
            nome=nome,
            sobrenome=sobrenome,
            cpf=cpf,
            saldo=saldo,
            telefone=telefone
        )
        # Sempre criar a carteira, mesmo que fichas_iniciais seja zero
        carteira = Carteira.objects.create(cliente=cliente, saldo_fichas=fichas_iniciais)
        # Registrar venda inicial de fichas, se houver
        venda = None
        if fichas_iniciais > 0:
            venda = VendaFicha.objects.create(cliente=cliente, quantidade=fichas_iniciais)
        cliente_data = {
            'id': cliente.id,
            'nome': cliente.nome,
            'sobrenome': cliente.sobrenome,
            'nome_completo': cliente.nome_completo,
            'cpf': cliente.cpf,
            'saldo': float(cliente.saldo),
            'saldo_formatado': cliente.saldo_formatado,
            'telefone': cliente.telefone,
            'data_criacao': cliente.data_criacao.strftime('%d/%m/%Y %H:%M'),
            'data_atualizacao': cliente.data_atualizacao.strftime('%d/%m/%Y %H:%M'),
            'saldo_fichas': carteira.saldo_fichas,
            'venda_inicial': {
                'id': venda.id,
                'quantidade': venda.quantidade,
                'data_venda': venda.data_venda.strftime('%d/%m/%Y %H:%M')
            } if venda else None
        }
        return JsonResponse({
            'success': True,
            'message': 'Cliente criado com sucesso',
            'cliente': cliente_data
        }, status=201)
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'JSON inválido'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def adicionar_fichas(request, cliente_id):
    """API para adicionar fichas a um cliente (nova venda)"""
    try:
        data = json.loads(request.body)
        quantidade = int(data.get('quantidade', 0))
        if quantidade <= 0:
            return JsonResponse({'success': False, 'error': 'Quantidade deve ser maior que zero.'}, status=400)
        cliente = Cliente.objects.get(id=cliente_id)
        carteira = getattr(cliente, 'carteira', None)
        if not carteira:
            return JsonResponse({'success': False, 'error': 'Carteira não encontrada.'}, status=404)
        # Registrar venda
        venda = VendaFicha.objects.create(cliente=cliente, quantidade=quantidade)
        # Atualizar carteira
        carteira.saldo_fichas += quantidade
        carteira.save()
        return JsonResponse({
            'success': True,
            'message': 'Fichas adicionadas com sucesso',
            'nova_venda': {
                'id': venda.id,
                'quantidade': venda.quantidade,
                'data_venda': venda.data_venda.strftime('%d/%m/%Y %H:%M')
            },
            'saldo_fichas': carteira.saldo_fichas
        })
    except Cliente.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Cliente não encontrado.'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def dar_baixa_fichas(request, cliente_id):
    """API para dar baixa (subtrair) fichas da carteira do cliente"""
    try:
        data = json.loads(request.body)
        quantidade = int(data.get('quantidade', 0))
        if quantidade <= 0:
            return JsonResponse({'success': False, 'error': 'Quantidade deve ser maior que zero.'}, status=400)
        cliente = Cliente.objects.get(id=cliente_id)
        carteira = getattr(cliente, 'carteira', None)
        if not carteira:
            return JsonResponse({'success': False, 'error': 'Carteira não encontrada.'}, status=404)
        if carteira.saldo_fichas < quantidade:
            return JsonResponse({'success': False, 'error': 'Saldo de fichas insuficiente.'}, status=400)
        # Subtrair fichas
        carteira.saldo_fichas -= quantidade
        carteira.save()
        return JsonResponse({
            'success': True,
            'message': 'Baixa de fichas realizada com sucesso',
            'saldo_fichas': carteira.saldo_fichas
        })
    except Cliente.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Cliente não encontrado.'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

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

@require_http_methods(["GET"])
def listar_clientes(request):
    """API para listar todos os clientes"""
    print("=== LISTAR CLIENTES ===")
    try:
        clientes = Cliente.objects.all()
        print(f"Clientes encontrados: {clientes.count()}")
        clientes_data = []
        
        for cliente in clientes:
            print(f"Processando cliente: {cliente.nome_completo}")
            # Buscar carteira e fichas
            try:
                carteira = cliente.carteira
                saldo_fichas = carteira.saldo_fichas
                print(f"  - Carteira encontrada com {saldo_fichas} fichas")
            except Exception as e:
                # Se não tem carteira, criar uma
                print(f"  - Criando carteira para cliente {cliente.nome_completo}")
                carteira = Carteira.objects.create(cliente=cliente, saldo_fichas=0)
                saldo_fichas = 0
                print(f"  - Carteira criada com {saldo_fichas} fichas")
            
            clientes_data.append({
                'id': cliente.id,
                'nome': cliente.nome,
                'sobrenome': cliente.sobrenome,
                'nome_completo': cliente.nome_completo,
                'cpf': cliente.cpf,
                'saldo': saldo_fichas,  # Usar saldo de fichas como saldo principal
                'saldo_formatado': f'{saldo_fichas} fichas',
                'telefone': cliente.telefone,
                'data_criacao': cliente.data_criacao.strftime('%d/%m/%Y %H:%M'),
                'data_atualizacao': cliente.data_atualizacao.strftime('%d/%m/%Y %H:%M'),
                'saldo_fichas': saldo_fichas
            })
        
        print(f"Total de clientes processados: {len(clientes_data)}")
        return JsonResponse({
            'success': True,
            'clientes': clientes_data,
            'total': len(clientes_data)
        })
    
    except Exception as e:
        print(f"Erro ao listar clientes: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@require_http_methods(["GET"])
def obter_cliente(request, cliente_id):
    """API para obter um cliente específico por ID"""
    print(f"=== OBTER CLIENTE ID: {cliente_id} ===")
    try:
        cliente = Cliente.objects.get(id=cliente_id)
        print(f"Cliente encontrado: {cliente.nome_completo}")
        
        try:
            carteira = cliente.carteira
            saldo_fichas = carteira.saldo_fichas
            print(f"Carteira encontrada com {saldo_fichas} fichas")
        except:
            # Se não tem carteira, criar uma
            print(f"Criando carteira para cliente {cliente.nome_completo}")
            carteira = Carteira.objects.create(cliente=cliente, saldo_fichas=0)
            saldo_fichas = 0
            print(f"Carteira criada com {saldo_fichas} fichas")
        
        vendas = VendaFicha.objects.filter(cliente=cliente).order_by('-data_venda')
        print(f"Vendas encontradas: {vendas.count()}")
        
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
            'saldo': saldo_fichas,  # Usar saldo de fichas como saldo principal
            'saldo_formatado': f'{saldo_fichas} fichas',
            'telefone': cliente.telefone,
            'data_criacao': cliente.data_criacao.strftime('%d/%m/%Y %H:%M'),
            'data_atualizacao': cliente.data_atualizacao.strftime('%d/%m/%Y %H:%M'),
            'saldo_fichas': saldo_fichas,
            'vendas_fichas': vendas_data
        }
        
        print(f"Dados do cliente preparados: {cliente_data}")
        
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
            saldo=0,  # Saldo em dinheiro sempre zero
            telefone=telefone
        )
        
        # Criar carteira com saldo de fichas
        saldo_fichas = int(saldo)  # Cada R$ 1,00 = 1 ficha
        carteira = Carteira.objects.create(cliente=cliente, saldo_fichas=saldo_fichas)
        
        # Registrar venda inicial de fichas, se houver
        venda = None
        if saldo_fichas > 0:
            venda = VendaFicha.objects.create(cliente=cliente, quantidade=saldo_fichas)
        
        cliente_data = {
            'id': cliente.id,
            'nome': cliente.nome,
            'sobrenome': cliente.sobrenome,
            'nome_completo': cliente.nome_completo,
            'cpf': cliente.cpf,
            'saldo': carteira.saldo_fichas,  # Usar saldo de fichas como saldo principal
            'saldo_formatado': f'{carteira.saldo_fichas} fichas',
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
    """API para adicionar fichas a um cliente (nova venda) e ao saldo em dinheiro"""
    from decimal import Decimal
    
    print(f"=== ADICIONAR FICHAS - Cliente ID: {cliente_id} ===")
    print(f"Request body: {request.body}")
    
    try:
        data = json.loads(request.body)
        quantidade = int(data.get('quantidade', 0))
        print(f"Quantidade solicitada: {quantidade}")
        
        if quantidade <= 0:
            print("Erro: Quantidade deve ser maior que zero")
            return JsonResponse({'success': False, 'error': 'Quantidade deve ser maior que zero.'}, status=400)
        
        cliente = Cliente.objects.get(id=cliente_id)
        print(f"Cliente encontrado: {cliente.nome_completo}")
        
        # Verificar se tem carteira, se não tiver, criar uma
        carteira = getattr(cliente, 'carteira', None)
        if not carteira:
            print("Carteira não encontrada. Criando uma nova...")
            carteira = Carteira.objects.create(cliente=cliente, saldo_fichas=0)
            print(f"Carteira criada com saldo inicial: {carteira.saldo_fichas}")
        
        print(f"Saldo atual de fichas: {carteira.saldo_fichas}")
        print(f"Saldo atual em dinheiro: {cliente.saldo}")
        
        # Calcular valor em dinheiro (cada ficha = R$ 1,00)
        valor_adicao = Decimal(str(quantidade))
        print(f"Valor a adicionar: R$ {valor_adicao}")
        
        # Registrar venda
        venda = VendaFicha.objects.create(cliente=cliente, quantidade=quantidade)
        
        # Atualizar carteira
        carteira.saldo_fichas += quantidade
        carteira.save()
        print(f"Novo saldo de fichas: {carteira.saldo_fichas}")
        
        return JsonResponse({
            'success': True,
            'message': 'Fichas adicionadas com sucesso',
            'nova_venda': {
                'id': venda.id,
                'quantidade': venda.quantidade,
                'data_venda': venda.data_venda.strftime('%d/%m/%Y %H:%M')
            },
            'saldo_fichas': carteira.saldo_fichas,
            'valor_adicao': float(valor_adicao)
        })
    except Cliente.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Cliente não encontrado.'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def dar_baixa_fichas(request, cliente_id):
    """API para dar baixa (subtrair) fichas da carteira do cliente e do saldo em dinheiro"""
    from decimal import Decimal
    
    print(f"=== DAR BAIXA FICHAS - Cliente ID: {cliente_id} ===")
    print(f"Request body: {request.body}")
    
    try:
        data = json.loads(request.body)
        quantidade = int(data.get('quantidade', 0))
        print(f"Quantidade solicitada: {quantidade}")
        
        if quantidade <= 0:
            print("Erro: Quantidade deve ser maior que zero")
            return JsonResponse({'success': False, 'error': 'Quantidade deve ser maior que zero.'}, status=400)
        
        cliente = Cliente.objects.get(id=cliente_id)
        print(f"Cliente encontrado: {cliente.nome_completo}")
        
        # Verificar se tem carteira, se não tiver, criar uma
        carteira = getattr(cliente, 'carteira', None)
        if not carteira:
            print("Carteira não encontrada. Criando uma nova...")
            carteira = Carteira.objects.create(cliente=cliente, saldo_fichas=0)
            print(f"Carteira criada com saldo inicial: {carteira.saldo_fichas}")
        
        print(f"Saldo atual de fichas: {carteira.saldo_fichas}")
        
        # Calcular valor em dinheiro (cada ficha = R$ 1,00)
        valor_baixa = Decimal(str(quantidade))
        
        # Verificar se há saldo suficiente apenas em fichas
        if carteira.saldo_fichas < quantidade:
            print(f"Erro: Saldo de fichas insuficiente. Fichas disponíveis: {carteira.saldo_fichas}, Solicitado: {quantidade}")
            return JsonResponse({
                'success': False, 
                'error': f'Saldo de fichas insuficiente. Disponível: {carteira.saldo_fichas}, Solicitado: {quantidade}'
            }, status=400)
        
        # Subtrair fichas
        carteira.saldo_fichas -= quantidade
        carteira.save()
        print(f"Fichas deduzidas: {quantidade}. Novo saldo de fichas: {carteira.saldo_fichas}")
        
        return JsonResponse({
            'success': True,
            'message': f'Baixa de {quantidade} fichas realizada com sucesso',
            'saldo_fichas': carteira.saldo_fichas,
            'valor_baixa': float(valor_baixa),
            'fichas_deduzidas': quantidade,
            'dinheiro_deduzido': 0
        })
    except Cliente.DoesNotExist:
        print(f"Erro: Cliente {cliente_id} não encontrado")
        return JsonResponse({'success': False, 'error': 'Cliente não encontrado.'}, status=404)
    except Exception as e:
        print(f"Erro inesperado: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

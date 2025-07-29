from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

def landing_page(request):
    """Landing page principal de divulgação"""
    return render(request, 'divulgacao/landing.html')

def sobre_sistema(request):
    """Página sobre o sistema"""
    return render(request, 'divulgacao/sobre.html')

def recursos(request):
    """Página de recursos do sistema"""
    return render(request, 'divulgacao/recursos.html')

def contato(request):
    """Página de contato"""
    return render(request, 'divulgacao/contato.html')

@csrf_exempt
def enviar_contato(request):
    """API para enviar formulário de contato"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            nome = data.get('nome', '')
            email = data.get('email', '')
            mensagem = data.get('mensagem', '')
            
            # Aqui você pode implementar o envio de email
            # Por enquanto, apenas retornamos sucesso
            
            return JsonResponse({
                'success': True,
                'message': 'Mensagem enviada com sucesso! Entraremos em contato em breve.'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': 'Erro ao enviar mensagem. Tente novamente.'
            }, status=500)
    
    return JsonResponse({'success': False, 'message': 'Método não permitido'}, status=405)

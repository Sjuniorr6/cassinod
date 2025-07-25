from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import get_user_model
from .forms import UsuarioCreationForm

Usuario = get_user_model()

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            if user.acesso:  # Usando o campo customizado
                login(request, user)
                return redirect('home')
            else:
                return JsonResponse({
                    'success': False,
                    'message': 'Aguardando aprovação do administrador.',
                    'type': 'warning'
                })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Usuário ou senha inválidos.',
                'type': 'error'
            })
    
    return render(request, 'usuarios/login.html')

def register_view(request):
    if request.method == 'POST':
        form = UsuarioCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            return JsonResponse({
                'success': True,
                'message': 'Usuário criado com sucesso! Aguarde a aprovação do administrador.',
                'type': 'success'
            })
        else:
            errors = {}
            for field, error_list in form.errors.items():
                errors[field] = error_list[0]
            return JsonResponse({
                'success': False,
                'message': 'Erro ao criar usuário.',
                'errors': errors,
                'type': 'error'
            })
    
    form = UsuarioCreationForm()
    return render(request, 'usuarios/register.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.success(request, 'Você foi desconectado com sucesso!')
    return redirect('usuarios:login')

@csrf_exempt
def check_login_status(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            if user.acesso:
                # Faz o login do usuário
                login(request, user)
                return JsonResponse({
                    'success': True,
                    'redirect': '/'
                })
            else:
                return JsonResponse({
                    'success': False,
                    'message': 'Aguardando aprovação do administrador.',
                    'type': 'warning'
                })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Usuário ou senha inválidos.',
                'type': 'error'
            })
    
    return JsonResponse({'success': False, 'message': 'Método não permitido.'}) 
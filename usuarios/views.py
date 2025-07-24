from django.shortcuts import render
from django.contrib.auth.views import LoginView

class UsuarioLoginView(LoginView):
    template_name = 'login.html' 
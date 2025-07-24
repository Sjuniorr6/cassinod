from django.contrib import admin
from django.urls import path, include
from django.shortcuts import render

def home(request):
    return render(request, 'home.html')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('usuarios/', include('usuarios.urls')),
    path('mesas/', include('mesas.urls')),
    path('', home, name='home'),
] 
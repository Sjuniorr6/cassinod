from django.contrib import admin
from django.urls import path, include
from django.shortcuts import render
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.decorators import login_required

@login_required
def home(request):
    return render(request, 'home.html')

def landing_page(request):
    return render(request, 'divulgacao/landing.html')

urlpatterns = [
    path('', home, name='home'),  # URL padrão para a raiz
    path('admin/', admin.site.urls),
    path('usuarios/', include('usuarios.urls')),
    path('mesas/', include('mesas.urls')),
    path('financeiro/', include('financeiro.urls')),
    path('sange/', include('sange.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('divulgacao/', include('divulgacao.urls')),
    path('croupiers/', include('croupiers.urls')),
    path('landing/', landing_page, name='landing_page'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    if hasattr(settings, 'STATICFILES_DIRS') and settings.STATICFILES_DIRS:
        urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0]) 
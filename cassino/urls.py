from django.contrib import admin
from django.urls import path, include
from django.shortcuts import render
from django.conf import settings
from django.conf.urls.static import static

def home(request):
    from mesas.views import mesas_home
    return mesas_home(request)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('usuarios/', include('usuarios.urls')),
    path('mesas/', include('mesas.urls')),
    path('financeiro/', include('financeiro.urls')),
    path('sange/', include('sange.urls')),
    path('', home, name='home'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0]) 
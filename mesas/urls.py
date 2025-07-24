from django.urls import path
from . import views

urlpatterns = [
    path('', views.mesas_home, name='mesas_home'),
    path('criar/', views.criar_mesa, name='criar_mesa'),
    
    # API Endpoints
    path('api/listar/', views.listar_mesas_api, name='listar_mesas_api'),
    path('api/obter/<int:mesa_id>/', views.obter_mesa_api, name='obter_mesa_api'),
    path('api/modelo/', views.modelo_info_api, name='modelo_info_api'),
    path('api/fechar/<int:mesa_id>/', views.fechar_mesa_api, name='fechar_mesa_api'),
    path('api/abrir/<int:mesa_id>/', views.abrir_mesa_api, name='abrir_mesa_api'),
] 
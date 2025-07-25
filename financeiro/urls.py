from django.urls import path
from . import views

app_name = 'financeiro'

urlpatterns = [
    # Página principal do financeiro
    path('', views.financeiro_home, name='home'),
    
    # APIs de Clientes
    path('api/clientes/', views.listar_clientes, name='listar_clientes'),
    path('api/clientes/criar/', views.criar_cliente, name='criar_cliente'),
    path('api/clientes/<int:cliente_id>/', views.obter_cliente, name='obter_cliente'),
    path('api/clientes/<int:cliente_id>/adicionar_fichas/', views.adicionar_fichas, name='adicionar_fichas'),
    path('api/clientes/<int:cliente_id>/dar_baixa_fichas/', views.dar_baixa_fichas, name='dar_baixa_fichas'),
] 
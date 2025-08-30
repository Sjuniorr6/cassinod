from django.urls import path
from . import views

app_name = 'sange'

urlpatterns = [
    # Páginas principais
    path('', views.listar_sanges, name='listar_sanges'),
    path('nova/', views.nova_sange, name='nova_sange'),
    path('historico/', views.historico_movimentos, name='historico_movimentos'),
    
    # Gerenciamento de caixas
    path('sange/<int:sange_id>/abrir-caixa/', views.abrir_caixa, name='abrir_caixa'),
    path('caixa/<int:caixa_id>/', views.detalhes_caixa, name='detalhes_caixa'),
    path('caixa/<int:caixa_id>/fechar/', views.fechar_caixa, name='fechar_caixa'),
    
    # Operações
    path('caixa/<int:caixa_id>/vender/', views.vender_fichas, name='vender_fichas'),
    path('caixa/<int:caixa_id>/trocar/', views.trocar_fichas, name='trocar_fichas'),
    
    # APIs
    path('api/calcular-valor-total/', views.api_calcular_valor_total, name='api_calcular_valor_total'),
    path('api/calcular-troca/', views.api_calcular_troca, name='api_calcular_troca'),
] 
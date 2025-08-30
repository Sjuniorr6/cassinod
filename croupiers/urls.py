from django.urls import path
from . import views

app_name = 'croupiers'

urlpatterns = [
    path('', views.listar_croupiers, name='listar_croupiers'),
    path('api/listar/', views.listar_croupiers_api, name='listar_croupiers_api'),
    path('api/criar/', views.criar_croupier_api, name='criar_croupier_api'),
    path('api/<int:croupier_id>/', views.obter_croupier_api, name='obter_croupier_api'),
    path('api/<int:croupier_id>/editar/', views.editar_croupier_api, name='editar_croupier_api'),
    path('api/<int:croupier_id>/excluir/', views.excluir_croupier_api, name='excluir_croupier_api'),
]

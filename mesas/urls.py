from django.urls import path
from . import views

urlpatterns = [
    path('', views.mesas_home, name='mesas_home'),
    path('todas/', views.todas_mesas, name='todas_mesas'),
    path('criar/', views.criar_mesa, name='criar_mesa'),
    path('api/mesas/', views.listar_mesas_api, name='listar_mesas_api'),
    path('api/mesa/criar/', views.criar_mesa_api, name='criar_mesa_api'),
    path('api/mesa/<int:mesa_id>/', views.mesa_detail_api, name='mesa_detail_api'),
    path('api/mesa/<int:mesa_id>/obter/', views.obter_mesa_api, name='obter_mesa_api'),
    path('api/mesa/<int:mesa_id>/editar/', views.editar_mesa_api, name='editar_mesa_api'),
    path('api/mesa/<int:mesa_id>/fechar/', views.fechar_mesa_api, name='fechar_mesa_api'),
    path('api/mesa/<int:mesa_id>/abrir/', views.abrir_mesa_api, name='abrir_mesa_api'),
    path('api/mesa/<int:mesa_id>/encerrar/', views.encerrar_mesa_api, name='encerrar_mesa_api'),
    path('api/mesa/<int:mesa_id>/testar/', views.testar_mesa_api, name='testar_mesa_api'),
    path('api/modelo-info/', views.modelo_info_api, name='modelo_info_api'),
    path('api/atualizar-metricas/', views.atualizar_metricas_api, name='atualizar_metricas_api'),
] 
from django.urls import path
from . import views

app_name = 'divulgacao'

urlpatterns = [
    path('', views.landing_page, name='landing'),
    path('sobre/', views.sobre_sistema, name='sobre'),
    path('recursos/', views.recursos, name='recursos'),
    path('contato/', views.contato, name='contato'),
    path('api/contato/', views.enviar_contato, name='enviar_contato'),
] 
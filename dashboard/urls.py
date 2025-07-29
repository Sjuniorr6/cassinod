from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_home, name='home'),
    path('api/estatisticas/', views.api_estatisticas, name='api_estatisticas'),
]
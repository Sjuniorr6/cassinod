from django.urls import path
from . import views

urlpatterns = [
    path('', views.mesas_home, name='mesas_home'),
    path('criar/', views.criar_mesa, name='criar_mesa'),
] 
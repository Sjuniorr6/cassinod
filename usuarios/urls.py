from django.urls import path
from .views import UsuarioLoginView

urlpatterns = [
    path('login/', UsuarioLoginView.as_view(), name='login'),
] 
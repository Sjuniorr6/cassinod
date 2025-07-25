from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator

class Usuario(AbstractUser):
    # Permite espaços no username
    username = models.CharField(
        max_length=150,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^[a-zA-Z0-9\s]+$',
                message='Nome de usuário pode conter apenas letras, números e espaços.'
            )
        ],
        verbose_name='Nome de usuário'
    )
    
    # Campo para controlar acesso ao sistema
    acesso = models.BooleanField(default=False, verbose_name='Acesso liberado?')
    
    # Campos adicionais opcionais
    data_criacao = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Data de criação'
    )
    
    data_aprovacao = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Data de aprovação'
    )
    
    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'
        db_table = 'usuarios'
    
    def __str__(self):
        return self.username
    
    def aprovar_acesso(self):
        """Aprova o acesso do usuário"""
        from django.utils import timezone
        self.acesso = True
        self.data_aprovacao = timezone.now()
        self.save()
    
    def revogar_acesso(self):
        """Revoga o acesso do usuário"""
        self.acesso = False
        self.data_aprovacao = None
        self.save()

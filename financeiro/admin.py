from django.contrib import admin
from .models import Cliente

# Register your models here.

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ['nome', 'sobrenome', 'cpf', 'saldo', 'telefone', 'data_criacao']
    list_filter = ['data_criacao', 'data_atualizacao']
    search_fields = ['nome', 'sobrenome', 'cpf', 'telefone']
    readonly_fields = ['data_criacao', 'data_atualizacao']
    ordering = ['-data_criacao']
    
    fieldsets = (
        ('Informações Pessoais', {
            'fields': ('nome', 'sobrenome', 'cpf', 'telefone')
        }),
        ('Informações Financeiras', {
            'fields': ('saldo',)
        }),
        ('Datas', {
            'fields': ('data_criacao', 'data_atualizacao'),
            'classes': ('collapse',)
        }),
    )

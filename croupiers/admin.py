from django.contrib import admin
from .models import Croupier

@admin.register(Croupier)
class CroupierAdmin(admin.ModelAdmin):
    list_display = ['nome', 'ativo', 'data_criacao', 'data_atualizacao']
    list_filter = ['ativo', 'data_criacao']
    search_fields = ['nome']
    ordering = ['nome']
    readonly_fields = ['data_criacao', 'data_atualizacao']
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('nome', 'ativo')
        }),
        ('Datas', {
            'fields': ('data_criacao', 'data_atualizacao'),
            'classes': ('collapse',)
        }),
    )

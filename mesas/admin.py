from django.contrib import admin
from .models import Mesa

@admin.register(Mesa)
class MesaAdmin(admin.ModelAdmin):
    list_display = ['numero_mesa', 'tipo_jogo', 'status', 'valor_total', 'data_criacao']
    list_filter = ['tipo_jogo', 'status', 'data_criacao']
    search_fields = ['numero_mesa']
    ordering = ['numero_mesa']
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('numero_mesa', 'tipo_jogo', 'status')
        }),
        ('Valores', {
            'fields': ('valor_total',)
        }),
        ('Datas', {
            'fields': ('data_criacao', 'data_atualizacao'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['data_criacao', 'data_atualizacao'] 
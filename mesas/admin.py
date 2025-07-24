from django.contrib import admin
from .models import Mesa

@admin.register(Mesa)
class MesaAdmin(admin.ModelAdmin):
    list_display = ['numero_mesa', 'tipo_jogo', 'valor_total', 'data_atualizacao']
    list_filter = ['tipo_jogo', 'data_criacao']
    search_fields = ['numero_mesa']
    readonly_fields = ['valor_total', 'data_criacao', 'data_atualizacao']
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('numero_mesa', 'tipo_jogo')
        }),
        ('Fichas', {
            'fields': (
                'fichas_5', 'fichas_25', 'fichas_100', 'fichas_500',
                'fichas_1000', 'fichas_5000', 'fichas_10000'
            )
        }),
        ('Informações do Sistema', {
            'fields': ('valor_total', 'data_criacao', 'data_atualizacao'),
            'classes': ('collapse',)
        }),
    )
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editando um objeto existente
            return self.readonly_fields + ('numero_mesa',)
        return self.readonly_fields 
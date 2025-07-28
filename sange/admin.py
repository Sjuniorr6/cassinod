from django.contrib import admin
from django.utils.html import format_html
from .models import Sange, CaixaSange, VendaFicha, TrocaFicha

@admin.register(Sange)
class SangeAdmin(admin.ModelAdmin):
    list_display = ['nome', 'ativo', 'caixa_aberto', 'data_criacao']
    list_filter = ['ativo', 'data_criacao']
    search_fields = ['nome']
    readonly_fields = ['data_criacao', 'data_atualizacao']
    
    def caixa_aberto(self, obj):
        if obj.caixa_aberto:
            return format_html('<span style="color: green;">● Aberto</span>')
        return format_html('<span style="color: red;">● Fechado</span>')
    caixa_aberto.short_description = 'Status do Caixa'

@admin.register(CaixaSange)
class CaixaSangeAdmin(admin.ModelAdmin):
    list_display = ['sange', 'data_abertura', 'data_fechamento', 'valor_total_inicial', 'valor_total_atual', 'status']
    list_filter = ['sange', 'data_abertura', 'data_fechamento']
    search_fields = ['sange__nome']
    readonly_fields = ['data_abertura', 'valor_total_inicial', 'valor_total_atual', 'fichas_atuais']
    
    def status(self, obj):
        if obj.esta_aberto:
            return format_html('<span style="color: green;">● Aberto</span>')
        return format_html('<span style="color: red;">● Fechado</span>')
    status.short_description = 'Status'

@admin.register(VendaFicha)
class VendaFichaAdmin(admin.ModelAdmin):
    list_display = ['caixa_sange', 'jogador', 'valor_unitario', 'quantidade', 'valor_total', 'data']
    list_filter = ['caixa_sange__sange', 'valor_unitario', 'data']
    search_fields = ['caixa_sange__sange__nome', 'jogador__nome']
    readonly_fields = ['valor_total', 'data']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('caixa_sange__sange', 'jogador')

@admin.register(TrocaFicha)
class TrocaFichaAdmin(admin.ModelAdmin):
    list_display = ['caixa_sange', 'valor_original', 'valor_ficha_troca', 'quantidade_gerada', 'data']
    list_filter = ['caixa_sange__sange', 'valor_original', 'valor_ficha_troca', 'data']
    search_fields = ['caixa_sange__sange__nome']
    readonly_fields = ['quantidade_gerada', 'data']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('caixa_sange__sange')

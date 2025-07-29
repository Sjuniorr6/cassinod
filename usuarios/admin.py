from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django.utils import timezone
from .models import Usuario

@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    list_display = ('username', 'email', 'acesso', 'data_criacao', 'last_login', 'acoes_rapidas')
    list_filter = ('acesso', 'is_active', 'is_staff', 'is_superuser', 'data_criacao')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('-data_criacao',)
    list_editable = ('acesso',)
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Informações Pessoais', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissões', {
            'fields': ('acesso', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Datas Importantes', {'fields': ('last_login', 'data_criacao', 'data_aprovacao')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'acesso'),
        }),
    )
    
    readonly_fields = ('data_criacao', 'last_login')
    
    def acoes_rapidas(self, obj):
        if obj.acesso:
            return format_html(
                '<span style="color: #28a745; font-weight: bold;">✓ Acesso Liberado</span>'
            )
        else:
            return format_html(
                '<span style="color: #dc3545; font-weight: bold;">✗ Aguardando Aprovação</span>'
            )
    acoes_rapidas.short_description = 'Status do Acesso'
    
    def aprovar_acesso_lote(self, request, queryset):
        count = queryset.update(acesso=True, data_aprovacao=timezone.now())
        self.message_user(request, f'{count} usuário(s) tiveram o acesso aprovado.')
    aprovar_acesso_lote.short_description = "Aprovar acesso para usuários selecionados"
    
    def revogar_acesso_lote(self, request, queryset):
        count = queryset.update(acesso=False, data_aprovacao=None)
        self.message_user(request, f'{count} usuário(s) tiveram o acesso revogado.')
    revogar_acesso_lote.short_description = "Revogar acesso para usuários selecionados"
    
    actions = [aprovar_acesso_lote, revogar_acesso_lote]

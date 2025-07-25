from django.db import models

# Create your models here.

class Cliente(models.Model):
    nome = models.CharField(max_length=100, verbose_name="Nome")
    sobrenome = models.CharField(max_length=100, null=True, blank=True, verbose_name="Sobrenome")
    cpf = models.CharField(max_length=14, null=True, blank=True, verbose_name="CPF")
    saldo = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Saldo")
    telefone = models.CharField(max_length=20, null=True, blank=True, verbose_name="Telefone")
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    data_atualizacao = models.DateTimeField(auto_now=True, verbose_name="Data de Atualização")

    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
        ordering = ['-data_criacao']

    def __str__(self):
        return f"{self.nome} {self.sobrenome or ''}".strip()

    @property
    def nome_completo(self):
        """Retorna o nome completo do cliente"""
        return f"{self.nome} {self.sobrenome or ''}".strip()

    @property
    def saldo_formatado(self):
        """Retorna o saldo formatado como moeda brasileira"""
        return f"R$ {self.saldo:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')

class Carteira(models.Model):
    cliente = models.OneToOneField(Cliente, on_delete=models.CASCADE, related_name='carteira')
    saldo_fichas = models.PositiveIntegerField(default=0, verbose_name="Saldo de Fichas")
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Carteira de {self.cliente.nome_completo} - Fichas: {self.saldo_fichas}"

class VendaFicha(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='vendas_fichas')
    quantidade = models.PositiveIntegerField(verbose_name="Quantidade de Fichas")
    data_venda = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Venda de {self.quantidade} fichas para {self.cliente.nome_completo} em {self.data_venda.strftime('%d/%m/%Y %H:%M')}"

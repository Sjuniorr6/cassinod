from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
import json

class Sange(models.Model):
    nome = models.CharField(max_length=100, verbose_name="Nome da Sange")
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    data_atualizacao = models.DateTimeField(auto_now=True, verbose_name="Última Atualização")

    class Meta:
        verbose_name = "Sange"
        verbose_name_plural = "Sanges"
        ordering = ['nome']

    def __str__(self):
        return self.nome

    @property
    def caixa_aberto(self):
        """Verifica se a sange tem um caixa aberto"""
        return self.caixasange_set.filter(data_fechamento__isnull=True).exists()

    @property
    def caixa_atual(self):
        """Retorna o caixa atual aberto da sange"""
        return self.caixasange_set.filter(data_fechamento__isnull=True).first()

class CaixaSange(models.Model):
    sange = models.ForeignKey(Sange, on_delete=models.CASCADE, verbose_name="Sange")
    data_abertura = models.DateTimeField(auto_now_add=True, verbose_name="Data de Abertura")
    data_fechamento = models.DateTimeField(null=True, blank=True, verbose_name="Data de Fechamento")
    fichas_iniciais = models.JSONField(default=dict, verbose_name="Fichas Iniciais")
    valor_total_inicial = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=Decimal('0.00'),
        verbose_name="Valor Total Inicial"
    )
    
    # Campos para controle das fichas atuais
    fichas_atuais = models.JSONField(default=dict, verbose_name="Fichas Atuais")
    valor_total_atual = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=Decimal('0.00'),
        verbose_name="Valor Total Atual"
    )

    class Meta:
        verbose_name = "Caixa de Sange"
        verbose_name_plural = "Caixas de Sange"
        ordering = ['-data_abertura']

    def __str__(self):
        return f"Caixa {self.sange.nome} - {self.data_abertura.strftime('%d/%m/%Y %H:%M')}"

    def save(self, *args, **kwargs):
        # Se é uma nova instância, inicializa as fichas atuais
        if not self.pk:
            self.fichas_atuais = self.fichas_iniciais.copy()
            self.valor_total_atual = self.valor_total_inicial
        
        # Calcula o valor total inicial se não foi calculado
        if self.valor_total_inicial == Decimal('0.00'):
            self.valor_total_inicial = self.calcular_valor_total(self.fichas_iniciais)
            self.valor_total_atual = self.valor_total_inicial
        
        super().save(*args, **kwargs)

    @staticmethod
    def calcular_valor_total(fichas_dict):
        """Calcula o valor total baseado no dicionário de fichas"""
        total = Decimal('0.00')
        for valor, quantidade in fichas_dict.items():
            if quantidade and valor:
                total += Decimal(str(valor)) * Decimal(str(quantidade))
        return total

    def atualizar_fichas_apos_venda(self, valor_unitario, quantidade):
        """Atualiza as fichas após uma venda"""
        valor_str = str(valor_unitario)
        if valor_str in self.fichas_atuais:
            self.fichas_atuais[valor_str] = max(0, self.fichas_atuais[valor_str] - quantidade)
        self.valor_total_atual = self.calcular_valor_total(self.fichas_atuais)
        self.save()

    def atualizar_fichas_apos_troca(self, valor_original, valor_ficha_troca, quantidade_gerada):
        """Atualiza as fichas após uma troca"""
        valor_original_str = str(valor_original)
        valor_ficha_troca_str = str(valor_ficha_troca)
        
        # Remove fichas do valor original
        if valor_original_str in self.fichas_atuais:
            self.fichas_atuais[valor_original_str] = max(0, self.fichas_atuais[valor_original_str] - 1)
        
        # Adiciona fichas do valor de troca
        if valor_ficha_troca_str in self.fichas_atuais:
            self.fichas_atuais[valor_ficha_troca_str] = self.fichas_atuais.get(valor_ficha_troca_str, 0) + quantidade_gerada
        
        self.valor_total_atual = self.calcular_valor_total(self.fichas_atuais)
        self.save()

    @property
    def esta_aberto(self):
        """Verifica se o caixa está aberto"""
        return self.data_fechamento is None

    def fechar_caixa(self):
        """Fecha o caixa"""
        from django.utils import timezone
        self.data_fechamento = timezone.now()
        self.save()

class VendaFicha(models.Model):
    caixa_sange = models.ForeignKey(CaixaSange, on_delete=models.CASCADE, verbose_name="Caixa da Sange")
    jogador = models.ForeignKey(
        'financeiro.Cliente', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        verbose_name="Jogador"
    )
    valor_unitario = models.IntegerField(
        validators=[MinValueValidator(1)],
        verbose_name="Valor Unitário da Ficha"
    )
    quantidade = models.IntegerField(
        validators=[MinValueValidator(1)],
        verbose_name="Quantidade"
    )
    valor_total = models.DecimalField(
        max_digits=12, 
        decimal_places=2,
        verbose_name="Valor Total"
    )
    data = models.DateTimeField(auto_now_add=True, verbose_name="Data da Venda")

    class Meta:
        verbose_name = "Venda de Ficha"
        verbose_name_plural = "Vendas de Fichas"
        ordering = ['-data']

    def __str__(self):
        return f"Venda {self.valor_unitario}x{self.quantidade} - {self.data.strftime('%d/%m/%Y %H:%M')}"

    def save(self, *args, **kwargs):
        # Calcula o valor total se não foi calculado
        if not self.valor_total:
            self.valor_total = Decimal(str(self.valor_unitario)) * Decimal(str(self.quantidade))
        
        # Se é uma nova instância, atualiza as fichas do caixa
        if not self.pk:
            self.caixa_sange.atualizar_fichas_apos_venda(self.valor_unitario, self.quantidade)
        
        super().save(*args, **kwargs)

class TrocaFicha(models.Model):
    caixa_sange = models.ForeignKey(CaixaSange, on_delete=models.CASCADE, verbose_name="Caixa da Sange")
    valor_original = models.IntegerField(
        validators=[MinValueValidator(1)],
        verbose_name="Valor Original"
    )
    valor_ficha_troca = models.IntegerField(
        validators=[MinValueValidator(1)],
        verbose_name="Valor da Ficha de Troca"
    )
    quantidade_gerada = models.IntegerField(
        validators=[MinValueValidator(1)],
        verbose_name="Quantidade Gerada"
    )
    data = models.DateTimeField(auto_now_add=True, verbose_name="Data da Troca")

    class Meta:
        verbose_name = "Troca de Ficha"
        verbose_name_plural = "Trocas de Fichas"
        ordering = ['-data']

    def __str__(self):
        return f"Troca {self.valor_original} por {self.valor_ficha_troca}x{self.quantidade_gerada} - {self.data.strftime('%d/%m/%Y %H:%M')}"

    def save(self, *args, **kwargs):
        # Calcula a quantidade gerada se não foi calculada
        if not self.quantidade_gerada:
            self.quantidade_gerada = self.valor_original // self.valor_ficha_troca
        
        # Se é uma nova instância, atualiza as fichas do caixa
        if not self.pk:
            self.caixa_sange.atualizar_fichas_apos_troca(
                self.valor_original, 
                self.valor_ficha_troca, 
                self.quantidade_gerada
            )
        
        super().save(*args, **kwargs)

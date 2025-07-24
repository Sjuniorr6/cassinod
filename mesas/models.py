from django.db import models

class Mesa(models.Model):
    TIPO_JOGO_CHOICES = [
        ('poker', 'Poker'),
        ('caribenho', 'Poker Caribenho'),
        ('ultimate', 'Poker Ultimate'),
        ('baccarat', 'Baccarat'),
        ('roleta', 'Roleta'),
    ]
    
    STATUS_CHOICES = [
        ('aberta', 'Aberta'),
        ('fechada', 'Fechada'),
        ('encerrada', 'Encerrada'),
    ]
    
    tipo_jogo = models.CharField(
        max_length=20,
        choices=TIPO_JOGO_CHOICES,
        verbose_name='Tipo de Jogo'
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='aberta',
        verbose_name='Status'
    )
    
    numero_mesa = models.IntegerField(
        verbose_name='Número da Mesa'
    )
    
    # Fichas de diferentes valores
    fichas_5 = models.IntegerField(
        default=0,
        verbose_name='Fichas de R$ 5'
    )
    
    fichas_25 = models.IntegerField(
        default=0,
        verbose_name='Fichas de R$ 25'
    )
    
    fichas_100 = models.IntegerField(
        default=0,
        verbose_name='Fichas de R$ 100'
    )
    
    fichas_500 = models.IntegerField(
        default=0,
        verbose_name='Fichas de R$ 500'
    )
    
    fichas_1000 = models.IntegerField(
        default=0,
        verbose_name='Fichas de R$ 1.000'
    )
    
    fichas_5000 = models.IntegerField(
        default=0,
        verbose_name='Fichas de R$ 5.000'
    )
    
    fichas_10000 = models.IntegerField(
        default=0,
        verbose_name='Fichas de R$ 10.000'
    )
    
    valor_total = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        verbose_name='Valor Total da Mesa'
    )
    
    valor_inicial = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        verbose_name='Valor Inicial da Mesa'
    )
    
    saldo = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        verbose_name='Saldo da Mesa'
    )
    
    data_criacao = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Data de Criação'
    )
    
    data_atualizacao = models.DateTimeField(
        auto_now=True,
        verbose_name='Última Atualização'
    )
    
    class Meta:
        verbose_name = 'Mesa'
        verbose_name_plural = 'Mesas'
        ordering = ['numero_mesa']
    
    def __str__(self):
        return f"Mesa {self.numero_mesa} - {self.get_tipo_jogo_display()}"
    
    def calcular_valor_total(self):
        """Calcula o valor total baseado na quantidade de fichas"""
        total = (
            self.fichas_5 * 5 +
            self.fichas_25 * 25 +
            self.fichas_100 * 100 +
            self.fichas_500 * 500 +
            self.fichas_1000 * 1000 +
            self.fichas_5000 * 5000 +
            self.fichas_10000 * 10000
        )
        return total
    
    def save(self, *args, **kwargs):
        """Sobrescreve o método save para calcular automaticamente o valor total e saldo"""
        # Se é uma nova mesa (não tem ID ainda), definir valor_inicial igual ao valor_total
        if not self.pk:
            self.valor_total = self.calcular_valor_total()
            self.valor_inicial = self.valor_total
        else:
            # Para mesas existentes, apenas recalcular valor_total
            self.valor_total = self.calcular_valor_total()
        
        self.saldo = self.valor_total - self.valor_inicial
        super().save(*args, **kwargs) 
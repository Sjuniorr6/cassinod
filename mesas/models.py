from django.db import models

class Mesa(models.Model):
    TIPO_JOGO_CHOICES = [
        ('blackjack', 'Blackjack'),
        ('poker', 'Poker'),
        ('roleta', 'Roleta'),
        ('baccarat', 'Baccarat'),
        ('craps', 'Craps'),
        ('caribenho', 'Caribenho'),
    ]
    
    STATUS_CHOICES = [
        ('aberta', 'Aberta'),
        ('fechada', 'Fechada'),
        ('encerrada', 'Encerrada'),
    ]
    
    numero_mesa = models.IntegerField(unique=True)
    tipo_jogo = models.CharField(max_length=20, choices=TIPO_JOGO_CHOICES, default='blackjack')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='aberta')
    valor_total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Mesa'
        verbose_name_plural = 'Mesas'
        ordering = ['numero_mesa']
    
    def __str__(self):
        return f"{self.get_tipo_jogo_display()} - Mesa {self.numero_mesa}"
    
    def get_tipo_jogo_display(self):
        choices_dict = dict(self.TIPO_JOGO_CHOICES)
        return choices_dict.get(self.tipo_jogo, self.tipo_jogo.title())
    
    def get_status_display(self):
        choices_dict = dict(self.STATUS_CHOICES)
        return choices_dict.get(self.status, self.status.title()) 
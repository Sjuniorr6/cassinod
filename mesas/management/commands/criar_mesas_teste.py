from django.core.management.base import BaseCommand
from mesas.models import Mesa
from decimal import Decimal

class Command(BaseCommand):
    help = 'Cria mesas de teste para demonstrar o sistema'

    def handle(self, *args, **options):
        # Limpar mesas existentes
        Mesa.objects.all().delete()
        
        # Criar mesas de teste
        mesas_teste = [
            {
                'numero_mesa': 1,
                'tipo_jogo': 'poker',
                'status': 'aberta',
                'fichas_5': 100,
                'fichas_25': 50,
                'fichas_100': 20,
                'fichas_500': 10,
                'fichas_1000': 5,
                'fichas_5000': 2,
                'fichas_10000': 1,
            },
            {
                'numero_mesa': 2,
                'tipo_jogo': 'roleta',
                'status': 'fechada',
                'fichas_5': 200,
                'fichas_25': 100,
                'fichas_100': 40,
                'fichas_500': 20,
                'fichas_1000': 10,
                'fichas_5000': 4,
                'fichas_10000': 2,
            },
            {
                'numero_mesa': 3,
                'tipo_jogo': 'baccarat',
                'status': 'aberta',
                'fichas_5': 150,
                'fichas_25': 75,
                'fichas_100': 30,
                'fichas_500': 15,
                'fichas_1000': 8,
                'fichas_5000': 3,
                'fichas_10000': 1,
            },
            {
                'numero_mesa': 4,
                'tipo_jogo': 'caribenho',
                'status': 'aberta',
                'fichas_5': 80,
                'fichas_25': 40,
                'fichas_100': 16,
                'fichas_500': 8,
                'fichas_1000': 4,
                'fichas_5000': 2,
                'fichas_10000': 1,
            },
        ]
        
        for dados_mesa in mesas_teste:
            mesa = Mesa.objects.create(**dados_mesa)
            self.stdout.write(
                self.style.SUCCESS(
                    f'Mesa {mesa.numero_mesa} criada com sucesso! '
                    f'Valor Total: R$ {mesa.valor_total}, '
                    f'Saldo: R$ {mesa.saldo}'
                )
            )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Criadas {len(mesas_teste)} mesas de teste com sucesso!'
            )
        ) 
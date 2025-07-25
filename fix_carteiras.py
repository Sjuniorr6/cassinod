#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cassino.settings')
django.setup()

from financeiro.models import Cliente, Carteira

def corrigir_carteiras():
    print("=== CORRIGINDO CARTEIRAS ===")
    
    # Encontrar clientes sem carteira
    clientes_sem_carteira = []
    for cliente in Cliente.objects.all():
        if not hasattr(cliente, 'carteira'):
            clientes_sem_carteira.append(cliente)
    
    print(f"Clientes encontrados sem carteira: {len(clientes_sem_carteira)}")
    
    if not clientes_sem_carteira:
        print("Todos os clientes já têm carteira!")
        return
    
    # Criar carteiras para clientes que não têm
    for cliente in clientes_sem_carteira:
        print(f"Criando carteira para cliente: {cliente.nome} {cliente.sobrenome}")
        Carteira.objects.create(cliente=cliente, saldo_fichas=0)
    
    print("✅ Todas as carteiras foram criadas com sucesso!")
    print(f"Total de carteiras criadas: {len(clientes_sem_carteira)}")

if __name__ == "__main__":
    corrigir_carteiras() 
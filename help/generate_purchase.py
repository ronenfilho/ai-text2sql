import csv
from faker import Faker
import random
from datetime import datetime, timedelta

# Cria um objeto Faker
fake = Faker()

# Define as opções para os produtos
products = ['iPhone', 'Tesla', 'Humane pin']

# Define o nome do arquivo CSV
csv_file = 'help/random_purchase_data.csv'

# Define o cabeçalho do arquivo CSV
header = ['purchase_id', 'purchase_date', 'product_name', 'employee_id', 'amount']

# Abre o arquivo CSV para escrever os dados
with open(csv_file, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(header)

    # Gera 1000 registros aleatórios
    for i in range(1, 1001):
        # Gera uma data aleatória nos últimos 365 dias
        purchase_date = fake.date_between(start_date='-365d', end_date='today')

        # Seleciona aleatoriamente um produto
        product_name = random.choice(products)

        # Gera um ID de funcionário aleatório
        employee_id = random.randint(1, 7)

        # Gera um valor aleatório para a compra
        if product_name == 'iPhone':
            amount = random.randint(500, 1000)
        elif product_name == 'Tesla':
            amount = random.randint(50000, 100000)
        else:
            amount = random.randint(100, 1000)

        # Escreve os dados no arquivo CSV
        writer.writerow([i, purchase_date, product_name, employee_id, amount])

print(f'Arquivo CSV "{csv_file}" gerado com sucesso com 1000 registros aleatórios de compras!')

import csv
from faker import Faker
import random

# Inicializa o Faker para gerar dados aleatórios
fake = Faker()

# Lista de nomes e e-mails de exemplo
employee_data = [
    {"employee_id": 1, "name": "Richard Hendricks", "email": "richard@piedpiper.com"},
    {"employee_id": 2, "name": "Erlich Bachman", "email": "erlich@aviato.com"},
    {"employee_id": 3, "name": "Dinesh Chugtai", "email": "dinesh@piedpiper.com"},
    {"employee_id": 4, "name": "Bertram Gilfoyle", "email": "gilfoyle@piedpiper.com"},
    {"employee_id": 5, "name": "Jared Dunn", "email": "jared@piedpiper.com"},
    {"employee_id": 6, "name": "Monica Hall", "email": "monica@raviga.com"},
    {"employee_id": 7, "name": "Gavin Belson", "email": "gavin@hooli.com"}
]

# Função para gerar dados aleatórios para um funcionário
def generate_random_employee(employee_id):
    name = fake.name()
    email = fake.email()
    return {"employee_id": employee_id, "name": name, "email": email}

# Função para escrever os dados em um arquivo CSV
def write_random_employee_data(filename, data, num_lines):
    with open(filename, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=data[0].keys())
        writer.writeheader()
        for i in range(num_lines):
            writer.writerow(generate_random_employee(i+1))

# Gerar 1000 linhas de dados de funcionários aleatórios e escrever em um arquivo CSV
write_random_employee_data('help/random_employee_data.csv', employee_data, 1000)

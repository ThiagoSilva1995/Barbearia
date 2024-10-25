import pandas as pd
import os
import django
import sys

# Define o diretório do projeto
project_dir = os.path.dirname(os.path.abspath(__file__))  # Obtém o diretório do script
sys.path.append(os.path.abspath(os.path.join(project_dir, '..')))  # Adiciona o diretório do projeto ao PATH

# Define o ambiente Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'barbearia.settings')  # Certifique-se de que 'barbearia' está em minúsculas
django.setup()

from controle.models import Cliente  # Importando o modelo Cliente

# Carregue o arquivo Excel 
file_path = 'clientes.xlsx'  # Substitua pelo caminho do seu arquivo
df = pd.read_excel(file_path)

# Função para limpar e converter a data
def clean_date(date_str):
    if isinstance(date_str, str):  # Verifica se é uma string
        # Substituir barras invertidas por barras normais
        date_str = date_str.replace('\\', '/').strip()  # Remove espaços em branco
        # Tentar converter a data
        try:
            # Verifique se o formato da data é válido
            return pd.to_datetime(date_str, format='%d/%m/%Y').strftime('%Y-%m-%d')
        except ValueError:
            print(f"A data inválida encontrada: {date_str}")  # Imprime a data inválida
            return None  # Retorna None se a conversão falhar
    return None  # Retorna None se não for uma string

# Aplicar a função de limpeza à coluna de data
df['data_nascimento'] = df['data_nascimento'].apply(clean_date)

# Verifique se há datas inválidas e imprima um aviso se houver
invalid_dates = df['data_nascimento'].isnull()
if invalid_dates.any():
    print("Atenção: Algumas datas são inválidas e não foram convertidas:")
    print(df.loc[invalid_dates, 'data_nascimento'])  # Imprime as datas inválidas

# Iterar sobre as linhas do DataFrame e criar ou atualizar os objetos Cliente
for index, row in df.iterrows():
    nome = row['nome']  # Substitua 'nome' pelo nome exato da coluna no Excel
    telefone = row['telefone']  # Substitua pela coluna correta
    data_nascimento = row['data_nascimento']  # Agora estará no formato correto

    # Crie ou atualize o cliente com base no telefone
    if pd.notnull(data_nascimento):
        Cliente.objects.update_or_create(
            telefone=telefone,  # Procura pelo telefone
            defaults={'nome': nome, 'data_nascimento': data_nascimento}  # Atualiza ou cria
        )

print("Importação concluída!")

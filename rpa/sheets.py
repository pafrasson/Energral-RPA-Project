import logging
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Define o escopo de acesso
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

# Autenticação Sheet
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)

planilha = client.open("Teste")

# Selecionar a aba (sheet) pelo nome ou índice
sheet = planilha.worksheet("Plan1")  # ou .get_worksheet(0)

# # Modificar uma célula (ex: A1)
# sheet.update_acell('A1', 'Olá, mundo!')

# Modificar uma linha inteira
sheet.insert_row(['NomeA', 'IdadeA', 'CidadeA'], index=1)

# # Modificar uma célula usando linha/coluna
# sheet.update_cell(2, 1, 'Maria')  # Linha 2, Coluna 1

print("Modificações feitas com sucesso!")


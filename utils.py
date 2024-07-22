import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

def auth_gspread():
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name("service_account.json", scope)
    client = gspread.authorize(creds)
    return client

def carregar_usuarios():
    return pd.DataFrame({
        'email': ['usuario1@example.com', 'usuario2@example.com'],
        'senha': ['senha1', 'senha2'],
        'id_cliente': [1, 2],
        'nome': ['teste1', 'teste2']
    })

def carregar_dados_planilha():
    url = "https://docs.google.com/spreadsheets/d/1AWjnzKLerxPDzjNviyKe4LfnSzBxpEAnTCszAGro5mw/edit#gid=0"
    client = auth_gspread()
    planilha = client.open_by_url(url)
    aba = planilha.sheet1
    dados = pd.DataFrame(aba.get_all_values()[1:], columns=aba.get_all_values()[0])
    dados = dados[['Dia', 'Impressões', 'Cliques', 'Gasto Plataforma']]
    dados['Dia'] = pd.to_datetime(dados['Dia'])
    dados['Impressões'] = pd.to_numeric(dados['Impressões'], errors='coerce')
    dados['Cliques'] = pd.to_numeric(dados['Cliques'], errors='coerce')
    dados['Gasto Plataforma'] = pd.to_numeric(dados['Gasto Plataforma'], errors='coerce')
    return dados

import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from prophet import Prophet

# Autenticação no Google Sheets
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

def verificar_login(email, senha, usuarios):
    usuario = usuarios[(usuarios['email'] == email) & (usuarios['senha'] == senha)]
    if not usuario.empty:
        st.session_state['email'] = email
        st.session_state['logado'] = True
        st.experimental_rerun()

def fazer_previsoes(dados, metrica):
    df_prophet = pd.DataFrame({
        'ds': dados['Dia'],
        'y': dados[metrica]
    })
    m = Prophet()
    m.fit(df_prophet)
    futuro = m.make_future_dataframe(periods=90)
    previsao = m.predict(futuro)
    return previsao[['ds', 'yhat', 'yhat_lower', 'yhat_upper']]

def mostrar_tela_login():
    st.title("Login")
    usuarios = carregar_usuarios()
    email = st.text_input("Email")
    senha = st.text_input("Senha", type="password")
    if st.button("Entrar"):
        verificar_login(email, senha, usuarios)
        if 'logado' in st.session_state and st.session_state['logado']:
            st.experimental_rerun()
        else:
            st.error("Usuário ou senha inválidos.")

def solicitar_link_planilha():
    st.write("Bem vindo(a),", st.session_state['email'])
    url = st.text_input("Por favor, insira o link da planilha:")
    if url:
        client = auth_gspread()
        try:
            planilha = client.open_by_url(url)
            aba = planilha.sheet1
            dados = pd.DataFrame(aba.get_all_values()[1:], columns=aba.get_all_values()[0])
            st.session_state['dados'] = dados
            st.experimental_rerun()
        except Exception as e:
            st.error(f"Não foi possível abrir a planilha: {e}")

def mostrar_totais(dados):
    st.write("### Totais atuais")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Impressões", dados['Impressões'].sum())
    col2.metric("Cliques", dados['Cliques'].sum())
    col3.metric("Reach", dados['Reach'].sum())
    col4.metric("Gasto Plataforma", f"R$ {dados['Gasto Plataforma'].sum():.2f}")

def mostrar_previsoes(dados):
    st.write("### Previsões")
    metrica = st.selectbox("Escolha a métrica para prever", ['Impressões', 'Cliques', 'Reach', 'Gasto Plataforma'])
    previsoes = fazer_previsoes(dados, metrica)
    st.line_chart(previsoes.set_index('ds'))

def ajustar_gastos(dados):
    st.write("### Ajuste de Gastos")
    novo_gasto = st.slider("Ajustar Gasto (R$)", min_value=0, max_value=2 * dados['Gasto Plataforma'].max(), value=dados['Gasto Plataforma'].mean(), step=0.1)
    st.write(f"Com um novo gasto de R$ {novo_gasto:.2f}, você pode ajustar suas métricas correspondentes.")

def mostrar_tela_principal():
    if 'dados' in st.session_state:
        dados = st.session_state['dados']
        st.sidebar.title("Menu")
        pagina = st.sidebar.radio("Escolha uma página:", ["Totais", "Previsões", "Ajuste de Gastos"])
        if pagina == "Totais":
            mostrar_totais(dados)
        elif pagina == "Previsões":
            mostrar_previsoes(dados)
        elif pagina == "Ajuste de Gastos":
            ajustar_gastos(dados)
    else:
        solicitar_link_planilha()

if 'logado' not in st.session_state or not st.session_state['logado']:
    mostrar_tela_login()
else:
    mostrar_tela_principal()

import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from prophet import Prophet
import altair as alt

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

def fazer_previsoes(dados, metrica, dias_a_prever=90):
    df_prophet = pd.DataFrame({
        'ds': dados['Dia'],
        'y': dados[metrica]
    })
    m = Prophet(yearly_seasonality=True, daily_seasonality=True)
    m.fit(df_prophet)
    futuro = m.make_future_dataframe(periods=dias_a_prever)
    previsao = m.predict(futuro)
    return previsao[['ds', 'yhat', 'yhat_lower', 'yhat_upper']]

def estimar_metrica(dados, novo_gasto, metrica):
    media_ratio = dados[metrica].sum() / dados['Gasto Plataforma'].sum()
    estimativa_metrica = novo_gasto * media_ratio
    return estimativa_metrica

def mostrar_tela_principal():
    st.title(f"Bem vindo(a), {st.session_state['email']}")
    dados = carregar_dados_planilha()

    st.sidebar.title("Menu")
    mostrar_totais = st.sidebar.button("Totais Atuais")
    mostrar_previsoes = st.sidebar.button("Previsões")
    ajustar_gastos = st.sidebar.button("Ajuste de Gastos")

    data_range = st.sidebar.date_input("Selecionar intervalo de datas", value=[dados['Dia'].min(), dados['Dia'].max()], format='DD/MM/YYYY')
    
    if len(data_range) == 2:
        data_inicial, data_final = data_range
        dados_filtrados = dados[(dados['Dia'] >= pd.to_datetime(data_inicial)) & (dados['Dia'] <= pd.to_datetime(data_final))]

        if mostrar_totais:
            st.session_state['pagina_atual'] = 'totais'
        if mostrar_previsoes:
            st.session_state['pagina_atual'] = 'previsoes'
        if ajustar_gastos:
            st.session_state['pagina_atual'] = 'gastos'

        if 'pagina_atual' in st.session_state:
            if st.session_state['pagina_atual'] == 'totais':
                st.write("### Totais atuais")
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Impressões", dados_filtrados['Impressões'].sum())
                col2.metric("Cliques", dados_filtrados['Cliques'].sum())
                col4.metric("Gasto", f"R$ {dados_filtrados['Gasto Plataforma'].sum():.2f}")
                st.line_chart(dados_filtrados.set_index('Dia')[['Impressões', 'Cliques', 'Gasto Plataforma']])
            elif st.session_state['pagina_atual'] == 'previsoes':
                metrica = st.selectbox("Escolha a métrica para visualizar no gráfico", ['Impressões', 'Cliques', 'Gasto Plataforma'])
                previsoes = fazer_previsoes(dados_filtrados, metrica)
                dados_grafico = pd.concat([
                    pd.DataFrame({
                        'data': dados_filtrados['Dia'],
                        'valor': dados_filtrados[metrica],
                        'tipo': 'Histórico'
                    }),
                    pd.DataFrame({
                        'data': previsoes['ds'],
                        'valor': previsoes['yhat'],
                        'tipo': 'Previsão'
                    })
                ])
                chart = alt.Chart(dados_grafico).mark_line().encode(
                    x='data:T',
                    y='valor:Q',
                    color='tipo:N',
                    tooltip=['data:T', 'valor:Q', 'tipo:N']
                ).interactive()
                st.altair_chart(chart, use_container_width=True)
            elif st.session_state['pagina_atual'] == 'gastos':
                st.write("### Ajuste de Gastos e Estimativa de Resultados")
                novo_gasto = st.slider("Ajustar Gasto (R$)", min_value=dados['Gasto Plataforma'].sum(), max_value=2 * dados['Gasto Plataforma'].sum(), value=dados['Gasto Plataforma'].sum(), step=0.1)
                if novo_gasto != dados['Gasto Plataforma'].sum():
                    estimativa_impressoes = estimar_metrica(dados, novo_gasto, 'Impressões')
                    estimativa_cliques = estimar_metrica(dados, novo_gasto, 'Cliques')
                    st.write(f"Com um novo gasto de R$ {novo_gasto:.2f}, estima-se aproximadamente {int(estimativa_impressoes)} impressões, {int(estimativa_cliques)} cliques")

if 'logado' not in st.session_state or not st.session_state['logado']:
    mostrar_tela_login()
else:
    mostrar_tela_principal()

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from prophet import Prophet



# Simula a função de carregar os dados do usuário (substitua pela sua lógica de banco de dados)
def carregar_usuarios():
    usuarios = pd.DataFrame({
        'email': ['usuario1@example.com', 'usuario2@example.com'],
        'senha': ['senha1', 'senha2'],
        'id_cliente': [1, 2],
        'nome' : ['teste1', 'teste2']
    })
    return usuarios

# Simula a função de verificar login
def verificar_login(email, senha, usuarios):
    usuario = usuarios[(usuarios['email'] == email) & (usuarios['senha'] == senha)]
    if not usuario.empty:
        st.session_state['email'] = email
        st.session_state['id_cliente'] = usuario['id_cliente'].values[0]
        st.session_state['logado'] = True



# Simula a função de carregar dados de atividades (substitua pela sua lógica real)
def carregar_dados_atividade(id_cliente):
    dados = pd.DataFrame({
        'id_cliente' : ['1', '1','1', '1','1'],
        'nome_do_usuario': ['usuario1', 'usuario1','usuario1', 'usuario1','usuario1'],
        'data': pd.to_datetime(['2023-03-25', '2023-03-26', '2023-03-27', '2023-03-28', '2023-03-29']),
        'impressoes': [5539, 74780,68888,63877,19155],
        'cliques': [78,2736,4094,4709,1310],
        'gasto': [88.9,641.44,633.01,577.51,184.3],
        'registros': [2,7,5,12,2]
    })
    return dados

# Função para renderizar a tela de login
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

def fazer_previsoes(dados, metrica):
    # Preparando os dados para o Prophet
    df_prophet = pd.DataFrame({
        'ds': dados['data'],
        'y': dados[metrica]
    })
    
    # Inicializando e ajustando o modelo
    m = Prophet(yearly_seasonality=True, daily_seasonality=True)
    m.fit(df_prophet)
    
    # Criando um dataframe para o futuro
    futuro = m.make_future_dataframe(periods=90)  # 3 meses
    
    # Fazendo as previsões
    previsao = m.predict(futuro)
    
    return previsao[['ds', 'yhat', 'yhat_lower', 'yhat_upper']]



def mostrar_tela_principal():
    st.title(f"Bem vindo(a), {st.session_state['email']}")

    dados = carregar_dados_atividade(st.session_state['id_cliente'])

    # KPIs alinhados horizontalmente
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Impressões", dados['impressoes'].sum())
    col2.metric("Cliques", dados['cliques'].sum())
    col3.metric("Registros", dados['registros'].sum())
    col4.metric("Gasto", f"R$ {dados['gasto'].sum():.2f}")

    # Seletor para métrica do gráfico de linha
    metrica = st.selectbox("Escolha a métrica para visualizar no gráfico", ['impressoes', 'cliques', 'registros', 'gasto'])
    
    # Previsões
    previsoes = fazer_previsoes(dados, metrica)
    
    
    # Plotando os resultados históricos e as previsões
    fig, ax = plt.subplots()
    ax.plot(dados['data'], dados[metrica], label='Histórico')
    ax.plot(previsoes['ds'], previsoes['yhat'], label='Previsão', linestyle='--')
    ax.fill_between(previsoes['ds'], previsoes['yhat_lower'], previsoes['yhat_upper'], alpha=0.3)
    ax.set_title(f'{metrica.capitalize()} ao longo do tempo com previsões')
    ax.set_xlabel('Data')
    ax.set_ylabel(metrica.capitalize())
    ax.legend()
    plt.xticks(rotation=45)
    st.pyplot(fig)

    # Criação do gráfico de barra para Gasto x Data
    fig, ax = plt.subplots()
    ax.bar(dados['data'], dados['gasto'], color='lightgreen')
    ax.set_title('Gasto ao longo do tempo')
    ax.set_xlabel('Data')
    ax.set_ylabel('Gasto')
    ax.grid(True)
    plt.xticks(rotation=45)
    st.pyplot(fig)

    if st.button("Sair"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.experimental_rerun()

# Verifica o estado do login para decidir qual tela mostrar
if 'logado' not in st.session_state or not st.session_state['logado']:
    mostrar_tela_login()
else:
    mostrar_tela_principal()

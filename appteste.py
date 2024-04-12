import streamlit as st
import pandas as pd
from prophet import Prophet
import matplotlib.pyplot as plt
import altair as alt


def carregar_usuarios():
    return pd.DataFrame({
        'email': ['usuario1@example.com', 'usuario2@example.com'],
        'senha': ['senha1', 'senha2'],
        'id_cliente': [1, 2],
        'nome' : ['teste1', 'teste2']
    })

def verificar_login(email, senha, usuarios):
    usuario = usuarios[(usuarios['email'] == email) & (usuarios['senha'] == senha)]
    if not usuario.empty:
        st.session_state['email'] = email
        st.session_state['id_cliente'] = usuario['id_cliente'].values[0]
        st.session_state['logado'] = True



def carregar_dados_atividade(id_cliente):
    return pd.DataFrame({
        'id_cliente': [id_cliente] * 10,
        'nome_do_usuario': ['usuario1'] * 10,
        'data': pd.to_datetime(['2023-03-25', '2023-03-26', '2023-03-27', '2023-03-28', '2023-03-29', '2023-03-30', '2023-03-31','2023-04-01','2023-04-02', '2023-04-03']),
        'impressoes': [5539, 74780, 68888, 63877, 19155, 90000, 99843, 23413, 47323, 13452],
        'cliques': [78, 2736, 4094, 4709, 1310, 23,5436,7546,2456,1345],
        'gasto': [88.9, 641.44, 633.01, 577.51, 184.3, 123.4, 234.5,765.4,423.1, 123.5],
        'registros': [2, 7, 5, 12, 2,21,2,4,5,6]
    })

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

def fazer_previsoes(dados, metrica, dias_a_prever=90):
    df_prophet = pd.DataFrame({
        'ds': dados['data'],
        'y': dados[metrica]
    })
    m = Prophet(yearly_seasonality=True, daily_seasonality=True)
    m.fit(df_prophet)
    futuro = m.make_future_dataframe(periods=dias_a_prever)
    previsao = m.predict(futuro)
    return previsao[['ds', 'yhat', 'yhat_lower', 'yhat_upper']]

def estimar_metrica(dados, novo_gasto, metrica):
    media_ratio = dados[metrica].sum() / dados['gasto'].sum()
    estimativa_metrica = novo_gasto * media_ratio
    return estimativa_metrica

def mostrar_tela_principal():
    st.title(f"Bem vindo(a), {st.session_state['email']}")
    dados = carregar_dados_atividade(st.session_state['id_cliente'])

    # Barra lateral com botões para navegação
    st.sidebar.title("Menu")
    mostrar_totais = st.sidebar.button("Totais Atuais")
    mostrar_previsoes = st.sidebar.button("Previsões")
    ajustar_gastos = st.sidebar.button("Ajuste de Gastos")

    # Data Selector na barra lateral
    data_range = st.sidebar.date_input(
        "Selecionar intervalo de datas",
        value=[dados['data'].min(), dados['data'].max()],
        format='DD/MM/YYYY'
    )

    # Verificar se duas datas foram selecionadas
    if len(data_range) == 2:
        data_inicial, data_final = data_range
    else:
        st.sidebar.error("Selecione um intervalo de datas.")
        return

    # Filtrando dados pelo intervalo de datas
    dados_filtrados = dados[(dados['data'] >= pd.to_datetime(data_inicial)) & (dados['data'] <= pd.to_datetime(data_final))]

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
            col1.metric("Impressões", dados_filtrados['impressoes'].sum())
            col2.metric("Cliques", dados_filtrados['cliques'].sum())
            col3.metric("Registros", dados_filtrados['registros'].sum())
            col4.metric("Gasto", f"R$ {dados_filtrados['gasto'].sum():.2f}")

            # Gráficos padrão do Streamlit
            st.line_chart(dados_filtrados.set_index('data')[['impressoes', 'cliques', 'registros', 'gasto']])


        elif st.session_state['pagina_atual'] == 'previsoes':
            metrica = st.selectbox("Escolha a métrica para visualizar no gráfico", ['impressoes', 'cliques', 'registros', 'gasto'])
            previsoes = fazer_previsoes(dados_filtrados, metrica)
            dados_grafico = pd.concat([
                pd.DataFrame({
                    'data': dados_filtrados['data'],
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
            novo_gasto = st.slider("Ajustar Gasto (R$)", min_value=dados['gasto'].sum(), max_value=2 * dados['gasto'].sum(), value=dados['gasto'].sum(), step=0.1)
            if novo_gasto != dados['gasto'].sum():
                estimativa_impressoes = estimar_metrica(dados, novo_gasto, 'impressoes')
                estimativa_cliques = estimar_metrica(dados, novo_gasto, 'cliques')
                estimativa_registros = estimar_metrica(dados, novo_gasto, 'registros')
                st.write(f"Com um novo gasto de R$ {novo_gasto:.2f}, estima-se aproximadamente {int(estimativa_impressoes)} impressões, {int(estimativa_cliques)} cliques e {int(estimativa_registros)} registros")
            
if 'logado' not in st.session_state or not st.session_state['logado']:
    mostrar_tela_login()
else:
    mostrar_tela_principal()
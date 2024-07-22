import streamlit as st
import pandas as pd
import altair as alt
from prophet import Prophet
from utils import carregar_dados_planilha

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

def mostrar_previsoes():
    dados = carregar_dados_planilha()
    data_range = st.sidebar.date_input("Selecionar intervalo de datas", value=[dados['Dia'].min(), dados['Dia'].max()], format='DD/MM/YYYY')
    data_inicial, data_final = data_range
    dados_filtrados = dados[(dados['Dia'] >= pd.to_datetime(data_inicial)) & (dados['Dia'] <= pd.to_datetime(data_final))]

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

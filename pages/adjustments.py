import streamlit as st
import pandas as pd
from utils import carregar_dados_planilha

def estimar_metrica(dados, novo_gasto, metrica):
    media_ratio = dados[metrica].sum() / dados['Gasto Plataforma'].sum()
    estimativa_metrica = novo_gasto * media_ratio
    return estimativa_metrica

def mostrar_ajuste_de_gastos():
    dados = carregar_dados_planilha()
    data_range = st.sidebar.date_input("Selecionar intervalo de datas", value=[dados['Dia'].min(), dados['Dia'].max()], format='DD/MM/YYYY')
    data_inicial, data_final = data_range
    dados_filtrados = dados[(dados['Dia'] >= pd.to_datetime(data_inicial)) & (dados['Dia'] <= pd.to_datetime(data_final))]

    st.write("### Ajuste de Gastos e Estimativa de Resultados")
    novo_gasto = st.slider("Ajustar Gasto (R$)", min_value=dados['Gasto Plataforma'].sum(), max_value=2 * dados['Gasto Plataforma'].sum(), value=dados['Gasto Plataforma'].sum(), step=0.1)
    if novo_gasto != dados['Gasto Plataforma'].sum():
        estimativa_impressoes = estimar_metrica(dados, novo_gasto, 'Impressões')
        estimativa_cliques = estimar_metrica(dados, novo_gasto, 'Cliques')
        st.write(f"Com um novo gasto de R$ {novo_gasto:.2f}, estima-se aproximadamente {int(estimativa_impressoes)} impressões, {int(estimativa_cliques)} cliques")

import streamlit as st
import pandas as pd
from utils import carregar_dados_planilha

def mostrar_totais():
    dados = carregar_dados_planilha()
    data_range = st.sidebar.date_input("Selecionar intervalo de datas", value=[dados['Dia'].min(), dados['Dia'].max()], format='DD/MM/YYYY')
    data_inicial, data_final = data_range
    dados_filtrados = dados[(dados['Dia'] >= pd.to_datetime(data_inicial)) & (dados['Dia'] <= pd.to_datetime(data_final))]

    st.write("### Totais atuais")
    
    # Ajustar as colunas para o layout desejado
    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        st.metric("Impressões", dados_filtrados['Impressões'].sum())
        st.metric("Cliques", dados_filtrados['Cliques'].sum())
        st.metric("Gasto", f"R$ {dados_filtrados['Gasto Plataforma'].sum():.2f}")

    with col2:
        with st.container():
            st.line_chart(dados_filtrados.set_index('Dia')[['Impressões', 'Cliques', 'Gasto Plataforma']], use_container_width=True)

    with col3:
        with st.container():
            st.write("### Gráficos de Barras")
            st.bar_chart(dados_filtrados.set_index('Dia')['Impressões'], use_container_width=True)
            st.bar_chart(dados_filtrados.set_index('Dia')['Cliques'], use_container_width=True)
            st.bar_chart(dados_filtrados.set_index('Dia')['Gasto Plataforma'], use_container_width=True)

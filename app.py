import streamlit as st
import pandas as pd

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

# Função para renderizar a tela após o login
def mostrar_tela_principal():
    st.title(f"Bem vindo(a), {st.session_state['email']}")
    
    dados = carregar_dados_atividade(st.session_state['id_cliente'])
    st.metric("Impressões", dados['impressoes'].sum())
    st.metric("Cliques", dados['cliques'].sum())
    st.metric("Registros", dados['registros'].sum())
    st.metric("Gasto", f"R$ {dados['gasto'].sum():.2f}")
    st.line_chart(dados.set_index('data')['impressoes'])

    if st.button("Sair"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.experimental_rerun()

# Verifica o estado do login para decidir qual tela mostrar
if 'logado' not in st.session_state or not st.session_state['logado']:
    mostrar_tela_login()
else:
    mostrar_tela_principal()

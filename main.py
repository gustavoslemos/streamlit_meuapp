import streamlit as st
from utils import carregar_usuarios

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

def verificar_login(email, senha, usuarios):
    usuario = usuarios[(usuarios['email'] == email) & (usuarios['senha'] == senha)]
    if not usuario.empty:
        st.session_state['email'] = email
        st.session_state['logado'] = True
        st.experimental_rerun()

def main():
    if 'logado' not in st.session_state or not st.session_state['logado']:
        mostrar_tela_login()
    else:
        st.title(f"Bem vindo(a), {st.session_state['email']}")
        st.sidebar.title("Menu")
        if st.sidebar.button("Totais Atuais"):
            st.session_state['pagina'] = "Totais Atuais"
        if st.sidebar.button("Previsões"):
            st.session_state['pagina'] = "Previsões"
        if st.sidebar.button("Ajuste de Gastos"):
            st.session_state['pagina'] = "Ajuste de Gastos"
        
        pagina = st.session_state.get('pagina', "Totais Atuais")
        if pagina == "Totais Atuais":
            from pages import totals
            totals.mostrar_totais()
        elif pagina == "Previsões":
            from pages import forecasts
            forecasts.mostrar_previsoes()
        elif pagina == "Ajuste de Gastos":
            from pages import adjustments
            adjustments.mostrar_ajuste_de_gastos()

if __name__ == "__main__":
    main()

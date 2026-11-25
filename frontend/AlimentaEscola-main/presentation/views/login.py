

from pathlib import Path

import requests
import streamlit as st

from infrastructure.api import auth_api


BASE_DIR = Path(__file__).resolve().parents[2]
LOGO = BASE_DIR / "assets" / "logo_alimenta_escola.png"


def mostrar_login():
    st.markdown("### Acesse sua conta")

    st.markdown(
        "Entre com seus dados para acessar o AlimentaEscola."
    )

    with st.form("form_login"):
        email = st.text_input(
            "E-mail",
            placeholder="Digite seu e-mail"
        )

        senha = st.text_input(
            "Senha",
            placeholder="Digite sua senha",
            type="password"
        )

        entrar = st.form_submit_button(
            "Entrar",
            width="stretch"
        )

    if entrar:
        if not email.strip() or not senha:
            st.warning("Preencha todos os campos.")
            return

        try:
            resposta = auth_api.login(
                email.strip(),
                senha
            )

            if resposta.status_code == 200:
                usuario = auth_api.usuario_atual()

                if usuario.status_code != 200:
                    st.error("Não foi possível validar a sessão.")
                    return

                st.session_state["autenticado"] = True
                st.session_state["modo_demonstracao"] = False
                st.session_state["usuario"] = usuario.json()
                st.session_state["pagina_atual"] = "Visão geral"

                st.rerun()

            elif resposta.status_code == 401:
                st.error("E-mail ou senha inválidos.")

            else:
                st.error(
                    f"Não foi possível entrar. "
                    f"Código: {resposta.status_code}"
                )

        except requests.exceptions.RequestException:
            st.error(
                "Não foi possível conectar ao servidor. "
                "Verifique se o backend está funcionando."
            )

    st.caption(
        "O cadastro do gestor é realizado pelo administrador "
        "responsável pela instalação do sistema."
    )


def render():
    _, coluna, _ = st.columns([1, 1.5, 1])

    with coluna:
        if LOGO.exists():
            _, centro, _ = st.columns([1, 1, 1])

            with centro:
                st.image(str(LOGO), width=220)

        mostrar_login()
        aviso = st.session_state.pop("aviso_logout", None)

    if aviso:
        st.warning(aviso)

    st.markdown(
        """
        <div style="text-align:center; color:#8b9bb1;
                    font-size:12px; padding:30px 0 10px;">
            AlimentaEscola · Protótipo acadêmico
        </div>
        """,
        unsafe_allow_html=True
    )


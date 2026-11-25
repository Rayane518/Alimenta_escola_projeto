
from pathlib import Path

import requests
import streamlit as st

from infrastructure.api import auth_api

BASE_DIR = Path(__file__).resolve().parent.parent
LOGO = BASE_DIR / "assets" / "logo_alimenta_escola.png"


PAGINAS_CADASTRO = {
    "Cardápios": ("Cadastro de cardápios", ":material/restaurant:"),
    "Turmas": ("Cadastro de turmas", ":material/groups:"),
}

PAGINAS_PRINCIPAIS = {
    "Gerar previsões": ("Gerar previsões", ":material/psychology:"),
    "Histórico": ("Histórico de previsões", ":material/history:"),
    "Indicadores": ("Indicadores", ":material/monitoring:"),
    "Sobre o projeto": ("Sobre o projeto", ":material/info:"),
}


def selecionar_pagina(pagina):
    st.session_state["pagina_atual"] = pagina

    paginas_cadastro = [
        destino for destino, icone in PAGINAS_CADASTRO.values()
    ]

    st.session_state["cadastros_aberto"] = pagina in paginas_cadastro


def alternar_cadastros():
    st.session_state["cadastros_aberto"] = not st.session_state.get(
        "cadastros_aberto",
        False,
    )


def logout():
    encerrado_no_backend = False

    try:
        resposta = auth_api.logout()
        encerrado_no_backend = resposta.status_code == 200

    except requests.exceptions.RequestException:
        pass

    finally:
        cliente = st.session_state.get("api_client")

        if cliente is not None:
            cliente.session.cookies.clear()
            cliente.close()

        st.session_state.clear()

        st.session_state["autenticado"] = False
        st.session_state["tela_login"] = "login"

        if not encerrado_no_backend:
            st.session_state["aviso_logout"] = (
                "Sessão local encerrada, mas não foi possível "
                "confirmar o logout no servidor."
            )



def aplicar_estilos_sidebar():
    st.markdown(
        """
        <style>
        [data-testid="stSidebar"] .stButton > button {
            display: flex;
            align-items: center;
            justify-content: flex-start;
            width: 100%;
            min-height: 44px;
            padding: 8px 13px;
            border-radius: 10px;
            text-align: left;
            font-size: 13px;
            font-weight: 600;
        }

        [data-testid="stSidebar"] .stButton > button > div {
            width: 100%;
            justify-content: flex-start;
        }

        [data-testid="stSidebar"] .stButton > button p {
            text-align: left;
        }

        [data-testid="stSidebar"] .stButton > button[kind="secondary"] {
            background: transparent;
            border: 1px solid transparent;
            color: #f5f8ff;
        }

        [data-testid="stSidebar"] .stButton > button[kind="secondary"]:hover {
            background: rgba(53, 112, 225, .25);
            border-color: rgba(125, 170, 255, .35);
        }

        [data-testid="stSidebar"] .stButton > button[kind="primary"] {
            background: linear-gradient(100deg, #2865d9, #1c4fae);
            border: 1px solid #6094f4;
            color: #ffffff;
        }

        [data-testid="stSidebar"] .st-key-menu_cadastros button {
            position: relative;
            padding-right: 35px;
        }

        [data-testid="stSidebar"] .st-key-menu_cadastros button::after {
            content: "▾";
            position: absolute;
            right: 14px;
            font-size: 15px;
            color: #a9c8ff;
        }

        [data-testid="stSidebar"] .st-key-menu_cadastros button:hover::after {
            color: #ffffff;
        }

        [data-testid="stSidebar"] .st-key-grupo_cadastros {
            background: rgba(76, 132, 207, .20);
            border: 1px solid rgba(150, 190, 245, .10);
            border-radius: 10px;
            padding: 8px;
            margin-top: 5px;
            margin-bottom: 8px;
        }

        [data-testid="stSidebar"] .st-key-grupo_cadastros .stButton > button {
            background: transparent;
            border: 1px solid transparent;
            border-radius: 8px;
            margin-bottom: 5px;
        }

        [data-testid="stSidebar"] .st-key-grupo_cadastros .stButton > button:hover {
            background: rgba(76, 132, 207, .38);
            border-color: rgba(150, 190, 245, .30);
        }

        [data-testid="stSidebar"] .st-key-grupo_cadastros .stButton > button[kind="primary"] {
            background: #2865d9;
            border-color: #6094f4;
        }

        .sidebar-menu-title {
            color: #91b7ff;
            font-size: 11px;
            font-weight: 800;
            letter-spacing: 2px;
            margin: 12px 0 14px 5px;
        }

        .sidebar-footer {
            padding-top: 15px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar():
    aplicar_estilos_sidebar()

    if "pagina_atual" not in st.session_state:
        st.session_state["pagina_atual"] = "Visão geral"

    if "cadastros_aberto" not in st.session_state:
        st.session_state["cadastros_aberto"] = (
            st.session_state["pagina_atual"]
            in [
                destino
                for destino, icone in PAGINAS_CADASTRO.values()
            ]
        )

    pagina_atual = st.session_state["pagina_atual"]

    with st.sidebar:
        if LOGO.exists():
            st.image(str(LOGO), width=95)

        st.markdown(
            '<div class="side-divider"></div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            '<div class="sidebar-menu-title">MENU</div>',
            unsafe_allow_html=True,
        )

        st.button(
            "Visão geral",
            key="menu_visao_geral",
            icon=":material/dashboard:",
            width="stretch",
            type="primary" if pagina_atual == "Visão geral" else "secondary",
            on_click=selecionar_pagina,
            args=("Visão geral",),
        )

        st.button(
            "Minha escola",
            key="menu_minha_escola",
            icon=":material/school:",
            width="stretch",
            type="primary" if pagina_atual == "Minha escola" else "secondary",
            on_click=selecionar_pagina,
            args=("Minha escola",),
        )

        st.button(
            "Cadastros",
            key="menu_cadastros",
            icon=":material/folder:",
            width="stretch",
            type="secondary",
            on_click=alternar_cadastros,
        )

        if st.session_state["cadastros_aberto"]:
            with st.container(key="grupo_cadastros"):
                for nome, (destino, icone) in PAGINAS_CADASTRO.items():
                    st.button(
                        nome,
                        key=f"menu_{destino}",
                        icon=icone,
                        width="stretch",
                        type="primary" if pagina_atual == destino else "secondary",
                        on_click=selecionar_pagina,
                        args=(destino,),
                    )

        for nome, (destino, icone) in PAGINAS_PRINCIPAIS.items():
            st.button(
                nome,
                key=f"menu_{destino}",
                icon=icone,
                width="stretch",
                type="primary" if pagina_atual == destino else "secondary",
                on_click=selecionar_pagina,
                args=(destino,),
            )

        st.markdown(
            '<div class="sidebar-footer"></div>',
            unsafe_allow_html=True,
        )

        st.divider()

        st.button(
            "Sair",
            key="botao_sair",
            icon=":material/logout:",
            width="stretch",
            on_click=logout,
        )

    return st.session_state["pagina_atual"]

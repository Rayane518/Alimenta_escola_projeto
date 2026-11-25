
from pathlib import Path

import streamlit as st

from presentation import sidebar
from presentation.views import about, classes, demand, history, indicators, login, meals, menus, overview, predictions, schools


BASE_DIR = Path(__file__).resolve().parent.parent
CSS_FILE = BASE_DIR / "presentation" / "styles" / "main.css"


def load_styles():
    if CSS_FILE.exists():
        css = CSS_FILE.read_text(encoding="utf-8")
        st.markdown(
            f"<style>{css}</style>",
            unsafe_allow_html=True,
        )

    st.markdown(
        """
        <style>
        [data-testid="stSidebar"] .stButton > button {
            width: 100%;
            min-height: 44px;
            justify-content: flex-start;
            text-align: left;
            padding: 8px 13px;
            border-radius: 10px;
            font-size: 13px;
            font-weight: 600;
            box-shadow: none;
            transition: all .2s ease;
        }

        [data-testid="stSidebar"] .stButton > button[kind="secondary"] {
            background: transparent;
            border: 1px solid transparent;
            color: #f5f8ff;
        }

        [data-testid="stSidebar"] .stButton > button[kind="secondary"]:hover {
            background: rgba(53, 112, 225, .25);
            border-color: rgba(125, 170, 255, .35);
            color: #ffffff;
        }

        [data-testid="stSidebar"] .stButton > button[kind="primary"] {
            background: linear-gradient(100deg, #2865d9, #1c4fae);
            border: 1px solid #6094f4;
            color: #ffffff;
        }

        [data-testid="stSidebar"] [data-testid="stExpander"] {
            border: 1px solid rgba(255, 255, 255, .12);
            border-radius: 10px;
            background: rgba(255, 255, 255, .035);
        }

        [data-testid="stSidebar"] [data-testid="stExpander"] summary {
            font-weight: 700;
            font-size: 13px;
        }

        [data-testid="stSidebar"] [data-testid="stExpander"] .stButton {
            margin-bottom: 5px;
        }

        [data-testid="stSidebar"] [data-testid="stExpander"] details {
            border: none;
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


def render_page(pagina):
    paginas_existentes = {
        "Visão geral": overview.render,
        "Minha escola": schools.render,
        "Cadastro de turmas": classes.render,
        "Cadastro de cardápios": menus.render,
        "Gestão de refeições": meals.render,
        "Gerar previsões": predictions.render,
        "Demanda de refeições": predictions.render,
        "Histórico de previsões": history.render,
        "Indicadores": indicators.render,
        "Sobre o projeto": about.render,
    }

    if pagina in paginas_existentes:
        paginas_existentes[pagina]()
        return

    st.title(pagina)

    st.info(
        "Esta funcionalidade está em desenvolvimento. "
        "Ela será implementada nas próximas etapas do projeto."
    )


def main():
    st.set_page_config(
        page_title="AlimentaEscola",
        page_icon="🍃",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    load_styles()

    if not st.session_state.get("autenticado", False):
        st.session_state["autenticado"] = False
        st.session_state["tela_login"] = st.session_state.get(
            "tela_login",
            "login",
        )

        st.markdown(
            """
            <style>
                [data-testid="stSidebar"] {
                    display: none;
                }
            </style>
            """,
            unsafe_allow_html=True,
        )

        login.render()
        return

    pagina = sidebar.render_sidebar()
    render_page(pagina)

    st.markdown(
        """
        <div style="
            text-align: center;
            color: #8b9bb1;
            font-size: 12px;
            padding: 30px 0 10px;
        ">
            AlimentaEscola
        </div>
        """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()

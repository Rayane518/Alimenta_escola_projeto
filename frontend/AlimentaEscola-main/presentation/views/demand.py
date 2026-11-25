
from datetime import date

import streamlit as st


def limpar_previsao():
    st.session_state["demanda_data"] = date.today()
    st.session_state["demanda_turno"] = "Selecione"
    st.session_state["demanda_evento"] = "Não"
    st.session_state["demanda_solicitacao_atual"] = None


def render():
    st.session_state.setdefault("demanda_data", date.today())
    st.session_state.setdefault("demanda_turno", "Selecione")
    st.session_state.setdefault("demanda_evento", "Não")
    st.session_state.setdefault("demanda_solicitacao_atual", None)

    st.markdown(
        '<div class="eyebrow">PLANEJAMENTO INTELIGENTE</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<h1 class="hero-title">Gerar previsões</h1>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="hero-subtitle">'
        'Informe a data e o turno para estimar a presença dos alunos '
        'e planejar a quantidade de refeições.'
        '</div>',
        unsafe_allow_html=True,
    )

    with st.form("demanda_form"):
        data_previsao = st.date_input(
            "Data da previsão",
            key="demanda_data",
        )

        turno = st.selectbox(
            "Turno",
            ["Selecione", "Manhã", "Tarde", "Integral"],
            key="demanda_turno",
        )

        evento = st.selectbox(
            "Haverá evento ou atividade especial?",
            ["Não", "Sim"],
            key="demanda_evento",
        )

        st.caption(
            "A quantidade de alunos será estimada automaticamente "
            "pelo modelo de Machine Learning."
        )

        col1, col2 = st.columns(2)

        with col1:
            enviar = st.form_submit_button(
                "Gerar previsão",
                width="stretch",
                type="primary",
            )

        with col2:
            st.form_submit_button(
                "Limpar previsão",
                width="stretch",
                on_click=limpar_previsao,
            )

    if enviar:
        if turno == "Selecione":
            st.error("Selecione o turno para continuar.")
            st.session_state["demanda_solicitacao_atual"] = None
        else:
            st.session_state["demanda_solicitacao_atual"] = {
                "Data": data_previsao,
                "Turno": turno,
                "Atividade especial": evento,
            }

    solicitacao = st.session_state.get(
        "demanda_solicitacao_atual"
    )

    if solicitacao:
        st.markdown(
            '<div class="section-title">Resumo da solicitação</div>',
            unsafe_allow_html=True,
        )

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "Data selecionada",
                solicitacao["Data"].strftime("%d/%m/%Y"),
            )

        with col2:
            st.metric(
                "Turno",
                solicitacao["Turno"],
            )

        with col3:
            st.metric(
                "Atividade especial",
                solicitacao["Atividade especial"],
            )

        st.info(
            "Solicitação preparada. A quantidade estimada de alunos "
            "e a recomendação de refeições serão exibidas após a "
            "integração com o modelo de Machine Learning."
        )

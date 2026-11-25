
import pandas as pd
import streamlit as st


def limpar_filtros(data_minima, data_maxima):
    st.session_state["historico_data_inicial"] = data_minima
    st.session_state["historico_data_final"] = data_maxima
    st.session_state["historico_dia"] = "Todos"
    st.session_state["historico_situacao"] = "Todas"


def limpar_historico():
    st.session_state["historico_previsoes"] = []
    st.session_state["confirmar_limpeza_historico"] = False


def solicitar_limpeza_historico():
    st.session_state["confirmar_limpeza_historico"] = True


def cancelar_limpeza_historico():
    st.session_state["confirmar_limpeza_historico"] = False


def render():
    st.markdown(
        '<div class="eyebrow">ACOMPANHAMENTO</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<h1 class="hero-title">Hist├│rico de previs├Áes</h1>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="hero-subtitle">'
        'Consulte e filtre as solicita├º├Áes de estimativa realizadas no sistema.'
        '</div>',
        unsafe_allow_html=True,
    )

    historico = st.session_state.get("historico_previsoes", [])

    if not historico:
        st.info(
            "Nenhuma solicita├º├úo registrada ainda. "
            "Acesse Demanda de refei├º├Áes para preparar uma solicita├º├úo."
        )
        return

    df = pd.DataFrame(historico)

    df["_data"] = pd.to_datetime(
        df["Data e hor├írio"],
        format="%d/%m/%Y %H:%M",
        errors="coerce",
    ).dt.date

    datas_validas = df["_data"].dropna()

    if datas_validas.empty:
        st.warning("N├úo existem datas v├ílidas para consulta.")
        return

    data_minima = min(datas_validas)
    data_maxima = max(datas_validas)

    dias = ["Todos"] + sorted(
        df["Dia da semana"].dropna().unique().tolist()
    )

    situacoes = ["Todas"] + sorted(
        df["Situa├º├úo"].dropna().unique().tolist()
    )

    st.session_state.setdefault("historico_data_inicial", data_minima)
    st.session_state.setdefault("historico_data_final", data_maxima)
    st.session_state.setdefault("historico_dia", "Todos")
    st.session_state.setdefault("historico_situacao", "Todas")

    st.markdown(
        '<div class="section-title">Filtros de consulta</div>',
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)

    with col1:
        data_inicial = st.date_input(
            "Data inicial",
            key="historico_data_inicial",
        )

    with col2:
        data_final = st.date_input(
            "Data final",
            key="historico_data_final",
        )

    col3, col4 = st.columns(2)

    with col3:
        dia_selecionado = st.selectbox(
            "Dia da semana",
            dias,
            key="historico_dia",
        )

    with col4:
        situacao_selecionada = st.selectbox(
            "Situa├º├úo",
            situacoes,
            key="historico_situacao",
        )

    col5, col6 = st.columns(2)

    with col5:
        st.button(
            "Limpar filtros",
            on_click=limpar_filtros,
            args=(data_minima, data_maxima),
            width="stretch",
        )

    with col6:
        st.button(
            "Limpar hist├│rico",
            on_click=solicitar_limpeza_historico,
            width="stretch",
            type="secondary",
        )

    if st.session_state.get("confirmar_limpeza_historico", False):
        st.warning(
            "Tem certeza de que deseja apagar todas as solicita├º├Áes "
            "registradas? Essa a├º├úo n├úo poder├í ser desfeita."
        )

        confirmar, cancelar = st.columns(2)

        with confirmar:
            st.button(
                "Sim, apagar hist├│rico",
                on_click=limpar_historico,
                width="stretch",
                type="primary",
            )

        with cancelar:
            st.button(
                "Cancelar",
                on_click=cancelar_limpeza_historico,
                width="stretch",
            )

    if data_inicial > data_final:
        st.error("A data inicial n├úo pode ser posterior ├á data final.")
        return

    filtrado = df[
        (df["_data"] >= data_inicial)
        & (df["_data"] <= data_final)
    ]

    if dia_selecionado != "Todos":
        filtrado = filtrado[
            filtrado["Dia da semana"] == dia_selecionado
        ]

    if situacao_selecionada != "Todas":
        filtrado = filtrado[
            filtrado["Situa├º├úo"] == situacao_selecionada
        ]

    st.divider()

    st.metric(
        "Solicita├º├Áes encontradas",
        len(filtrado),
    )

    st.markdown(
        '<div class="section-title">Solicita├º├Áes registradas</div>',
        unsafe_allow_html=True,
    )

    if filtrado.empty:
        st.warning("Nenhuma solicita├º├úo encontrada com esses filtros.")
        return

    colunas = [
        "Data e hor├írio",
        "Alunos previstos",
        "Dia da semana",
        "Atividade especial",
        "Situa├º├úo",
    ]

    st.dataframe(
        filtrado[colunas],
        width="stretch",
        hide_index=True,
    )

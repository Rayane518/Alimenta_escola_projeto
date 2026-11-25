
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
        '<h1 class="hero-title">Histórico de previsões</h1>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="hero-subtitle">'
        'Consulte e filtre as solicitações de estimativa realizadas no sistema.'
        '</div>',
        unsafe_allow_html=True,
    )

    historico = st.session_state.get("historico_previsoes", [])

    if not historico:
        st.info(
            "Nenhuma solicitação registrada ainda. "
            "Acesse Gerar previsões para preparar uma solicitação."
        )
        return

    df = pd.DataFrame(historico)

    colunas_necessarias = [
        "Data e horário",
        "Alunos previstos",
        "Dia da semana",
        "Atividade especial",
        "Situação",
    ]

    if not all(coluna in df.columns for coluna in colunas_necessarias):
        st.error(
            "Os registros encontrados possuem uma estrutura diferente "
            "da esperada pelo histórico."
        )
        return

    df["_data"] = pd.to_datetime(
        df["Data e horário"],
        format="%d/%m/%Y %H:%M",
        errors="coerce",
    ).dt.date

    datas_validas = df["_data"].dropna()

    if datas_validas.empty:
        st.warning("Não existem datas válidas para consulta.")
        return

    data_minima = min(datas_validas)
    data_maxima = max(datas_validas)

    dias = ["Todos"] + sorted(
        df["Dia da semana"].dropna().unique().tolist()
    )

    situacoes = ["Todas"] + sorted(
        df["Situação"].dropna().unique().tolist()
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
            "Situação",
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
            "Limpar histórico",
            on_click=solicitar_limpeza_historico,
            width="stretch",
            type="secondary",
        )

    if st.session_state.get("confirmar_limpeza_historico", False):
        st.warning(
            "Tem certeza de que deseja apagar todas as solicitações "
            "registradas? Essa ação não poderá ser desfeita."
        )

        confirmar, cancelar = st.columns(2)

        with confirmar:
            st.button(
                "Sim, apagar histórico",
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
        st.error("A data inicial não pode ser posterior à data final.")
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
            filtrado["Situação"] == situacao_selecionada
        ]

    st.divider()

    st.metric(
        "Solicitações encontradas",
        len(filtrado),
    )

    st.markdown(
        '<div class="section-title">Solicitações registradas</div>',
        unsafe_allow_html=True,
    )

    if filtrado.empty:
        st.warning("Nenhuma solicitação encontrada com esses filtros.")
        return

    st.dataframe(
        filtrado[colunas_necessarias],
        width="stretch",
        hide_index=True,
    )

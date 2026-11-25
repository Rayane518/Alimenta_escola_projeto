
from datetime import date, timedelta

import pandas as pd
import streamlit as st


def gerar_dados_demonstrativos():
    registros = []

    dados_turnos = {
        "Manhã": {
            "previstos": 112,
            "planejadas": 112,
            "preparadas": 115,
            "servidas": 108,
        },
        "Tarde": {
            "previstos": 86,
            "planejadas": 86,
            "preparadas": 89,
            "servidas": 83,
        },
    }

    for dia in range(6, -1, -1):
        data_registro = date.today() - timedelta(days=dia)

        for turno, valores in dados_turnos.items():
            variacao = dia % 4

            preparados = valores["preparadas"] + variacao
            servidos = valores["servidas"] + variacao

            registros.append({
                "Data": data_registro,
                "Turno": turno,
                "Alunos previstos": valores["previstos"] + variacao,
                "Planejadas": valores["planejadas"] + variacao,
                "Preparadas": preparados,
                "Servidas": servidos,
                "Sobras": preparados - servidos,
            })

    return pd.DataFrame(registros)


def render():
    st.markdown(
        '<div class="eyebrow">ACOMPANHAMENTO E RESULTADOS</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<h1 class="hero-title">Indicadores</h1>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="hero-subtitle">'
        'Acompanhe os resultados da alimentação escolar e visualize '
        'os dados de planejamento e desperdício.'
        '</div>',
        unsafe_allow_html=True,
    )

    st.info(
        "Protótipo acadêmico: todos os dados apresentados nesta página "
        "são fictícios e utilizados apenas para demonstração. "
        "Ainda não representam dados reais de escolas."
    )

    dados = gerar_dados_demonstrativos()

    col1, col2, col3 = st.columns(3)

    with col1:
        data_inicial = st.date_input(
            "Data inicial",
            value=date.today() - timedelta(days=6),
            key="indicadores_data_inicial",
        )

    with col2:
        data_final = st.date_input(
            "Data final",
            value=date.today(),
            key="indicadores_data_final",
        )

    with col3:
        turno_selecionado = st.selectbox(
            "Turno",
            ["Todos", "Manhã", "Tarde"],
            key="indicadores_turno",
        )

    if data_inicial > data_final:
        st.error("A data inicial não pode ser posterior à data final.")
        return

    dados_filtrados = dados[
        (dados["Data"] >= data_inicial)
        & (dados["Data"] <= data_final)
    ]

    if turno_selecionado != "Todos":
        dados_filtrados = dados_filtrados[
            dados_filtrados["Turno"] == turno_selecionado
        ]

    if dados_filtrados.empty:
        st.warning(
            "Não existem dados demonstrativos para o período selecionado."
        )
        return

    alunos = int(dados_filtrados["Alunos previstos"].sum())
    planejadas = int(dados_filtrados["Planejadas"].sum())
    preparadas = int(dados_filtrados["Preparadas"].sum())
    servidas = int(dados_filtrados["Servidas"].sum())
    sobras = int(dados_filtrados["Sobras"].sum())

    percentual_sobras = (
        (sobras / preparadas) * 100
        if preparadas > 0
        else 0
    )

    st.markdown(
        '<div class="section-title">Resumo dos indicadores</div>',
        unsafe_allow_html=True,
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Alunos previstos",
            f"{alunos:,}".replace(",", "."),
        )

    with col2:
        st.metric(
            "Refeições planejadas",
            f"{planejadas:,}".replace(",", "."),
        )

    with col3:
        st.metric(
            "Refeições preparadas",
            f"{preparadas:,}".replace(",", "."),
        )

    with col4:
        st.metric(
            "Refeições servidas",
            f"{servidas:,}".replace(",", "."),
        )

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "Sobras de refeições",
            f"{sobras:,}".replace(",", "."),
        )

    with col2:
        st.metric(
            "Percentual de sobras",
            f"{percentual_sobras:.1f}%".replace(".", ","),
        )

    st.divider()

    st.markdown(
        '<div class="section-title">Planejamento e execução</div>',
        unsafe_allow_html=True,
    )

    resumo_diario = (
        dados_filtrados
        .groupby("Data")[["Planejadas", "Preparadas", "Servidas"]]
        .sum()
    )

    st.bar_chart(
        resumo_diario,
        height=320,
    )

    st.markdown(
        '<div class="section-title">Acompanhamento das sobras</div>',
        unsafe_allow_html=True,
    )

    sobras_diarias = (
        dados_filtrados
        .groupby("Data")[["Sobras"]]
        .sum()
    )

    st.line_chart(
        sobras_diarias,
        height=280,
    )

    st.markdown(
        '<div class="section-title">Detalhamento dos registros</div>',
        unsafe_allow_html=True,
    )

    tabela = dados_filtrados.copy()

    tabela["Data"] = tabela["Data"].apply(
        lambda valor: valor.strftime("%d/%m/%Y")
    )

    tabela = tabela.rename(columns={
        "Planejadas": "Refeições planejadas",
        "Preparadas": "Refeições preparadas",
        "Servidas": "Refeições servidas",
    })

    st.dataframe(
        tabela,
        width="stretch",
        hide_index=True,
    )

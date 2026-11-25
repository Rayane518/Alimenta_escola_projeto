
import pandas as pd
import streamlit as st
import requests

from infrastructure.api.api_client import get_api_client


def consultar_api(endpoint):
    try:
        resposta = get_api_client().get(endpoint)

        if resposta.status_code == 401:
            st.error(
                "Sua sessão expirou. Faça o login novamente."
            )
            return None

        if resposta.status_code != 200:
            st.error(
                f"Não foi possível consultar {endpoint}."
            )
            return None

        return resposta.json()

    except requests.exceptions.ConnectionError:
        st.error(
            "Não foi possível conectar ao backend. "
            "Verifique se o Flask está em execução."
        )
        return None

    except requests.exceptions.Timeout:
        st.error(
            "O backend demorou muito para responder."
        )
        return None

    except requests.exceptions.RequestException:
        st.error(
            "Ocorreu um erro na comunicação com o backend."
        )
        return None

    except ValueError:
        st.error("A API retornou um JSON inválido.")
        return None


def formatar_numero(valor):
    return f"{int(valor):,}".replace(",", ".")


def formatar_percentual(valor):
    if valor is None:
        return "—"

    return f"{float(valor):.2f}%".replace(".", ",")


def limpar_filtros(data_minima, data_maxima):
    st.session_state["indicadores_data_inicial"] = data_minima
    st.session_state["indicadores_data_final"] = data_maxima
    st.session_state["indicadores_turno"] = "Todos"


def mostrar_indicadores_gerais(indicadores):

    st.markdown(
        '<div class="section-title">'
        'Indicadores gerais da escola'
        '</div>',
        unsafe_allow_html=True,
    )

    st.caption(
        "Totais de todos os registros de merenda "
        "armazenados no banco, independentemente dos filtros."
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Refeições preparadas",
            formatar_numero(
                indicadores["total_refeicoes_preparadas"]
            ),
        )

    with col2:
        st.metric(
            "Refeições servidas",
            formatar_numero(
                indicadores["total_refeicoes_servidas"]
            ),
        )

    with col3:
        st.metric(
            "Sobras de refeições",
            formatar_numero(
                indicadores["total_sobras"]
            ),
        )

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "Registros de merenda",
            formatar_numero(
                indicadores["registros"]
            ),
        )

    with col2:
        st.metric(
            "Percentual geral de sobras",
            formatar_percentual(
                indicadores[
                    "percentual_sobras_sobre_preparadas"
                ]
            ),
        )


def render():

    st.markdown(
        '<div class="eyebrow">'
        'ACOMPANHAMENTO E RESULTADOS'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<h1 class="hero-title">Indicadores</h1>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="hero-subtitle">'
        'Acompanhe os resultados da alimentação escolar '
        'e visualize os indicadores de consumo e desperdício.'
        '</div>',
        unsafe_allow_html=True,
    )

    st.info(
        "Protótipo acadêmico: a base atual contém dados "
        "simulados para demonstração do sistema."
    )

    # Consulta os indicadores gerais
    indicadores = consultar_api("/api/indicadores")

    if indicadores is None:
        return

    campos_indicadores = [
        "registros",
        "total_refeicoes_preparadas",
        "total_refeicoes_servidas",
        "total_sobras",
        "percentual_sobras_sobre_preparadas",
    ]

    if not isinstance(indicadores, dict) or not all(
        campo in indicadores
        for campo in campos_indicadores
    ):
        st.error(
            "A API retornou indicadores em formato inesperado."
        )
        return

    mostrar_indicadores_gerais(indicadores)

    st.divider()

    # Consulta os registros para filtros e gráficos
    historico = consultar_api("/api/historico")

    if historico is None:
        return

    if not isinstance(historico, list):
        st.error(
            "A API retornou um histórico em formato inesperado."
        )
        return

    if not historico:
        st.info(
            "Não existem registros de frequência e merenda "
            "disponíveis para análise por período."
        )
        return

    dados = pd.DataFrame(historico)

    colunas_necessarias = [
        "data",
        "turno",
        "alunos_previstos",
        "alunos_presentes",
        "cardapio",
        "refeicoes_preparadas",
        "refeicoes_servidas",
        "sobras",
    ]

    if not all(
        coluna in dados.columns
        for coluna in colunas_necessarias
    ):
        st.error(
            "Os registros possuem uma estrutura diferente "
            "da esperada."
        )
        return

    # Tratamento das datas
    dados["Data"] = pd.to_datetime(
        dados["data"],
        errors="coerce",
    ).dt.date

    dados = dados.dropna(
        subset=["Data"]
    ).copy()

    if dados.empty:
        st.warning("Não existem datas válidas para consulta.")
        return

    # Tratamento dos turnos
    dados["Turno"] = dados["turno"].replace({
        "MANHÃ": "Manhã",
        "MANHA": "Manhã",
        "TARDE": "Tarde",
    })

    # Conversão dos campos numéricos
    colunas_numericas = [
        "alunos_previstos",
        "alunos_presentes",
        "refeicoes_preparadas",
        "refeicoes_servidas",
        "sobras",
    ]

    for coluna in colunas_numericas:
        dados[coluna] = pd.to_numeric(
            dados[coluna],
            errors="coerce",
        )

    if dados[colunas_numericas].isna().any().any():
        st.error(
            "Existem registros com valores numéricos inválidos."
        )
        return

    data_minima = min(dados["Data"])
    data_maxima = max(dados["Data"])

    st.session_state.setdefault(
        "indicadores_data_inicial",
        data_minima,
    )

    st.session_state.setdefault(
        "indicadores_data_final",
        data_maxima,
    )

    st.session_state.setdefault(
        "indicadores_turno",
        "Todos",
    )

    st.markdown(
        '<div class="section-title">'
        'Filtros de consulta'
        '</div>',
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        data_inicial = st.date_input(
            "Data inicial",
            key="indicadores_data_inicial",
        )

    with col2:
        data_final = st.date_input(
            "Data final",
            key="indicadores_data_final",
        )

    with col3:
        turno_selecionado = st.selectbox(
            "Turno",
            ["Todos", "Manhã", "Tarde"],
            key="indicadores_turno",
        )

    st.button(
        "Limpar filtros",
        on_click=limpar_filtros,
        args=(data_minima, data_maxima),
        width="stretch",
    )

    if data_inicial is None or data_final is None:
        st.warning("Informe o período da consulta.")
        return

    if data_inicial > data_final:
        st.error(
            "A data inicial não pode ser posterior à data final."
        )
        return

    # Aplicação dos filtros
    dados_filtrados = dados[
        (dados["Data"] >= data_inicial)
        & (dados["Data"] <= data_final)
    ].copy()

    if turno_selecionado != "Todos":
        dados_filtrados = dados_filtrados[
            dados_filtrados["Turno"] == turno_selecionado
        ].copy()

    if dados_filtrados.empty:
        st.warning(
            "Não existem registros para o período "
            "e turno selecionados."
        )
        return

    # Cálculo dos indicadores do período
    alunos = int(
        dados_filtrados["alunos_previstos"].sum()
    )

    presentes = int(
        dados_filtrados["alunos_presentes"].sum()
    )

    preparadas = int(
        dados_filtrados["refeicoes_preparadas"].sum()
    )

    servidas = int(
        dados_filtrados["refeicoes_servidas"].sum()
    )

    sobras = int(
        dados_filtrados["sobras"].sum()
    )

    percentual_sobras = (
        sobras / preparadas * 100
        if preparadas > 0
        else None
    )

    st.markdown(
        '<div class="section-title">'
        'Resumo dos indicadores do período'
        '</div>',
        unsafe_allow_html=True,
    )

    st.caption(
        "Resultados dos registros de frequência e merenda "
        "correspondentes aos filtros selecionados."
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Alunos previstos (acumulado)",
            formatar_numero(alunos),
        )

    with col2:
        st.metric(
            "Presenças registradas",
            formatar_numero(presentes),
        )

    with col3:
        st.metric(
            "Refeições preparadas",
            formatar_numero(preparadas),
        )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Refeições servidas",
            formatar_numero(servidas),
        )

    with col2:
        st.metric(
            "Sobras de refeições",
            formatar_numero(sobras),
        )

    with col3:
        st.metric(
            "Percentual de sobras",
            formatar_percentual(percentual_sobras),
        )

    st.caption(
        "Os totais de alunos e presenças são acumulados "
        "por data e turno, não representam alunos únicos."
    )

    st.divider()

    # Gráfico de refeições preparadas e servidas
    st.markdown(
        '<div class="section-title">'
        'Preparação e consumo de refeições'
        '</div>',
        unsafe_allow_html=True,
    )

    resumo_diario = (
        dados_filtrados
        .groupby("Data")[
            [
                "refeicoes_preparadas",
                "refeicoes_servidas",
            ]
        ]
        .sum()
        .sort_index()
        .rename(columns={
            "refeicoes_preparadas": "Preparadas",
            "refeicoes_servidas": "Servidas",
        })
    )

    st.bar_chart(
        resumo_diario,
        height=320,
    )

    # Gráfico de sobras
    st.markdown(
        '<div class="section-title">'
        'Acompanhamento das sobras'
        '</div>',
        unsafe_allow_html=True,
    )

    sobras_diarias = (
        dados_filtrados
        .groupby("Data")[["sobras"]]
        .sum()
        .sort_index()
        .rename(columns={
            "sobras": "Sobras",
        })
    )

    st.line_chart(
        sobras_diarias,
        height=280,
    )

    # Tabela detalhada
    st.markdown(
        '<div class="section-title">'
        'Detalhamento dos registros'
        '</div>',
        unsafe_allow_html=True,
    )

    tabela = dados_filtrados.sort_values(
        by=["Data", "Turno"],
        ascending=[False, True],
    ).copy()

    tabela["Data"] = tabela["Data"].apply(
        lambda valor: valor.strftime("%d/%m/%Y")
    )

    tabela = tabela[
        [
            "Data",
            "Turno",
            "cardapio",
            "alunos_previstos",
            "alunos_presentes",
            "refeicoes_preparadas",
            "refeicoes_servidas",
            "sobras",
        ]
    ].rename(columns={
        "cardapio": "Cardápio",
        "alunos_previstos": "Alunos previstos",
        "alunos_presentes": "Alunos presentes",
        "refeicoes_preparadas": "Refeições preparadas",
        "refeicoes_servidas": "Refeições servidas",
        "sobras": "Sobras",
    })

    st.dataframe(
        tabela,
        width="stretch",
        hide_index=True,
    )

    st.caption(
        f"Total de registros encontrados: {len(tabela)}. "
        "Informações consultadas no banco de dados pela API."
    )

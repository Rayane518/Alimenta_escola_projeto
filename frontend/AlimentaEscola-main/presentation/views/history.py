
import pandas as pd
import streamlit as st
import requests

from infrastructure.api.api_client import get_api_client


DIAS_SEMANA = {
    0: "Segunda-feira",
    1: "Terça-feira",
    2: "Quarta-feira",
    3: "Quinta-feira",
    4: "Sexta-feira",
    5: "Sábado",
    6: "Domingo",
}


def limpar_filtros(data_minima, data_maxima):
    st.session_state["historico_data_inicial"] = data_minima
    st.session_state["historico_data_final"] = data_maxima
    st.session_state["historico_dia"] = "Todos"
    st.session_state["historico_turno"] = "Todos"


def consultar_historico():
    try:
        resposta = get_api_client().get(
            "/api/previsoes/historico"
        )

        if resposta.status_code == 401:
            st.error(
                "Sua sessão expirou. Faça o login novamente."
            )
            return None

        if resposta.status_code != 200:
            st.error(
                "Não foi possível consultar o histórico de previsões."
            )
            return None

        dados = resposta.json()

        if not isinstance(dados, list):
            st.error(
                "A API retornou um formato de dados inesperado."
            )
            return None

        return dados

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
        st.error("A resposta da API não é um JSON válido.")
        return None


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
        'Consulte e filtre as previsões realizadas no sistema.'
        '</div>',
        unsafe_allow_html=True,
    )

    # Consulta os registros reais pela API
    historico = consultar_historico()

    if historico is None:
        return

    if not historico:
        st.info(
            "Nenhuma previsão registrada ainda. "
            "Acesse Gerar previsões para realizar uma estimativa."
        )
        return

    df = pd.DataFrame(historico)

    colunas_necessarias = [
        "id_previsao",
        "data_prevista",
        "turno",
        "alunos_referencia",
        "quantidade_prevista",
        "margem_seguranca",
        "refeicoes_recomendadas",
        "tipo_previsao",
        "modelo_utilizado",
        "criado_em",
    ]

    if not all(
        coluna in df.columns
        for coluna in colunas_necessarias
    ):
        st.error(
            "Os registros retornados pela API possuem "
            "uma estrutura diferente da esperada."
        )
        return

    # Tratamento das datas
    df["_data_prevista"] = pd.to_datetime(
        df["data_prevista"],
        errors="coerce",
    )

    df["_criado_em"] = pd.to_datetime(
        df["criado_em"],
        errors="coerce",
    )

    df = df.dropna(
        subset=["_data_prevista"]
    ).copy()

    if df.empty:
        st.warning(
            "Não existem datas válidas para consulta."
        )
        return

    df["_data"] = df["_data_prevista"].dt.date

    # Dia da semana em português
    df["Dia da semana"] = (
        df["_data_prevista"]
        .dt.dayofweek
        .map(DIAS_SEMANA)
    )

    # Formatação dos turnos
    df["Turno"] = df["turno"].replace({
        "MANHÃ": "Manhã",
        "MANHA": "Manhã",
        "TARDE": "Tarde",
    })

    data_minima = min(df["_data"])
    data_maxima = max(df["_data"])

    dias = ["Todos"] + [
        dia for dia in DIAS_SEMANA.values()
        if dia in df["Dia da semana"].values
    ]

    turnos = ["Todos"] + sorted(
        df["Turno"].dropna().unique().tolist()
    )

    st.session_state.setdefault(
        "historico_data_inicial",
        data_minima,
    )

    st.session_state.setdefault(
        "historico_data_final",
        data_maxima,
    )

    st.session_state.setdefault(
        "historico_dia",
        "Todos",
    )

    st.session_state.setdefault(
        "historico_turno",
        "Todos",
    )

    if st.session_state["historico_dia"] not in dias:
        st.session_state["historico_dia"] = "Todos"

    if st.session_state["historico_turno"] not in turnos:
        st.session_state["historico_turno"] = "Todos"

    # Filtros
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
        turno_selecionado = st.selectbox(
            "Turno",
            turnos,
            key="historico_turno",
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
    filtrado = df[
        (df["_data"] >= data_inicial)
        & (df["_data"] <= data_final)
    ].copy()

    if dia_selecionado != "Todos":
        filtrado = filtrado[
            filtrado["Dia da semana"] == dia_selecionado
        ].copy()

    if turno_selecionado != "Todos":
        filtrado = filtrado[
            filtrado["Turno"] == turno_selecionado
        ].copy()

    st.divider()

    st.metric(
        "Previsões encontradas",
        len(filtrado),
    )

    st.markdown(
        '<div class="section-title">'
        'Previsões registradas'
        '</div>',
        unsafe_allow_html=True,
    )

    if filtrado.empty:
        st.warning(
            "Nenhuma previsão encontrada com esses filtros."
        )
        return

    # Ordena os registros mais recentes primeiro
    filtrado = filtrado.sort_values(
        by=["_criado_em", "id_previsao"],
        ascending=[False, False],
    )

    # Organização das informações para exibição
    tabela = pd.DataFrame({
        "ID": filtrado["id_previsao"],

        "Data da previsão": (
            filtrado["_data_prevista"]
            .dt.strftime("%d/%m/%Y")
        ),

        "Dia da semana": filtrado["Dia da semana"],

        "Turno": filtrado["Turno"],

        "Alunos de referência": pd.to_numeric(
            filtrado["alunos_referencia"],
            errors="coerce",
        ),

        "Refeições previstas": pd.to_numeric(
            filtrado["quantidade_prevista"],
            errors="coerce",
        ),

        "Margem de segurança": pd.to_numeric(
            filtrado["margem_seguranca"],
            errors="coerce",
        ),

        "Refeições recomendadas": pd.to_numeric(
            filtrado["refeicoes_recomendadas"],
            errors="coerce",
        ),

        "Tipo de previsão": (
            filtrado["tipo_previsao"]
            .astype(str)
            .str.capitalize()
        ),

        "Modelo utilizado": filtrado["modelo_utilizado"],

        "Registrada em": (
            filtrado["_criado_em"]
            .dt.strftime("%d/%m/%Y %H:%M")
        ),
    })

    st.dataframe(
        tabela,
        width="stretch",
        hide_index=True,
        column_config={
            "ID": st.column_config.NumberColumn(
                format="%d",
            ),

            "Alunos de referência": (
                st.column_config.NumberColumn(
                    format="%.0f",
                )
            ),

            "Refeições previstas": (
                st.column_config.NumberColumn(
                    format="%.0f",
                )
            ),

            "Margem de segurança": (
                st.column_config.NumberColumn(
                    format="%.1f%%",
                )
            ),

            "Refeições recomendadas": (
                st.column_config.NumberColumn(
                    format="%.0f",
                )
            ),
        },
    )

    st.caption(
        "Os registros apresentados são consultados "
        "diretamente do banco de dados por meio da API."
    )

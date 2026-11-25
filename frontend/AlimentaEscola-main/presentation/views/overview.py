
import unicodedata
from html import escape

import pandas as pd
import requests
import streamlit as st

from infrastructure.api.api_client import get_api_client


FUNCIONALIDADES = {
    "Cardápios": {
        "pagina": "Cadastro de cardápios",
        "palavras": ["cardapio", "cardapios", "menu", "alimentacao"],
        "icone": "🍽️",
    },
        "Minha escola": {
        "pagina": "Minha escola",
        "palavras": [
            "escola",
            "escolas",
            "minha escola",
            "instituicao",
            "cnpj",
            "endereco",
            "dados da escola",
        ],
        "icone": "🏫",
    },
    "Turmas": {
        "pagina": "Cadastro de turmas",
        "palavras": ["turma", "turmas", "alunos", "estudantes"],
        "icone": "👩‍🎓",
    },
    "Gerar previsões": {
        "pagina": "Gerar previsões",
        "palavras": ["previsao", "previsoes", "prever", "demanda"],
        "icone": "🤖",
    },
    "Histórico": {
        "pagina": "Histórico de previsões",
        "palavras": ["historico", "registros", "consultar"],
        "icone": "📋",
    },
    "Indicadores": {
        "pagina": "Indicadores",
        "palavras": ["indicador", "indicadores", "graficos", "resultados"],
        "icone": "📊",
    },
    "Gestão de refeições": {
        "pagina": "Gestão de refeições",
        "palavras": ["refeicao", "refeicoes", "gestao alimentar"],
        "icone": "🥗",
    },
    "Sobre o projeto": {
        "pagina": "Sobre o projeto",
        "palavras": ["sobre", "projeto", "informacoes"],
        "icone": "ℹ️",
    },
}


def normalizar_texto(texto):
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(
        caractere
        for caractere in texto
        if not unicodedata.combining(caractere)
    )
    return texto.lower().strip()


def buscar_funcionalidades(termo):
    termo = normalizar_texto(termo)

    if not termo:
        return []

    resultados = []

    for nome, dados in FUNCIONALIDADES.items():
        palavras = [nome] + dados["palavras"]

        if any(
            termo in normalizar_texto(palavra)
            for palavra in palavras
        ):
            resultados.append((nome, dados))

    return resultados


def navigate_to(page):
    st.session_state["pagina_atual"] = page
    st.rerun()


def render_pesquisa():
    st.markdown(
        '<div class="section-title">🔎 &nbsp; O que você procura?</div>',
        unsafe_allow_html=True,
    )

    termo = st.text_input(
        "Pesquisar funcionalidades",
        placeholder="Digite escola, turma, cardápio, previsão...",
        label_visibility="collapsed",
        key="pesquisa_dashboard",
    )

    if termo:
        resultados = buscar_funcionalidades(termo)

        if resultados:
            st.caption("Funcionalidades encontradas")

            colunas = st.columns(2)

            for indice, (nome, dados) in enumerate(resultados):
                with colunas[indice % 2]:
                    st.button(
                        f"{dados['icone']}  {nome}  →",
                        key=f"pesquisa_{nome}",
                        width="stretch",
                        on_click=navigate_to,
                        args=(dados["pagina"],),
                    )
        else:
            st.info("Nenhuma funcionalidade encontrada.")


def render_graficos(dados):

    if dados.empty:
        st.info(
            "Ainda não existem registros históricos "
            "para gerar os gráficos."
        )
        return

    resumo_diario = (
        dados.groupby("Data")[
            [
                "alunos_previstos",
                "alunos_presentes",
                "refeicoes_preparadas",
                "refeicoes_servidas",
                "sobras",
            ]
        ]
        .sum()
        .sort_index()
        .tail(7)
    )

    data_inicial = (
        resumo_diario.index.min()
        .strftime("%d/%m/%Y")
    )

    data_final = (
        resumo_diario.index.max()
        .strftime("%d/%m/%Y")
    )

    st.caption(
        "Últimos sete dias com registros disponíveis: "
        f"{data_inicial} a {data_final}."
    )

    col1, col2 = st.columns(2)

    with col1:
        with st.container(border=True):

            st.markdown(
                "**👩‍🎓 Frequência de alunos**"
            )

            st.caption(
                "Comparação entre alunos previstos "
                "e presentes."
            )

            frequencia = resumo_diario[
                [
                    "alunos_previstos",
                    "alunos_presentes",
                ]
            ].rename(columns={
                "alunos_previstos": "Previstos",
                "alunos_presentes": "Presentes",
            })

            st.line_chart(
                frequencia,
                height=280,
            )

    with col2:
        with st.container(border=True):

            st.markdown(
                "**🍽️ Refeições preparadas x servidas**"
            )

            st.caption(
                "Comparação entre preparação "
                "e consumo de refeições."
            )

            refeicoes = resumo_diario[
                [
                    "refeicoes_preparadas",
                    "refeicoes_servidas",
                ]
            ].rename(columns={
                "refeicoes_preparadas": "Preparadas",
                "refeicoes_servidas": "Servidas",
            })

            st.bar_chart(
                refeicoes,
                height=280,
            )

    with st.container(border=True):

        st.markdown(
            "**♻️ Sobras e desperdício**"
        )

        st.caption(
            "Acompanhamento das sobras de refeições "
            "por dia."
        )

        sobras = resumo_diario[
            ["sobras"]
        ].rename(columns={
            "sobras": "Sobras",
        })

        st.line_chart(
            sobras,
            height=280,
        )


def render():

    st.markdown(
        '<div class="eyebrow">PAINEL DE CONTROLE</div>'
        '<h1 class="hero-title">Dashboard</h1>',
        unsafe_allow_html=True,
    )

    render_pesquisa()

    st.caption(
        "Protótipo acadêmico — base atual com dados "
        "simulados para demonstração."
    )

    # Consulta os indicadores gerais
    indicadores = consultar_api(
        "/api/indicadores"
    )

    if indicadores is None:
        return

    campos_necessarios = [
        "registros",
        "total_refeicoes_preparadas",
        "total_refeicoes_servidas",
        "total_sobras",
        "percentual_sobras_sobre_preparadas",
    ]

    if not isinstance(indicadores, dict) or not all(
        campo in indicadores
        for campo in campos_necessarios
    ):
        st.error(
            "Formato de indicadores inesperado."
        )
        return

    # Consulta o histórico de frequência e merenda
    historico = consultar_api(
        "/api/historico"
    )

    if historico is None:
        return

    dados = preparar_historico(historico)

    if dados is None:
        return

    st.markdown(
        '<div class="section-title">'
        '📊 &nbsp; Indicadores gerais'
        '</div>',
        unsafe_allow_html=True,
    )

    render_indicadores(
        indicadores,
        dados,
    )

    st.caption(
        "Os indicadores são acumulados. "
        "As presenças não representam alunos únicos."
    )

    st.markdown(
        '<div class="section-title" '
        'style="margin-top:30px;">'
        '📈 &nbsp; Análise da alimentação escolar'
        '</div>',
        unsafe_allow_html=True,
    )

    render_graficos(dados)


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
            "Erro na comunicação com o backend."
        )
        return None

    except ValueError:
        st.error("A API retornou um JSON inválido.")
        return None


def formatar_numero(valor):
    return f"{int(valor):,}".replace(",", ".")


def preparar_historico(historico):
    if not isinstance(historico, list):
        st.error("Formato de histórico inesperado.")
        return None

    if not historico:
        return pd.DataFrame()

    dados = pd.DataFrame(historico)

    colunas_numericas = [
        "alunos_previstos",
        "alunos_presentes",
        "refeicoes_preparadas",
        "refeicoes_servidas",
        "sobras",
    ]

    colunas_necessarias = [
        "data",
        "turno",
    ] + colunas_numericas

    if not all(
        coluna in dados.columns
        for coluna in colunas_necessarias
    ):
        st.error(
            "O histórico possui uma estrutura inesperada."
        )
        return None

    dados["Data"] = pd.to_datetime(
        dados["data"],
        errors="coerce",
    )

    for coluna in colunas_numericas:
        dados[coluna] = pd.to_numeric(
            dados[coluna],
            errors="coerce",
        )

    if dados[["Data"] + colunas_numericas].isna().any().any():
        st.error(
            "Existem registros inválidos no histórico."
        )
        return None

    return dados.sort_values("Data")


    
def render_indicadores(indicadores, dados):

    presentes = (
        formatar_numero(
            dados["alunos_presentes"].sum()
        )
        if not dados.empty
        else "—"
    )

    preparadas = formatar_numero(
        indicadores["total_refeicoes_preparadas"]
    )

    servidas = formatar_numero(
        indicadores["total_refeicoes_servidas"]
    )

    sobras = formatar_numero(
        indicadores["total_sobras"]
    )

    percentual = indicadores[
        "percentual_sobras_sobre_preparadas"
    ]

    percentual_formatado = (
        f"{float(percentual):.2f}%".replace(".", ",")
        if percentual is not None
        else "—"
    )

    cartoes = [
        (
            "👩‍🎓",
            "Presenças registradas",
            "icon-blue",
            presentes,
            "Total acumulado no histórico",
        ),
        (
            "🍽️",
            "Refeições preparadas",
            "icon-green",
            preparadas,
            "Total acumulado",
        ),
        (
            "🥗",
            "Refeições servidas",
            "icon-blue",
            servidas,
            "Total acumulado",
        ),
        (
            "♻️",
            "Sobras de refeições",
            "icon-orange",
            sobras,
            f"{percentual_formatado} do total preparado",
        ),
    ]

    colunas = st.columns(4)

    for coluna, (
        icone,
        titulo,
        estilo,
        valor,
        descricao,
    ) in zip(colunas, cartoes):

        with coluna:

            html = (
                '<div class="metric">'
                f'<div class="metric-icon {estilo}">'
                f'{icone}'
                '</div>'
                '<div class="metric-label">'
                f'{escape(titulo)}'
                '</div>'
                '<div class="metric-value">'
                f'{escape(str(valor))}'
                '</div>'
                '<div style="color:#8b9bb1;'
                'font-size:11px;margin-top:8px;">'
                f'{escape(descricao)}'
                '</div>'
                '</div>'
            )

            st.markdown(
                html,
                unsafe_allow_html=True,
            )



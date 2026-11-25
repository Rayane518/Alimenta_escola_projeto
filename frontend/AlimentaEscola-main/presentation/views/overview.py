
import unicodedata

import streamlit as st


FUNCIONALIDADES = {
    "Cardápios": {
        "pagina": "Cadastro de cardápios",
        "palavras": ["cardapio", "cardapios", "menu", "alimentacao"],
        "icone": "🍽️",
    },
    "Escolas": {
        "pagina": "Cadastro de escolas",
        "palavras": ["escola", "escolas", "cnpj"],
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


def render_indicadores():
    indicadores = [
        ("👩‍🎓", "Alunos presentes", "icon-blue"),
        ("🍽️", "Refeições planejadas", "icon-green"),
        ("🥗", "Refeições servidas", "icon-blue"),
        ("♻️", "Sobras e desperdício", "icon-orange"),
    ]

    colunas = st.columns(4)

    for coluna, (icone, titulo, estilo) in zip(
        colunas,
        indicadores,
    ):
        with coluna:
            st.markdown(
                f"""
                <div class="metric">
                    <div class="metric-icon {estilo}">
                        {icone}
                    </div>
                    <div class="metric-label">
                        {titulo}
                    </div>
                    <div class="metric-value">—</div>
                    <div style="
                        color:#8b9bb1;
                        font-size:11px;
                        margin-top:8px;
                    ">
                        Aguardando dados
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def render_grafico(titulo, icone, descricao):
    st.markdown(
        f"""
        <div class="info-card" style="margin-top:0;min-height:245px;">
            <div class="info-heading">
                {icone} &nbsp; {titulo}
            </div>
            <div class="info-text" style="font-size:12px;">
                {descricao}
            </div>
            <div style="
                min-height:120px;
                display:flex;
                flex-direction:column;
                align-items:center;
                justify-content:center;
                color:#8b9bb1;
                text-align:center;
            ">
                <div style="font-size:30px;">📊</div>
                <div style="font-size:12px;">
                    Aguardando integração dos dados
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_graficos():
    col1, col2 = st.columns(2)

    with col1:
        render_grafico(
            "Frequência de alunos",
            "👩‍🎓",
            "Acompanhamento de alunos presentes por período.",
        )

    with col2:
        render_grafico(
            "Refeições planejadas x servidas",
            "🍽️",
            "Comparação entre refeições planejadas e servidas.",
        )

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    render_grafico(
        "Sobras e desperdício",
        "♻️",
        "Acompanhamento das sobras e do desperdício alimentar.",
    )


def render():
    st.markdown(
        """
        <div class="eyebrow">PAINEL DE CONTROLE</div>
        <h1 class="hero-title">Dashboard</h1>
        """,
        unsafe_allow_html=True,
    )

    render_pesquisa()

    st.markdown(
        '<div class="section-title">📊 &nbsp; Indicadores gerais</div>',
        unsafe_allow_html=True,
    )

    render_indicadores()

    st.markdown(
        '<div class="section-title" style="margin-top:30px;">'
        '📈 &nbsp; Análise da alimentação escolar'
        '</div>',
        unsafe_allow_html=True,
    )

    render_graficos()

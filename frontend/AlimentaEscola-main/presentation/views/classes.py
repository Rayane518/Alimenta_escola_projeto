
import streamlit as st


SERIES = [
    "Selecione",
    "Educação Infantil",
    "1º Ano",
    "2º Ano",
    "3º Ano",
    "4º Ano",
    "5º Ano",
    "6º Ano",
    "7º Ano",
    "8º Ano",
    "9º Ano",
    "1º Ano do Ensino Médio",
    "2º Ano do Ensino Médio",
    "3º Ano do Ensino Médio",
]

TURNOS = [
    "Selecione",
    "Manhã",
    "Tarde",
    "Integral",
]


def limpar_campos():
    campos = [
        "turma_escola",
        "turma_identificacao",
        "turma_serie",
        "turma_turno",
        "turma_alunos",
    ]

    for campo in campos:
        st.session_state[campo] = "" if campo == "turma_identificacao" else (
            0 if campo == "turma_alunos" else "Selecione"
        )


def render():
    st.markdown(
        '<div class="eyebrow">GESTÃO ALIMENTAR</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<h1 class="hero-title">Cadastro de turmas</h1>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="hero-subtitle">'
        'Cadastre as turmas e vincule cada uma à sua unidade escolar.'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="section-title">Dados da turma</div>',
        unsafe_allow_html=True,
    )

    with st.form("form_cadastro_turma"):
        escola = st.selectbox(
            "Escola vinculada *",
            ["Selecione"],
            key="turma_escola",
        )

        identificacao = st.text_input(
            "Identificação da turma *",
            placeholder="Ex.: 5º Ano A",
            key="turma_identificacao",
        )

        col1, col2 = st.columns(2)

        with col1:
            serie = st.selectbox(
                "Série/ano escolar *",
                SERIES,
                key="turma_serie",
            )

        with col2:
            turno = st.selectbox(
                "Turno *",
                TURNOS,
                key="turma_turno",
            )

        alunos = st.number_input(
            "Quantidade de alunos *",
            min_value=0,
            step=1,
            key="turma_alunos",
        )

        st.caption("* Campos obrigatórios.")

        col3, col4 = st.columns(2)

        with col3:
            cadastrar = st.form_submit_button(
                "Cadastrar turma",
                width="stretch",
                type="primary",
            )

        with col4:
            st.form_submit_button(
                "Limpar formulário",
                width="stretch",
                on_click=limpar_campos,
            )

    if cadastrar:
        erros = []

        if escola == "Selecione":
            erros.append("Selecione uma escola cadastrada.")

        if not identificacao.strip():
            erros.append("Informe a identificação da turma.")

        if serie == "Selecione":
            erros.append("Selecione a série ou ano escolar.")

        if turno == "Selecione":
            erros.append("Selecione o turno.")

        if alunos <= 0:
            erros.append("Informe uma quantidade de alunos maior que zero.")

        if erros:
            for erro in erros:
                st.error(erro)
        else:
            st.info(
                "Os dados da turma foram validados. "
                "O cadastro será gravado quando o backend Flask "
                "e o banco de dados estiverem integrados."
            )

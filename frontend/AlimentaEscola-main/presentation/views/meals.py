
import streamlit as st


TURNOS = [
    "Selecione",
    "Manhã",
    "Tarde",
    "Integral",
]

TIPOS_REFEICAO = [
    "Selecione",
    "Café da manhã",
    "Lanche",
    "Almoço",
    "Jantar",
]


def limpar_campos():
    st.session_state["refeicao_escola"] = "Selecione"
    st.session_state["refeicao_data"] = None
    st.session_state["refeicao_turma"] = "Selecione"
    st.session_state["refeicao_turno"] = "Selecione"
    st.session_state["refeicao_tipo"] = "Selecione"
    st.session_state["refeicao_planejada"] = 0
    st.session_state["refeicao_preparada"] = 0
    st.session_state["refeicao_servida"] = 0
    st.session_state["refeicao_observacoes"] = ""


def render():
    st.markdown(
        '<div class="eyebrow">GESTÃO ALIMENTAR</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<h1 class="hero-title">Gestão de refeições</h1>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="hero-subtitle">'
        'Registre e acompanhe as refeições planejadas, preparadas e servidas.'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="section-title">Identificação da refeição</div>',
        unsafe_allow_html=True,
    )

    with st.form("form_gestao_refeicoes"):
        escola = st.selectbox(
            "Escola vinculada *",
            ["Selecione"],
            key="refeicao_escola",
        )

        data = st.date_input(
            "Data do registro *",
            value=None,
            key="refeicao_data",
        )

        turma = st.selectbox(
            "Turma *",
            ["Selecione"],
            key="refeicao_turma",
        )

        col1, col2 = st.columns(2)

        with col1:
            turno = st.selectbox(
                "Turno *",
                TURNOS,
                key="refeicao_turno",
            )

        with col2:
            tipo = st.selectbox(
                "Tipo de refeição *",
                TIPOS_REFEICAO,
                key="refeicao_tipo",
            )

        st.markdown(
            '<div class="section-title">Controle de quantidades</div>',
            unsafe_allow_html=True,
        )

        col3, col4 = st.columns(2)

        with col3:
            planejada = st.number_input(
                "Refeições planejadas *",
                min_value=0,
                step=1,
                key="refeicao_planejada",
            )

        with col4:
            preparada = st.number_input(
                "Refeições preparadas *",
                min_value=0,
                step=1,
                key="refeicao_preparada",
            )

        servida = st.number_input(
            "Refeições servidas *",
            min_value=0,
            step=1,
            key="refeicao_servida",
        )

        observacoes = st.text_area(
            "Observações",
            placeholder="Registre ocorrências ou informações importantes.",
            key="refeicao_observacoes",
        )

        st.caption("* Campos obrigatórios.")

        col5, col6 = st.columns(2)

        with col5:
            cadastrar = st.form_submit_button(
                "Registrar refeições",
                width="stretch",
                type="primary",
            )

        with col6:
            st.form_submit_button(
                "Limpar formulário",
                width="stretch",
                on_click=limpar_campos,
            )

    if cadastrar:
        erros = []

        if escola == "Selecione":
            erros.append("Selecione uma escola cadastrada.")

        if data is None:
            erros.append("Informe a data do registro.")

        if turma == "Selecione":
            erros.append("Selecione uma turma cadastrada.")

        if turno == "Selecione":
            erros.append("Selecione o turno.")

        if tipo == "Selecione":
            erros.append("Selecione o tipo de refeição.")

        if planejada <= 0:
            erros.append("Informe a quantidade de refeições planejadas.")

        if preparada <= 0:
            erros.append("Informe a quantidade de refeições preparadas.")

        if servida > preparada:
            erros.append(
                "A quantidade de refeições servidas não pode "
                "ser maior que a quantidade preparada."
            )

        if erros:
            for erro in erros:
                st.error(erro)
        else:
            sobras = preparada - servida

            st.markdown(
                '<div class="section-title">Resultado do registro</div>',
                unsafe_allow_html=True,
            )

            col7, col8, col9 = st.columns(3)

            col7.metric("Planejadas", int(planejada))
            col8.metric("Preparadas", int(preparada))
            col9.metric("Servidas", int(servida))

            st.metric("Sobras calculadas", int(sobras))

            st.info(
                "Os dados foram validados, mas ainda não foram salvos. "
                "A gravação permanente será implementada na integração "
                "com o backend Flask e o banco de dados."
            )

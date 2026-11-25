
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
    st.session_state["cardapio_escola"] = "Selecione"
    st.session_state["cardapio_data"] = None
    st.session_state["cardapio_turno"] = "Selecione"
    st.session_state["cardapio_tipo"] = "Selecione"
    st.session_state["cardapio_alimentos"] = ""


def render():
    st.markdown(
        '<div class="eyebrow">GESTÃO ALIMENTAR</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<h1 class="hero-title">Cadastro de cardápios</h1>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="hero-subtitle">'
        'Organize as refeições e os alimentos oferecidos pelas escolas.'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="section-title">Dados do cardápio</div>',
        unsafe_allow_html=True,
    )

    with st.form("form_cadastro_cardapio"):
        escola = st.selectbox(
            "Escola vinculada *",
            ["Selecione"],
            key="cardapio_escola",
        )

        data = st.date_input(
            "Data do cardápio *",
            value=None,
            key="cardapio_data",
        )

        col1, col2 = st.columns(2)

        with col1:
            turno = st.selectbox(
                "Turno *",
                TURNOS,
                key="cardapio_turno",
            )

        with col2:
            tipo = st.selectbox(
                "Tipo de refeição *",
                TIPOS_REFEICAO,
                key="cardapio_tipo",
            )

        alimentos = st.text_area(
            "Alimentos do cardápio *",
            placeholder=(
                "Digite um alimento por linha.\n"
                "Exemplo:\nArroz\nFeijão\nFrango\nSalada"
            ),
            height=160,
            key="cardapio_alimentos",
        )

        st.caption("* Campos obrigatórios. Informe um alimento por linha.")

        col3, col4 = st.columns(2)

        with col3:
            cadastrar = st.form_submit_button(
                "Cadastrar cardápio",
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

        if data is None:
            erros.append("Informe a data do cardápio.")

        if turno == "Selecione":
            erros.append("Selecione o turno.")

        if tipo == "Selecione":
            erros.append("Selecione o tipo de refeição.")

        lista_alimentos = [
            alimento.strip()
            for alimento in alimentos.splitlines()
            if alimento.strip()
        ]

        if not lista_alimentos:
            erros.append("Informe pelo menos um alimento.")

        if erros:
            for erro in erros:
                st.error(erro)
        else:
            st.info(
                "Os dados do cardápio foram validados. "
                "O cadastro será gravado quando o backend Flask "
                "e o banco de dados estiverem integrados."
            )

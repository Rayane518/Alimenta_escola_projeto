
import re

import streamlit as st


ESTADOS = [
    "Selecione",
    "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES",
    "GO", "MA", "MT", "MS", "MG", "PA", "PB", "PR",
    "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC",
    "SP", "SE", "TO",
]


def validar_cnpj(cnpj):
    cnpj = re.sub(r"\D", "", cnpj)

    if len(cnpj) != 14 or len(set(cnpj)) == 1:
        return False

    pesos_1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    pesos_2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]

    soma = sum(
        int(digito) * peso
        for digito, peso in zip(cnpj[:12], pesos_1)
    )

    resto = soma % 11
    primeiro = 0 if resto < 2 else 11 - resto

    soma = sum(
        int(digito) * peso
        for digito, peso in zip(
            cnpj[:12] + str(primeiro),
            pesos_2,
        )
    )

    resto = soma % 11
    segundo = 0 if resto < 2 else 11 - resto

    return cnpj[-2:] == f"{primeiro}{segundo}"


def limpar_campos():
    campos = [
        "escola_nome",
        "escola_cnpj",
        "escola_cep",
        "escola_endereco",
        "escola_numero",
        "escola_complemento",
        "escola_bairro",
        "escola_cidade",
        "escola_estado",
        "escola_telefone",
        "escola_email",
    ]

    for campo in campos:
        st.session_state[campo] = "" if campo != "escola_estado" else "Selecione"


def render():
    st.markdown(
        '<div class="eyebrow">GESTÃO ALIMENTAR</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<h1 class="hero-title">Cadastro de escolas</h1>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="hero-subtitle">'
        'Cadastre e organize as informações das unidades escolares.'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="section-title">Dados da escola</div>',
        unsafe_allow_html=True,
    )

    with st.form("form_cadastro_escola"):
        nome = st.text_input(
            "Nome da escola *",
            placeholder="Digite o nome da escola",
            key="escola_nome",
        )

        cnpj = st.text_input(
            "CNPJ *",
            placeholder="00.000.000/0000-00",
            max_chars=18,
            key="escola_cnpj",
        )

        cep = st.text_input(
            "CEP *",
            placeholder="00000-000",
            max_chars=9,
            key="escola_cep",
        )

        endereco = st.text_input(
            "Endereço *",
            placeholder="Rua, avenida ou estrada",
            key="escola_endereco",
        )

        col1, col2 = st.columns(2)

        with col1:
            numero = st.text_input(
                "Número *",
                placeholder="Número",
                key="escola_numero",
            )

        with col2:
            complemento = st.text_input(
                "Complemento",
                placeholder="Sala, bloco ou referência",
                key="escola_complemento",
            )

        col3, col4 = st.columns(2)

        with col3:
            bairro = st.text_input(
                "Bairro *",
                placeholder="Digite o bairro",
                key="escola_bairro",
            )

        with col4:
            cidade = st.text_input(
                "Cidade *",
                placeholder="Digite a cidade",
                key="escola_cidade",
            )

        col5, col6 = st.columns(2)

        with col5:
            estado = st.selectbox(
                "Estado *",
                ESTADOS,
                key="escola_estado",
            )

        with col6:
            telefone = st.text_input(
                "Telefone",
                placeholder="(00) 00000-0000",
                key="escola_telefone",
            )

        email = st.text_input(
            "E-mail institucional",
            placeholder="contato@escola.com.br",
            key="escola_email",
        )

        st.caption("* Campos obrigatórios.")

        col7, col8 = st.columns(2)

        with col7:
            cadastrar = st.form_submit_button(
                "Cadastrar escola",
                width="stretch",
                type="primary",
            )

        with col8:
            st.form_submit_button(
                "Limpar formulário",
                width="stretch",
                on_click=limpar_campos,
            )

    if cadastrar:
        erros = []

        if not nome.strip():
            erros.append("Informe o nome da escola.")

        if not validar_cnpj(cnpj):
            erros.append("Informe um CNPJ válido.")

        if len(re.sub(r"\D", "", cep)) != 8:
            erros.append("Informe um CEP válido com 8 dígitos.")

        if not endereco.strip():
            erros.append("Informe o endereço.")

        if not numero.strip():
            erros.append("Informe o número.")

        if not bairro.strip():
            erros.append("Informe o bairro.")

        if not cidade.strip():
            erros.append("Informe a cidade.")

        if estado == "Selecione":
            erros.append("Selecione o estado.")

        if email.strip() and not re.fullmatch(
            r"[^@\s]+@[^@\s]+\.[^@\s]+",
            email.strip(),
        ):
            erros.append("Informe um e-mail válido.")

        if erros:
            for erro in erros:
                st.error(erro)
        else:
            st.info(
                "Os dados foram validados. O cadastro será gravado "
                "quando o backend Flask e o banco de dados estiverem "
                "integrados."
            )

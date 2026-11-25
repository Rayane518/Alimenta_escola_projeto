import re

import requests
import streamlit as st

from infrastructure.api.api_client import get_api_client


ESTADOS = [
    "Selecione",
    "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES",
    "GO", "MA", "MT", "MS", "MG", "PA", "PB", "PR",
    "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC",
    "SP", "SE", "TO",
]


CAMPOS = [
    "nome",
    "cnpj",
    "cep",
    "endereco",
    "numero",
    "complemento",
    "bairro",
    "cidade",
    "estado",
    "telefone",
    "email",
]


def validar_cnpj(cnpj):
    cnpj = re.sub(r"[./-]", "", cnpj)

    if not re.fullmatch(r"[0-9]{14}", cnpj):
        return False

    if len(set(cnpj)) == 1:
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


def carregar_escola():
    try:
        resposta = get_api_client().get("/api/escola")

        if resposta.status_code == 401:
            st.error("Sessão expirada. Realize o login novamente.")
            return None

        if resposta.status_code != 200:
            st.error("Não foi possível consultar os dados da escola.")
            return None

        return resposta.json()

    except requests.RequestException:
        st.error("Não foi possível conectar ao backend.")
        return None

    except ValueError:
        st.error("Resposta inválida recebida do backend.")
        return None


def preencher_campos(escola):
    for campo in CAMPOS:
        valor = escola.get(campo)

        if campo == "estado":
            valor = valor if valor in ESTADOS else "Selecione"
        else:
            valor = str(valor) if valor is not None else ""

        st.session_state[f"escola_{campo}"] = valor


def iniciar_edicao():
    st.session_state["escola_editando"] = True
    st.session_state["escola_recarregar"] = True


def cancelar_edicao():
    st.session_state["escola_editando"] = False
    st.session_state["escola_recarregar"] = True


def salvar_escola(dados):
    try:
        resposta = get_api_client().put(
            "/api/escola",
            json=dados,
        )

        if resposta.status_code == 200:
            resultado = resposta.json()

            st.session_state["escola_mensagem"] = (
                resultado.get(
                    "mensagem",
                    "Dados atualizados com sucesso."
                )
            )

            st.session_state["escola_editando"] = False
            st.session_state["escola_recarregar"] = True
            st.rerun()

        elif resposta.status_code == 401:
            st.error("Sessão expirada. Realize o login novamente.")

        else:
            try:
                erro = resposta.json().get(
                    "erro",
                    "Não foi possível atualizar a escola."
                )
            except ValueError:
                erro = "Não foi possível atualizar a escola."

            st.error(erro)

    except requests.RequestException:
        st.error("Não foi possível conectar ao backend.")

def exibir_campo(titulo, valor):
    st.caption(titulo)
    st.write(str(valor) if valor else "Não informado")


def exibir_dados_escola(escola):

    st.markdown(
        '<div class="section-title">'
        'Instituição vinculada ao sistema'
        '</div>',
        unsafe_allow_html=True,
    )

    with st.container(border=True):

        st.subheader(
            escola.get("nome") or "Escola não identificada"
        )

        st.caption(
            "Instituição de ensino cadastrada no Alimenta Escola."
        )

        st.divider()

        st.markdown("**Dados institucionais**")

        col1, col2 = st.columns(2)

        with col1:
            exibir_campo("CNPJ", escola.get("cnpj"))
            exibir_campo("Telefone", escola.get("telefone"))

        with col2:
            exibir_campo("E-mail institucional", escola.get("email"))

        st.divider()

        st.markdown("**Endereço da instituição**")

        col3, col4 = st.columns(2)

        with col3:
            exibir_campo("Logradouro", escola.get("endereco"))
            exibir_campo("Número", escola.get("numero"))
            exibir_campo("Bairro", escola.get("bairro"))
            exibir_campo("CEP", escola.get("cep"))

        with col4:
            exibir_campo("Complemento", escola.get("complemento"))
            exibir_campo("Cidade", escola.get("cidade"))
            exibir_campo("Estado", escola.get("estado"))

    st.button(
        "Editar dados da escola",
        type="primary",
        on_click=iniciar_edicao,
        key="btn_editar_escola",
    )

def render():
    st.markdown(
        '<div class="eyebrow">GESTÃO ESCOLAR</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<h1 class="hero-title">Minha escola</h1>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="hero-subtitle">'
        'Consulte e atualize as informações da sua instituição.'
        '</div>',
        unsafe_allow_html=True,
    )

    escola = carregar_escola()

    if escola is None:
        return

    mensagem = st.session_state.pop(
        "escola_mensagem", None
    )

    if mensagem:
        st.success(mensagem)

    if not st.session_state.get("escola_editando", False):
        exibir_dados_escola(escola)
        return

    recarregar = st.session_state.pop(
        "escola_recarregar", False
    )

    campos_ausentes = any(
        f"escola_{campo}" not in st.session_state
        for campo in CAMPOS
    )

    if recarregar or campos_ausentes:
        preencher_campos(escola)

    st.markdown(
        '<div class="section-title">Editar dados institucionais</div>',
        unsafe_allow_html=True,
    )

    with st.form("form_cadastro_escola"):

        nome = st.text_input(
            "Nome da escola *",
            max_chars=150,
            key="escola_nome",
        )

        cnpj = st.text_input(
            "CNPJ",
            placeholder="00.000.000/0000-00",
            max_chars=18,
            key="escola_cnpj",
        )

        cep = st.text_input(
            "CEP",
            placeholder="00000-000",
            max_chars=9,
            key="escola_cep",
        )

        endereco = st.text_input(
            "Endereço *",
            placeholder="Rua, avenida ou estrada",
            max_chars=255,
            key="escola_endereco",
        )

        col1, col2 = st.columns(2)

        with col1:
            numero = st.text_input(
                "Número *",
                max_chars=20,
                key="escola_numero",
            )

        with col2:
            complemento = st.text_input(
                "Complemento",
                max_chars=100,
                key="escola_complemento",
            )

        col3, col4 = st.columns(2)

        with col3:
            bairro = st.text_input(
                "Bairro *",
                max_chars=100,
                key="escola_bairro",
            )

        with col4:
            cidade = st.text_input(
                "Cidade *",
                max_chars=100,
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
                max_chars=20,
                key="escola_telefone",
            )

        email = st.text_input(
            "E-mail institucional",
            placeholder="contato@escola.com.br",
            max_chars=150,
            key="escola_email",
        )

        st.caption("* Campos obrigatórios.")

        col7, col8 = st.columns(2)

        with col7:
            salvar = st.form_submit_button(
                "Salvar alterações",
                width="stretch",
                type="primary",
            )

        with col8:
            st.form_submit_button(
             "Cancelar",
            width="stretch",
            on_click=cancelar_edicao,
    )

    if salvar:
        erros = []

        if not nome.strip():
            erros.append("Informe o nome da escola.")

        if cnpj.strip() and not validar_cnpj(cnpj.strip()):
            erros.append("Informe um CNPJ válido.")

        if cep.strip() and not re.fullmatch(
            r"[0-9]{8}", cep.strip().replace("-", "")
        ):
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

        if telefone.strip():
            telefone_limpo = re.sub(
                r"[^0-9]", "", telefone
            )

            if (
                not re.fullmatch(r"[0-9()\s-]+", telefone)
                or len(telefone_limpo) not in (10, 11)
            ):
                erros.append("Informe um telefone válido.")

        if email.strip() and not re.fullmatch(
            r"[^@\s]+@[^@\s]+\.[^@\s]+",
            email.strip(),
        ):
            erros.append("Informe um e-mail válido.")

        if erros:
            for erro in erros:
                st.error(erro)

        else:
            dados = {
                "nome": nome.strip(),
                "cnpj": cnpj.strip() or None,
                "cep": cep.strip() or None,
                "endereco": endereco.strip(),
                "numero": numero.strip(),
                "complemento": complemento.strip() or None,
                "bairro": bairro.strip(),
                "cidade": cidade.strip(),
                "estado": estado,
                "telefone": telefone.strip() or None,
                "email": email.strip() or None,
            }

            salvar_escola(dados)

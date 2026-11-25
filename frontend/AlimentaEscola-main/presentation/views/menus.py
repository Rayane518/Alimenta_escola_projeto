
from datetime import date

import requests
import streamlit as st

from infrastructure.api.api_client import get_api_client


# LIMPAR FORMULÁRIO
def limpar_campos():
    st.session_state["cardapio_data"] = None
    st.session_state["cardapio_alimentos"] = ""


# TRATAMENTO DE ERROS DA API
def exibir_erro(resposta):
    if resposta.status_code == 401:
        st.error(
            "Sessão expirada. Realize o login novamente."
        )
        return

    try:
        mensagem = resposta.json().get(
            "erro",
            "Não foi possível realizar a operação."
        )

    except (ValueError, AttributeError):
        mensagem = "Erro na comunicação com o servidor."

    st.error(mensagem)


# CONSULTAR ESCOLA VINCULADA
def carregar_escola():
    try:
        resposta = get_api_client().get("/api/escola")

        if resposta.status_code == 200:
            return resposta.json()

        exibir_erro(resposta)

    except requests.RequestException:
        st.error("Não foi possível consultar a escola.")

    return None


# CONSULTAR CARDÁPIOS
def carregar_cardapios(data_consulta=None):
    try:
        parametros = {}

        if data_consulta is not None:
            parametros["data"] = data_consulta.isoformat()

        resposta = get_api_client().get(
            "/api/cardapios",
            params=parametros
        )

        if resposta.status_code == 200:
            return resposta.json()

        exibir_erro(resposta)

    except requests.RequestException:
        st.error("Não foi possível consultar os cardápios.")

    return None


# CADASTRAR CARDÁPIO
def cadastrar_cardapio(dados):
    try:
        resposta = get_api_client().post(
            "/api/cardapios",
            json=dados
        )

        if resposta.status_code == 201:
            st.session_state["cardapio_mensagem"] = (
                "Cardápio cadastrado com sucesso."
            )

            st.session_state["cardapio_limpar"] = True

            st.rerun()

        exibir_erro(resposta)

    except requests.RequestException:
        st.error(
            "Não foi possível cadastrar o cardápio."
        )


# INDICADORES
def render_resumo(cardapios):
    col1, col2 = st.columns(2)

    col1.metric(
        "Cardápios cadastrados",
        len(cardapios)
    )

    col2.metric(
        "Turnos atendidos",
        2
    )


# FORMULÁRIO DE CADASTRO
def render_cadastro():
    st.markdown(
        '<div class="section-title">'
        'Dados do cardápio'
        '</div>',
        unsafe_allow_html=True,
    )

    with st.form("form_cadastro_cardapio"):

        data_cardapio = st.date_input(
            "Data do cardápio *",
            value=None,
            format="DD/MM/YYYY",
            key="cardapio_data",
        )

        alimentos = st.text_area(
            "Alimentos do cardápio *",
            placeholder=(
                "Digite um alimento por linha.\n"
                "Exemplo:\n"
                "Arroz\n"
                "Feijão\n"
                "Frango\n"
                "Salada"
            ),
            height=160,
            max_chars=500,
            key="cardapio_alimentos",
        )

        st.caption(
            "* Campos obrigatórios. "
            "Informe um alimento por linha."
        )

        st.info(
            "O cardápio cadastrado será utilizado "
            "nos turnos manhã e tarde."
        )

        col1, col2 = st.columns(2)

        with col1:
            cadastrar = st.form_submit_button(
                "Cadastrar cardápio",
                width="stretch",
                type="primary",
            )

        with col2:
            st.form_submit_button(
                "Limpar formulário",
                width="stretch",
                on_click=limpar_campos,
            )

    if cadastrar:
        erros = []

        if data_cardapio is None:
            erros.append("Informe a data do cardápio.")

        lista_alimentos = [
            alimento.strip()
            for alimento in alimentos.splitlines()
            if alimento.strip()
        ]

        if not lista_alimentos:
            erros.append("Informe pelo menos um alimento.")

        descricao = ", ".join(lista_alimentos)

        if len(descricao) > 500:
            erros.append(
                "A descrição deve ter até 500 caracteres."
            )

        if erros:
            for erro in erros:
                st.error(erro)

            return

        dados = {
            "data": data_cardapio.isoformat(),
            "descricao": descricao,
        }

        cadastrar_cardapio(dados)


# LISTAGEM E FILTROS
def render_listagem(cardapios):
    st.markdown(
        '<div class="section-title">'
        'Cardápios cadastrados'
        '</div>',
        unsafe_allow_html=True,
    )

    if not cardapios:
        st.info("Nenhum cardápio cadastrado.")
        return

    tipo_consulta = st.selectbox(
        "Tipo de consulta",
        [
            "Todos os cardápios",
            "Consultar por data",
            "Filtrar por período",
        ],
        key="cardapio_tipo_consulta",
    )

    cardapios_filtrados = cardapios

    # CONSULTA POR DATA UTILIZANDO A API
    if tipo_consulta == "Consultar por data":

        data_consulta = st.date_input(
            "Selecione a data",
            value=date.today(),
            format="DD/MM/YYYY",
            key="cardapio_consulta_data",
        )

        cardapios_filtrados = carregar_cardapios(
            data_consulta
        )

        if cardapios_filtrados is None:
            return

    # FILTRO POR PERÍODO NO FRONTEND
    elif tipo_consulta == "Filtrar por período":

        hoje = date.today()

        col1, col2 = st.columns(2)

        with col1:
            data_inicial = st.date_input(
                "Data inicial",
                value=hoje.replace(day=1),
                format="DD/MM/YYYY",
                key="cardapio_data_inicial",
            )

        with col2:
            data_final = st.date_input(
                "Data final",
                value=hoje,
                format="DD/MM/YYYY",
                key="cardapio_data_final",
            )

        if data_inicial > data_final:
            st.error(
                "A data inicial não pode ser "
                "posterior à data final."
            )
            return

        cardapios_filtrados = [
            cardapio
            for cardapio in cardapios
            if data_inicial
            <= date.fromisoformat(cardapio["data"])
            <= data_final
        ]

    if not cardapios_filtrados:
        st.info(
            "Nenhum cardápio encontrado "
            "para a consulta realizada."
        )
        return

    tabela = []

    for cardapio in cardapios_filtrados:

        data_formatada = date.fromisoformat(
            cardapio["data"]
        ).strftime("%d/%m/%Y")

        tabela.append({
            "Data": data_formatada,
            "Cardápio": cardapio["descricao"],
        })

    st.dataframe(
        tabela,
        hide_index=True,
        width="stretch",
    )

    st.caption(
        f"Total de cardápios encontrados: "
        f"{len(cardapios_filtrados)}"
    )


# PÁGINA PRINCIPAL
def render():

    st.markdown(
        '<div class="eyebrow">GESTÃO ALIMENTAR</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<h1 class="hero-title">'
        'Cadastro de cardápios'
        '</h1>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="hero-subtitle">'
        'Organize as refeições e os alimentos '
        'oferecidos pela sua instituição.'
        '</div>',
        unsafe_allow_html=True,
    )

    escola = carregar_escola()

    if escola is None:
        return

    st.caption("Escola vinculada")
    st.write(escola["nome"])

    cardapios = carregar_cardapios()

    if cardapios is None:
        return

    if st.session_state.pop(
        "cardapio_limpar", False
    ):
        limpar_campos()

    mensagem = st.session_state.pop(
        "cardapio_mensagem", None
    )

    if mensagem:
        st.success(mensagem)

    render_resumo(cardapios)

    st.divider()

    render_cadastro()

    st.divider()

    render_listagem(cardapios)

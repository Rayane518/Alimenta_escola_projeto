
import requests
import streamlit as st

from infrastructure.api.api_client import get_api_client


TURNOS = ["Selecione", "MANHÃ", "TARDE"]


# LIMPAR FORMULÁRIO
def limpar_campos():
    st.session_state["turma_identificacao"] = ""
    st.session_state["turma_faixa_etaria"] = ""
    st.session_state["turma_turno"] = "Selecione"
    st.session_state["turma_alunos"] = 0


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
        st.error("Não foi possível conectar ao backend.")

    return None


# LISTAR TURMAS
def carregar_turmas():
    try:
        resposta = get_api_client().get("/api/turmas")

        if resposta.status_code == 200:
            return resposta.json()["turmas"]

        exibir_erro(resposta)

    except requests.RequestException:
        st.error("Não foi possível consultar as turmas.")

    return None


# VALIDAR DADOS
def validar_dados(nome, faixa_etaria, turno, alunos):
    erros = []

    if not nome.strip():
        erros.append("Informe a identificação da turma.")

    if len(nome.strip()) > 100:
        erros.append("O nome deve ter até 100 caracteres.")

    if not faixa_etaria.strip():
        erros.append("Informe a faixa etária.")

    if len(faixa_etaria.strip()) > 20:
        erros.append(
            "A faixa etária deve ter até 20 caracteres."
        )

    if turno not in ("MANHÃ", "TARDE"):
        erros.append("Selecione um turno válido.")

    if alunos < 0:
        erros.append(
            "A quantidade de alunos não pode ser negativa."
        )

    for erro in erros:
        st.error(erro)

    return not erros


# CADASTRAR TURMA
def cadastrar_turma(dados):
    try:
        resposta = get_api_client().post(
            "/api/turmas",
            json=dados
        )

        if resposta.status_code == 201:
            st.session_state["turma_mensagem"] = (
                "Turma cadastrada com sucesso."
            )
            st.session_state["turma_limpar"] = True
            st.rerun()

        exibir_erro(resposta)

    except requests.RequestException:
        st.error("Não foi possível cadastrar a turma.")


# CONSULTAR TURMA ESPECÍFICA
def consultar_turma(id_turma):
    try:
        resposta = get_api_client().get(
            f"/api/turmas/{id_turma}"
        )

        if resposta.status_code == 200:
            return resposta.json()

        exibir_erro(resposta)

    except requests.RequestException:
        st.error("Não foi possível consultar a turma.")

    return None


# ATUALIZAR TURMA
def atualizar_turma(id_turma, dados):
    try:
        resposta = get_api_client().put(
            f"/api/turmas/{id_turma}",
            json=dados
        )

        if resposta.status_code == 200:
            st.session_state["turma_mensagem"] = (
                "Turma atualizada com sucesso."
            )

            st.session_state.pop("turma_em_edicao", None)
            st.rerun()

        exibir_erro(resposta)

    except requests.RequestException:
        st.error("Não foi possível atualizar a turma.")


# ATIVAR OU DESATIVAR TURMA
def alterar_status(id_turma, ativa):
    try:
        resposta = get_api_client().patch(
            f"/api/turmas/{id_turma}/status",
            json={"ativa": bool(ativa)}
        )

        if resposta.status_code == 200:
            mensagem = (
                "Turma reativada com sucesso."
                if ativa
                else "Turma desativada com sucesso."
            )

            st.session_state["turma_mensagem"] = mensagem

            st.session_state.pop(
                "turma_confirmar_status", None
            )

            st.rerun()

        exibir_erro(resposta)

    except requests.RequestException:
        st.error("Não foi possível alterar o status.")


# RESUMO DAS TURMAS
def render_resumo(turmas):
    ativas = [
        turma for turma in turmas
        if turma["ativa"]
    ]

    alunos_manha = sum(
        turma["quantidade_alunos"]
        for turma in ativas
        if turma["turno"] == "MANHÃ"
    )

    alunos_tarde = sum(
        turma["quantidade_alunos"]
        for turma in ativas
        if turma["turno"] == "TARDE"
    )

    col1, col2, col3 = st.columns(3)

    col1.metric("Turmas ativas", len(ativas))
    col2.metric("Alunos — Manhã", alunos_manha)
    col3.metric("Alunos — Tarde", alunos_tarde)


# FORMULÁRIO DE CADASTRO
def render_cadastro():
    st.markdown(
        '<div class="section-title">Dados da turma</div>',
        unsafe_allow_html=True,
    )

    with st.form("form_cadastro_turma"):

        identificacao = st.text_input(
            "Identificação da turma *",
            placeholder="Ex.: Infantil A",
            max_chars=100,
            key="turma_identificacao",
        )

        col1, col2 = st.columns(2)

        with col1:
            faixa_etaria = st.text_input(
                "Faixa etária *",
                placeholder="Ex.: 4-5 anos",
                max_chars=20,
                key="turma_faixa_etaria",
            )

        with col2:
            turno = st.selectbox(
                "Turno *",
                TURNOS,
                format_func=lambda valor: valor.capitalize(),
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
        if validar_dados(
            identificacao,
            faixa_etaria,
            turno,
            alunos
        ):
            dados = {
                "nome": identificacao.strip(),
                "faixa_etaria": faixa_etaria.strip(),
                "turno": turno,
                "quantidade_alunos": int(alunos),
            }

            cadastrar_turma(dados)


# FORMULÁRIO DE EDIÇÃO
def render_edicao(id_turma):
    turma = consultar_turma(id_turma)

    if turma is None:
        if st.button("Cancelar edição"):
            st.session_state.pop("turma_em_edicao", None)
            st.rerun()
        return

    st.markdown(
        '<div class="section-title">Editar turma</div>',
        unsafe_allow_html=True,
    )

    with st.form(f"form_editar_turma_{id_turma}"):

        nome = st.text_input(
            "Identificação da turma *",
            value=turma["nome"],
            max_chars=100,
        )

        col1, col2 = st.columns(2)

        with col1:
            faixa_etaria = st.text_input(
                "Faixa etária *",
                value=turma["faixa_etaria"],
                max_chars=20,
            )

        with col2:
            opcoes = ["MANHÃ", "TARDE"]

            turno = st.selectbox(
                "Turno *",
                opcoes,
                index=opcoes.index(turma["turno"]),
                format_func=lambda valor: valor.capitalize(),
            )

        alunos = st.number_input(
            "Quantidade de alunos *",
            min_value=0,
            value=int(turma["quantidade_alunos"]),
            step=1,
        )

        st.caption(
            "O turno não poderá ser alterado caso "
            "a turma possua histórico de presença."
        )

        col3, col4 = st.columns(2)

        with col3:
            salvar = st.form_submit_button(
                "Salvar alterações",
                type="primary",
                width="stretch",
            )

        with col4:
            cancelar = st.form_submit_button(
                "Cancelar edição",
                width="stretch",
            )

    if cancelar:
        st.session_state.pop("turma_em_edicao", None)
        st.rerun()

    if salvar:
        if validar_dados(
            nome,
            faixa_etaria,
            turno,
            alunos
        ):
            dados = {
                "nome": nome.strip(),
                "faixa_etaria": faixa_etaria.strip(),
                "turno": turno,
                "quantidade_alunos": int(alunos),
            }

            atualizar_turma(id_turma, dados)


# LISTAGEM E GERENCIAMENTO
def render_listagem(turmas):
    st.markdown(
        '<div class="section-title">'
        'Turmas cadastradas'
        '</div>',
        unsafe_allow_html=True,
    )

    if not turmas:
        st.info("Nenhuma turma cadastrada.")
        return

    col1, col2 = st.columns(2)

    with col1:
        filtro_turno = st.selectbox(
            "Filtrar por turno",
            ["Todos", "MANHÃ", "TARDE"],
        )

    with col2:
        filtro_status = st.selectbox(
            "Filtrar por status",
            ["Todos", "Ativas", "Inativas"],
        )

    turmas_filtradas = []

    for turma in turmas:
        if (
            filtro_turno != "Todos"
            and turma["turno"] != filtro_turno
        ):
            continue

        if filtro_status == "Ativas" and not turma["ativa"]:
            continue

        if filtro_status == "Inativas" and turma["ativa"]:
            continue

        turmas_filtradas.append(turma)

    if not turmas_filtradas:
        st.info("Nenhuma turma encontrada com esses filtros.")
        return

    tabela = [
        {
            "Turma": turma["nome"],
            "Faixa etária": turma["faixa_etaria"],
            "Turno": turma["turno"].capitalize(),
            "Alunos": turma["quantidade_alunos"],
            "Status": "Ativa" if turma["ativa"] else "Inativa",
        }
        for turma in turmas_filtradas
    ]

    st.dataframe(
        tabela,
        hide_index=True,
        width="stretch",
    )

    st.caption(
        f"Total de turmas encontradas: {len(turmas_filtradas)}"
    )

    mapa_turmas = {
        turma["id_turma"]: turma
        for turma in turmas_filtradas
    }

    id_selecionado = st.selectbox(
        "Selecione uma turma para gerenciar",
        options=list(mapa_turmas.keys()),
        format_func=lambda id_turma: (
            f'{mapa_turmas[id_turma]["nome"]} — '
            f'{mapa_turmas[id_turma]["turno"].capitalize()}'
        ),
    )

    turma = mapa_turmas[id_selecionado]
    ativa = bool(turma["ativa"])

    col3, col4 = st.columns(2)

    with col3:
        if st.button(
            "Editar turma",
            width="stretch",
            key="btn_editar_turma",
        ):
            st.session_state["turma_em_edicao"] = (
                id_selecionado
            )

            st.session_state.pop(
                "turma_confirmar_status", None
            )

            st.rerun()

    with col4:
        texto_botao = (
            "Desativar turma" if ativa else "Reativar turma"
        )

        if st.button(
            texto_botao,
            width="stretch",
            key="btn_status_turma",
        ):
            st.session_state["turma_confirmar_status"] = {
                "id": id_selecionado,
                "ativa": not ativa,
                "nome": turma["nome"],
            }

    confirmacao = st.session_state.get(
        "turma_confirmar_status"
    )

    if confirmacao:
        acao = (
            "reativar"
            if confirmacao["ativa"]
            else "desativar"
        )

        st.warning(
            f'Deseja realmente {acao} a turma '
            f'{confirmacao["nome"]}?'
        )

        if not confirmacao["ativa"]:
            st.caption(
                "A turma deixará de ser contabilizada "
                "nas matrículas ativas utilizadas nas "
                "novas previsões. O histórico será preservado."
            )

        col5, col6 = st.columns(2)

        with col5:
            if st.button(
                "Confirmar alteração",
                type="primary",
                width="stretch",
            ):
                alterar_status(
                    confirmacao["id"],
                    confirmacao["ativa"],
                )

        with col6:
            if st.button(
                "Cancelar alteração",
                width="stretch",
            ):
                st.session_state.pop(
                    "turma_confirmar_status", None
                )
                st.rerun()


# PÁGINA PRINCIPAL
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
        'Cadastre e gerencie as turmas da sua instituição.'
        '</div>',
        unsafe_allow_html=True,
    )

    escola = carregar_escola()

    if escola is None:
        return

    st.caption("Escola vinculada")
    st.write(escola["nome"])

    turmas = carregar_turmas()

    if turmas is None:
        return

    if st.session_state.pop("turma_limpar", False):
        limpar_campos()

    mensagem = st.session_state.pop(
        "turma_mensagem", None
    )

    if mensagem:
        st.success(mensagem)

    render_resumo(turmas)

    st.divider()

    id_edicao = st.session_state.get("turma_em_edicao")

    if id_edicao is not None:
        render_edicao(id_edicao)
    else:
        render_cadastro()

    st.divider()

    render_listagem(turmas)

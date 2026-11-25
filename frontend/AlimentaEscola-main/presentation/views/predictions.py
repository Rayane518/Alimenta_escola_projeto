
from datetime import datetime

import requests
import streamlit as st

from infrastructure.api.api_client import get_api_client


TURNOS = ["Selecione", "Manhã", "Tarde"]


def limpar_campos():
    st.session_state["previsao_data"] = None
    st.session_state["previsao_turno"] = "Selecione"
    st.session_state["previsao_cardapio"] = ""
    st.session_state["previsao_margem"] = 10

    st.session_state.pop("resultado_previsao", None)
    st.session_state.pop("cardapio_resultado", None)


def aplicar_estilos():
    st.markdown(
        """
        <style>

        .resultado-card {
            background-color: #ffffff;
            border: 1px solid #dce5f2;
            border-radius: 14px;
            padding: 20px;
            margin-bottom: 16px;
            min-height: 145px;
            box-shadow: 0 3px 10px rgba(16,44,80,.05);
        }

        .resultado-label {
            font-size: 14px;
            font-weight: 600;
            color: #526780;
        }

        .resultado-valor {
            font-size: 36px;
            font-weight: 800;
            color: #2057b5;
            margin: 8px 0;
        }

        .resultado-descricao {
            font-size: 12px;
            color: #788ba3;
        }

        .resultado-total {
            background: linear-gradient(
                120deg, #102c50, #2865d9
            );
            border-radius: 16px;
            padding: 28px 15px;
            text-align: center;
            color: #ffffff;
            margin: 12px 0 24px;
        }

        .resultado-total-titulo {
            font-size: 17px;
            font-weight: 600;
        }

        .resultado-total-valor {
            font-size: 42px;
            font-weight: 800;
            margin: 10px 0;
        }

        .resultado-total-descricao {
            font-size: 13px;
            opacity: .85;
        }

        </style>
        """,
        unsafe_allow_html=True,
    )



def criar_cartao(titulo, valor, descricao):
    html = (
        '<div class="resultado-card">'
        f'<div class="resultado-label">{titulo}</div>'
        f'<div class="resultado-valor">{valor}</div>'
        f'<div class="resultado-descricao">{descricao}</div>'
        '</div>'
    )

    st.markdown(html, unsafe_allow_html=True)


def mostrar_resultado(resultado):

    try:
        alunos = int(
            resultado["alunos_estimados"]
        )

        refeicoes = int(
            resultado["refeicoes_estimadas"]
        )

        margem = float(
            resultado["margem_seguranca"]
        )

        recomendado = int(
            resultado["refeicoes_recomendadas"]
        )

        data = datetime.strptime(
            resultado["data_prevista"],
            "%Y-%m-%d",
        ).strftime("%d/%m/%Y")

        turno = resultado["turno"].capitalize()

    except (KeyError, ValueError, TypeError, AttributeError):
        st.error(
            "Não foi possível apresentar os resultados "
            "retornados pelo servidor."
        )
        return

    adicionais = recomendado - refeicoes

    st.success("Previsão gerada com sucesso!")

    st.markdown(
        '<div class="section-title">'
        'Resultado da previsão'
        '</div>',
        unsafe_allow_html=True,
    )

    with st.container(border=True):

        col_data, col_turno = st.columns(2)

        with col_data:
            st.caption("Data da previsão")
            st.markdown(f"**{data}**")

        with col_turno:
            st.caption("Turno")
            st.markdown(f"**{turno}**")

        cardapio = st.session_state.get(
            "cardapio_resultado"
        )

        if cardapio:
            st.caption("Cardápio")
            st.write(cardapio)

    st.markdown(" ")

    col1, col2 = st.columns(2)

    with col1:
        criar_cartao(
            "Alunos estimados",
            alunos,
            "Estimativa de presença no turno",
        )

    with col2:
        criar_cartao(
            "Refeições previstas",
            refeicoes,
            "Demanda estimada pelo modelo",
        )

    col3, col4 = st.columns(2)

    with col3:
        criar_cartao(
            "Margem de segurança",
            f"{margem:g}%",
            "Percentual definido pelo gestor",
        )

    with col4:
        criar_cartao(
            "Refeições adicionais",
            adicionais,
            "Quantidade adicional de segurança",
        )

    st.markdown(
        f"""
        <div class="resultado-total">

            <div class="resultado-total-titulo">
                Total de refeições recomendadas
            </div>

            <div class="resultado-total-valor">
                {recomendado} refeições
            </div>

            <div class="resultado-total-descricao">
                Quantidade recomendada para preparação
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.expander("Detalhes da previsão"):

        st.write(
            "**Identificação da previsão:**",
            resultado.get(
                "id_previsao",
                "Não informado",
            ),
        )

        st.write(
            "**Tipo de previsão:**",
            str(
                resultado.get(
                    "tipo_previsao",
                    "Não informado",
                )
            ).capitalize(),
        )

        origem = resultado.get(
            "origem_presenca",
            "Não informado",
        )

        if origem == "machine_learning":
            origem = "Machine Learning"

        st.write(
            "**Origem da estimativa de presença:**",
            origem,
        )

        st.write(
            "**Modelo utilizado:**",
            resultado.get(
                "modelo_utilizado",
                "Não informado",
            ),
        )

        st.divider()

        st.markdown("**Cálculo da recomendação**")

        st.write(
            f"{refeicoes} refeições previstas + "
            f"{adicionais} refeições adicionais = "
            f"{recomendado} refeições recomendadas."
        )

    st.info(
        resultado.get(
            "observacao",
            "Estimativa de apoio ao planejamento; "
            "deve ser validada pela equipe escolar.",
        )
    )

    if resultado.get("id_previsao") is not None:
        st.caption(
            "Previsão registrada no histórico do sistema."
        )


def gerar_previsao(data, turno, cardapio, margem):

    dados = {
        "data": data.isoformat(),
        "turno": turno.upper(),
        "cardapio": cardapio.strip(),
        "tipo_previsao": "antecipada",
        "margem_seguranca": margem,
    }

    try:
        with st.spinner(
            "Analisando os dados e gerando previsão..."
        ):

            resposta = get_api_client().post(
                "/api/previsao",
                json=dados,
            )

        if resposta.status_code in (200, 201):

            try:
                resultado = resposta.json()

            except ValueError:
                st.error(
                    "O servidor retornou uma resposta inválida."
                )
                return

            if not isinstance(resultado, dict):
                st.error(
                    "Formato de resposta inesperado."
                )
                return

            st.session_state["resultado_previsao"] = (
                resultado
            )

            st.session_state["cardapio_resultado"] = (
                cardapio.strip()
            )

        elif resposta.status_code == 401:

            st.error(
                "Sessão expirada. Saia e entre novamente."
            )

        else:

            mensagem = (
                f"Não foi possível gerar a previsão. "
                f"Código: {resposta.status_code}"
            )

            try:
                erro_api = resposta.json()

                if isinstance(erro_api, dict):
                    mensagem = (
                        erro_api.get("mensagem")
                        or erro_api.get("erro")
                        or erro_api.get("message")
                        or mensagem
                    )

            except ValueError:
                pass

            st.error(mensagem)

    except requests.exceptions.Timeout:

        st.error(
            "O servidor demorou para responder. "
            "Consulte o histórico antes de tentar novamente."
        )

    except requests.exceptions.RequestException:

        st.error(
            "Não foi possível conectar ao backend. "
            "Verifique se o Flask está funcionando."
        )


def render():

    aplicar_estilos()

    st.markdown(
        '<div class="eyebrow">'
        'INTELIGÊNCIA ARTIFICIAL'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<h1 class="hero-title">'
        'Gerar previsões'
        '</h1>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="hero-subtitle">'
        'Estime a demanda por refeições escolares '
        'com apoio de Machine Learning.'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="section-title">'
        'Dados da previsão'
        '</div>',
        unsafe_allow_html=True,
    )

    with st.form("form_gerar_previsao"):

        data = st.date_input(
            "Data da previsão *",
            value=None,
            key="previsao_data",
            format="DD/MM/YYYY",
        )

        turno = st.selectbox(
            "Turno *",
            TURNOS,
            key="previsao_turno",
        )

        cardapio = st.text_input(
            "Cardápio *",
            placeholder="Ex.: Arroz, feijão e legumes",
            key="previsao_cardapio",
        )

        margem = st.slider(
            "Margem de segurança (%)",
            min_value=0,
            max_value=20,
            value=10,
            step=1,
            key="previsao_margem",
        )

        st.caption(
            "A margem de segurança adiciona refeições "
            "à quantidade prevista pelo modelo."
        )

        st.info(
            "A quantidade de alunos presentes será "
            "estimada automaticamente pelo sistema, "
            "considerando as turmas ativas do turno."
        )

        st.caption("* Campos obrigatórios.")

        col1, col2 = st.columns(2)

        with col1:
            gerar = st.form_submit_button(
                "Gerar previsão",
                width="stretch",
                type="primary",
            )

        with col2:
            st.form_submit_button(
                "Limpar formulário",
                width="stretch",
                on_click=limpar_campos,
            )

    if gerar:

        st.session_state.pop(
            "resultado_previsao",
            None,
        )

        st.session_state.pop(
            "cardapio_resultado",
            None,
        )

        erros = []

        if data is None:
            erros.append(
                "Informe a data da previsão."
            )

        if turno == "Selecione":
            erros.append(
                "Selecione o turno."
            )

        if not cardapio.strip():
            erros.append(
                "Informe o cardápio."
            )

        if erros:

            for erro in erros:
                st.error(erro)

        else:

            gerar_previsao(
                data,
                turno,
                cardapio,
                margem,
            )

    resultado = st.session_state.get(
        "resultado_previsao"
    )

    if resultado is not None:

        st.divider()

        mostrar_resultado(resultado)


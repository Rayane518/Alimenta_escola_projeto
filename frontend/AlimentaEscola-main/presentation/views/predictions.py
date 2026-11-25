from datetime import date, datetime

import requests
import streamlit as st

from infrastructure.api.api_client import get_api_client

TURNOS = ["Manhã", "Tarde"]


def limpar_resultado():
    st.session_state.pop("resultado_previsao", None)
    st.session_state.pop("cardapio_resultado", None)


def limpar_campos():
    st.session_state["previsao_data"] = None
    st.session_state["previsao_turno"] = None
    st.session_state["previsao_cardapio"] = None
    st.session_state["previsao_margem"] = 10
    limpar_resultado()


def consultar_lista(endpoint):
    try:
        resposta = get_api_client().get(endpoint)
        if resposta.status_code == 401:
            st.error("Sessão expirada. Realize o login novamente.")
            return None
        if resposta.status_code != 200:
            st.error(f"Não foi possível consultar {endpoint}.")
            return None
        dados = resposta.json()
        if not isinstance(dados, list) or any(not isinstance(item, dict) for item in dados):
            raise ValueError("Formato inválido")
        return dados
    except (requests.RequestException, ValueError):
        st.error(f"Falha ao consultar {endpoint}. Verifique o backend.")
        return None


def turnos_disponiveis(historico, data):
    if data is None:
        return []
    ocupados = {item["turno"].upper() for item in historico
                if item["data_prevista"] == data.isoformat()}
    return [turno for turno in TURNOS if turno.upper() not in ocupados]


def aplicar_estilos():
    st.markdown(
        """
        <style>
        .resultado-card {
            background: #ffffff;
            border: 1px solid #dce5f2;
            border-radius: 14px;
            padding: 20px;
            margin-bottom: 14px;
            min-height: 145px;
            box-shadow: 0 3px 10px rgba(16,44,80,.05);
        }

        .resultado-label {
            color: #526780;
            font-size: 14px;
            font-weight: 600;
        }

        .resultado-valor {
            color: #2057b5;
            font-size: 36px;
            font-weight: 800;
            margin: 6px 0;
        }

        .resultado-descricao {
            color: #788ba3;
            font-size: 12px;
        }

        .resultado-total {
            background: linear-gradient(
                120deg, #102c50, #2057b5
            );
            border-radius: 16px;
            padding: 28px 15px;
            text-align: center;
            color: #ffffff;
            margin: 10px 0 24px;
            box-shadow: 0 4px 12px rgba(16,44,80,.15);
        }

        .resultado-total-titulo {
            font-size: 16px;
            font-weight: 600;
        }

        .resultado-total-valor {
            font-size: 42px;
            font-weight: 800;
            margin: 8px 0;
        }

        .resultado-total-descricao {
            font-size: 13px;
            opacity: .85;
        }

        div[data-testid="stSlider"] [role="slider"] {
            background-color: #2865d9 !important;
        }

        div[data-testid="stSlider"] [data-testid="stThumbValue"] {
            color: #2865d9 !important;
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
        alunos = int(resultado["alunos_estimados"])
        refeicoes = int(resultado["refeicoes_estimadas"])
        margem = float(resultado["margem_seguranca"])
        recomendado = int(resultado["refeicoes_recomendadas"])

        data = datetime.strptime(
            resultado["data_prevista"],
            "%Y-%m-%d",
        ).strftime("%d/%m/%Y")

        turno = resultado["turno"].capitalize()

    except (KeyError, ValueError, TypeError):
        st.error(
            "Não foi possível apresentar os resultados. "
            "Verifique os dados retornados pelo servidor."
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

    col_data, col_turno = st.columns(2)

    with col_data:
        st.markdown(f"**Data da previsão:** {data}")

    with col_turno:
        st.markdown(f"**Turno:** {turno}")

    cardapio = st.session_state.get(
        "cardapio_resultado"
    )

    if cardapio:
        st.write("**Cardápio:**", cardapio)

    st.divider()

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
            "Demanda estimada pelo Machine Learning",
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

    html_total = (
        '<div class="resultado-total">'
        '<div class="resultado-total-titulo">'
        'Total de refeições recomendadas'
        '</div>'
        '<div class="resultado-total-valor">'
        f'{recomendado} refeições'
        '</div>'
        '<div class="resultado-total-descricao">'
        'Quantidade recomendada para preparação'
        '</div>'
        '</div>'
    )

    st.markdown(html_total, unsafe_allow_html=True)

    with st.expander("Detalhes da previsão"):

        st.write(
            "**Identificação da previsão:**",
            resultado.get("id_previsao", "Não informado"),
        )

        st.write(
            "**Tipo de previsão:**",
            resultado.get(
                "tipo_previsao",
                "Não informado",
            ).capitalize(),
        )

        origem = resultado.get("origem_presenca")

        if origem == "machine_learning":
            origem = "Machine Learning"

        st.write(
            "**Origem da estimativa de presença:**",
            origem or "Não informado",
        )

        st.write(
            "**Modelo utilizado:**",
            resultado.get(
                "modelo_utilizado",
                "Não informado",
            ),
        )

        st.markdown("**Cálculo da recomendação:**")

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


def render():
    aplicar_estilos()
    st.markdown('<div class="eyebrow">INTELIGÊNCIA ARTIFICIAL</div>', unsafe_allow_html=True)
    st.markdown('<h1 class="hero-title">Gerar previsões</h1>', unsafe_allow_html=True)
    st.markdown('<div class="hero-subtitle">Estime a demanda por refeições escolares com apoio de Machine Learning.</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Dados da previsão</div>', unsafe_allow_html=True)

    historico = consultar_lista("/api/previsoes/historico")
    menus = consultar_lista("/api/cardapios")
    if historico is None or menus is None:
        return
    try:
        for item in historico:
            date.fromisoformat(item["data_prevista"])
            if item["turno"].upper() not in ("MANHÃ", "TARDE"):
                raise ValueError("Turno inválido")
        opcoes = sorted({item["descricao"].strip() for item in menus
                         if item["descricao"].strip()}, key=str.casefold)
    except (KeyError, TypeError, ValueError, AttributeError):
        st.error("Dados de histórico ou cardápios inválidos.")
        return

    hoje = date.today()
    if st.session_state.get("previsao_data") is not None and st.session_state["previsao_data"] < hoje:
        limpar_campos()

    data = st.date_input("Data da previsão *", value=None, min_value=hoje,
                         key="previsao_data", format="DD/MM/YYYY",
                         on_change=limpar_resultado)
    disponiveis = turnos_disponiveis(historico, data)
    if data is not None and not disponiveis:
        st.warning("Os dois turnos já possuem previsão. Consulte o histórico de previsões.")
    elif data is not None and len(disponiveis) == 1:
        st.info("O outro turno já possui previsão. Consulte o histórico para visualizá-la.")
    if not opcoes:
        st.warning("Cadastre um cardápio antes de gerar uma previsão.")

    if st.session_state.get("previsao_turno") not in disponiveis:
        st.session_state["previsao_turno"] = None
    if st.session_state.get("previsao_cardapio") not in opcoes:
        st.session_state["previsao_cardapio"] = None

    turno = st.selectbox("Turno disponível *", disponiveis, index=None,
                         placeholder="Selecione o turno", key="previsao_turno",
                         disabled=not disponiveis, on_change=limpar_resultado)
    cardapio = st.selectbox("Cardápio *", opcoes, index=None,
                            placeholder="Selecione um cardápio cadastrado",
                            key="previsao_cardapio", disabled=not opcoes,
                            on_change=limpar_resultado)
    margem = st.slider("Margem de segurança (%)", 0, 20, 10, step=1,
                       key="previsao_margem", on_change=limpar_resultado)
    st.caption("A margem de segurança adiciona refeições à quantidade prevista pelo modelo.")
    st.info("A quantidade de alunos presentes será estimada automaticamente pelo sistema, considerando as turmas ativas do turno.")
    st.caption("* Campos obrigatórios.")
    col1, col2 = st.columns(2)
    with col1:
        gerar = st.button("Gerar previsão", width="stretch", type="primary",
                          disabled=not (data and turno in disponiveis and cardapio in opcoes))
    with col2:
        st.button("Limpar formulário", width="stretch", on_click=limpar_campos)

    if gerar:
        limpar_resultado()
        if data is None or data < date.today() or turno not in disponiveis or cardapio not in opcoes:
            st.error("Selecione uma data, turno e cardápio válidos.")
            return
        dados = {"data": data.isoformat(), "turno": turno.upper(),
                 "cardapio": cardapio, "tipo_previsao": "antecipada",
                 "margem_seguranca": margem}
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
                    resultado_api = resposta.json()

                except ValueError:
                    st.error(
                        "O servidor retornou uma "
                        "resposta inválida."
                    )
                    return

                if not isinstance(resultado_api, dict):
                    st.error(
                        "Formato de resposta inesperado."
                    )
                    return

                st.session_state["resultado_previsao"] = (
                    resultado_api
                )

                st.session_state["cardapio_resultado"] = (
                    cardapio.strip()
                )
                st.rerun()

            elif resposta.status_code == 401:

                st.error(
                    "Sessão expirada. "
                    "Saia e entre novamente."
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
                "Consulte o histórico antes de tentar "
                "gerar a mesma previsão novamente."
            )

        except requests.exceptions.RequestException:

            st.error(
                "Não foi possível conectar ao backend. "
                "Verifique se o Flask está funcionando."
            )

    resultado = st.session_state.get("resultado_previsao")
    if resultado is not None:
        st.divider()
        mostrar_resultado(resultado)

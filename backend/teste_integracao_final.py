import requests
from getpass import getpass
from datetime import date, timedelta

BASE_URL = "http://127.0.0.1:5000/api"

# Usar uma data futura para a demonstração
DATA_TESTE = (
    date.today() + timedelta(days=1)
).isoformat()


def mostrar_resultado(nome, resposta):
    print(f"\n=== {nome} ===")
    print("STATUS:", resposta.status_code)

    try:
        print("RESPOSTA:", resposta.json())
    except ValueError:
        print("RESPOSTA:", resposta.text)


def executar_testes():
    print("=== ALIMENTA ESCOLA ===")
    print("TESTE FINAL DO BACKEND")

    email = input("E-mail do gestor: ")
    senha = getpass("Senha do gestor: ")

    with requests.Session() as sessao:

        # 1. LOGIN
        resposta = sessao.post(
            f"{BASE_URL}/login",
            json={
                "email": email,
                "senha": senha
            },
            timeout=10
        )

        mostrar_resultado("LOGIN", resposta)

        if resposta.status_code != 200:
            print("Login não realizado. Testes encerrados.")
            return

        # 2. VERIFICAR SESSÃO
        resposta = sessao.get(
            f"{BASE_URL}/me",
            timeout=10
        )

        mostrar_resultado("SESSÃO", resposta)

        # 3. PREVISÃO ANTECIPADA
        dados_antecipada = {
            "data": DATA_TESTE,
            "turno": "MANHÃ",
            "tipo_previsao": "ANTECIPADA",
            "cardapio": "Arroz, feijão e frango",
            "margem_seguranca": 10
        }

        resposta = sessao.post(
            f"{BASE_URL}/previsao",
            json=dados_antecipada,
            timeout=30
        )

        mostrar_resultado(
            "PREVISÃO ANTECIPADA",
            resposta
        )

        # 4. PREVISÃO ATUALIZADA
        dados_atualizada = {
            "data": DATA_TESTE,
            "turno": "MANHÃ",
            "tipo_previsao": "ATUALIZADA",
            "alunos_referencia": 40,
            "cardapio": "Arroz, feijão e frango",
            "margem_seguranca": 10
        }

        resposta = sessao.post(
            f"{BASE_URL}/previsao",
            json=dados_atualizada,
            timeout=30
        )

        mostrar_resultado(
            "PREVISÃO ATUALIZADA",
            resposta
        )

        # 5. HISTÓRICO DE PREVISÕES
        resposta = sessao.get(
            f"{BASE_URL}/previsoes/historico",
            timeout=10
        )

        mostrar_resultado(
            "HISTÓRICO DE PREVISÕES",
            resposta
        )

        # 6. INDICADORES
        resposta = sessao.get(
            f"{BASE_URL}/indicadores",
            timeout=10
        )

        mostrar_resultado(
            "INDICADORES",
            resposta
        )

        # 7. LOGOUT
        resposta = sessao.post(
            f"{BASE_URL}/logout",
            timeout=10
        )

        mostrar_resultado("LOGOUT", resposta)

        # 8. VERIFICAR SESSÃO ENCERRADA
        resposta = sessao.get(
            f"{BASE_URL}/me",
            timeout=10
        )

        mostrar_resultado(
            "ACESSO APÓS LOGOUT",
            resposta
        )

    print("\n=== TESTES FINALIZADOS ===")


if __name__ == "__main__":
    try:
        executar_testes()
    except requests.RequestException as erro:
        print("Erro de comunicação com o backend:", erro)

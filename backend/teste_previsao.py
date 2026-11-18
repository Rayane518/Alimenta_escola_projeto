import requests

BASE_URL = "http://127.0.0.1:5000"

sessao = requests.Session()

# 1. Autenticar o gestor
print("\n=== TESTE DE LOGIN ===")

email = input("E-mail do gestor: ")
senha = input("Senha do gestor: ")

resposta = sessao.post(
    f"{BASE_URL}/api/login",
    json={
        "email": email,
        "senha": senha
    },
    timeout=15
)

print("Status:", resposta.status_code)
print("Resposta:", resposta.json())

if resposta.status_code != 200:
    raise SystemExit("Login falhou. Teste encerrado.")

# 2. Solicitar previsão
print("\n=== TESTE DE PREVISÃO ===")

dados = {
    "data": "2026-11-20",
    "turno": "MANHÃ",
    "tipo_previsao": "ANTECIPADA",
    "cardapio": "Arroz, feijão e frango",
    "margem_seguranca": 10
}

resposta = sessao.post(
    f"{BASE_URL}/api/previsao",
    json=dados,
    timeout=60
)

print("Status:", resposta.status_code)
print("Resposta:", resposta.json())

if resposta.status_code != 201:
    raise SystemExit("Erro ao gerar previsão.")

resultado = resposta.json()

# 3. Conferir margem de segurança
print("\n=== RESULTADO ===")

print(
    "Alunos estimados:",
    resultado.get("alunos_estimados")
)

print(
    "Previsão original:",
    resultado.get("refeicoes_estimadas")
)

print(
    "Margem aplicada:",
    resultado.get("margem_seguranca"),
    "%"
)

print(
    "Quantidade recomendada:",
    resultado.get("refeicoes_recomendadas")
)

print(
    "ID da previsão:",
    resultado.get("id_previsao")
)

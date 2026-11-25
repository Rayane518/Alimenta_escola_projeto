
from infrastructure.api.api_client import get_api_client


def login(email, senha):
    return get_api_client().post(
        "/api/login",
        json={
            "email": email,
            "senha": senha
        }
    )


def usuario_atual():
    return get_api_client().get("/api/me")


def logout():
    return get_api_client().post("/api/logout")

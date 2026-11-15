from flask import (
    Blueprint,
    jsonify,
    request,
    session,
    current_app
)

from app.services.auth_service import AuthService
from app.domain.exceptions.business_error import BusinessError


auth_bp = Blueprint("auth", __name__)
service = AuthService()


@auth_bp.post("/login")
def login():
    try:
        dados = request.get_json(silent=True)

        if not isinstance(dados, dict):
            return jsonify({
                "erro": "Envie um JSON com e-mail e senha."
            }), 400

        email = dados.get("email")
        senha = dados.get("senha")

        usuario = service.login(email, senha)

        session.clear()
        session["id_usuario"] = usuario["id_usuario"]
        session["id_escola"] = usuario["id_escola"]

        return jsonify({
            "mensagem": "Login realizado com sucesso.",
            "usuario": usuario
        }), 200

    except BusinessError as error:
        return jsonify({"erro": str(error)}), 401

    except Exception:
        current_app.logger.exception(
            "Erro inesperado na autenticação."
        )
        return jsonify({
            "erro": "Não foi possível realizar o login."
        }), 500


@auth_bp.get("/me")
def usuario_autenticado():
    if "id_usuario" not in session:
        return jsonify({
            "erro": "Usuário não autenticado."
        }), 401

    return jsonify({
        "id_usuario": session["id_usuario"],
        "id_escola": session["id_escola"]
    }), 200


@auth_bp.post("/logout")
def logout():
    session.clear()

    return jsonify({
        "mensagem": "Logout realizado com sucesso."
    }), 200

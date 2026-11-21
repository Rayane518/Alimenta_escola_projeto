
from flask import (
    Blueprint,
    jsonify,
    request,
    session,
    current_app
)

from mysql.connector import IntegrityError

from app.services.menu_service import MenuService
from app.domain.exceptions.business_error import BusinessError


menu_bp = Blueprint("menu", __name__)
service = MenuService()


@menu_bp.post("/cardapios")
def register_menu():

    id_escola = session.get("id_escola")
    id_usuario = session.get("id_usuario")

    if id_escola is None or id_usuario is None:
        return jsonify({
            "erro": "Usuário não autenticado."
        }), 401

    try:
        dados = request.get_json(silent=True)

        resultado = service.register_menu(
            id_escola,
            dados
        )

        return jsonify(resultado), 201

    except BusinessError as error:
        return jsonify({
            "erro": str(error)
        }), 400

    except IntegrityError as error:

        if error.errno == 1062:
            return jsonify({
                "erro": (
                    "Já existe um cardápio cadastrado "
                    "para esta data."
                )
            }), 409

        current_app.logger.exception(
            "Erro de integridade ao cadastrar cardápio."
        )

        return jsonify({
            "erro": "Não foi possível cadastrar o cardápio."
        }), 500

    except Exception:
        current_app.logger.exception(
            "Erro inesperado ao cadastrar cardápio."
        )

        return jsonify({
            "erro": "Não foi possível cadastrar o cardápio."
        }), 500


@menu_bp.get("/cardapios")
def get_menus():

    id_escola = session.get("id_escola")
    id_usuario = session.get("id_usuario")

    if id_escola is None or id_usuario is None:
        return jsonify({
            "erro": "Usuário não autenticado."
        }), 401

    try:
        target_date = request.args.get("data")

        resultado = service.get_menus(
            id_escola,
            target_date
        )

        return jsonify(resultado), 200

    except BusinessError as error:
        return jsonify({
            "erro": str(error)
        }), 400

    except Exception:
        current_app.logger.exception(
            "Erro inesperado ao consultar cardápios."
        )

        return jsonify({
            "erro": "Não foi possível consultar os cardápios."
        }), 500

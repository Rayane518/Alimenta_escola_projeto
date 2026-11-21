
from flask import (
    Blueprint,
    jsonify,
    request,
    session,
    current_app
)

from mysql.connector import IntegrityError
from app.services.meal_service import MealService
from app.domain.exceptions.business_error import BusinessError


meal_bp = Blueprint("meal", __name__)
service = MealService()


@meal_bp.post("/merenda")
def register_meal():

    # Verificar autenticação
    id_escola = session.get("id_escola")
    id_usuario = session.get("id_usuario")

    if id_escola is None or id_usuario is None:
        return jsonify({
            "erro": "Usuário não autenticado."
        }), 401

    try:
        # Receber os dados do frontend
        dados = request.get_json(silent=True)

        # Validar e salvar o registro
        resultado = service.register_meal(
            id_escola,
            dados
        )

        return jsonify(resultado), 201

    except BusinessError as error:
        return jsonify({
            "erro": str(error)
        }), 400

    except IntegrityError as error:

        # Registro duplicado
        if error.errno == 1062:
            return jsonify({
                "erro": (
                    "Já existe um registro de merenda "
                    "para esta data e turno."
                )
            }), 409

        # Violação de chave estrangeira
        if error.errno == 1452:
            return jsonify({
                "erro": (
                    "Cardápio inválido ou incompatível "
                    "com a escola e a data informadas."
                )
            }), 400

        current_app.logger.exception(
            "Erro de integridade ao registrar merenda."
        )

        return jsonify({
            "erro": "Não foi possível registrar a merenda."
        }), 500

    except Exception:
        current_app.logger.exception(
            "Erro inesperado ao registrar merenda."
        )

        return jsonify({
            "erro": "Não foi possível registrar a merenda."
        }), 500

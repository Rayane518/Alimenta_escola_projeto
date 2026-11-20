from flask import (
    Blueprint,
    jsonify,
    request,
    session,
    current_app
)

from app.services.school_service import SchoolService
from app.domain.exceptions.business_error import BusinessError


school_bp = Blueprint("school", __name__)
service = SchoolService()


@school_bp.get("/escola")
def get_school():
    school_id = session.get("id_escola")

    if not session.get("id_usuario") or not school_id:
        return jsonify({
            "erro": "Usuário não autenticado."
        }), 401

    try:
        school = service.get_school(school_id)
        return jsonify(school), 200

    except BusinessError as error:
        return jsonify({"erro": str(error)}), 404

    except Exception:
        current_app.logger.exception(
            "Erro ao consultar escola."
        )
        return jsonify({
            "erro": "Erro interno ao consultar escola."
        }), 500


@school_bp.put("/escola")
def update_school():
    school_id = session.get("id_escola")

    if not session.get("id_usuario") or not school_id:
        return jsonify({
            "erro": "Usuário não autenticado."
        }), 401

    try:
        data = request.get_json(silent=True)
        school = service.update_school(school_id, data)

        return jsonify({
            "mensagem": "Escola atualizada com sucesso.",
            "escola": school
        }), 200

    except BusinessError as error:
        return jsonify({"erro": str(error)}), 400

    except Exception:
        current_app.logger.exception(
            "Erro ao atualizar escola."
        )
        return jsonify({
            "erro": "Erro interno ao atualizar escola."
        }), 500

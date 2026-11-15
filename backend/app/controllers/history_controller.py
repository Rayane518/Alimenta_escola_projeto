from flask import (
    Blueprint,
    jsonify,
    session,
    current_app
)

from app.services.history_service import HistoryService


history_bp = Blueprint("history", __name__)
service = HistoryService()


def _school_id():
    # Obtém a escola vinculada ao gestor autenticado
    id_escola = session.get("id_escola")

    if id_escola is None:
        return None

    return id_escola


@history_bp.get("/historico")
def history():

    id_escola = _school_id()

    if id_escola is None:
        return jsonify({
            "erro": "Usuário não autenticado."
        }), 401

    try:
        resultado = service.get_history(id_escola)

        return jsonify(resultado), 200

    except ValueError as error:
        return jsonify({
            "erro": str(error)
        }), 400

    except Exception:
        current_app.logger.exception(
            "Erro inesperado ao consultar o histórico."
        )

        return jsonify({
            "erro": "Não foi possível consultar o histórico."
        }), 500


@history_bp.get("/indicadores")
def indicators():

    id_escola = _school_id()

    if id_escola is None:
        return jsonify({
            "erro": "Usuário não autenticado."
        }), 401

    try:
        resultado = service.get_indicators(id_escola)

        return jsonify(resultado), 200

    except ValueError as error:
        return jsonify({
            "erro": str(error)
        }), 400

    except Exception:
        current_app.logger.exception(
            "Erro inesperado ao calcular os indicadores."
        )

        return jsonify({
            "erro": "Não foi possível calcular os indicadores."
        }), 500
    
@history_bp.get("/previsoes/historico")
def predictions_history():

    id_escola = _school_id()

    if id_escola is None:
        return jsonify({
            "erro": "Usuário não autenticado."
        }), 401

    try:
        resultado = service.get_predictions_history(id_escola)

        return jsonify(resultado), 200

    except Exception:
        current_app.logger.exception(
            "Erro ao consultar o histórico de previsões."
        )

        return jsonify({
            "erro": "Não foi possível consultar as previsões."
        }), 500

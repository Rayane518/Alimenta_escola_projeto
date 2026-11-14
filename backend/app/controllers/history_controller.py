from flask import Blueprint, jsonify, request, current_app
from app.services.history_service import HistoryService

history_bp = Blueprint("history", __name__)
service = HistoryService()

def _school_id():
    value = request.args.get("id_escola")
    if value is None:
        return None
    try:
        parsed = int(value)
        if parsed <= 0: raise ValueError
        return parsed
    except ValueError:
        raise ValueError("id_escola deve ser um inteiro positivo.")

@history_bp.get("/historico")
def history():
    try:
        return jsonify(service.get_history(_school_id())), 200
    except ValueError as error:
        return jsonify({"erro": str(error)}), 400
    except Exception:
        current_app.logger.exception(
            "Erro inesperado ao consultar o histórico."
        )
        return jsonify({
            "erro": "Não foi possível consultar o histórico."
        }), 500
    
@history_bp.get("/indicadores")
def indicators():
    try:
        return jsonify(service.get_indicators(_school_id())), 200
    except ValueError as error:
        return jsonify({"erro": str(error)}), 400
    except Exception:
        current_app.logger.exception(
            "Erro inesperado ao calcular os indicadores."
        )
        return jsonify({
            "erro": "Não foi possível calcular os indicadores."
        }), 500
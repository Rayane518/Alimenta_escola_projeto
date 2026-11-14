from flask import Blueprint, jsonify, current_app
from app.services.health_service import database_status

health_bp = Blueprint("health", __name__)


@health_bp.get("/api/saude")
def health():
    try:
        return jsonify(database_status()), 200

    except Exception:
        current_app.logger.exception(
            "Erro ao verificar a conexão com o MySQL."
        )

        return jsonify({
            "api": "online",
            "mysql": "erro_na_conexao"
        }), 503


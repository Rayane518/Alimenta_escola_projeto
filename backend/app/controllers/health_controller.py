from flask import Blueprint, jsonify
from app.services.health_service import database_status

health_bp = Blueprint("health", __name__)

@health_bp.get("/api/saude")
def health():
    try:
        return jsonify(database_status()), 200
    except Exception:
        # Não expõe detalhes internos/credenciais da conexão na resposta pública.
        return jsonify({"api": "online", "mysql": "erro_na_conexao"}), 503

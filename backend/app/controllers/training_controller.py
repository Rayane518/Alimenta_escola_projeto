from flask import Blueprint, jsonify, current_app, session

from app.services.training_service import TrainingService
from app.domain.exceptions.business_error import BusinessError


training_bp = Blueprint("training", __name__)
service = TrainingService()


@training_bp.post("/modelo/treinar")
def train_model():


    id_usuario = session.get("id_usuario")
    id_escola = session.get("id_escola")

    if id_usuario is None or id_escola is None:
        return jsonify({
            "erro": "Usuário não autenticado."
        }), 401

    try:
       
        resultado = service.train(id_escola)

        
        return jsonify(resultado), 200

    except BusinessError as error:
        return jsonify({
            "erro": str(error)
        }), 400

    except Exception:
        current_app.logger.exception(
            "Erro inesperado ao treinar os modelos."
        )

        return jsonify({
            "erro": "Não foi possível treinar os modelos."
        }), 500

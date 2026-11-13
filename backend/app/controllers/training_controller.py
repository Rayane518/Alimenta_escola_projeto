from flask import Blueprint, jsonify, request
from app.services.training_service import TrainingService
from app.domain.exceptions.business_error import BusinessError

training_bp = Blueprint("training", __name__)
service = TrainingService()

@training_bp.post("/modelo/treinar")
def train_model():
    try:
        payload = request.get_json(silent=True) or {}
        school_id = payload.get("id_escola")
        if school_id is not None:
            school_id = int(school_id)
            if school_id <= 0:
                raise ValueError
        return jsonify(service.train(school_id)), 200
    except (TypeError, ValueError):
        return jsonify({"erro": "id_escola deve ser um inteiro positivo."}), 400
    except BusinessError as error:
        return jsonify({"erro": str(error)}), 400
    except Exception:
        return jsonify({"erro": "Não foi possível treinar o modelo."}), 500

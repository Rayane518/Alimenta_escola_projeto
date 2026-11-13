from flask import Blueprint, jsonify, request
from app.schemas.prediction_schema import validate_prediction_payload
from app.services.prediction_service import PredictionService
from app.domain.exceptions.business_error import BusinessError

prediction_bp = Blueprint("prediction", __name__)
service = PredictionService()

@prediction_bp.post("/previsao")
def create_prediction():
    try:
        payload = validate_prediction_payload(request.get_json(silent=True))
        result = service.predict(payload)
        return jsonify(result), 201
    except BusinessError as error:
        return jsonify({"erro": str(error)}), 400
    except Exception:
        return jsonify({"erro": "Não foi possível gerar e salvar a previsão."}), 500

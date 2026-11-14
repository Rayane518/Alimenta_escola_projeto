from flask import Blueprint, jsonify, request, current_app
from app.services.training_service import TrainingService
from app.domain.exceptions.business_error import BusinessError

training_bp = Blueprint("training", __name__)
service = TrainingService()


@training_bp.post("/modelo/treinar")
def train_model():
    try:
        payload = request.get_json(silent=True)

        if not isinstance(payload, dict):
            raise BusinessError(
                "Envie um objeto JSON com o id_escola."
            )

        school_id = payload.get("id_escola")

        if school_id is None or isinstance(school_id, bool):
            raise BusinessError(
                "O campo id_escola é obrigatório."
            )

        try:
            school_id = int(school_id)
        except (TypeError, ValueError):
            raise BusinessError(
                "id_escola deve ser um inteiro positivo."
            )

        if school_id <= 0:
            raise BusinessError(
                "id_escola deve ser maior que zero."
            )

        resultado = service.train(school_id)

        return jsonify(resultado), 200

    except BusinessError as error:
        return jsonify({"erro": str(error)}), 400

    except Exception:
        current_app.logger.exception(
            "Erro inesperado ao treinar os modelos."
        )

        return jsonify({
            "erro": "Não foi possível treinar os modelos."
        }), 500

from datetime import date, datetime

from flask import (
    Blueprint,
    jsonify,
    request,
    current_app,
    session
)

from app.schemas.prediction_schema import validate_prediction_payload
from app.services.prediction_service import PredictionService
from app.domain.exceptions.business_error import BusinessError


prediction_bp = Blueprint("prediction", __name__)
service = PredictionService()


@prediction_bp.post("/previsao")
def create_prediction():

    # 1. Verificar autenticação
    id_escola = session.get("id_escola")

    if id_escola is None or session.get("id_usuario") is None:
        return jsonify({
            "erro": "Usuário não autenticado."
        }), 401

    try:
        # 2. Receber os dados enviados pelo frontend
        dados = request.get_json(silent=True)

        if not isinstance(dados, dict):
            raise BusinessError(
                "O corpo da requisição deve ser um objeto JSON."
            )

        # 3. Utilizar somente a escola da sessão
        dados["id_escola"] = id_escola

        # 4. Validar os dados
        payload = validate_prediction_payload(dados)

        # 5. Executar o serviço de previsão
        result = service.predict(payload)

        # 6. Padronizar as datas para o frontend
        for campo in ("data_prevista", "data"):
            valor = result.get(campo)

            if isinstance(valor, (date, datetime)):
                result[campo] = valor.isoformat()

        # 7. Retornar a previsão gerada e salva
        return jsonify(result), 201

    except BusinessError as error:
        return jsonify({
            "erro": str(error)
        }), 400

    except Exception:
        current_app.logger.exception(
            "Erro inesperado ao gerar previsão."
        )

        return jsonify({
            "erro": "Não foi possível gerar e salvar a previsão."
        }), 500

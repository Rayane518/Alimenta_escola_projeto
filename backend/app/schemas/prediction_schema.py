from datetime import date
from app.domain.entities.prediction import PredictionRequest
from app.domain.exceptions.business_error import BusinessError

VALID_SHIFTS = {"MANHÃ", "TARDE"}
VALID_TYPES = {"ANTECIPADA", "ATUALIZADA"}


def validate_prediction_payload(data):
    if not isinstance(data, dict):
        raise BusinessError("O corpo da requisição deve ser um objeto JSON.")

    required = ("id_escola", "data", "turno")
    missing = [field for field in required if data.get(field) in (None, "")]

    if missing:
        raise BusinessError(
            f"Campos obrigatórios ausentes: {', '.join(missing)}."
        )

    try:
        school_id = int(data["id_escola"])
        target_date = date.fromisoformat(data["data"])
    except (TypeError, ValueError):
        raise BusinessError(
            "Informe id_escola inteiro e data no formato AAAA-MM-DD."
        )

    if school_id <= 0:
        raise BusinessError("id_escola deve ser maior que zero.")

    shift = str(data["turno"]).strip().upper()

    if shift not in VALID_SHIFTS:
        raise BusinessError("turno deve ser MANHÃ ou TARDE.")

    prediction_type = str(
        data.get("tipo_previsao", "ANTECIPADA")
    ).strip().upper()

    if prediction_type not in VALID_TYPES:
        raise BusinessError(
            "tipo_previsao deve ser ANTECIPADA ou ATUALIZADA."
        )

    students = data.get("alunos_referencia")

    if students is not None:
        try:
            students = int(students)
        except (TypeError, ValueError):
            raise BusinessError(
                "alunos_referencia deve ser um número inteiro."
            )

        if students < 0:
            raise BusinessError(
                "alunos_referencia não pode ser negativo."
            )

    if prediction_type == "ATUALIZADA" and students is None:
        raise BusinessError(
            "Para previsão ATUALIZADA, informe alunos_referencia confirmados."
        )

    # NOVO: validação da margem de segurança
    safety_margin = data.get("margem_seguranca", 10)

    if type(safety_margin) is not int:
        raise BusinessError(
            "margem_seguranca deve ser um número inteiro."
        )

    if not 0 <= safety_margin <= 20:
        raise BusinessError(
            "margem_seguranca deve estar entre 0 e 20."
        )

    return PredictionRequest(
        school_id=school_id,
        target_date=target_date,
        shift=shift,
        students_reference=students,
        prediction_type=prediction_type,
        menu_description=str(
            data.get("cardapio", "não informado")
        ),
        safety_margin=safety_margin
    )

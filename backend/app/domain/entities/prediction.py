from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class PredictionRequest:
    school_id: int
    target_date: date
    shift: str
    students_reference: int | None = None
    prediction_type: str = "ANTECIPADA"
    menu_description: str = "não informado"
    safety_margin: int = 10
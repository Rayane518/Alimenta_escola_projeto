import pytest
from app.schemas.prediction_schema import validate_prediction_payload
from app.domain.exceptions.business_error import BusinessError

def test_valid_anticipated_prediction():
    request = validate_prediction_payload({"id_escola": 1, "data": "2026-11-13", "turno": "MANHÃ"})
    assert request.school_id == 1
    assert request.shift == "MANHÃ"

def test_invalid_shift():
    with pytest.raises(BusinessError):
        validate_prediction_payload({"id_escola": 1, "data": "2026-11-13", "turno": "NOITE"})

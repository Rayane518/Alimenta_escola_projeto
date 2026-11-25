def prepare_demand_request(expected_students: int) -> dict:
    if expected_students < 0:
        raise ValueError("A quantidade de alunos não pode ser negativa.")
    return {
        "expected_students": expected_students,
        "message": "Modelo de Machine Learning ainda será integrado."
    }

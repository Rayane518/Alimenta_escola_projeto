from datetime import date

from app.domain.exceptions.business_error import BusinessError
from app.repositories.mysql.mysql_meal_repository import MySQLMealRepository


class MealService:

    def __init__(self, repository=None):
        self.repository = repository or MySQLMealRepository()

    def register_meal(self, school_id, data):
        if not isinstance(data, dict):
            raise BusinessError(
                "O corpo da requisição deve ser um objeto JSON."
            )

        try:
            meal_date = date.fromisoformat(data["data"])
        except (KeyError, TypeError, ValueError):
            raise BusinessError(
                "Informe uma data válida no formato AAAA-MM-DD."
            )

        shift = str(data.get("turno", "")).strip().upper()

        if shift not in ("MANHÃ", "TARDE"):
            raise BusinessError(
                "O turno deve ser MANHÃ ou TARDE."
            )

        def validate_integer(field):
            value = data.get(field)

            if type(value) is not int or value < 0:
                raise BusinessError(
                    f"{field} deve ser um inteiro maior ou igual a zero."
                )

            return value

        prepared = validate_integer("refeicoes_preparadas")
        served = validate_integer("refeicoes_servidas")

        if served > prepared:
            raise BusinessError(
                "Refeições servidas não podem ultrapassar "
                "as refeições preparadas."
            )

        menu_id = data.get("id_cardapio")

        if type(menu_id) is not int or menu_id <= 0:
            raise BusinessError(
                "Informe um id_cardapio válido."
            )

        leftovers = prepared - served

        record = {
            "id_escola": school_id,
            "id_cardapio": menu_id,
            "data": meal_date,
            "turno": shift,
            "refeicoes_preparadas": prepared,
            "refeicoes_servidas": served,
            "sobras": leftovers
        }

        record_id = self.repository.save_meal_record(record)

        return {
            "id_registro": record_id,
            **record,
            "data": meal_date.isoformat()
        }
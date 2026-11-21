
from datetime import date

from app.domain.exceptions.business_error import BusinessError
from app.repositories.mysql.mysql_menu_repository import MySQLMenuRepository


class MenuService:

    def __init__(self, repository=None):
        self.repository = repository or MySQLMenuRepository()

    @staticmethod
    def validate_date(value):
        if not isinstance(value, str):
            raise BusinessError(
                "Informe uma data no formato AAAA-MM-DD."
            )

        try:
            parsed_date = date.fromisoformat(value)

            if parsed_date.isoformat() != value:
                raise ValueError

            return parsed_date

        except ValueError:
            raise BusinessError(
                "Informe uma data válida no formato AAAA-MM-DD."
            )

    def register_menu(self, school_id, data):

        if not isinstance(data, dict):
            raise BusinessError(
                "O corpo da requisição deve ser um objeto JSON."
            )

        menu_date = self.validate_date(data.get("data"))

        description = data.get("descricao")

        if not isinstance(description, str):
            raise BusinessError(
                "Informe a descrição do cardápio."
            )

        description = description.strip()

        if not description:
            raise BusinessError(
                "A descrição do cardápio não pode estar vazia."
            )

        menu = {
            "id_escola": school_id,
            "data": menu_date,
            "descricao": description
        }

        menu_id = self.repository.save_menu(menu)

        return {
            "id_cardapio": menu_id,
            "id_escola": school_id,
            "data": menu_date.isoformat(),
            "descricao": description
        }

    def get_menus(self, school_id, target_date=None):

        if target_date is not None:
            target_date = self.validate_date(target_date)

        return self.repository.get_menus(
            school_id,
            target_date
        )

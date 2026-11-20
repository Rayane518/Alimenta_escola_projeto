from app.repositories.mysql.mysql_school_repository import MySQLSchoolRepository
from app.domain.exceptions.business_error import BusinessError


class SchoolService:

    def __init__(self, repository=None):
        self.repository = repository or MySQLSchoolRepository()

    def get_school(self, school_id):
        school = self.repository.get_by_id(school_id)

        if not school:
            raise BusinessError("Escola não encontrada.")

        return school

    def update_school(self, school_id, data):
        if not isinstance(data, dict):
            raise BusinessError("Envie um JSON válido.")

        escola_atual = self.get_school(school_id)

        nome = data.get("nome", escola_atual["nome"])
        endereco = data.get("endereco", escola_atual["endereco"])

        if not isinstance(nome, str) or not nome.strip():
            raise BusinessError("O nome da escola é obrigatório.")

        nome = nome.strip()

        if len(nome) > 150:
            raise BusinessError(
            "O nome da escola deve ter até 150 caracteres."
        )

        if endereco is not None:
            if not isinstance(endereco, str):
                raise BusinessError("Endereço inválido.")

            endereco = endereco.strip()

            if len(endereco) > 255:
                raise BusinessError(
                "O endereço deve ter até 255 caracteres."
            )

        self.repository.update(school_id, nome, endereco)

        return self.get_school(school_id)

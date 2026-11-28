from mysql.connector import IntegrityError

from app.repositories.mysql.mysql_class_repository import MySQLClassRepository
from app.domain.exceptions.business_error import BusinessError


class ClassService:

    def __init__(self, repository=None):
        self.repository = repository or MySQLClassRepository()

    def list_classes(self, school_id):
        return self.repository.list_by_school(school_id)

  
    def create_class(self, school_id, data):
        if not isinstance(data, dict):
            raise BusinessError("Envie um JSON válido.")

        name = data.get("nome")
        age_range = data.get("faixa_etaria")
        shift = data.get("turno")
        students = data.get("quantidade_alunos")

        if not isinstance(name, str) or not name.strip():
            raise BusinessError("O nome da turma é obrigatório.")

        name = name.strip()

        if len(name) > 100:
            raise BusinessError("O nome deve ter até 100 caracteres.")

        if not isinstance(age_range, str) or not age_range.strip():
            raise BusinessError("A faixa etária é obrigatória.")

        age_range = age_range.strip()

        if len(age_range) > 20:
            raise BusinessError("A faixa etária deve ter até 20 caracteres.")

        if shift not in ("MANHÃ", "TARDE"):
            raise BusinessError("O turno deve ser MANHÃ ou TARDE.")

        if type(students) is not int or students < 0:
            raise BusinessError(
                "A quantidade de alunos deve ser um inteiro não negativo."
            )

        try:
            class_id = self.repository.create(
                school_id, name, age_range, shift, students
            )

        except IntegrityError as error:
            if error.errno == 1062:
                raise BusinessError(
                    "Já existe uma turma com esse nome e turno."
                ) from error
            raise

        return self.get_class(school_id, class_id)

    def get_class(self, school_id, class_id):
        if type(class_id) is not int or class_id <= 0:
            raise BusinessError("ID da turma inválido.")

        turma = self.repository.get_by_id(school_id, class_id)

        if not turma:
            raise BusinessError("Turma não encontrada.")

        return turma

    def update_class(self, school_id, class_id, data):
        if not isinstance(data, dict) or not data:
            raise BusinessError("Informe um JSON com os dados da turma.")

        turma_atual = self.get_class(school_id, class_id)

        name = data.get("nome", turma_atual["nome"])
        age_range = data.get("faixa_etaria", turma_atual["faixa_etaria"])
        shift = data.get("turno", turma_atual["turno"])
        students = data.get(
            "quantidade_alunos",
            turma_atual["quantidade_alunos"]
        )

        
        if shift != turma_atual["turno"]:
            if self.repository.has_attendance_history(
                school_id, class_id
            ):
                raise BusinessError(
                    "Não é permitido alterar o turno de uma "
                    "turma que possui histórico de presença."
                )

        if not isinstance(name, str) or not name.strip():
            raise BusinessError("O nome da turma é obrigatório.")

        name = name.strip()

        if len(name) > 100:
            raise BusinessError("O nome deve ter até 100 caracteres.")

        if not isinstance(age_range, str) or not age_range.strip():
            raise BusinessError("A faixa etária é obrigatória.")

        age_range = age_range.strip()

        if len(age_range) > 20:
            raise BusinessError("A faixa etária deve ter até 20 caracteres.")

        if shift not in ("MANHÃ", "TARDE"):
            raise BusinessError("O turno deve ser MANHÃ ou TARDE.")

        if type(students) is not int or students < 0:
            raise BusinessError(
                "A quantidade de alunos deve ser um inteiro não negativo."
            )

        try:
            self.repository.update(
                school_id,
                class_id,
                name,
                age_range,
                shift,
                students
            )

        except IntegrityError as error:
            if error.errno == 1062:
                raise BusinessError(
                    "Já existe uma turma com esse nome e turno."
                ) from error
            raise

        return self.get_class(school_id, class_id)
    
    def update_class_status(self, school_id, class_id, data):
        if not isinstance(data, dict):
            raise BusinessError("Envie um JSON válido.")

        if "ativa" not in data:
            raise BusinessError("Informe o status da turma.")

        active = data["ativa"]

        if type(active) is not bool:
            raise BusinessError(
                "O campo ativa deve ser true ou false."
            )

       
        self.get_class(school_id, class_id)

        self.repository.update_status(
            school_id,
            class_id,
            int(active)
        )

        return self.get_class(school_id, class_id)

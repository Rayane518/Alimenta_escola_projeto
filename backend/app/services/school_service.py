
import re

from app.repositories.mysql.mysql_school_repository import MySQLSchoolRepository
from app.domain.exceptions.business_error import BusinessError


class SchoolService:

    ESTADOS = {
        "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES",
        "GO", "MA", "MT", "MS", "MG", "PA", "PB", "PR",
        "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC",
        "SP", "SE", "TO"
    }

    def __init__(self, repository=None):
        self.repository = repository or MySQLSchoolRepository()

    def get_school(self, school_id):
        school = self.repository.get_by_id(school_id)

        if not school:
            raise BusinessError("Escola não encontrada.")

        return school

    @staticmethod
    def validar_texto(valor, campo, limite, obrigatorio=False):
        if valor is None:
            if obrigatorio:
                raise BusinessError(f"O campo {campo} é obrigatório.")
            return None

        if not isinstance(valor, str):
            raise BusinessError(f"O campo {campo} é inválido.")

        valor = valor.strip()

        if not valor:
            if obrigatorio:
                raise BusinessError(f"O campo {campo} é obrigatório.")
            return None

        if len(valor) > limite:
            raise BusinessError(
                f"O campo {campo} deve ter até {limite} caracteres."
            )

        return valor

    @staticmethod
    def validar_cnpj(cnpj):
        if not re.fullmatch(r"[0-9]{14}", cnpj):
            return False

        if len(set(cnpj)) == 1:
            return False

        pesos_1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
        pesos_2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]

        soma = sum(
            int(digito) * peso
            for digito, peso in zip(cnpj[:12], pesos_1)
        )

        resto = soma % 11
        primeiro = 0 if resto < 2 else 11 - resto

        soma = sum(
            int(digito) * peso
            for digito, peso in zip(
                cnpj[:12] + str(primeiro),
                pesos_2
            )
        )

        resto = soma % 11
        segundo = 0 if resto < 2 else 11 - resto

        return cnpj[-2:] == f"{primeiro}{segundo}"

    def update_school(self, school_id, data):
        if not isinstance(data, dict):
            raise BusinessError("Envie um JSON válido.")

        escola_atual = self.get_school(school_id)

        def obter(campo):
            return data.get(campo, escola_atual.get(campo))

        nome = self.validar_texto(
            obter("nome"), "nome da escola", 150, True
        )

        endereco = self.validar_texto(
            obter("endereco"), "endereço", 255, True
        )

        numero = self.validar_texto(
            obter("numero"), "número", 20, True
        )

        complemento = self.validar_texto(
            obter("complemento"), "complemento", 100
        )

        bairro = self.validar_texto(
            obter("bairro"), "bairro", 100, True
        )

        cidade = self.validar_texto(
            obter("cidade"), "cidade", 100, True
        )

        estado = self.validar_texto(
            obter("estado"), "estado", 2, True
        )

        estado = estado.upper()

        if estado not in self.ESTADOS:
            raise BusinessError("Informe um estado válido.")

        cnpj = self.validar_texto(
            obter("cnpj"), "CNPJ", 18
        )

        if cnpj:
            cnpj = re.sub(r"[./-]", "", cnpj)

            if not self.validar_cnpj(cnpj):
                raise BusinessError("Informe um CNPJ válido.")

        cep = self.validar_texto(
            obter("cep"), "CEP", 9
        )

        if cep:
            cep = cep.replace("-", "")

            if not re.fullmatch(r"[0-9]{8}", cep):
                raise BusinessError(
                    "O CEP deve possuir 8 dígitos."
                )

        telefone = self.validar_texto(
            obter("telefone"), "telefone", 20
        )

        if telefone:
            if not re.fullmatch(r"[0-9()\s-]+", telefone):
                raise BusinessError("Informe um telefone válido.")

            telefone = re.sub(r"[^0-9]", "", telefone)

            if len(telefone) not in (10, 11):
                raise BusinessError(
                    "O telefone deve possuir 10 ou 11 dígitos."
                )

        email = self.validar_texto(
            obter("email"), "e-mail institucional", 150
        )

        if email:
            if not re.fullmatch(
                r"[^@\s]+@[^@\s]+\.[^@\s]+",
                email
            ):
                raise BusinessError("Informe um e-mail válido.")

        atualizado = self.repository.update(
            school_id=school_id,
            name=nome,
            address=endereco,
            cnpj=cnpj,
            cep=cep,
            numero=numero,
            complemento=complemento,
            bairro=bairro,
            cidade=cidade,
            estado=estado,
            telefone=telefone,
            email=email
        )

        if not atualizado:
            raise BusinessError(
                "Não foi possível atualizar os dados da escola."
            )

        return self.get_school(school_id)

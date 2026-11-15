from werkzeug.security import check_password_hash

from app.repositories.mysql.mysql_auth_repository import MySQLAuthRepository
from app.domain.exceptions.business_error import BusinessError


class AuthService:

    def __init__(self, repository=None):
        self.repository = repository or MySQLAuthRepository()

    def login(self, email, senha):

        if not isinstance(email, str) or not isinstance(senha, str):
            raise BusinessError("E-mail e senha são obrigatórios.")

        email = email.strip().lower()

        if not email or not senha:
            raise BusinessError("E-mail e senha são obrigatórios.")

        usuarios = self.repository.find_by_email(email)

        if not usuarios:
            raise BusinessError("E-mail ou senha inválidos.")

        if not usuarios["ativo"]:
            raise BusinessError("E-mail ou senha inválidos.")

        senha_valida = check_password_hash(
            usuarios["senha_hash"],
            senha
        )

        if not senha_valida:
            raise BusinessError("E-mail ou senha inválidos.")

        return {
            "id_usuario": usuarios["id_usuario"],
            "id_escola": usuarios["id_escola"],
            "nome": usuarios["nome"],
            "email": usuarios["email"]
        }

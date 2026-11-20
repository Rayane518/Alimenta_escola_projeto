import re

from mysql.connector import IntegrityError
from werkzeug.security import (
    check_password_hash,
    generate_password_hash
)

from app.repositories.mysql.mysql_auth_repository import MySQLAuthRepository
from app.domain.exceptions.business_error import BusinessError
from app.domain.cpf_validator import validar_cpf


class AuthService:

    def __init__(self, repository=None):
        self.repository = repository or MySQLAuthRepository()

    # ==========================================
    # VALIDAÇÃO DE SENHA
    # ==========================================
    @staticmethod
    def validar_nova_senha(senha):

        if not isinstance(senha, str):
            raise BusinessError(
                "A senha deve ser um texto válido."
            )

        if len(senha) < 8 or len(senha) > 20:
            raise BusinessError(
                "A senha deve conter entre 8 e 20 caracteres."
            )

        if re.search(r"\s", senha):
            raise BusinessError(
                "A senha não pode conter espaços."
            )

        if not re.search(r"[A-Z]", senha):
            raise BusinessError(
                "A senha deve conter pelo menos uma letra maiúscula."
            )

        if not re.search(r"[a-z]", senha):
            raise BusinessError(
                "A senha deve conter pelo menos uma letra minúscula."
            )

        if not re.search(r"[0-9]", senha):
            raise BusinessError(
                "A senha deve conter pelo menos um número."
            )

        if not re.search(r"[^A-Za-z0-9\s]", senha):
            raise BusinessError(
                "A senha deve conter pelo menos um caractere especial."
            )

        return True

    # ==========================================
    # LOGIN DO GESTOR
    # ==========================================
    def login(self, email, senha):

        if not isinstance(email, str) or not isinstance(senha, str):
            raise BusinessError(
                "E-mail e senha são obrigatórios."
            )

        email = email.strip().lower()

        if not email or not senha:
            raise BusinessError(
                "E-mail e senha são obrigatórios."
            )

        usuario = self.repository.find_by_email(email)

        if not usuario or not usuario["ativo"]:
            raise BusinessError(
                "E-mail ou senha inválidos."
            )

        if not check_password_hash(
            usuario["senha_hash"],
            senha
        ):
            raise BusinessError(
                "E-mail ou senha inválidos."
            )

        return {
            "id_usuario": usuario["id_usuario"],
            "id_escola": usuario["id_escola"],
            "nome": usuario["nome"],
            "email": usuario["email"]
        }

    # ==========================================
    # CADASTRO DO GESTOR
    # ==========================================
    def cadastrar_gestor(
        self,
        school_id,
        nome,
        cpf,
        email,
        senha,
        confirmar_senha
    ):

        # Validar escola
        if (
            not isinstance(school_id, int)
            or isinstance(school_id, bool)
            or school_id <= 0
        ):
            raise BusinessError(
                "Escola inválida."
            )

        # Validar nome
        if not isinstance(nome, str) or not nome.strip():
            raise BusinessError(
                "Informe o nome do gestor."
            )

        nome = nome.strip()

        if len(nome) > 150:
            raise BusinessError(
                "O nome deve ter no máximo 150 caracteres."
            )

        # Validar e-mail
        if not isinstance(email, str) or not email.strip():
            raise BusinessError(
                "Informe o e-mail do gestor."
            )

        email = email.strip().lower()

        if len(email) > 150:
            raise BusinessError(
                "O e-mail deve ter no máximo 150 caracteres."
            )

        if not re.fullmatch(
            r"[^@\s]+@[^@\s]+\.[^@\s]+",
            email
        ):
            raise BusinessError(
                "Informe um e-mail válido."
            )

        # Validar CPF
        if not validar_cpf(cpf):
            raise BusinessError(
                "CPF inválido."
            )

        cpf_limpo = cpf.replace(".", "").replace("-", "")

        # Validar senha
        self.validar_nova_senha(senha)

        # Confirmar senha
        if senha != confirmar_senha:
            raise BusinessError(
                "As senhas não coincidem."
            )

        # Verificar e-mail duplicado
        if self.repository.find_by_email(email):
            raise BusinessError(
                "Este e-mail já está cadastrado."
            )

        # Verificar CPF duplicado
        if self.repository.find_by_cpf(cpf_limpo):
            raise BusinessError(
                "Este CPF já está cadastrado."
            )

        # Verificar gestor existente
        if self.repository.find_by_school(school_id):
            raise BusinessError(
                "Esta escola já possui um gestor cadastrado."
            )

        # Gerar hash da senha
        senha_hash = generate_password_hash(senha)

        # Salvar gestor no banco
        try:
            usuario_id = self.repository.create(
                school_id=school_id,
                name=nome,
                cpf=cpf_limpo,
                email=email,
                password_hash=senha_hash
            )

        except IntegrityError:
            raise BusinessError(
                "Não foi possível cadastrar: "
                "e-mail, CPF ou escola já utilizado."
            )

        return {
            "id_usuario": usuario_id,
            "id_escola": school_id,
            "nome": nome,
            "email": email,
            "mensagem": "Gestor cadastrado com sucesso."
        }

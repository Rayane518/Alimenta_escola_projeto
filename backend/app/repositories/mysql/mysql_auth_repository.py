
from app.infrastructure.database.connection import get_connection


class MySQLAuthRepository:

    # CONSULTAR USUÁRIO PELO E-MAIL
    def find_by_email(self, email):
        sql = """
            SELECT
                id_usuario,
                id_escola,
                nome,
                email,
                senha_hash,
                ativo
            FROM usuarios
            WHERE email = %s
            LIMIT 1
        """

        connection = get_connection()
        cursor = None

        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(sql, (email,))
            return cursor.fetchone()

        finally:
            if cursor is not None:
                cursor.close()

            connection.close()

    def find_by_cpf(self, cpf):
        sql = """
            SELECT id_usuario
            FROM usuarios
            WHERE cpf = %s
            LIMIT 1
        """

        connection = get_connection()
        cursor = None

        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(sql, (cpf,))
            return cursor.fetchone()

        finally:
            if cursor is not None:
                cursor.close()

            connection.close()

    # VERIFICAR SE A ESCOLA JÁ POSSUI GESTOR
    def find_by_school(self, school_id):
        sql = """
            SELECT id_usuario
            FROM usuarios
            WHERE id_escola = %s
            LIMIT 1
        """

        connection = get_connection()
        cursor = None

        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(sql, (school_id,))
            return cursor.fetchone()

        finally:
            if cursor is not None:
                cursor.close()

            connection.close()

   
    def create(self, school_id, name, cpf, email, password_hash):
        sql = """
            INSERT INTO usuarios (
                id_escola,
                nome,
                cpf,
                email,
                senha_hash,
                ativo
            )
            VALUES (%s, %s, %s, %s, %s, 1)
        """

        connection = get_connection()
        cursor = None

        try:
            cursor = connection.cursor()

            cursor.execute(
                sql,
                (school_id, name, cpf, email, password_hash)
            )

            connection.commit()

            return cursor.lastrowid

        except Exception:
            connection.rollback()
            raise

        finally:
            if cursor is not None:
                cursor.close()

            connection.close()


from app.infrastructure.database.connection import get_connection


class MySQLAuthRepository:

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

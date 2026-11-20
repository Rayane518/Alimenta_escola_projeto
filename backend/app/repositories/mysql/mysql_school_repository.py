from app.infrastructure.database.connection import get_connection


class MySQLSchoolRepository:

    def get_by_id(self, school_id):
        connection = get_connection()

        try:
            cursor = connection.cursor(dictionary=True)

            cursor.execute(
                """
                SELECT id_escola, nome, endereco, criado_em
                FROM escolas
                WHERE id_escola = %s
                """,
                (school_id,)
            )

            return cursor.fetchone()

        finally:
            connection.close()

    def update(self, school_id, name, address):
        connection = get_connection()

        try:
            cursor = connection.cursor()

            cursor.execute(
                """
                UPDATE escolas
                SET nome = %s, endereco = %s
                WHERE id_escola = %s
                """,
                (name, address, school_id)
            )

            connection.commit()

            return cursor.rowcount > 0

        except Exception:
            connection.rollback()
            raise

        finally:
            connection.close()


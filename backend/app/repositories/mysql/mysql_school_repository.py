
from app.infrastructure.database.connection import get_connection


class MySQLSchoolRepository:

    def get_by_id(self, school_id):
        connection = get_connection()

        try:
            cursor = connection.cursor(dictionary=True)

            cursor.execute(
                """
                SELECT
                    id_escola,
                    nome,
                    endereco,
                    criado_em,
                    cnpj,
                    cep,
                    numero,
                    complemento,
                    bairro,
                    cidade,
                    estado,
                    telefone,
                    email
                FROM escolas
                WHERE id_escola = %s
                """.replace("id_esola", "id_escola"),
                (school_id,)
            )

            return cursor.fetchone()

        finally:
            connection.close()

    def update(
        self,
        school_id,
        name,
        address,
        cnpj,
        cep,
        numero,
        complemento,
        bairro,
        cidade,
        estado,
        telefone,
        email
    ):
        connection = get_connection()

        try:
            cursor = connection.cursor()

            cursor.execute(
                """
                UPDATE escolas
                SET
                    nome = %s,
                    endereco = %s,
                    cnpj = %s,
                    cep = %s,
                    numero = %s,
                    complemento = %s,
                    bairro = %s,
                    cidade = %s,
                    estado = %s,
                    telefone = %s,
                    email = %s
                WHERE id_escola = %s
                """,
                (
                    name,
                    address,
                    cnpj,
                    cep,
                    numero,
                    complemento,
                    bairro,
                    cidade,
                    estado,
                    telefone,
                    email,
                    school_id
                )
            )

            if cursor.rowcount == 0:
                cursor.execute(
                    """
                    SELECT id_escola
                    FROM escolas
                    WHERE id_escola = %s
                    """,
                    (school_id,)
                )

                if cursor.fetchone() is None:
                    connection.rollback()
                    return False

            connection.commit()

            return True

        except Exception:
            connection.rollback()
            raise

        finally:
            connection.close()

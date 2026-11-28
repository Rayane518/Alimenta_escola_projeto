from app.infrastructure.database.connection import get_connection


class MySQLClassRepository:

    def list_by_school(self, school_id):
        connection = get_connection()

        try:
            cursor = connection.cursor(dictionary=True)

            cursor.execute(
                """
                SELECT
                    id_turma,
                    id_escola,
                    nome,
                    faixa_etaria,
                    turno,
                    quantidade_alunos,
                    ativa
                FROM turmas
                WHERE id_escola = %s
                ORDER BY turno, nome
                """,
                (school_id,)
            )

            return cursor.fetchall()

        finally:
            connection.close()

    def create(self, school_id, name, age_range, shift, students):
        connection = get_connection()

        try:
            cursor = connection.cursor()

            cursor.execute(
                """
                INSERT INTO turmas (
                    id_escola,
                    nome,
                    faixa_etaria,
                    turno,
                    quantidade_alunos,
                    ativa
                )
                VALUES (%s, %s, %s, %s, %s, 1)
                """,
                (school_id, name, age_range, shift, students)
            )

            connection.commit()
            return cursor.lastrowid

        except Exception:
            connection.rollback()
            raise

        finally:
            connection.close()

    def get_by_id(self, school_id, class_id):
        connection = get_connection()

        try:
            cursor = connection.cursor(dictionary=True)

            cursor.execute(
                """
                SELECT
                    id_turma,
                    id_escola,
                    nome,
                    faixa_etaria,
                    turno,
                    quantidade_alunos,
                    ativa
                FROM turmas
                WHERE id_turma = %s
                  AND id_escola = %s
                """,
                (class_id, school_id)
            )

            return cursor.fetchone()

        finally:
            connection.close()

    def update(self, school_id, class_id, name, age_range, shift, students):
        connection = get_connection()

        try:
            cursor = connection.cursor()

            cursor.execute(
                """
                UPDATE turmas
                SET nome = %s,
                    faixa_etaria = %s,
                    turno = %s,
                    quantidade_alunos = %s
                WHERE id_turma = %s
                  AND id_escola = %s
                """,
                (
                    name,
                    age_range,
                    shift,
                    students,
                    class_id,
                    school_id
                )
            )

            connection.commit()
            return cursor.rowcount

        except Exception:
            connection.rollback()
            raise

        finally:
            connection.close()

    def update_status(self, school_id, class_id, active):
        connection = get_connection()

        try:
            cursor = connection.cursor()

            cursor.execute(
                """
                UPDATE turmas
                SET ativa = %s
                WHERE id_turma = %s
                  AND id_escola = %s
                """,
                (active, class_id, school_id)
            )

            connection.commit()
            return cursor.rowcount

        except Exception:
            connection.rollback()
            raise

        finally:
            connection.close()

    def has_attendance_history(self, school_id, class_id):
        connection = get_connection()

        try:
            cursor = connection.cursor()

            cursor.execute(
                """
                SELECT EXISTS (
                    SELECT 1
                    FROM presencas p
                    INNER JOIN turmas t
                        ON t.id_turma = p.id_turma
                    WHERE t.id_turma = %s
                      AND t.id_escola = %s
                )
                """,
                (class_id, school_id)
            )

            resultado = cursor.fetchone()

            return bool(resultado[0])

        finally:
            connection.close()

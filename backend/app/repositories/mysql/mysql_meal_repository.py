from app.infrastructure.database.connection import get_connection
from app.repositories.interfaces.meal_repository import MealRepository

class MySQLMealRepository(MealRepository):
    """Implementação MySQL alinhada ao esquema técnico do Alimenta Escola."""

    def fetch_training_history(self, school_id=None):
        # Agrega presenças por escola/data/turno antes de associar os registros
        # de merenda. Isso evita multiplicar refeições ao juntar várias turmas.
        sql = """
            WITH presenca_turno AS (
                SELECT t.id_escola, p.data, t.turno,
                       SUM(p.alunos_previstos) AS alunos_previstos,
                       SUM(p.alunos_presentes) AS alunos_presentes
                FROM presencas p
                INNER JOIN turmas t ON t.id_turma = p.id_turma
                GROUP BY t.id_escola, p.data, t.turno
            )
            SELECT pt.id_escola, pt.data, pt.turno,
                   pt.alunos_previstos, pt.alunos_presentes,
                   c.descricao AS cardapio,
                   rm.refeicoes_preparadas, rm.refeicoes_servidas, rm.sobras
            FROM presenca_turno pt
            LEFT JOIN cardapios c
              ON c.id_escola = pt.id_escola AND c.data = pt.data
            INNER JOIN registros_merenda rm
              ON rm.id_escola = pt.id_escola
             AND rm.data = pt.data AND rm.turno = pt.turno
            WHERE (%s IS NULL OR pt.id_escola = %s)
            ORDER BY pt.data, pt.id_escola, pt.turno
        """
        connection = get_connection()
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(sql, (school_id, school_id))
            rows = cursor.fetchall()
            for row in rows:
                if row.get("data"):
                    row["data"] = row["data"].isoformat()
            return rows
        finally:
            cursor.close()
            connection.close()

    def get_active_enrollment(self, school_id, shift):
        sql = "SELECT COALESCE(SUM(quantidade_alunos), 0) AS total FROM turmas WHERE id_escola = %s AND turno = %s AND ativa = TRUE"
        connection = get_connection()
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(sql, (school_id, shift))
            return int(cursor.fetchone()["total"])
        finally:
            cursor.close()
            connection.close()

    def get_attendance_rate(self, school_id, shift):
        sql = """
            SELECT SUM(p.alunos_presentes) / NULLIF(SUM(p.alunos_previstos), 0) AS taxa
            FROM presencas p
            INNER JOIN turmas t ON t.id_turma = p.id_turma
            WHERE t.id_escola = %s AND t.turno = %s AND t.ativa = TRUE
        """
        connection = get_connection()
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(sql, (school_id, shift))
            result = cursor.fetchone() or {}
            return float(result["taxa"]) if result.get("taxa") is not None else None
        finally:
            cursor.close()
            connection.close()

    def save_prediction(self, prediction):
        sql = """
            INSERT INTO previsoes (
                id_escola,
                data_prevista,
                turno,
                alunos_referencia,
                quantidade_prevista,
                tipo_previsao,
                modelo_utilizado,
                margem_seguranca,
                refeicoes_recomendadas
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        values = (
            prediction["id_escola"],
            prediction["data_prevista"],
            prediction["turno"],
            prediction["alunos_referencia"],
            prediction["quantidade_prevista"],
            prediction["tipo_previsao"],
            prediction["modelo_utilizado"],
            prediction["margem_seguranca"],
            prediction["refeicoes_recomendadas"]
        )

        connection = get_connection()
        cursor = None

        try:
            cursor = connection.cursor()
            cursor.execute(sql, values)
            connection.commit()

            return cursor.lastrowid

        except Exception:
            connection.rollback()
            raise

        finally:
            if cursor is not None:
                cursor.close()

            connection.close()
            
    def get_predictions_history(self, school_id):
        """Consulta as previsões salvas de uma escola."""

        sql = """
            SELECT
                id_previsao,
                id_escola,
                data_prevista,
                turno,
                alunos_referencia,
                quantidade_prevista,
                margem_seguranca,
                refeicoes_recomendadas,
                tipo_previsao,
                modelo_utilizado,
                criado_em
            FROM previsoes
            WHERE id_escola = %s
            ORDER BY criado_em DESC, id_previsao DESC
        """

        connection = get_connection()
        cursor = None

        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(sql, (school_id,))

            rows = cursor.fetchall()

            for row in rows:
                for campo in ("data_prevista", "criado_em"):
                    valor = row.get(campo)

                    if valor is not None:
                        row[campo] = valor.isoformat()

                if row.get("quantidade_prevista") is not None:
                    row["quantidade_prevista"] = float(
                        row["quantidade_prevista"]
                    )

            return rows

        finally:
            if cursor is not None:
                cursor.close()

            connection.close()

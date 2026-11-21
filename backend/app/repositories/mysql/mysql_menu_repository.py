
from app.infrastructure.database.connection import get_connection
from app.repositories.interfaces.menu_repository import MenuRepository


class MySQLMenuRepository(MenuRepository):

    def save_menu(self, menu):
        """Cadastra um novo cardápio."""

        sql = """
            INSERT INTO cardapios (
                id_escola,
                data,
                descricao
            )
            VALUES (%s, %s, %s)
        """

        values = (
            menu["id_escola"],
            menu["data"],
            menu["descricao"]
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
            try:
                if cursor is not None:
                    cursor.close()
            finally:
                connection.close()

    def get_menus(self, school_id, target_date=None):
        """Consulta os cardápios de uma escola."""

        sql = """
            SELECT
                id_cardapio,
                id_escola,
                data,
                descricao
            FROM cardapios
            WHERE id_escola = %s
        """

        values = [school_id]

        if target_date is not None:
            sql += " AND data = %s"
            values.append(target_date)

        sql += " ORDER BY data DESC"

        connection = get_connection()
        cursor = None

        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(sql, tuple(values))

            rows = cursor.fetchall()

            for row in rows:
                if row.get("data") is not None:
                    row["data"] = row["data"].isoformat()

            return rows

        finally:
            try:
                if cursor is not None:
                    cursor.close()
            finally:
                connection.close()

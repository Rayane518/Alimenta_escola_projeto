import mysql.connector
from mysql.connector import Error
from app.infrastructure.config import load_config


def get_connection():
    config = load_config()
    missing = [key for key in ("DB_USER", "DB_NAME") if not config.get(key)]
    if missing:
        raise RuntimeError("Configure DB_USER e DB_NAME no arquivo .env.")
    return mysql.connector.connect(
        host=config["DB_HOST"], port=config["DB_PORT"],
        user=config["DB_USER"], password=config["DB_PASSWORD"],
        database=config["DB_NAME"], connection_timeout=10
    )


def check_connection():
    connection = get_connection()
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchone()
        return True
    finally:
        cursor.close()
        connection.close()

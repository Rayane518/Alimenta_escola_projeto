from app.infrastructure.database.connection import check_connection

def database_status():
    check_connection()
    return {"api": "online", "mysql": "conectado"}
